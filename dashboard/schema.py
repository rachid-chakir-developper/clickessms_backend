import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

import datetime
from django.conf import settings
from decimal import Decimal
from statistics import mean

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate

from works.schema import TaskType,TaskActionType
from human_ressources.schema import EmployeeType
from companies.schema import EstablishmentType
from qualities.schema import UndesirableEventType

from works.models import Task, STATUS_All, TaskAction
from qualities.models import UndesirableEvent
from companies.models import Establishment
from human_ressources.models import BeneficiaryEntry
from finance.models import DecisionDocumentItem

class BudgetTaskType(graphene.ObjectType):
    name = graphene.String()
    estimated_budget = graphene.Float()
    spendings = graphene.Float()

class TaskPercentType(graphene.ObjectType):
    label = graphene.String()
    value = graphene.Float()

class UndesirableEventPercentType(graphene.ObjectType):
    label = graphene.String()
    value = graphene.Float()

class BudgetMonthType(graphene.ObjectType):
    date = graphene.String()
    budget = graphene.Float()

class SpendingsMonthType(graphene.ObjectType):
    date = graphene.String()
    spendings = graphene.Float()

class RevenueMonthType(graphene.ObjectType):
    date = graphene.String()
    revenue = graphene.Float()

class TasksWeekType(graphene.ObjectType):
    day = graphene.String()
    count = graphene.Float()

class UndesirableEventsWeekType(graphene.ObjectType):
    day = graphene.String()
    count = graphene.Float()

class ActivityTrackingMonthType(graphene.ObjectType):
    month = graphene.String()
    year = graphene.String()
    entries_count = graphene.Float()
    exits_count = graphene.Float()
    planned_exits_count = graphene.Float()
    presents_month_count = graphene.Float()
    days_count = graphene.Float()
    objective_days_count = graphene.Float()
    gap_days_count= graphene.Float()
    objective_occupancy_rate = graphene.Float()
    occupancy_rate = graphene.Float()
    valuation = graphene.Decimal()
    objective_valuation = graphene.Decimal()
    gap_valuation = graphene.Decimal()

class ActivityTrackingAccumulationType(graphene.ObjectType):
    label = graphene.String()
    year = graphene.String()
    entries_count = graphene.Float()
    exits_count = graphene.Float()
    planned_exits_count = graphene.Float()
    presents_month_count = graphene.Float()
    days_count = graphene.Float()
    objective_days_count = graphene.Float()
    gap_days_count= graphene.Float()
    objective_occupancy_rate = graphene.Float()
    occupancy_rate = graphene.Float()
    valuation = graphene.Decimal()
    objective_valuation = graphene.Decimal()
    gap_valuation = graphene.Decimal()

class ActivityTrackingEstablishmentType(graphene.ObjectType):
    title = graphene.String()
    establishment = graphene.Field(EstablishmentType)
    year = graphene.String()
    months = graphene.List(graphene.String)
    activity_tracking_month = graphene.List(ActivityTrackingMonthType)
    activity_tracking_accumulation = graphene.Field(ActivityTrackingAccumulationType)

class ActivityTrackingType(graphene.ObjectType):
    activity_tracking_month = graphene.List(ActivityTrackingMonthType)
    activity_tracking_accumulation = graphene.Field(ActivityTrackingAccumulationType)

