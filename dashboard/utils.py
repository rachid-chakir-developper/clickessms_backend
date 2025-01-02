from datetime import date

def calculate_age(birth_date):
    """
    Calcule l'âge d'une personne à partir de sa date de naissance.
    """
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_age_range(present_beneficiaries):
    """
    Retourne la marge d'âge (minimum et maximum) des bénéficiaires présents.

    :param present_beneficiaries: Liste des objets BeneficiaryEntry avec un champ `beneficiary.birth_date`.
    :return: Chaîne indiquant la marge d'âge (ex: "15-17 ans") ou "Aucun bénéficiaire".
    """
    ages = []

    for entry in present_beneficiaries:
        beneficiary = entry.beneficiary
        if not beneficiary or not beneficiary.birth_date:
            continue

        # Calculer l'âge
        age = calculate_age(beneficiary.birth_date)
        ages.append(age)

    if not ages:
        return "-"

    # Calculer le minimum et le maximum
    min_age = min(ages)
    max_age = max(ages)
    if not min_age and not max_age:
        return "-"

    return f"{min_age}-{max_age} ans"
