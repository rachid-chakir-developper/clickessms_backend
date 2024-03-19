import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

import datetime
from django.conf import settings

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate

from works.schema import TaskType

from works.models import Task, STATUS_All

class BudgetTaskType(graphene.ObjectType):
    name = graphene.String()
    estimated_budget = graphene.Float()
    spendings = graphene.Float()

class TaskPercentType(graphene.ObjectType):
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

class DashboardType(graphene.ObjectType):
    budget_month = graphene.Field(BudgetMonthType)
    spendings_month = graphene.Field(SpendingsMonthType)
    revenue_month = graphene.Field(RevenueMonthType)
    tasks_week = graphene.List(TasksWeekType)
    task_percent = graphene.List(TaskPercentType)
    tasks = graphene.List(TaskType)
    def resolve_budget_month(instance, info, **kwargs):
        user = info.context.user
        today = datetime.date.today()
        budget_month = BudgetMonthType(
            date=settings.MONTHS[today.month - 1],
            budget=Task.objects.filter(starting_date_time__month=today.month).aggregate(Sum('estimated_budget'))['estimated_budget__sum'] or 0
        )
        return budget_month

    def resolve_spendings_month(instance, info, **kwargs):
        user = info.context.user
        today = datetime.date.today()
        spendings_month = SpendingsMonthType(
            date=settings.MONTHS[today.month - 1],
            spendings=Task.objects.filter(starting_date_time__month=today.month, status=STATUS_All['FINISHED']).aggregate(Sum('estimated_budget'))['estimated_budget__sum'] or 0
        )
        return spendings_month

    def resolve_revenue_month(instance, info, **kwargs):
        user = info.context.user
        today = datetime.date.today()
        revenue_month = RevenueMonthType(
            date=settings.MONTHS[today.month - 1],
            revenue=Task.objects.filter(starting_date_time__month=today.month, status=STATUS_All['FINISHED']).aggregate(Sum('total_price_ttc'))['total_price_ttc__sum'] or 0
        )
        return revenue_month

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

    def resolve_task_percent(instance, info, **kwargs):
        task_percent = Task.objects.all().values('status').annotate(value=Count('status'))

        return [TaskPercentType(label=Task(status=status['status']).get_status_display(), value=status['value']) for status in task_percent]

    def resolve_tasks(root, info, **kwargs):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        tasks = Task.objects.all()
        today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        tasks = tasks.filter(starting_date_time__range=(today_start, today_end))
        tasks = tasks.order_by('starting_date_time')
        return tasks

class DashboardQuery(graphene.ObjectType):
    dashboard = graphene.Field(DashboardType)
    def resolve_dashboard(root, info):
        # We can easily optimize query count in the resolve method
        dashboard = 0
        return dashboard