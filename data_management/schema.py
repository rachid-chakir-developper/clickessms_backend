import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.apps import apps

from data_management.models import HumanGender, AdmissionDocumentType, PhoneNumber, HomeAddress, DataModel, EstablishmentType, EstablishmentCategory, AbsenceReason, UndesirableEventNormalType, UndesirableEventSeriousType, UndesirableEventFrequency, MeetingReason, TypeMeeting, EmployeeContractType

        
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

        
class EmployeeContractTypeType(DjangoObjectType):
    class Meta:
        model = EmployeeContractType
        fields = "__all__"

class DataQuery(graphene.ObjectType):
    datas = graphene.List(DataType, typeData = graphene.String())
    data = graphene.Field(DataType, typeData = graphene.String(), id = graphene.ID())
    
    def resolve_datas(root, info, typeData):
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        # We can easily optimize query count in the resolve method
        datas = apps.get_model('data_management', typeData).objects.filter(company=company)
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


class DataMutation(graphene.ObjectType):
    create_data = CreateData.Field()
    update_data = UpdateData.Field()
    delete_data = DeleteData.Field()