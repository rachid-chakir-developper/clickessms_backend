# validation/utils.py

def resolve_validator(step, requester):
    # Étape 1 : vérifier s’il existe une règle personnalisée applicable
    for rule in step.rules.filter(is_active=True, is_deleted=False):
        if rule.target_user and rule.target_user != requester:
            continue
        if rule.target_role and getattr(requester, "role", None) != rule.target_role:
            continue
        if rule.target_service and getattr(requester, "service", None) != rule.target_service:
            continue

        # Règle applicable : retour du validateur défini
        if rule.validator_user:
            return rule.validator_user
        elif rule.validator_role:
            return requester.company.employees.filter(role=rule.validator_role, is_active=True, is_deleted=False).first()
        elif rule.validator_position:
            return requester.company.employees.filter(position=rule.validator_position, is_active=True, is_deleted=False).first()

    # Étape 2 : logique par défaut (fallback standard)
    if step.validator_type == "MANAGER":
        return requester.manager

    elif step.validator_type == "POSITION":
        if step.positions.exists():
            return step.positions.first().employees.filter(is_active=True, is_deleted=False).first()

    elif step.validator_type == "ROLE":
        if step.roles:
            for role in step.roles:
                employee = requester.company.employees.filter(role=role, is_active=True, is_deleted=False).first()
                if employee:
                    return employee

    if step.employees.exists():
        return step.employees.filter(is_active=True).first()

    return None


def resolve_fallback(step, requester):
    for fallback in step.fallbacks.filter(is_deleted=False).order_by("order"):
        if fallback.fallback_type == "HIERARCHY":
            manager = requester.manager
            if is_available(manager):
                return manager

        elif fallback.fallback_type == "POSITION" and fallback.fallback_position:
            employees = requester.company.employees.filter(
                position=fallback.fallback_position, is_active=True, is_deleted=False
            )
            for emp in employees:
                if is_available(emp):
                    return emp

        elif fallback.fallback_type == "ROLE" and fallback.fallback_role:
            employees = requester.company.employees.filter(
                role=fallback.fallback_role, is_active=True, is_deleted=False
            )
            for emp in employees:
                if is_available(emp):
                    return emp

        elif fallback.fallback_type == "ADMIN":
            notify_admin_of_missing_validator(step, requester)
            # Pas de retour — notification seulement

    return None


def is_available(employee):
    return (
        employee
        and employee.is_active
        and not getattr(employee, "is_on_leave", lambda: False)()
    )


def get_validators_for(request_type_code, requester, company):
    validators = []
    workflow = ValidationWorkflow.objects.filter(
        company=company,
        request_type=request_type_code,
        is_deleted=False,
        is_active=True
    ).first()

    if not workflow:
        return []

    for step in workflow.validation_steps.filter(is_deleted=False).order_by("step_order"):
        if step.condition_expression:
            try:
                if not eval(step.condition_expression, {}, {"employee": requester}):
                    continue
            except Exception:
                continue

        validator = resolve_validator(step, requester)
        if not validator or not is_available(validator):
            fallback = resolve_fallback(step, requester)
            if fallback:
                validators.append(fallback)
        else:
            validators.append(validator)

    return validators
