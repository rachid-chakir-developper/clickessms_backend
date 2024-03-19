import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.apps import apps

from data_management.models import DataModel, AbsenceReason, UndesirableEventNormalType, UndesirableEventSeriousType, UndesirableEventFrequency

class DataType(DjangoObjectType):
    class Meta:
        model = DataModel
        fields = "__all__"

class AbsenceReasonType(DjangoObjectType):
    class Meta:
        model = AbsenceReason
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

class DataQuery(graphene.ObjectType):
    datas = graphene.List(DataType, typeData = graphene.String())
    data = graphene.Field(DataType, typeData = graphene.String(), id = graphene.ID())
    
    def resolve_datas(root, info, typeData):
        # We can easily optimize query count in the resolve method
        datas = apps.get_model('data_management', typeData).objects.all()
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
        descreption = graphene.String(required=False)
        typeData = graphene.String()

    data = graphene.Field(DataType)

    def mutate(root, info, typeData, **otherFields):
        creator = info.context.user
        data = apps.get_model('data_management', typeData)(**otherFields)
        data.creator = creator
        data.save()
        data.__class__ = DataModel
        return CreateData(data=data)

class UpdateData(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        descreption = graphene.String(required=False)
        typeData = graphene.String()
        id = graphene.ID()

    data = graphene.Field(DataType)

    def mutate(root, info, id, typeData, **otherFields):
        apps.get_model('data_management', typeData).objects.filter(pk=id).update(**otherFields)
        data = apps.get_model('data_management', typeData).objects.get(pk=id)
        # data.name = name
        # data.descreption = descreption
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