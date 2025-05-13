def resolve_validator(step, requester):
    if step.validator_type == "MANAGER":
        return requester.manager
    elif step.validator_type == "POSITION" and step.position:
        return requester.company.employees.filter(position=step.position, is_active=True).first()
    elif step.validator_type == "ROLE" and step.role:
        return requester.company.employees.filter(role=step.role, is_active=True).first()
    return None


def resolve_fallback(step, requester):
    for fallback in step.fallbacks.filter(is_deleted=False).order_by("order"):
        if fallback.fallback_type == "HIERARCHY":
            manager = requester.manager
            if is_available(manager):
                return manager

        elif fallback.fallback_type == "POSITION" and fallback.fallback_position:
            employee = requester.company.employees.filter(position=fallback.fallback_position, is_active=True).first()
            if is_available(employee):
                return employee

        elif fallback.fallback_type == "ROLE" and fallback.fallback_role:
            employee = requester.company.employees.filter(role=fallback.fallback_role, is_active=True).first()
            if is_available(employee):
                return employee

        elif fallback.fallback_type == "ADMIN":
            notify_admin_of_missing_validator(step, requester)
            # Aucun retour de validator, juste notification
    return None


def is_available(employee):
    return employee and employee.is_active and not getattr(employee, "is_on_leave", lambda: False)()


def get_validators_for(request_type_code, requester, company):
    validators = []
    workflow = ValidationWorkflow.objects.filter(
        company=company,
        request_type=request_type_code,
        is_deleted=False
    ).first()

    if not workflow:
        return []

    for step in workflow.steps.filter(is_deleted=False).order_by("step_order"):
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
