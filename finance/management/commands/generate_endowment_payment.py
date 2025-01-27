from django.core.management.base import BaseCommand
from django.db.models import Q
from datetime import datetime
from finance.models import EndowmentPayment, Endowment
from human_ressources.models import BeneficiaryEndowmentEntry
from django.utils import timezone

class Command(BaseCommand):
    help = 'Génère les paiements des dotations pour les bénéficiaires éligibles'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()  # Date du jour

        # Étape 1 : Récupérer les dotations actives pour aujourd'hui
        endowments = Endowment.objects.filter(
            Q(starting_date_time__lte=today),
            Q(ending_date_time__gte=today) | Q(ending_date_time__isnull=True),
            is_active=True,
            is_deleted=False
        )

        for endowment in endowments:
            self.stdout.write(self.style.SUCCESS(f"Dotation: {endowment.id} - {endowment.label}"))
            # Étape 2 : Récupérer les entrées de dotation des bénéficiaires qui sont éligibles aujourd'hui
            eligible_entries = BeneficiaryEndowmentEntry.objects.filter(
                Q(endowment_type=endowment.endowment_type),
                Q(starting_date__lte=today),
                Q(ending_date__gte=today) | Q(ending_date__isnull=True)
            )

            for entry in eligible_entries:
                # Étape 3 : Vérification des critères supplémentaires (genre, âge, statut professionnel)
                self.stdout.write(self.style.SUCCESS(f"entry de *{entry.beneficiary.first_name}* : starting_date- {entry.starting_date.date()} - ending_date- {entry.ending_date}"))
                if not self.is_eligible_based_on_additional_criteria(entry, endowment):
                    continue  # Si le bénéficiaire ne correspond pas aux critères, on passe au suivant

                # Vérifier si un paiement a déjà été généré pour cette date
                existing_payment = EndowmentPayment.objects.filter(
                    beneficiary=entry.beneficiary,
                    endowment_type=endowment.endowment_type,
                    date=today,
                    is_deleted=False
                )

                if not existing_payment.exists():  # Si pas de paiement existant pour aujourd'hui
                    # Étape 4 : Générer un nouveau paiement uniquement si la date correspond à la récurrence
                    self.stdout.write(self.style.SUCCESS(f"existing_payment.exists(): {endowment.amount_allocated} - {today}"))
                    if self.is_payment_due_for_recurring(endowment, today):
                        EndowmentPayment.objects.create(
                            label=f"Paiement {endowment.label} - {entry.beneficiary.first_name} - {today}",  # Libellé descriptif
                            beneficiary=entry.beneficiary,
                            endowment_type=endowment.endowment_type,
                            endowment=endowment,
                            amount=endowment.amount_allocated,  # Le montant est extrait de l'Endowment
                            date=today,
                            company=entry.beneficiary.company,
                            creator=entry.beneficiary.creator  # Ajoutez l'utilisateur ou la logique pour le créateur
                        )
                        self.stdout.write(self.style.SUCCESS(f"Paiement généré pour {entry.beneficiary} - {endowment.label}"))

    def is_eligible_based_on_additional_criteria(self, entry, endowment):
        """Vérifie si un bénéficiaire respecte les critères supplémentaires (genre, âge, statut professionnel)"""
        self.stdout.write(self.style.SUCCESS(
            f"endowment.gender {endowment.gender} - entry.beneficiary.gender {entry.beneficiary.gender}")
        )
        self.stdout.write(self.style.SUCCESS(
            f"endowment.professional_status {endowment.professional_status.name} - entry.beneficiary.professional_status {entry.beneficiary.professional_status.name}")
        )
        
        # Vérification du genre
        if endowment.gender:
            if entry.beneficiary.gender != endowment.gender:
                return False  # Le genre ne correspond pas

        # Vérification de l'âge
        if endowment.age_min and endowment.age_max:
            # Vérifie que l'âge est dans l'intervalle
            if not (entry.beneficiary.age >= endowment.age_min and entry.beneficiary.age <= endowment.age_max):
                return False  # L'âge est en dehors de la plage définie
        elif endowment.age_min:
            # Vérifie que l'âge est supérieur ou égal à age_min
            if entry.beneficiary.age < endowment.age_min:
                return False  # L'âge est inférieur à l'âge minimum
        elif endowment.age_max:
            # Vérifie que l'âge est inférieur ou égal à age_max
            if entry.beneficiary.age > endowment.age_max:
                return False  # L'âge est supérieur à l'âge maximum

        # Vérification du statut professionnel
        if endowment.professional_status:
            if entry.beneficiary.professional_status != endowment.professional_status:
                return False  # Le statut professionnel ne correspond pas

        # Si toutes les vérifications passent, le bénéficiaire est éligible
        return True

    def is_payment_due_for_recurring(self, endowment, today):
        """Vérifie si le paiement est dû en fonction de la récurrence"""
        if endowment.recurrence_frequency == 'DAILY':
            # Tous les jours sont valides pour la récurrence quotidienne
            return True
        elif endowment.recurrence_frequency == 'WEEKLY':
            # Pour la récurrence hebdomadaire, on vérifie si aujourd'hui est le jour de la semaine correspondant
            return today.weekday() == 0  # Assurez-vous` contient l'indice du jour (0=Monday, 6=Sunday)
        elif endowment.recurrence_frequency == 'MONTHLY':
            # Pour la récurrence mensuelle, on vérifie si aujourd'hui est le 1er du mois
            return today.day == 1
        elif endowment.recurrence_frequency == 'YEARLY':
            # Pour la récurrence annuelle, on vérifie si aujourd'hui est le 1er janvier
            return today.month == 1 and today.day == 1
        return False  # Par défaut, aucune récurrence n'est due
