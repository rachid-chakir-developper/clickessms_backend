import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

import datetime
from django.conf import settings

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate

from works.schema import TaskType,TaskActionType
from human_ressources.schema import EmployeeType
from qualities.schema import UndesirableEventType

from works.models import Task, STATUS_All, TaskAction
from qualities.models import UndesirableEvent

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
        company = user.current_company if user.current_company is not None else user.company
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
        company = user.current_company if user.current_company is not None else user.company
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
        company = user.current_company if user.current_company is not None else user.company
        return TaskAction.objects.filter(company=company, employees=user.get_employee_in_company()).exclude(status="DONE").order_by('-due_date')[0:10]

    def resolve_undesirable_events(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        undesirable_events = UndesirableEvent.objects.filter(company=company, status="NEW")
        if not user.can_manage_quality():
            if user.is_manager():
                undesirable_events = undesirable_events.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                undesirable_events = undesirable_events.filter(creator=user)
        undesirable_events = undesirable_events.order_by('-created_at')
        return undesirable_events

    def resolve_current_employee(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        return user.get_employee_in_company(company=company)

class DashboardQuery(graphene.ObjectType):
    dashboard = graphene.Field(DashboardType)
    def resolve_dashboard(root, info):
        # We can easily optimize query count in the resolve method
        dashboard = 0
        return dashboard