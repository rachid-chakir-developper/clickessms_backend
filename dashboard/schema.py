import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

import datetime
from calendar import monthrange
from django.conf import settings
from decimal import Decimal
from statistics import mean
from django.core.exceptions import PermissionDenied

from django.db.models import Sum, Count, Q, Case, When
from django.db.models.functions import TruncDate


from dashboard.utils import get_age_range
from dashboard.models import DashboardComment

from works.schema import TaskType,TaskActionType
from human_ressources.schema import EmployeeType
from companies.schema import EstablishmentType
from qualities.schema import UndesirableEventType

from works.models import Task, STATUS_All, TaskAction
from qualities.models import UndesirableEvent
from companies.models import Establishment
from human_ressources.models import BeneficiaryEntry, BeneficiaryAdmission
from finance.models import DecisionDocumentItem
from human_ressources.schema import BeneficiaryType, BeneficiaryEntryType, BeneficiaryAdmissionType

class DashboardCommentType(DjangoObjectType):
    class Meta:
        model = DashboardComment
        fields = "__all__"

class DashboardCommentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    text = graphene.String(required=False)
    comment_type = graphene.String(required=False)
    year = graphene.String(required=False)
    month = graphene.String(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class DashboardActivityFilterInput(graphene.InputObjectType):
        keyword = graphene.String(required=False)
        year = graphene.String(required=False)
        month = graphene.String(required=False)
        establishments = graphene.List(graphene.Int, required=False)

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
    year = graphene.String()
    month = graphene.String()
    is_current_month = graphene.Boolean()
    is_future_month = graphene.Boolean()
    entries_count = graphene.Float()
    entry_beneficiary_entries = graphene.List(BeneficiaryEntryType)
    exits_count = graphene.Float()
    release_beneficiary_entries = graphene.List(BeneficiaryEntryType)
    planned_exits_count = graphene.Float()
    due_beneficiary_entries = graphene.List(BeneficiaryEntryType)
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

class ActivityBeneficiaryMonthType(graphene.ObjectType):
    year = graphene.String()
    month = graphene.String()
    is_current_month = graphene.Boolean()
    is_future_month = graphene.Boolean()
    days_count = graphene.Float()

class ActivityBeneficiaryType(graphene.ObjectType):
    year = graphene.String()
    beneficiary = graphene.Field(BeneficiaryType)
    days_count = graphene.Float()
    activity_beneficiary_months = graphene.List(ActivityBeneficiaryMonthType)

class ActivityBeneficiaryEstablishmentType(graphene.ObjectType):
    title = graphene.String()
    establishment = graphene.Field(EstablishmentType)
    year = graphene.String()
    months = graphene.List(graphene.String)
    activity_beneficiaries = graphene.List(ActivityBeneficiaryType)

class ActivitySynthesisMonthType(graphene.ObjectType):
    label = graphene.String()
    month = graphene.String()
    year = graphene.String()
    count_received = graphene.Int()
    gap_received = graphene.Int()
    count_approved = graphene.Int()
    count_rejected = graphene.Int()
    gap_rejected = graphene.Int()
    count_canceled = graphene.Int()
    capacity = graphene.Int()
    count_occupied_places = graphene.Int()
    count_available_places = graphene.Int()
    dashboard_comments = graphene.List(DashboardCommentType)
    dashboard_comment = graphene.Field(DashboardCommentType)
    beneficiary_admissions = graphene.List(BeneficiaryAdmissionType)
    beneficiary_entries = graphene.List(BeneficiaryEntryType)

class ActivityTotalSynthesisMonthType(graphene.ObjectType):
    label = graphene.String()
    month = graphene.String()
    year = graphene.String()
    total_received = graphene.Int()
    total_gap_received = graphene.Int()
    total_approved = graphene.Int()
    total_rejected = graphene.Int()
    total_gap_rejected = graphene.Int()
    total_canceled = graphene.Int()
    total_available_places = graphene.Int()
    total_dashboard_comment = graphene.Int()

class ActivitySynthesisEstablishmentType(graphene.ObjectType):
    title = graphene.String()
    establishment = graphene.Field(EstablishmentType)
    year = graphene.String()
    months = graphene.List(graphene.String)
    activity_synthesis_month = graphene.List(ActivitySynthesisMonthType)
    activity_total_synthesis_month = graphene.Field(ActivityTotalSynthesisMonthType)

class ActivitySynthesisType(graphene.ObjectType):
    title = graphene.String()
    year = graphene.String()
    months = graphene.List(graphene.String)
    month_totals = graphene.List(graphene.Int)
    activity_synthesis_establishments = graphene.List(ActivitySynthesisEstablishmentType)

class ActivityMonthEstablishmentType(graphene.ObjectType):
    title = graphene.String()
    establishment = graphene.Field(EstablishmentType)
    year = graphene.String()
    month = graphene.String()
    capacity = graphene.Int()
    count_outside_places_department = graphene.Int()
    count_occupied_places = graphene.Int()
    count_available_places = graphene.Int()
    ages_text = graphene.String()
    beneficiary_entries = graphene.List(BeneficiaryEntryType)

class ActivityMonthType(graphene.ObjectType):
    title = graphene.String()
    year = graphene.String()
    month = graphene.String()
    activity_month_establishments = graphene.List(ActivityMonthEstablishmentType)

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
        
    def resolve_undesirable_events_week( instance, info, **kwargs ):
        user = info.context.user
        company = user.the_current_company
        date = datetime.date.today()
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(7)
        undesirable_events_week = []
        for i, day in enumerate(settings.DAYS):
            item = UndesirableEventsWeekType(day = day,  count = 0)
            undesirable_events_week.append(item)
        undesirable_events = UndesirableEvent.objects.filter(company=company, is_deleted=False).exclude(status='DRAFT')
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
        tasks = Task.objects.filter(company=company, is_deleted=False, status__in=['TO_DO', 'PENDING'])
        if not user.can_manage_facility():
            if user.is_manager():
                tasks = tasks.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user) | Q(workers__employee=user.get_employee_in_company()))
            else:
                tasks = tasks.filter(workers__employee=user.get_employee_in_company(), status__in=['TO_DO'])
        tasks = tasks.distinct()
        return tasks

    def resolve_task_actions(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        return TaskAction.objects.filter(company=company, is_deleted=False, employees=user.get_employee_in_company()).exclude(status="DONE").order_by('-due_date').distinct()[0:10]

    def resolve_undesirable_events(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        undesirable_events = UndesirableEvent.objects.filter(company=company, is_deleted=False, status="NEW")
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
    return round(value if value else 0, 2)
def get_item_object(monthly_statistics, establishment_id, month, key):
    establishment_data = monthly_statistics.get(establishment_id, {})
    month_data = establishment_data.get(month, {})
    value = month_data.get(key, [])
    return value
class DashboardActivityType(graphene.ObjectType):
    activity_tracking_establishments = graphene.List(ActivityTrackingEstablishmentType)
    activity_beneficiary_establishments = graphene.List(ActivityBeneficiaryEstablishmentType)
    activity_synthesis = graphene.Field(ActivitySynthesisType)
    activity_month = graphene.Field(ActivityMonthType)

    def resolve_activity_tracking_establishments(instance, info, **kwargs):
        user = info.context.user
        dashboard_activity_filter = getattr(info.context, 'dashboard_activity_filter', None)
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        current_year = date.year
        current_month = date.month
        prev_month_index = 11
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        establishments = Establishment.objects.filter(company=company)

        if dashboard_activity_filter:
            the_year = dashboard_activity_filter.get('year', None)
            establishment_ids = dashboard_activity_filter.get('establishments', None)
            if the_year:
                year=the_year
            if establishment_ids:
                order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(establishment_ids)])
                establishments=establishments.filter(id__in=establishment_ids).annotate(ordering=order).order_by('ordering')
        if user.is_manager() and not user.can_manage_activity():
            establishments = establishments.filter(
                Q(managers__employee=user.get_employee_in_company()) | 
                Q(establishment_parent__managers__employee=user.get_employee_in_company())
            )

        beneficiary_entry_monthly_presence_statistics = BeneficiaryEntry.monthly_presence_statistics(year=year, establishments=establishments, company=company)
        decision_document_monthly_statistics = DecisionDocumentItem.monthly_statistics(year=year, establishments=establishments, company=company)

        activity_tracking_establishments = []
        for j, establishment in enumerate(establishments):
            # Initialiser les activity_tracking_month par mois
            activity_tracking_month = []
            children_establishments = establishment.get_all_children()
            children_beneficiary_entry_monthly_presence_statistics=None
            children_document_monthly_statistics=None
            if len(children_establishments)> 0:
                children_beneficiary_entry_monthly_presence_statistics = BeneficiaryEntry.monthly_presence_statistics(year=year, establishments=children_establishments, company=company)
                children_document_monthly_statistics = DecisionDocumentItem.monthly_statistics(year=year, establishments=children_establishments, company=company)
            for i, month in enumerate(settings.MONTHS):  # Assurez-vous que `settings.MONTHS` contient les noms des mois
                is_current_month = (int(year) == current_year and i+1 == current_month)
                prev_month_index = i - 1 if i > 0 and is_current_month else prev_month_index
                is_future_month = (int(year) > current_year) or (int(year) == current_year and i+1 > current_month)
                days_in_month = monthrange(int(year), i+1)[1]

                capacity = establishment.get_monthly_capacity(year, i+1)
                price = establishment.get_monthly_unit_price(year, i+1)
                objective_occupancy_rate = get_item_count(decision_document_monthly_statistics, establishment.id, i+1, 'occupancy_rate')

                days_count=0
                entries_count=0
                entry_beneficiary_entries=[]
                exits_count=0
                release_beneficiary_entries=[]
                planned_exits_count=0
                due_beneficiary_entries=[]
                presents_month_count=0

                if children_beneficiary_entry_monthly_presence_statistics:
                    capacity_total = 0
                    for k, children_establishment in enumerate(children_establishments):
                        if not price or price==0:
                            price = children_establishment.get_monthly_unit_price(year, i+1)
                        if not objective_occupancy_rate or objective_occupancy_rate==0:
                            objective_occupancy_rate = get_item_count(children_document_monthly_statistics, children_establishment.id, i+1, 'occupancy_rate')
                        capacity_total+= children_establishment.get_monthly_capacity(year, i+1)
                        days_count+=get_item_count(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'total_days_present')
                        entries_count+=get_item_count(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'total_entries')
                        entry_beneficiary_entries+=get_item_object(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'entry_beneficiary_entries')
                        exits_count+=get_item_count(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'total_releases')
                        release_beneficiary_entries+=get_item_object(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'release_beneficiary_entries')
                        planned_exits_count+=get_item_count(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'total_due')
                        due_beneficiary_entries+=get_item_object(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'due_beneficiary_entries')
                        presents_month_count+=get_item_count(children_beneficiary_entry_monthly_presence_statistics, children_establishment.id, i+1, 'present_at_end_of_month')
                    if not capacity or capacity==0:
                        capacity = capacity_total
                else:
                    days_count=get_item_count(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'total_days_present')
                    entries_count=get_item_count(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'total_entries')
                    entry_beneficiary_entries=get_item_object(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'entry_beneficiary_entries')
                    exits_count=get_item_count(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'total_releases')
                    release_beneficiary_entries=get_item_object(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'release_beneficiary_entries')
                    planned_exits_count=get_item_count(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'total_due')
                    due_beneficiary_entries=get_item_object(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'due_beneficiary_entries')
                    presents_month_count=get_item_count(beneficiary_entry_monthly_presence_statistics, establishment.id, i+1, 'present_at_end_of_month')

                objective_days_count=round(days_in_month*capacity*objective_occupancy_rate/100)
                objective_valuation = Decimal(capacity)*Decimal(price)
                valuation = Decimal(days_count)*Decimal(price)


                item = ActivityTrackingMonthType(
                    month=month,
                    is_current_month=is_current_month,
                    is_future_month=is_future_month,
                    year=year,
                    entries_count=entries_count,
                    entry_beneficiary_entries=entry_beneficiary_entries,
                    exits_count=exits_count,
                    release_beneficiary_entries=release_beneficiary_entries,
                    planned_exits_count=planned_exits_count,
                    due_beneficiary_entries=due_beneficiary_entries,
                    presents_month_count=presents_month_count,
                    objective_days_count=objective_days_count,
                    days_count=days_count,
                    gap_days_count=days_count-objective_days_count,
                    objective_occupancy_rate=objective_occupancy_rate,
                    occupancy_rate=round(((days_count/(days_in_month*capacity))*100 if capacity else 0), 2),
                    valuation=valuation,
                    objective_valuation=objective_valuation,
                    gap_valuation=valuation-objective_valuation,
                )  # 'day' utilisé pour le nom du mois
                activity_tracking_month.append(item)

            # Calcul des agrégats pour ActivityTrackingAccumulationType
            past_months = [
                item for item in activity_tracking_month if (not item.is_current_month and not item.is_future_month)
            ]
            entries_count_sum = sum(item.entries_count for item in past_months)
            exits_count_sum = sum(item.exits_count for item in past_months)
            planned_exits_count_sum = sum(item.planned_exits_count for item in past_months)
            presents_month_count_sum = sum(item.presents_month_count for item in past_months)
            objective_days_count_sum = sum(item.objective_days_count for item in past_months)
            days_count_sum = sum(item.days_count for item in past_months)
            gap_days_count_sum = sum(item.gap_days_count for item in past_months)
            valuation_sum = sum(item.valuation for item in past_months)
            objective_valuation_sum = sum(item.objective_valuation for item in past_months)
            gap_valuation_sum = sum(item.gap_valuation for item in past_months)

            # Calcul de la moyenne pour les pourcentages
            objective_occupancy_rate_avg = mean(item.objective_occupancy_rate for item in past_months)
            occupancy_rate_avg = mean(item.occupancy_rate for item in past_months)

            activity_tracking_accumulation = ActivityTrackingAccumulationType(
                label=f'Cumul à fin {settings.MONTHS[prev_month_index]}',
                year=year,
                entries_count=round(entries_count_sum, 2),
                exits_count=round(exits_count_sum, 2),
                planned_exits_count=round(planned_exits_count_sum, 2),
                presents_month_count=round(presents_month_count_sum, 2),
                objective_days_count=round(objective_days_count_sum, 2),
                days_count=round(days_count_sum, 2),
                gap_days_count=round(gap_days_count_sum, 2),
                objective_occupancy_rate=round(objective_occupancy_rate_avg, 2),  # Moyenne des pourcentages
                occupancy_rate=round(occupancy_rate_avg, 2),  # Moyenne des pourcentages
                valuation=round(valuation_sum, 2),
                objective_valuation=round(objective_valuation_sum, 2),
                gap_valuation=round(gap_valuation_sum, 2),
            )
            activity_tracking_establishments.append(
                ActivityTrackingEstablishmentType(
                    months=settings.MONTHS,
                    year=year,
                    establishment=establishment,
                    activity_tracking_month=activity_tracking_month,
                    activity_tracking_accumulation=activity_tracking_accumulation
                    )
                )
        return activity_tracking_establishments

    def resolve_activity_beneficiary_establishments(instance, info, **kwargs):
        user = info.context.user
        dashboard_activity_filter = getattr(info.context, 'dashboard_activity_filter', None)
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        current_year = date.year
        current_month = date.month
        prev_month_index = 11
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        establishments = Establishment.objects.filter(company=company)

        if dashboard_activity_filter:
            the_year = dashboard_activity_filter.get('year', None)
            establishment_ids = dashboard_activity_filter.get('establishments', None)
            if the_year:
                year=the_year
            if establishment_ids:
                order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(establishment_ids)])
                establishments=establishments.filter(id__in=establishment_ids).annotate(ordering=order).order_by('ordering')
        if user.is_manager() and not user.can_manage_activity():
            establishments = establishments.filter(
                Q(managers__employee=user.get_employee_in_company()) | 
                Q(establishment_parent__managers__employee=user.get_employee_in_company())
            )

        monthly_beneficiary_attendance = BeneficiaryEntry.monthly_beneficiary_attendance(year=year, establishments=establishments, company=company)

        activity_beneficiary_establishments = []
        for i, establishment in enumerate(establishments):
            # Initialiser les activity_beneficiary_month par mois
            activity_beneficiaries=[]
            activity_beneficiary_entries=monthly_beneficiary_attendance.get(establishment.id, [])

            children_establishments = establishment.get_all_children()
            if len(children_establishments)> 0:
                children_monthly_beneficiary_attendance = BeneficiaryEntry.monthly_beneficiary_attendance(year=year, establishments=children_establishments, company=company)
                for k, children_establishment in enumerate(children_establishments):
                    activity_beneficiary_entries+=children_monthly_beneficiary_attendance.get(children_establishment.id, [])
            for i, activity_beneficiary_entry in enumerate(activity_beneficiary_entries):
                beneficiary = activity_beneficiary_entry["beneficiary"]
                monthly_attendance = activity_beneficiary_entry["monthly_attendance"]
                activity_beneficiary_months = []
                for i, month in enumerate(settings.MONTHS):  # Assurez-vous que `settings.MONTHS` contient les noms des mois
                    is_current_month = (int(year) == current_year and i+1 == current_month)
                    prev_month_index = i - 1 if i > 0 and is_current_month else prev_month_index
                    is_future_month = (int(year) > current_year) or (int(year) == current_year and i+1 > current_month)
                    days_count=monthly_attendance.get(i+1, {}).get("days_count", 0)
                    item = ActivityBeneficiaryMonthType(
                    year=year,
                    month=month,
                    is_current_month=is_current_month,
                    is_future_month=is_future_month,
                    days_count=days_count,
                    )  # 'day' utilisé pour le nom du mois
                    activity_beneficiary_months.append(item)
                past_months = [
                    item for item in activity_beneficiary_months if not item.is_future_month
                ]
                activity_beneficiaries.append(
                    ActivityBeneficiaryType(
                        year=year,
                        beneficiary=beneficiary,
                        days_count=sum(m.days_count for m in past_months),
                        activity_beneficiary_months=activity_beneficiary_months
                        )
                    )

            activity_beneficiary_establishments.append(
                ActivityBeneficiaryEstablishmentType(
                    months=settings.MONTHS,
                    year=year,
                    establishment=establishment,
                    activity_beneficiaries=activity_beneficiaries,
                    )
                )

        return activity_beneficiary_establishments

    def resolve_activity_synthesis(instance, info, **kwargs):
        user = info.context.user
        dashboard_activity_filter = getattr(info.context, 'dashboard_activity_filter', None)
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        establishments = Establishment.objects.filter(company=company)
        if dashboard_activity_filter:
            the_year = dashboard_activity_filter.get('year', None)
            establishment_ids = dashboard_activity_filter.get('establishments', None)
            if the_year:
                year=the_year
            if establishment_ids:
                order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(establishment_ids)])
                establishments=establishments.filter(id__in=establishment_ids).annotate(ordering=order).order_by('ordering')
        if user.is_manager() and not user.can_manage_activity():
            establishments = establishments.filter(
                Q(managers__employee=user.get_employee_in_company()) | 
                Q(establishment_parent__managers__employee=user.get_employee_in_company())
            )

        beneficiary_admission_monthly_statistics = BeneficiaryAdmission.monthly_statistics(year=year, establishments=establishments, company=company)
        beneficiary_admission_monthly_admissions = BeneficiaryAdmission.monthly_admissions(year=year, establishments=establishments, company=company)
        beneficiary_entry_monthly_present_beneficiaries = BeneficiaryEntry.monthly_present_beneficiaries(year=year, establishments=establishments, company=company)
        activity_synthesis_establishments = []
        month_totals = [0 for _ in range(12)]
        for i, establishment in enumerate(establishments):
            # Initialiser les activity_tracking_month par mois
            activity_synthesis_month = []
            children_establishments = establishment.get_all_children()
            children_beneficiary_admission_monthly_statistics=None
            children_beneficiary_admission_monthly_admissions=None
            children_beneficiary_entry_monthly_present_beneficiaries=None
            if len(children_establishments)> 0: 
                children_beneficiary_admission_monthly_statistics = BeneficiaryAdmission.monthly_statistics(year=year, establishments=children_establishments, company=company)
                children_beneficiary_admission_monthly_admissions = BeneficiaryAdmission.monthly_admissions(year=year, establishments=children_establishments, company=company)
                children_beneficiary_entry_monthly_present_beneficiaries = BeneficiaryEntry.monthly_present_beneficiaries(year=year, establishments=children_establishments, company=company)
            for i, month in enumerate(settings.MONTHS):  # Assurez-vous que `settings.MONTHS` contient les noms des mois
                days_in_month = monthrange(int(year), i+1)[1]
                capacity = establishment.get_monthly_capacity(year, i+1)
                beneficiary_entries = get_item_object(beneficiary_entry_monthly_present_beneficiaries, establishment.id, i+1, 'presences')
                beneficiary_admissions = get_item_object(beneficiary_admission_monthly_admissions, establishment.id, i+1, 'admissions')
                if children_beneficiary_entry_monthly_present_beneficiaries:
                    for k, children_establishment in enumerate(children_establishments):
                        if not establishment==children_establishment:
                            beneficiary_entries += get_item_object(children_beneficiary_entry_monthly_present_beneficiaries, children_establishment.id, i+1, 'presences')
                if children_beneficiary_admission_monthly_admissions:
                    for k, children_establishment in enumerate(children_establishments):
                        if not establishment==children_establishment:
                            beneficiary_admissions += get_item_object(children_beneficiary_admission_monthly_admissions, children_establishment.id, i+1, 'admissions')

                count_occupied_places_prev_month = 0
                count_received = 0
                count_rejected = 0
                count_approved = 0
                count_canceled = 0

                if children_beneficiary_admission_monthly_statistics:
                    capacity_total = 0
                    for k, children_establishment in enumerate(children_establishments):
                        count_occupied_places_prev_month += BeneficiaryEntry.count_present_beneficiaries(year=year, month=i, establishments=[children_establishment.id], company=company)
                        count_received += get_item_count(beneficiary_admission_monthly_statistics, children_establishment.id, i+1, 'count_received')
                        count_rejected += get_item_count(beneficiary_admission_monthly_statistics, children_establishment.id, i+1, 'count_rejected')
                        count_approved += get_item_count(beneficiary_admission_monthly_statistics, children_establishment.id, i+1, 'count_approved')
                        count_canceled += get_item_count(beneficiary_admission_monthly_statistics, children_establishment.id, i+1, 'count_canceled')
                    if not capacity or capacity==0:
                        capacity = capacity_total
                else:
                    count_occupied_places_prev_month = BeneficiaryEntry.count_present_beneficiaries(year=year, month=i, establishments=[establishment.id], company=company)
                    count_received = get_item_count(beneficiary_admission_monthly_statistics, establishment.id, i+1, 'count_received')
                    count_rejected = get_item_count(beneficiary_admission_monthly_statistics, establishment.id, i+1, 'count_rejected')
                    count_approved = get_item_count(beneficiary_admission_monthly_statistics, establishment.id, i+1, 'count_approved')
                    count_canceled = get_item_count(beneficiary_admission_monthly_statistics, establishment.id, i+1, 'count_canceled')

                count_occupied_places= len(beneficiary_entries)
                dashboard_comment = DashboardComment.objects.filter(establishment=establishment, comment_type='SYNTHESIS_ALL', year=str(year), month=str(i+1)).first()
                dashboard_comments = DashboardComment.objects.filter(establishment=establishment, comment_type='SYNTHESIS', year=str(year), month=str(i+1))
                count_available_places = capacity-count_occupied_places_prev_month
                gap_received = int(dashboard_comment.text) if dashboard_comment and dashboard_comment.text.isdigit() else 0
                if gap_received==0:
                    gap_received=count_available_places
                gap_received=(gap_received-count_received)*days_in_month
                gap_rejected=count_rejected*days_in_month

                item = ActivitySynthesisMonthType(
                    month=month,
                    year=year,
                    count_received=count_received,
                    gap_received=gap_received,
                    count_approved=count_approved,
                    count_rejected=count_rejected,
                    gap_rejected=gap_rejected,
                    count_canceled=count_canceled,
                    beneficiary_admissions=beneficiary_admissions,
                    dashboard_comment=dashboard_comment,
                    dashboard_comments=dashboard_comments,
                    beneficiary_entries=beneficiary_entries,
                    capacity=capacity,
                    count_occupied_places=count_occupied_places,
                    count_available_places=count_available_places,
                )  # 'day' utilisé pour le nom du mois
                activity_synthesis_month.append(item)
                month_total = month_totals[i]
                month_totals[i] = month_total+item.count_received+item.count_approved+item.count_rejected+item.count_canceled

            # Calcul des agrégats pour ActivityTrackingAccumulationType
            total_received = sum(item.count_received for item in activity_synthesis_month)
            total_gap_received = sum(item.gap_received for item in activity_synthesis_month)
            total_approved = sum(item.count_approved for item in activity_synthesis_month)
            total_rejected = sum(item.count_rejected for item in activity_synthesis_month)
            total_gap_rejected = sum(item.gap_rejected for item in activity_synthesis_month)
            total_canceled = sum(item.count_canceled for item in activity_synthesis_month)
            total_available_places = sum(item.count_available_places for item in activity_synthesis_month)
            total_dashboard_comment = sum(
                int(item.dashboard_comment.text) if item.dashboard_comment and item.dashboard_comment.text.isdigit() else 0 
                for item in activity_synthesis_month
            )

            activity_total_synthesis_month = ActivityTotalSynthesisMonthType(
                year=year,
                total_received=round(total_received, 2),
                total_gap_received=round(total_gap_received, 2),
                total_approved=round(total_approved, 2),
                total_rejected=round(total_rejected, 2),
                total_gap_rejected=round(total_gap_rejected, 2),
                total_canceled=round(total_canceled, 2),
                total_available_places=round(total_available_places, 2),
                total_dashboard_comment=round(total_dashboard_comment, 2),
            )
            activity_synthesis_establishments.append(
                ActivitySynthesisEstablishmentType(
                    months=settings.MONTHS,
                    year=year,
                    establishment=establishment,
                    activity_synthesis_month=activity_synthesis_month,
                    activity_total_synthesis_month=activity_total_synthesis_month
                    )
                )
        return ActivitySynthesisType(
                year=year,
                months=settings.MONTHS,
                activity_synthesis_establishments=activity_synthesis_establishments,
                month_totals=month_totals
            )

    def resolve_activity_month(instance, info, **kwargs):
        user = info.context.user
        dashboard_activity_filter = getattr(info.context, 'dashboard_activity_filter', None)
        company = user.the_current_company

        # Obtenir l'année en cours pour filtrer par année
        date = datetime.date.today()
        year=str(date.year)
        month=date.month - 1
        if month <= 0:  
            month = 12  
            year -= 1  
        elif month > 12:  
            month = 1  
            year += 1 
        start_year = date.replace(month=1, day=1)  # Début de l'année
        end_year = date.replace(month=12, day=31)  # Fin de l'année

        establishments = Establishment.objects.filter(company=company)
        if dashboard_activity_filter:
            the_year = dashboard_activity_filter.get('year', None)
            the_month = dashboard_activity_filter.get('month', None)
            establishment_ids = dashboard_activity_filter.get('establishments', None)
            if the_year:
                year=the_year
            if the_month:
                month=the_month
            if establishment_ids:
                order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(establishment_ids)])
                establishments=establishments.filter(id__in=establishment_ids).annotate(ordering=order).order_by('ordering')
        if user.is_manager() and not user.can_manage_activity():
            establishments = establishments.filter(
                Q(managers__employee=user.get_employee_in_company()) | 
                Q(establishment_parent__managers__employee=user.get_employee_in_company())
            )

        present_beneficiaries = BeneficiaryEntry.present_beneficiaries(year=year, month=month, establishments=establishments, company=company)

        activity_month_establishments = []
        for i, establishment in enumerate(establishments):
            beneficiary_entries=present_beneficiaries.get(establishment.id, [])
            capacity = establishment.get_monthly_capacity(year, month)
            count_occupied_places= len(beneficiary_entries)
            activity_month_establishments.append(
                ActivityMonthEstablishmentType(
                    month=settings.MONTHS[int(month)-1],
                    year=year,
                    establishment=establishment,
                    capacity=capacity,
                    count_outside_places_department=0,
                    count_occupied_places=count_occupied_places,
                    count_available_places=capacity-count_occupied_places,
                    ages_text=get_age_range(beneficiary_entries),
                    beneficiary_entries=beneficiary_entries
                    )
                )
        last_day = monthrange(int(year), int(month))[1]
        return ActivityMonthType(
                title=f"EFFECTIFS DE L'ASSOCIATION {company.name.upper()} AU {str(last_day)} {int(month):02d} {year}",
                year=year,
                month=settings.MONTHS[int(month)-1],
                activity_month_establishments=activity_month_establishments,
            )

