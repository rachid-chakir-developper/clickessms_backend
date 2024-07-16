import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
import re
from django.utils.dateparse import parse_date

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

def extract_parts_name(full_name):
    words = full_name.split()
    first_name = None
    preferred_name = None
    last_name = None
    for i, word in enumerate(words):
        if word.lower() in ["né", "née"]:
            last_name = " ".join(words[i+1:]).upper()
            break
        elif word.isupper():
            preferred_name = word
        elif word[0].isupper() and i > 0:
            first_name = word
    if not preferred_name and not first_name:
        first_name = words[0].capitalize() if words else None
        preferred_name = words[1].upper() if len(words) > 1 else None
    return first_name, preferred_name, last_name

def import_data_from_file(entity, model, file, fields, user=None):
    count = 0
    wb = openpyxl.load_workbook(file, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_data = dict(zip(headers, row))
        data = {field: row_data[field] for field in fields if field in row_data}
        # model.objects.create(**data)
        if entity == 'Employee':
            try:
                registration_number, name, social_security_number = data['registration_number'], data['name'], data['social_security_number']
                first_name, last_name, preferred_name = extract_parts_name(full_name=name)
                employee = model.objects.get(Q(first_name=first_name, last_name=last_name))
                if not employee.social_security_number or employee.social_security_number == '' :
                    model.objects.filter(pk=employee.id).update(social_security_number=social_security_number)
                if not employee.registration_number or employee.registration_number == '' :
                    model.objects.filter(pk=employee.id).update(registration_number=registration_number)
            except model.DoesNotExist:
                # model.objects.create(
                #     registration_number=registration_number,
                #     first_name=first_name,
                #     last_name=preferred_name if preferred_name else last_name,
                #     preferred_name=last_name if preferred_name else preferred_name,
                #     social_security_number=social_security_number,
                #     company=user.company,
                #     creator=user,
                #     )
                pass
            except Exception as e:
                pass
            count += 1
        if entity == 'Beneficiary':
            try:
                gender, first_name, last_name, birth_date = data['gender'], data['first_name'], data['last_name'], data['birth_date']
                # birth_date = parse_date(birth_date)
                # first_name, last_name, preferred_name = extract_parts_name(full_name=name)
                beneficiary = model.objects.get(Q(first_name=first_name, last_name=last_name))
                if not beneficiary.birth_date:
                    model.objects.filter(pk=beneficiary.id).update(birth_date=birth_date)
            except model.DoesNotExist:
                model.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    preferred_name=last_name,
                    birth_date=birth_date,
                    company=user.company,
                    creator=user,
                    )
            except Exception as e:
                raise e
            count += 1
    return count

class ImportDataMutation(graphene.Mutation):
    class Arguments:
        entity = graphene.String(required=True)
        file = Upload(required=True)
        fields = graphene.List(graphene.String, required=True)

    count = graphene.Int()
    done = graphene.Boolean()
    success = graphene.Boolean()

    def mutate(self, info, entity=None, file=None, fields=None):
        user = info.context.user
        done = True
        success = True
        count = 0
        try:
            if entity == 'Employee' or entity == 'Beneficiary':
                model_app = 'human_ressources'
            else:
                done = False
                success = False
            model = apps.get_model(model_app, entity)
            count = import_data_from_file(entity=entity, model=model, file=file, fields=fields, user=user)
        except Exception as e:
            print(e)
            done = False
            success = False
        return ImportDataMutation(success=success, done=done, count=count)

#**************************************************************************************************

class DataMutation(graphene.ObjectType):
    create_data = CreateData.Field()
    update_data = UpdateData.Field()
    delete_data = DeleteData.Field()

    import_data = ImportDataMutation.Field()