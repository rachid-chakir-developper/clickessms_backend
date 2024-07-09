import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.apps import apps

from django.db.models import Q
import openpyxl

from data_management.models import HumanGender, AdmissionDocumentType, PhoneNumber, HomeAddress, DataModel, EstablishmentType, EstablishmentCategory, AbsenceReason, UndesirableEventNormalType, UndesirableEventSeriousType, UndesirableEventFrequency, MeetingReason, TypeMeeting, DocumentType, VehicleBrand, VehicleModel

        
class HumanGenderType(DjangoObjectType):
    class Meta:
        model = HumanGender
        fields = "__all__"

class AdmissionDocumentTypeType(DjangoObjectType):
    class Meta:
        model = AdmissionDocumentType
        fields = "__all__"
        
class PhoneNumberType(DjangoObjectType):
    class Meta:
        model = PhoneNumber
        fields = "__all__"
    name = graphene.String()
    def resolve_name( instance, info, **kwargs ):
        return instance.name if instance.name else 'Sans nom'

class PhoneNumberNodeType(graphene.ObjectType):
    nodes = graphene.List(PhoneNumberType)
    total_count = graphene.Int()
        
class HomeAddressType(DjangoObjectType):
    class Meta:
        model = HomeAddress
        fields = "__all__"

class HomeAddressNodeType(graphene.ObjectType):
    nodes = graphene.List(HomeAddressType)
    total_count = graphene.Int()

class DataType(DjangoObjectType):
    class Meta:
        model = DataModel
        fields = "__all__"

class AbsenceReasonType(DjangoObjectType):
    class Meta:
        model = AbsenceReason
        fields = "__all__"
        
class EstablishmentCategoryType(DjangoObjectType):
    class Meta:
        model = EstablishmentCategory
        fields = "__all__"

class EstablishmentTypeType(DjangoObjectType):
    class Meta:
        model = EstablishmentType
        fields = "__all__"

class UndesirableEventNormalTypeType(DjangoObjectType):
    class Meta:
        model = UndesirableEventNormalType
        fields = "__all__"

class UndesirableEventSeriousTypeType(DjangoObjectType):
    class Meta:
        model = UndesirableEventSeriousType
        fields = "__all__"

class UndesirableEventFrequencyType(DjangoObjectType):
    class Meta:
        model = UndesirableEventFrequency
        fields = "__all__"

class MeetingReasonType(DjangoObjectType):
    class Meta:
        model = MeetingReason
        fields = "__all__"

class TypeMeetingType(DjangoObjectType):
    class Meta:
        model = TypeMeeting
        fields = "__all__"
class DocumentTypeType(DjangoObjectType):
    class Meta:
        model = DocumentType
        fields = "__all__"
        
class VehicleBrandType(DjangoObjectType):
    class Meta:
        model = VehicleBrand
        fields = "__all__"

        
class VehicleModelType(DjangoObjectType):
    class Meta:
        model = VehicleModel
        fields = "__all__"

class DataQuery(graphene.ObjectType):
    datas = graphene.List(DataType, typeData = graphene.String())
    data = graphene.Field(DataType, typeData = graphene.String(), id = graphene.ID())
    
    def resolve_datas(root, info, typeData):
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        # We can easily optimize query count in the resolve method
        datas = apps.get_model('data_management', typeData).objects.filter(Q(company=company) | Q(creator__is_superuser=True))
        for data in datas:
            data.__class__ = DataModel
        return datas

    def resolve_data(root, info, typeData, id):
        # We can easily optimize query count in the resolve method
        data = apps.get_model('data_management', typeData).objects.get(pk=id)
        data.__class__ = DataModel
        return data

class CreateData(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String(required=False)
        typeData = graphene.String()

    data = graphene.Field(DataType)

    def mutate(root, info, typeData, **otherFields):
        creator = info.context.user
        data = apps.get_model('data_management', typeData)(**otherFields)
        data.creator = creator
        data.company = creator.current_company if creator.current_company is not None else creator.company
        data.save()
        data.__class__ = DataModel
        return CreateData(data=data)

class UpdateData(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String(required=False)
        typeData = graphene.String()
        id = graphene.ID()

    data = graphene.Field(DataType)

    def mutate(root, info, id, typeData, **otherFields):
        apps.get_model('data_management', typeData).objects.filter(pk=id).update(**otherFields)
        data = apps.get_model('data_management', typeData).objects.get(pk=id)
        # data.name = name
        # data.description = description
        data.__class__ = DataModel
        return UpdateData(data=data)

class DeleteData(graphene.Mutation):
    class Arguments:
        typeData = graphene.String()
        id = graphene.ID()

    data = graphene.Field(DataType)
    deleted = graphene.Boolean()

    def mutate(root, info, id, typeData):
        data = apps.get_model('data_management', typeData).objects.get(pk=id)
        data.delete()
        return DeleteData(deleted=True)

#**************************************************************************************************

def import_data(model, file, fields):
    wb = openpyxl.load_workbook(file, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_data = dict(zip(headers, row))
        data = {field: row_data[field] for field in fields if field in row_data}
        model.objects.create(**data)

class ImportDataMutation(graphene.Mutation):
    class Arguments:
        model_data = graphene.String(required=True)
        file = graphene.String(required=True)
        fields = graphene.List(graphene.String, required=True)

    count_elements = 0
    success = graphene.Boolean()

    def mutate(self, info, model_data, file, fields):
        success = True
        try:
            if model_data == 'Employee' or model_data == 'Beneficiary':
                model_app = 'human_ressources'
            else:
                success = False
            model = apps.get_model(model_app, model_data)
            count_elements = import_data(model=model, file=file, fields=fields)
        except Exception as e:
            success = False
        return ImportDataMutation(success=success, count_elements=count_elements)

#**************************************************************************************************

class DataMutation(graphene.ObjectType):
    create_data = CreateData.Field()
    update_data = UpdateData.Field()
    delete_data = DeleteData.Field()

    import_data = ImportDataMutation.Field()