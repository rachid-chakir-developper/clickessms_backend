from decimal import Decimal

def calculate_amounts(unit_price=0, quantity=1, tva=0, discount=0):
    """
    Calcule le montant HT et le montant TTC à partir du prix unitaire, de la quantité, 
    de la TVA et de la remise.

    :param unit_price: Prix unitaire de l'article (float ou Decimal)
    :param quantity: Quantité d'articles (float ou Decimal)
    :param tva: TVA en pourcentage (float ou Decimal)
    :param discount: Remise en pourcentage (float ou Decimal)
    :return: Tuple (amount_ht, amount_ttc) en Decimal
    """
    unit_price = Decimal(unit_price)
    quantity = Decimal(quantity)
    discount = Decimal(discount) / Decimal(100)
    tva = Decimal(tva) / Decimal(100)

    # Calcul du montant HT après remise
    amount_ht = unit_price * quantity * (Decimal(1) - discount)

    # Calcul du montant TTC après application de la TVA
    amount_ttc = amount_ht * (Decimal(1) + tva)

    return amount_ht, amount_ttc