class DashboardType(graphene.ObjectType):
    budget_month = graphene.Field(BudgetMonthType)
    spendings_month = graphene.Field(SpendingsMonthType)
    revenue_month = graphene.Field(RevenueMonthType)
    tasks_week = graphene.List(TasksWeekType)
    task_percent = graphene.List(TaskPercentType)
    tasks = graphene.List(TaskType)
    task_actions = graphene.List(TaskActionType)
    undesirable_events = graphene.List(UndesirableEventType)
    undesirable_event_percent = graphene.List(UndesirableEventPercentType)
    undesirable_events_week = graphene.List(UndesirableEventsWeekType)
    current_employee = graphene.Field(EmployeeType)
    def resolve_tasks_week ( instance, info, **kwargs ):
        date = datetime.date.today()
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(7)
        tasks_week = []
        for i, day in enumerate(settings.DAYS):
            item = TasksWeekType(day = day,  count = 0)
            tasks_week.append(item)
        tasks = Task.objects.filter(starting_date_time__range=[start_week, end_week]).annotate(day=TruncDate('starting_date_time')).values('day').annotate(count=Count("status"))
        for task in tasks:
            tasks_week[task['day'].weekday()].count = task['count']
        return tasks_week
        
    def resolve_undesirable_events_week ( instance, info, **kwargs ):
        user = info.context.user
        company = user.the_current_company
        date = datetime.date.today()
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(7)
        undesirable_events_week = []
        for i, day in enumerate(settings.DAYS):
            item = UndesirableEventsWeekType(day = day,  count = 0)
            undesirable_events_week.append(item)
        undesirable_events = UndesirableEvent.objects.filter(company=company).exclude(status='DRAFT')
        if not user.can_manage_quality():
            if user.is_manager():
                undesirable_events = undesirable_events.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                undesirable_events = undesirable_events.filter(creator=user)
        undesirable_events = undesirable_events.filter(starting_date_time__range=[start_week, end_week]).annotate(day=TruncDate('starting_date_time')).values('day').annotate(count=Count("status"))
        for undesirable_event in undesirable_events:
            undesirable_events_week[undesirable_event['day'].weekday()].count = undesirable_event['count']
        return undesirable_events_week


    def resolve_task_percent(instance, info, **kwargs):
        task_percent = Task.objects.all().values('status').annotate(value=Count('status'))

        return [TaskPercentType(label=Task(status=status['status']).get_status_display(), value=status['value']) for status in task_percent]

    def resolve_tasks(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        tasks = Task.objects.filter(company=company, status__in=['TO_DO', 'PENDING'])
        if not user.can_manage_facility():
            if user.is_manager():
                tasks = tasks.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user) | Q(workers__employee=user.get_employee_in_company()))
            else:
                tasks = tasks.filter(workers__employee=user.get_employee_in_company(), status__in=['TO_DO'])
        return tasks

    def resolve_task_actions(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        return TaskAction.objects.filter(company=company, employees=user.get_employee_in_company()).exclude(status="DONE").order_by('-due_date')[0:10]

    def resolve_undesirable_events(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        undesirable_events = UndesirableEvent.objects.filter(company=company, status="NEW")
        if not user.can_manage_quality():
            if user.is_manager():
                undesirable_events = undesirable_events.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                undesirable_events = undesirable_events.filter(creator=user)
        undesirable_events = undesirable_events.order_by('-created_at').distinct()
        return undesirable_events

    def resolve_current_employee(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        return user.get_employee_in_company(company=company)

def get_item_count(monthly_statistics, establishment_id, month, key):
    establishment_data = monthly_statistics.get(establishment_id, {})
    month_data = establishment_data.get(month, {})
    value = month_data.get(key, 0)
    return round(value, 2)
class DashboardActivityType(graphene.ObjectType):
    activity_tracking = graphene.Field(ActivityTrackingType)
    activity_tracking_establishments = graphene.List(ActivityTrackingEstablishmentType)
    def resolve_activity_tracking(instance, info, **kwargs):
        user = info.context.user
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        # Initialiser les activity_tracking_month par mois
        activity_tracking_month = []
        for i, month in enumerate(settings.MONTHS):  # Assurez-vous que `settings.MONTHS` contient les noms des mois
            item = ActivityTrackingMonthType(
            month=month,
            year=str(date.year),
            objective_days_count=10,
            days_count=4.5,
            gap_days_count=5.5,
            objective_occupancy_rate=10,
            occupancy_rate=2.5,
            valuation=Decimal(8.5),
            objective_valuation=Decimal(10),
            gap_valuation=Decimal(-1.5),
            )  # 'day' utilisé pour le nom du mois
            activity_tracking_month.append(item)

        # Calcul des agrégats pour ActivityTrackingAccumulationType
        objective_days_count_sum = sum(item.objective_days_count for item in activity_tracking_month)
        days_count_sum = sum(item.days_count for item in activity_tracking_month)
        valuation_sum = sum(item.valuation for item in activity_tracking_month)
        objective_valuation_sum = sum(item.objective_valuation for item in activity_tracking_month)
        gap_valuation_sum = sum(item.gap_valuation for item in activity_tracking_month)

        # Calcul de la moyenne pour les pourcentages
        objective_occupancy_rate_avg = mean(item.objective_occupancy_rate for item in activity_tracking_month)
        occupancy_rate_avg = mean(item.occupancy_rate for item in activity_tracking_month)

        activity_tracking_accumulation = ActivityTrackingAccumulationType(
            year=year,
            objective_days_count=objective_days_count_sum,
            days_count=days_count_sum,
            gap_days_count=objective_days_count_sum-days_count_sum,
            objective_occupancy_rate=objective_occupancy_rate_avg,  # Moyenne des pourcentages
            occupancy_rate=occupancy_rate_avg,  # Moyenne des pourcentages
            valuation=valuation_sum,
            objective_valuation=objective_valuation_sum,
            gap_valuation=gap_valuation_sum,
        )
        return ActivityTrackingType(activity_tracking_month=activity_tracking_month, activity_tracking_accumulation=activity_tracking_accumulation)
    def resolve_activity_tracking_establishments(instance, info, **kwargs):
        user = info.context.user
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        establishments = Establishment.objects.filter(company=company)
        beneficiary_entry_monthly_statistics = BeneficiaryEntry.monthly_statistics(year=year, establishments=establishments, company=company)
        decision_document_monthly_statistics = DecisionDocumentItem.monthly_statistics(year=year, establishments=establishments, company=company)
        activity_tracking_establishments = []
        for i, establishment in enumerate(establishments):
            # Initialiser les activity_tracking_month par mois
            activity_tracking_month = []
            for i, month in enumerate(settings.MONTHS):  # Assurez-vous que `settings.MONTHS` contient les noms des mois
                item = ActivityTrackingMonthType(
                month=month,
                year=year,
                entries_count=get_item_count(beneficiary_entry_monthly_statistics, establishment.id, i+1, 'total_entries'),
                exits_count=get_item_count(beneficiary_entry_monthly_statistics, establishment.id, i+1, 'total_releases'),
                planned_exits_count=get_item_count(beneficiary_entry_monthly_statistics, establishment.id, i+1, 'total_due'),
                presents_month_count=get_item_count(beneficiary_entry_monthly_statistics, establishment.id, i+1, 'present_at_end_of_month'),
                objective_days_count=get_item_count(decision_document_monthly_statistics, establishment.id, i+1, 'total_theoretical_number_unit_work'),
                days_count=get_item_count(beneficiary_entry_monthly_statistics, establishment.id, i+1, 'total_days_present'),
                gap_days_count=5.5,
                objective_occupancy_rate=get_item_count(decision_document_monthly_statistics, establishment.id, i+1, 'average_occupancy_rate'),
                occupancy_rate=2.5,
                valuation=Decimal(8.5),
                objective_valuation=Decimal(10),
                gap_valuation=Decimal(-1.5),
                )  # 'day' utilisé pour le nom du mois
                activity_tracking_month.append(item)

            # Calcul des agrégats pour ActivityTrackingAccumulationType
            entries_count_sum = sum(item.entries_count for item in activity_tracking_month)
            exits_count_sum = sum(item.exits_count for item in activity_tracking_month)
            planned_exits_count_sum = sum(item.planned_exits_count for item in activity_tracking_month)
            presents_month_count_sum = sum(item.presents_month_count for item in activity_tracking_month)
            objective_days_count_sum = sum(item.objective_days_count for item in activity_tracking_month)
            days_count_sum = sum(item.days_count for item in activity_tracking_month)
            valuation_sum = sum(item.valuation for item in activity_tracking_month)
            objective_valuation_sum = sum(item.objective_valuation for item in activity_tracking_month)
            gap_valuation_sum = sum(item.gap_valuation for item in activity_tracking_month)

            # Calcul de la moyenne pour les pourcentages
            objective_occupancy_rate_avg = mean(item.objective_occupancy_rate for item in activity_tracking_month)
            occupancy_rate_avg = mean(item.occupancy_rate for item in activity_tracking_month)

            activity_tracking_accumulation = ActivityTrackingAccumulationType(
                label='Cumul à fin Nov.',
                year=year,
                entries_count=round(entries_count_sum, 2),
                exits_count=round(exits_count_sum, 2),
                planned_exits_count=round(planned_exits_count_sum, 2),
                presents_month_count=round(presents_month_count_sum, 2),
                objective_days_count=round(objective_days_count_sum, 2),
                days_count=round(days_count_sum, 2),
                gap_days_count=round(objective_days_count_sum-days_count_sum, 2),
                objective_occupancy_rate=round(objective_occupancy_rate_avg, 2),  # Moyenne des pourcentages
                occupancy_rate=round(occupancy_rate_avg, 2),  # Moyenne des pourcentages
                valuation=round(valuation_sum, 2),
                objective_valuation=round(objective_valuation_sum, 2),
                gap_valuation=round(gap_valuation_sum, 2),
            )
            activity_tracking_establishments.append(
                ActivityTrackingEstablishmentType(
                    months=settings.MONTHS,
                    year=str(date.year),
                    establishment=establishment,
                    activity_tracking_month=activity_tracking_month,
                    activity_tracking_accumulation=activity_tracking_accumulation
                    )
                )
        return activity_tracking_establishments

class DashboardQuery(graphene.ObjectType):
    dashboard = graphene.Field(DashboardType)
    dashboard_activity = graphene.Field(DashboardActivityType)
    def resolve_dashboard(root, info):
        # We can easily optimize query count in the resolve method
        dashboard = 0
        return dashboard
    def resolve_dashboard_activity(root, info):
        # We can easily optimize query count in the resolve method
        dashboard_activity = 0
        return dashboard_activity