class DashboardQuery(graphene.ObjectType):
    dashboard = graphene.Field(DashboardType, dashboard_activity_filter= DashboardActivityFilterInput(required=False))
    dashboard_activity = graphene.Field(DashboardActivityType, dashboard_activity_filter= DashboardActivityFilterInput(required=False))
    def resolve_dashboard(root, info, dashboard_activity_filter=None):
        # We can easily optimize query count in the resolve method
        info.context.dashboard_activity_filter = dashboard_activity_filter
        dashboard = 0
        return dashboard
    def resolve_dashboard_activity(root, info, dashboard_activity_filter=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        if not user.can_manage_activity() and not user.is_manager():
            raise PermissionDenied("Impossible d'exporter : vous n'avez pas les droits nécessaires.")
        info.context.dashboard_activity_filter = dashboard_activity_filter
        dashboard_activity = 0
        return dashboard_activity


#************************************************************************

class CreateDashboardComment(graphene.Mutation):
    class Arguments:
        dashboard_comment_data = DashboardCommentInput(required=True)

    dashboard_comment = graphene.Field(DashboardCommentType)

    def mutate(root, info, dashboard_comment_data=None):
        creator = info.context.user
        dashboard_comment = DashboardComment(**dashboard_comment_data)
        dashboard_comment.creator = creator
        dashboard_comment.company = creator.the_current_company
        dashboard_comment.save()
        return CreateDashboardComment(dashboard_comment=dashboard_comment)

class UpdateDashboardComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        dashboard_comment_data = DashboardCommentInput(required=True)

    dashboard_comment = graphene.Field(DashboardCommentType)

    def mutate(root, info, id, dashboard_comment_data=None):
        creator = info.context.user
        DashboardComment.objects.filter(pk=id).update(**dashboard_comment_data)
        dashboard_comment = DashboardComment.objects.get(pk=id)
        return UpdateDashboardComment(dashboard_comment=dashboard_comment)


class DeleteDashboardComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    dashboard_comment = graphene.Field(DashboardCommentType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        if current_user.is_superuser or True:
            dashboard_comment = DashboardComment.objects.get(pk=id)
            broadcastDashboardCommentDeleted(dashboard_comment)
            dashboard_comment.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteDashboardComment(deleted=deleted, success=success, message=message, id=id)

# **********************************************************************************************

#************************************************************************
#*******************************************************************************************************************************

class DashboardMutation(graphene.ObjectType):
    create_dashboard_comment = CreateDashboardComment.Field()
    update_dashboard_comment = UpdateDashboardComment.Field()
    delete_dashboard_comment = DeleteDashboardComment.Field()