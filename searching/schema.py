import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.db.models import Q

from works.schema import TaskNodeType
from works.models import Task

from human_ressources.schema import EmployeeNodeType
from human_ressources.models import Employee

from sales.schema import ClientNodeType
from sales.models import Client

from purchases.schema import SupplierNodeType
from purchases.models import Supplier

class SearchResultType(graphene.ObjectType):
    tasks = graphene.Field(TaskNodeType)
    employees = graphene.Field(EmployeeNodeType)
    clients = graphene.Field(ClientNodeType)
    suppliers = graphene.Field(SupplierNodeType)

class SearchType(graphene.ObjectType):
    results = graphene.Field(SearchResultType)

class SearchFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    type_search = graphene.String(required=False)

class SearchQuery(graphene.ObjectType):
    search = graphene.Field(SearchType, search_filter=SearchFilterInput(required=False), offset=graphene.Int(required=False), limit=graphene.Int(required=False), page=graphene.Int(required=False))

    def resolve_search(root, info, search_filter=None, offset=None, limit=None, page=None):
        tasks = Task.objects.all()
        employees = Employee.objects.all()
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()

        # Apply search filter if keyword is provided
        if search_filter and search_filter.keyword:
            keyword = search_filter.keyword.lower()
            tasks = tasks.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))  # Assuming 'name' is a field in Task model
            employees = employees.filter(Q(number__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))  # Assuming 'name' is a field in Employee model
            clients = clients.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))
            suppliers = suppliers.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))

        # Apply date range filter if starting_date_time and ending_date_time are provided
        if search_filter and search_filter.starting_date_time and search_filter.ending_date_time:
            tasks = tasks.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            employees = employees.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            clients = clients.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            suppliers = suppliers.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))

        # Apply additional filters based on your requirements

        # Apply pagination if offset, limit, and page are provided
        if offset is not None and limit is not None:
            start_index = offset
            end_index = offset + limit
            tasks = tasks[start_index:end_index]
            employees = employees[start_index:end_index]
            clients = clients[start_index:end_index]
            suppliers = suppliers[start_index:end_index]

        return {
            "results": {
                "tasks": {'total_count': len(tasks), 'nodes' : tasks},
                "employees": {'total_count': len(employees), 'nodes' : employees},
                "clients": {'total_count': len(clients), 'nodes' : clients},
                "suppliers": {'total_count': len(suppliers), 'nodes' : suppliers},
            }
        }
