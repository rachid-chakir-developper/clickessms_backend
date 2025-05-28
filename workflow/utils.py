from django.db.models import Q
from django.utils import timezone
from workflow.models import ValidationWorkflow

def is_available(employee):
    return (
        employee
        and employee.is_active
        and not employee.is_deleted
        and not getattr(employee, "is_on_leave", lambda: False)()
    )
def get_available_employees(employees):
    if not employees:
        return []

    return [e for e in employees if is_available(e)]

def get_employees_from_roles(company, roles=[]):
    employees = company.employees.filter(
        managed_companies__roles__name__in=roles,
        is_active=True,
        is_deleted=False
    ).distinct()
    return get_available_employees(employees) if employees else []


def get_group_managers(requester):
    if not requester:
        return []

    employee_items = requester.employee_items.select_related('employee_group').filter(
        employee_group__is_deleted=False,
        employee_group__is_active=True,
    ).prefetch_related('employee_group__managers__employee').distinct()

    managers = []

    for employee_item in employee_items:
        group = employee_item.employee_group
        for manager_link in group.managers.all():
            manager = manager_link.employee
            if manager and is_available(manager) and manager != requester:
                managers.append(manager)

    # Éliminer les doublons par ID
    unique_managers = list({m.id: m for m in managers}.values())
    return get_available_employees(unique_managers)

def get_employees_from_positions(company, positions=[]):
    """
    Retourne les employés disponibles (actifs, non supprimés, même entreprise que le requester)
    à partir d'une liste de positions.
    """
    current_time = timezone.now()

    employees = company.employees.filter(
        Q(employee_contracts__ending_date__isnull=True) | Q(employee_contracts__ending_date__gte=current_time),
        employee_contracts__starting_date__lte=current_time,
        employee_contracts__position__in=positions,
        employee_contracts__is_active=True,
        employee_contracts__is_deleted=False,
        is_active=True,
        is_deleted=False
    ).distinct()

    return get_available_employees(employees) if employees else []

def is_have_any_roles(target_roles, requester):
    if not target_roles or not requester:
        return False
    requester_user = requester.user
    requester_roles = requester_user.get_roles_in_company()
    if not requester_roles:
        return False
    return any(role in requester_roles for role in target_roles)

def is_in_groups(target_employee_groups, requester):
    if not requester or not target_employee_groups:
        return False

    return requester.employee_items.filter(
        employee_group__in=target_employee_groups,
        employee_group__is_deleted=False
    ).exists()

def is_in_list_employees(target_employees, requester):
    if not target_employees or not requester:
        return False
    return requester in target_employees

def is_have_any_positions(target_positions, requester):
    if not target_positions or not requester:
        return False

    employee_position = getattr(getattr(requester, "current_contract", None), "employee_position", None)
    if not employee_position:
        return False

    return employee_position in target_positions

def resolve_validators(validation_step, requester):
    # Étape 1 : vérifier s’il existe une règle personnalisée applicable
    for validation_rule in validation_step.validation_rules.filter(is_active=True, is_deleted=False):
        if (
            is_have_any_roles(validation_rule.target_roles, requester)
            or is_in_groups(validation_rule.target_employee_groups, requester)
            or is_in_list_employees(validation_rule.target_employees, requester)
            or is_have_any_positions(validation_rule.target_positions, requester)
        ):
            continue

        # Règle applicable : retour du validateur défini
        if validation_rule.validator_type == "MANAGER":
            return get_group_managers(requester)

        elif validation_rule.validator_type == "POSITION":
            employees = get_employees_from_positions(company=requester.company, positions=validation_rule.validator_positions.all())
            return employees

        elif validation_rule.validator_type == "ROLE":
            employees = get_employees_from_roles(company=requester.company, roles=validation_rule.validator_roles)
            return employees

        if validation_rule.target_employees.exists():
            return validation_rule.target_employees.filter(is_active=True, is_deleted=False).distinct()

    return None

def resolve_fallbacks(validation_step, requester):
    for fallback_rule in validation_step.fallback_rules.filter(is_deleted=False).order_by("order"):
        if fallback_rule.fallback_type == "REPLACEMENT":
            replacements = getattr(requester, "replacements", None)
            if get_available_employees(replacements):
                return replacements

        elif fallback_rule.fallback_type == "HIERARCHY":
            managers = get_group_managers(requester)
            if get_available_employees(managers):
                return managers

        elif fallback_rule.fallback_type == "ADMIN":
            return requester.company.company_admins
            # notify_admin_of_missing_validator(validation_step, requester)
            # Notification uniquement, pas de retour

    return None


def get_validators_for(request_type, requester):
    company = requester.company
    validators = []
    validation_workflow = ValidationWorkflow.objects.filter(
        company=company,
        request_type=request_type,
        is_deleted=False,
        is_active=True
    ).first()

    if not validation_workflow:
        return []

    for validation_step in validation_workflow.validation_steps.filter(is_deleted=False).order_by("order"):
        if validation_step.condition_expression:
            try:
                if not eval(validation_step.condition_expression, {}, {"employee": requester}):
                    continue
            except Exception:
                continue

        list_validators = resolve_validators(validation_step, requester)
        available_validators = get_available_employees(list_validators)
        if not available_validators:
            fallbacks = resolve_fallbacks(validation_step, requester)
            if fallbacks:
                validators.extend(fallbacks)
        else:
            validators.extend(available_validators)

    return validators

