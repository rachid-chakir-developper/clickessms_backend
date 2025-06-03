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

def get_unavailable_employees(employees):
    if not employees:
        return []
    return [e for e in employees if not is_available(e)]

def get_employees_from_roles(company, roles=[]):
    employees = company.employees.filter(
        managed_companies__roles__name__in=roles,
        is_active=True,
        is_deleted=False
    ).distinct()
    return employees


def get_group_managers(requester):
    if not requester:
        return []

    return requester.company.employees.filter(
        employee_group_manager__employee_group__employee_group_items__employee=requester,
        employee_group_manager__employee_group__is_active=True,
        employee_group_manager__employee_group__is_deleted=False,
    ).exclude(id=requester.id).distinct()

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

    return employees

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
    company = requester.company
    validators = company.employees.none()
    for validation_rule in validation_step.validation_rules.filter(is_active=True, is_deleted=False):
        if (
            is_have_any_roles(validation_rule.target_roles, requester)
            or is_in_groups(validation_rule.target_employee_groups, requester)
            or is_in_list_employees(validation_rule.target_employees, requester)
            or is_have_any_positions(validation_rule.target_positions, requester)
        ):
            continue

        if validation_rule.target_employees.exists():
            validators |= validation_rule.target_employees.filter(is_active=True, is_deleted=False).distinct()
        if validation_rule.validator_type == "CUSTOM":
            if validation_rule.validator_positions.exists():
                validators |= get_employees_from_positions(company=company, roles=validation_rule.validator_positions.all())

            if validation_rule.validator_roles:
                validators |= get_employees_from_roles(company=company, roles=validation_rule.validator_roles)

        # Règle applicable : retour du validateur défini
        elif validation_rule.validator_type == "MANAGER":
            validators |= get_group_managers(requester)

        elif validation_rule.validator_type == "POSITION" and validation_rule.validator_positions.exists():
            validators |= get_employees_from_positions(company=company, positions=validation_rule.validator_positions.all())

        elif validation_rule.validator_type == "ROLE" and validation_rule.validator_roles:
            validators |= get_employees_from_roles(company=company, roles=validation_rule.validator_roles)

    return validators

def resolve_fallbacks(validation_step, requester):
    company = requester.company
    validators = company.employees.none()
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
            return requester.company.employee_admins
            # notify_admin_of_missing_validator(validation_step, requester)
            # Notification uniquement, pas de retour

    return None


def get_validators_for(request_type, requester):
    company = requester.company
    validators = company.employees.none()
    validation_workflow = ValidationWorkflow.objects.filter(
        company=company,
        request_type=request_type,
        is_deleted=False,
        is_active=True
    ).first()

    if not validation_workflow:
        return []

    for validation_step in validation_workflow.validation_steps.filter(is_deleted=False).order_by("order"):
        validators = resolve_validators(validation_step, requester)
        available_validators= get_available_employees(validators)
        if not available_validators:
            fallbacks = resolve_fallbacks(validation_step, requester)
            if fallbacks:
                validators |= fallbacks
    return validators



