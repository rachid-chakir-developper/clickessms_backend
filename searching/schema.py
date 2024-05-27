import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.db.models import Q

from works.schema import TaskNodeType
from works.models import Task

from human_ressources.schema import EmployeeNodeType
from human_ressources.models import Employee

from human_ressources.schema import BeneficiaryNodeType
from human_ressources.models import Beneficiary

from sales.schema import ClientNodeType
from sales.models import Client

from purchases.schema import SupplierNodeType
from purchases.models import Supplier

from partnerships.schema import PartnerNodeType
from partnerships.models import Partner

from companies.schema import EstablishmentNodeType
from companies.models import Establishment

from data_management.schema import PhoneNumberNodeType
from data_management.models import PhoneNumber

class SearchResultType(graphene.ObjectType):
    tasks = graphene.Field(TaskNodeType)
    employees = graphene.Field(EmployeeNodeType)
    clients = graphene.Field(ClientNodeType)
    suppliers = graphene.Field(SupplierNodeType)
    partners = graphene.Field(PartnerNodeType)
    beneficiaries = graphene.Field(BeneficiaryNodeType)
    establishments = graphene.Field(EstablishmentNodeType)
    phone_numbers = graphene.Field(PhoneNumberNodeType)

class SearchType(graphene.ObjectType):
    results = graphene.Field(SearchResultType)

class SearchFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    type_search = graphene.String(required=False)

class SearchQuery(graphene.ObjectType):
    search = graphene.Field(SearchType, search_filter=SearchFilterInput(required=False), offset=graphene.Int(required=False), limit=graphene.Int(required=False), page=graphene.Int(required=False))
    search_numbers = graphene.Field(SearchType, search_filter=SearchFilterInput(required=False), offset=graphene.Int(required=False), limit=graphene.Int(required=False), page=graphene.Int(required=False))

    def resolve_search(root, info, search_filter=None, offset=None, limit=None, page=None):
        tasks = Task.objects.all()
        employees = Employee.objects.all()
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        beneficiaries = Beneficiary.objects.all()
        establishments = Establishment.objects.all()

        # Apply search filter if keyword is provided
        if search_filter and search_filter.keyword:
            keyword = search_filter.keyword.lower()
            tasks = tasks.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))  # Assuming 'name' is a field in Task model
            employees = employees.filter(Q(number__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))  # Assuming 'name' is a field in Employee model
            beneficiaries = beneficiaries.filter(Q(number__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))  # Assuming 'name' is a field in Employee model
            clients = clients.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))
            suppliers = suppliers.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))
            establishments = establishments.filter(Q(number__icontains=keyword) | Q(name__icontains=keyword))

        # Apply date range filter if starting_date_time and ending_date_time are provided
        if search_filter and search_filter.starting_date_time and search_filter.ending_date_time:
            tasks = tasks.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            employees = employees.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            beneficiaries = beneficiaries.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            clients = clients.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            suppliers = suppliers.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))
            establishments = establishments.filter(created_at__range=(search_filter.starting_date_time, search_filter.ending_date_time))

        # Apply additional filters based on your requirements

        # Apply pagination if offset, limit, and page are provided
        if offset is not None and limit is not None:
            start_index = offset
            end_index = offset + limit
            tasks = tasks[start_index:end_index]
            employees = employees[start_index:end_index]
            beneficiaries = beneficiaries[start_index:end_index]
            clients = clients[start_index:end_index]
            suppliers = suppliers[start_index:end_index]
            establishments = establishments[start_index:end_index]

        return {
            "results": {
                "tasks": {'total_count': len(tasks), 'nodes' : tasks},
                "employees": {'total_count': len(employees), 'nodes' : employees},
                "beneficiaries": {'total_count': len(beneficiaries), 'nodes' : beneficiaries},
                "clients": {'total_count': len(clients), 'nodes' : clients},
                "suppliers": {'total_count': len(suppliers), 'nodes' : suppliers},
                "establishments": {'total_count': len(establishments), 'nodes' : establishments},
            }
        }

    def resolve_search_numbers(root, info, search_filter=None, offset=None, limit=None, page=None):
        employees = Employee.objects.all()
        clients = Client.objects.all()
        suppliers = Supplier.objects.all()
        partners = Partner.objects.all()
        beneficiaries = Beneficiary.objects.all()
        establishments = Establishment.objects.all()
        phone_numbers = PhoneNumber.objects.all()

        # Apply search filter if keyword is provided
        if search_filter and search_filter.keyword:
            keyword = search_filter.keyword.lower()
            employees = employees.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))  # Assuming 'name' is a field in Employee model
            beneficiaries = beneficiaries.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
            clients = clients.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(name__icontains=keyword))
            suppliers = suppliers.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(name__icontains=keyword))
            partners = partners.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(name__icontains=keyword))
            establishments = establishments.filter(Q(fix__icontains=keyword) | Q(mobile__icontains=keyword) | Q(name__icontains=keyword))
            phone_numbers = phone_numbers.filter(Q(phone__icontains=keyword) | Q(name__icontains=keyword))

        # Apply additional filters based on your requirements

        # Apply pagination if offset, limit, and page are provided
        if offset is not None and limit is not None:
            start_index = offset
            end_index = offset + limit
            employees = employees[start_index:end_index]
            clients = clients[start_index:end_index]
            suppliers = suppliers[start_index:end_index]
            partners = partners[start_index:end_index]
            beneficiaries = beneficiaries[start_index:end_index]
            establishments = establishments[start_index:end_index]
            phone_numbers = phone_numbers[start_index:end_index]

        return {
            "results": {
                "employees": {'total_count': len(employees), 'nodes' : employees},
                "clients": {'total_count': len(clients), 'nodes' : clients},
                "suppliers": {'total_count': len(suppliers), 'nodes' : suppliers},
                "partners": {'total_count': len(partners), 'nodes' : partners},
                "beneficiaries": {'total_count': len(beneficiaries), 'nodes' : beneficiaries},
                "establishments": {'total_count': len(establishments), 'nodes' : establishments},
                "phone_numbers": {'total_count': len(phone_numbers), 'nodes' : phone_numbers},
            }
        }