def get_target_employees_for_request_type(current_employee, request_type):
    company = current_employee.company
    validation_workflow = ValidationWorkflow.objects.filter(
        request_type=request_type,
        company=company,
        is_active=True,
        is_deleted=False
    ).first()
    
    if not validation_workflow:
        return company.employees.none()

    validation_steps = validation_workflow.validation_steps.filter(is_deleted=False)
    all_employees = company.employees.filter(is_deleted=False)

    targets = all_employees.none()

    for validation_step in validation_steps:
        for validation_rule in validation_step.validation_rules.filter(is_active=True, is_deleted=False):
            is_validator = False

            if is_have_any_roles(validation_rule.validator_roles, current_employee):
                is_validator = True
            elif is_in_list_employees(validation_rule.validator_employees.filter(company=company, is_active=True, is_deleted=False), current_employee):
                is_validator = True
            elif is_have_any_positions(validation_rule.validator_positions.all(), current_employee):
                is_validator = True
            elif validation_rule.validator_type == "MANAGER":
                managed_employees = all_employees.filter(employee_groups__managers=current_employee)
                targets |= managed_employees
                continue

            if is_validator:
                rule_targets = all_employees.none()

                if validation_rule.target_employees.exists():
                    rule_targets |= validation_rule.target_employees.filter(company=company, is_active=True, is_deleted=False)
                if validation_rule.target_roles:
                    rule_targets |= get_employees_from_roles(company=current_employee.company, roles=validation_rule.target_roles)
                if validation_rule.target_employee_groups.exists():
                    rule_targets |= all_employees.filter(employee_groups__in=validation_rule.target_employee_groups.filter(is_active=True, is_deleted=False), is_active=True, is_deleted=False)
                if validation_rule.target_positions.exists():
                    rule_targets |= get_employees_from_positions(company=current_employee.company, positions=validation_rule.target_positions.all())

                targets |= rule_targets
    return targets

def get_employees_following_fallback_due_to_invalid_validators(current_employee, request_type):

    employees_to_return = set()
    company = current_employee.company
    validation_workflow = ValidationWorkflow.objects.filter(
        request_type=request_type,
        company=company,
        is_active=True,
        is_deleted=False
    ).first()
    
    if not validation_workflow:
        return company.employees.none()

    validation_steps = validation_workflow.validation_steps.filter(is_deleted=False)
    all_employees = company.employees.filter(is_active=True, is_deleted=False)

    for validation_step in validation_steps:
        for validation_rule in validation_step.validation_rules.filter(is_active=True, is_deleted=False):
            # --- Demandeurs (current_employees) ---
            target_employees = set(validation_rule.target_employees.filter(is_active=True, is_deleted=False))

            # Groupes
            if validation_rule.target_employee_groups.exists():
                group_employees = all_employees.filter(
                    employee_items__employee_group__in=validation_rule.target_employee_groups.all(),
                    employee_items__employee_group__is_active=True, employee_items__employee_group__is_deleted=False,
                    is_active=True, is_deleted=False
                ).distinct()
                target_employees.update(group_employees)

            # Par poste
            if validation_rule.target_positions.exists():
                position_employees = get_employees_from_positions(company=company, roles=validation_rule.target_positions.all())
                target_employees.update(position_employees)

            # Par rôles
            if validation_rule.target_roles:
                role_employees = get_employees_from_roles(company=company, roles=validation_rule.target_roles)
                target_employees.update(role_employees)

            # --- Validateurs ---
            validators = set()

            if validation_rule.validator_type == "CUSTOM":
                validators.update(validation_rule.validator_employees.all())

                if validation_rule.validator_positions.exists():
                    validators.update(get_employees_from_positions(company=company, roles=validation_rule.validator_positions.all()))

                if validation_rule.validator_roles:
                    validators.update(get_employees_from_roles(company=company, roles=validation_rule.validator_roles))

            elif validation_rule.validator_type == "MANAGER":
                managers_of_targets = all_employees.filter(
                    employee_group_manager__employee_group__employee_items__employee__in=target_employees,
                    employee_group_manager__employee_group__is_active=True,
                    employee_group_manager__employee_group__is_deleted=False,
                ).distinct()
                validators.update(managers_of_targets)

            elif validation_rule.validator_type == "ROLE" and validation_rule.validator_roles:
                validators.update(get_employees_from_roles(company=company, roles=validation_rule.validator_roles))

            elif validation_rule.validator_type == "POSITION" and validation_rule.validator_positions.exists():
                validators.update(get_employees_from_positions(company=company, roles=validation_rule.validator_positions.all()))

            # --- Vérification des validateurs invalides ---
            invalid_validators = {v for v in validators if not is_available(v)}
            # Appliquer les fallbacks dans l'ordre
            for fallback_rule in validation_step.fallback_rules.filter(is_deleted=False).order_by("order"):
                fallback_type = fallback_rule.fallback_type

                fallback_candidates = set()

                if fallback_type == "REPLACEMENT":
                    for validator in invalid_validators:
                        if validator.replacement and is_available(validator.replacement):
                            fallback_candidates.add(validator.replacement)
                    if current_employee in fallback_candidates:
                        employees_to_return.update(target_employees)

                elif fallback_type == "HIERARCHY" and not fallback_candidates and not validators:
                    target_employees = target_employees.filter(employee_groups__managers=current_employee)
                    targets |= managed_employees

                elif fallback_type == "ADMIN":
                    fallback_candidates.update([
                        admin for admin in company.company_admins.filter(is_active=True, is_deleted=False)
                        if is_available(admin)
                    ])

                # Si l’employé connecté fait partie des fallback_candidates, il doit valider
                if current_employee in fallback_candidates:
                    employees_to_return.update(target_employees)
                    break  # inutile de tester d’autres fallbacks, on a trouvé

    return all_employees.filter(id__in=employees_to_return)