def get_employees_from_fallback(validation_steps, all_employees, current_employee, request_type):

    company = current_employee.company
    employees_to_return = all_employees.none()
    if not validation_steps:
        return employees_to_return

    for validation_step in validation_steps:
        fallback_rules = validation_step.fallback_rules.filter(is_deleted=False).order_by("order")
        for validation_rule in validation_step.validation_rules.filter(is_active=True, is_deleted=False):
            # --- Demandeurs (current_employees) ---
            target_employees = validation_rule.target_employees.filter(is_active=True, is_deleted=False).distinct()
            unmanaged_target_employees = all_employees.none()

            # Groupes
            if validation_rule.target_employee_groups.exists():
                group_employees = all_employees.filter(
                    employee_items__employee_group__in=validation_rule.target_employee_groups.all(),
                    employee_items__employee_group__is_active=True, employee_items__employee_group__is_deleted=False,
                    is_active=True, is_deleted=False
                ).distinct()
                target_employees |= group_employees

            # Par poste
            if validation_rule.target_positions.exists():
                position_employees = get_employees_from_positions(company=company, roles=validation_rule.target_positions.all())
                target_employees |= position_employees

            # Par rôles
            if validation_rule.target_roles:
                role_employees = get_employees_from_roles(company=company, roles=validation_rule.target_roles)
                target_employees |= role_employees

            # --- Validateurs ---
            validators = all_employees.none()
            validator_employees = validation_rule.validator_employees.all().distinct()
            validators |= validator_employees
            if validation_rule.validator_type == "CUSTOM":
                if validation_rule.validator_positions.exists():
                    validators |= get_employees_from_positions(company=company, roles=validation_rule.validator_positions.all())

                if validation_rule.validator_roles:
                    validators |= get_employees_from_roles(company=company, roles=validation_rule.validator_roles)

            elif validation_rule.validator_type == "MANAGER": # il faut penser aux target_employees qui ont pas des managers
                managers_of_targets = all_employees.filter(
                    employee_group_manager__employee_group__employee_items__employee__in=target_employees,
                    employee_group_manager__employee_group__is_active=True,
                    employee_group_manager__employee_group__is_deleted=False,
                ).distinct()
                validators |= managers_of_targets
                if not get_available_employees(validator_employees):
                    unmanaged_employees = target_employees.exclude(
                        employee_items__employee_group__managers__employee__in=managers_of_targets,
                        employee_items__employee_group__is_active=True,
                        employee_items__employee_group__is_deleted=False,
                    ).distinct()
                    unmanaged_target_employees |= unmanaged_employees

            elif validation_rule.validator_type == "ROLE" and validation_rule.validator_roles:
                validators |= get_employees_from_roles(company=company, roles=validation_rule.validator_roles)

            elif validation_rule.validator_type == "POSITION" and validation_rule.validator_positions.exists():
                validators |= get_employees_from_positions(company=company, roles=validation_rule.validator_positions.all())

            # --- Vérification des validateurs invalides ---
            available_validators = get_available_employees(validators)
            unavailable_validators = get_unavailable_employees(validators)

            # Appliquer les fallbacks dans l'ordre
            for fallback_rule in fallback_rules:
                fallback_candidates = all_employees.none()
                fallback_type = fallback_rule.fallback_type
                target_employees = target_employees.exclude(id__in=employees_to_return.values_list("id", flat=True)).distinct()

                if fallback_type == "REPLACEMENT" or unmanaged_target_employees:
                    for validator in unavailable_validators:
                        if validator.replacement and is_available(validator.replacement):
                            fallback_candidates.add(validator.replacement)
                            if current_employee==validator.replacement:
                                if validation_rule.validator_type == "MANAGER":
                                    managed_employees = target_employees.filter(
                                        employee_items__employee_group__managers__employee=validator,
                                        employee_items__employee_group__is_active=True,
                                        employee_items__employee_group__is_deleted=False,
                                    )
                                    employees_to_return |= managed_employees
                                    employees_to_return |= unmanaged_target_employees
                                    unmanaged_target_employees = all_employees.none()
                                else:
                                    employees_to_return |= target_employees

                elif fallback_type == "HIERARCHY" and not fallback_candidates:
                    target_employees = target_employees.filter(
                        employee_items__employee_group__managers__employee=current_employee,
                        employee_items__employee_group__is_active=True,
                        employee_items__employee_group__is_deleted=False,
                    )
                    employees_to_return |= target_employees

                elif fallback_type == "ADMIN" and not fallback_candidates or unmanaged_target_employees:
                    fallback_candidates |= [
                        admin for admin in company.employee_admins
                        if is_available(admin)
                    ]
                    if current_employee in fallback_candidates:
                        employees_to_return |= target_employees
                        employees_to_return|= unmanaged_target_employees
                        unmanaged_target_employees = all_employees.none()

    return employees_to_return

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
                managed_employees = all_employees.filter(
                    employee_items__employee_group__managers__employee=current_employee,
                    employee_items__employee_group__is_active=True,
                    employee_items__employee_group__is_deleted=False,
                )
                targets |= managed_employees
                continue

            if is_validator:
                rule_targets = all_employees.none()

                if validation_rule.target_employees.exists():
                    rule_targets |= validation_rule.target_employees.filter(company=company, is_active=True, is_deleted=False)
                if validation_rule.target_roles:
                    rule_targets |= get_employees_from_roles(company=current_employee.company, roles=validation_rule.target_roles)
                if validation_rule.target_employee_groups.exists():
                    rule_targets |= all_employees.filter(
                        employee_items__employee_group__managers__employee__in=validation_rule.target_employee_groups.filter(is_active=True, is_deleted=False),
                        employee_items__employee_group__is_active=True,
                        employee_items__employee_group__is_deleted=False,
                    )
                if validation_rule.target_positions.exists():
                    rule_targets |= get_employees_from_positions(company=current_employee.company, positions=validation_rule.target_positions.all())

                targets |= rule_targets
    all_employees = all_employees.exclude(id__in=targets.values_list('id', flat=True))
    targets |= get_employees_from_fallback(
        validation_steps=validation_steps,
        all_employees=all_employees,
        current_employee=current_employee,
        request_type=request_type,
    )
    return targets