import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from django.utils import timezone

from django.db.models import Q

from companies.models import Company, Establishment, EstablishmentManager, ActivityAuthorization
from medias.models import File, Folder
from human_ressources.models import Employee

class CompanyType(DjangoObjectType):
    class Meta:
        model = Company
        fields = "__all__"
    logo = graphene.String()
    cover_image = graphene.String()
    def resolve_logo( instance, info, **kwargs ):
        return instance.logo and info.context.build_absolute_uri(instance.logo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class CompanyNodeType(graphene.ObjectType):
    nodes = graphene.List(CompanyType)
    total_count = graphene.Int()

class EstablishmentManagerType(DjangoObjectType):
    class Meta:
        model = EstablishmentManager
        fields = "__all__"

class ActivityAuthorizationType(DjangoObjectType):
    class Meta:
        model = ActivityAuthorization
        fields = "__all__"
    document = graphene.String()
    def resolve_document( instance, info, **kwargs ):
        return instance.document and info.context.build_absolute_uri(instance.document.file.url)

class EstablishmentType(DjangoObjectType):
    class Meta:
        model = Establishment
        fields = "__all__"
    logo = graphene.String()
    cover_image = graphene.String()
    current_capacity = graphene.Float()
    current_temporary_capacity = graphene.Float()
    def resolve_logo( instance, info, **kwargs ):
        return instance.logo and info.context.build_absolute_uri(instance.logo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)
    def resolve_current_capacity( instance, info, **kwargs ):
        now = timezone.now().date()
        current_authorization = instance.activity_authorizations.filter(
            starting_date_time__date__lte=now
        ).order_by('-ending_date_time').first()
        return current_authorization.capacity if current_authorization else None
    def resolve_current_temporary_capacity( instance, info, **kwargs ):
        now = timezone.now().date()
        current_authorization = instance.activity_authorizations.filter(
            starting_date_time__date__lte=now
        ).order_by('-ending_date_time').first()
        return current_authorization.temporary_capacity if current_authorization else None

class EstablishmentNodeType(graphene.ObjectType):
    nodes = graphene.List(EstablishmentType)
    total_count = graphene.Int()

class EstablishmentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishment_categories = graphene.List(graphene.String, required=False)
    establishment_types = graphene.List(graphene.String, required=False)

class CompanyInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    primary_color = graphene.String(required=False)
    secondary_color = graphene.String(required=False)
    text_color = graphene.String(required=False)
    opening_date = graphene.DateTime(required=False)
    closing_date = graphene.DateTime(required=False)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    email = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)

class ActivityAuthorizationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    document = Upload(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    capacity = graphene.Float(required=False)
    temporary_capacity = graphene.Float(required=False)
    is_active = graphene.Boolean(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class EstablishmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    siret = graphene.String(required=False)
    finess = graphene.String(required=False)
    ape_code = graphene.String(required=False)
    primary_color = graphene.String(required=False)
    secondary_color = graphene.String(required=False)
    text_color = graphene.String(required=False)
    opening_date = graphene.DateTime(required=False)
    closing_date = graphene.DateTime(required=False)
    measurement_activity_unit = graphene.String(required=False)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
    additional_address = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    email = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishment_category_id = graphene.Int(name="establishmentCategory", required=False)
    establishment_type_id = graphene.Int(name="establishmentType", required=False)
    establishment_parent_id = graphene.Int(name="establishmentParent", required=False)
    establishment_childs = graphene.List(graphene.Int, required=False)
    managers = graphene.List(graphene.Int, required=False)
    activity_authorizations = graphene.List(ActivityAuthorizationInput, required=False)


class CompanyQuery(graphene.ObjectType):
    companies = graphene.Field(CompanyNodeType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    company = graphene.Field(CompanyType, id = graphene.ID(required=False))
    establishments = graphene.Field(EstablishmentNodeType, id_parent = graphene.ID(required=False), establishment_filter= EstablishmentFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    establishment = graphene.Field(EstablishmentType, id = graphene.ID())

    def resolve_companies(root, info, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        total_count = Company.objects.all().count()
        if page:
            offset = limit*(page-1)
        if offset is not None and limit is not None:
            companies = Company.objects.all()[offset:offset+limit]
        else:
            companies = Company.objects.all()
        return CompanyNodeType(nodes=companies, total_count=total_count)

    def resolve_company(root, info, id=None):
        user = info.context.user
        # We can easily optimize query count in the resolve method
        try:
            # company = Company.objects.get(pk=id)
            company = user.company
        except Exception as e:
            print(f"Exception: {e}")
            company = None
        return company

    def resolve_establishments(root, info, id_parent=None, establishment_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        establishments = Establishment.objects.filter(company=company)
        if id_parent:
            establishments = establishments.filter(establishment_parent__id=id_parent if int(id_parent) > 0 else None)
        if establishment_filter:
            keyword = establishment_filter.get('keyword', '')
            starting_date_time = establishment_filter.get('starting_date_time')
            ending_date_time = establishment_filter.get('ending_date_time')
            establishment_categories = establishment_filter.get('establishment_categories')
            establishment_types = establishment_filter.get('establishment_types')
            if establishment_categories:
                establishments = establishments.filter(establishment_category_id__in=establishment_categories)
            if establishment_types:
                establishments = establishments.filter(establishment_type_id__in=establishment_types)
            if keyword:
                establishments = establishments.filter(Q(name__icontains=keyword) | Q(siret__icontains=keyword) | Q(finess__icontains=keyword) | Q(ape_code__icontains=keyword) | Q(zip_code__icontains=keyword) | Q(address__icontains=keyword))
            if starting_date_time:
                establishments = establishments.filter(opening_date__gte=starting_date_time)
            if ending_date_time:
                establishments = establishments.filter(opening_date__lte=ending_date_time)
        establishments = establishments.order_by('-created_at')
        total_count = establishments.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            establishments = establishments[offset:offset + limit]
        return EstablishmentNodeType(nodes=establishments, total_count=total_count)

    def resolve_establishment(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            establishment = Establishment.objects.get(pk=id)
        except Establishment.DoesNotExist:
            establishment = None
        return establishment


#************************************************************************

class CreateCompany(graphene.Mutation):
    class Arguments:
        company_data = CompanyInput(required=True)
        logo = Upload(required=False)
        cover_image = Upload(required=False)

    company = graphene.Field(CompanyType)

    def mutate(root, info, logo=None, cover_image=None, company_data=None):
        creator = info.context.user
        company = Company(**company_data)
        company.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if logo and isinstance(logo, UploadedFile):
                logo_file = company.logo
                if not logo_file:
                    logo_file = File()
                    logo_file.creator = creator
                logo_file.image = logo
                logo_file.save()
                company.logo = logo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = company.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                company.cover_image = cover_image_file
        company.save()
        return CreateCompany(company=company)

class UpdateCompany(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        company_data = CompanyInput(required=True)
        logo = Upload(required=False)
        cover_image = Upload(required=False)

    company = graphene.Field(CompanyType)

    def mutate(root, info, id=None, logo=None, cover_image=None, company_data=None):
        creator = info.context.user
        company = creator.current_company if creator.current_company is not None else creator.company
        if not company:
            company = Company(**company_data)
            company.creator = creator
            company.save()
            creator.company = company
            creator.save()
        else:
            Company.objects.filter(pk=company.id).update(**company_data)
        company = Company.objects.get(pk=company.id)

        if not company.folder:
            folder = Folder(name=str(company.id)+'_'+company.name, creator=creator)
            folder.save()
            company.folder = folder
            company.save()
        if not logo and company.logo:
            logo_file = company.logo
            logo_file.delete()
        if not cover_image and company.cover_image:
            cover_image_file = company.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if logo and isinstance(logo, UploadedFile):
                logo_file = company.logo
                if not logo_file:
                    logo_file = File()
                    logo_file.creator = creator
                logo_file.image = logo
                logo_file.save()
                company.logo = logo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = company.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                company.cover_image = cover_image_file
            company.save()
        return UpdateCompany(company=company)


class DeleteCompany(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    company = graphene.Field(CompanyType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        if current_user.is_superuser:
            company = Company.objects.get(pk=id)
            company.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteCompany(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateEstablishment(graphene.Mutation):
    class Arguments:
        establishment_data = EstablishmentInput(required=True)
        logo = Upload(required=False)
        cover_image = Upload(required=False)

    establishment = graphene.Field(EstablishmentType)

    def mutate(root, info, logo=None, cover_image=None,  establishment_data=None):
        creator = info.context.user
        establishment_childs_ids = establishment_data.pop("establishment_childs")
        managers_ids = establishment_data.pop("managers")
        activity_authorizations = establishment_data.pop("activity_authorizations")
        establishment_childs = Establishment.objects.filter(id__in=establishment_childs_ids)
        establishment = Establishment(**establishment_data)
        establishment.creator = creator
        establishment.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if logo and isinstance(logo, UploadedFile):
                logo_file = establishment.logo
                if not logo_file:
                    logo_file = File()
                    logo_file.creator = creator
                logo_file.image = logo
                logo_file.save()
                establishment.logo = logo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = establishment.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                establishment.cover_image = cover_image_file
        establishment.save()
        folder = Folder.objects.create(name=str(establishment.id)+'_'+establishment.name,creator=creator)
        establishment.folder = folder
        establishment.establishment_childs.set(establishment_childs)

        employees = Employee.objects.filter(id__in=managers_ids)
        for employee in employees:
            try:
                establishment_manager = EstablishmentManager.objects.get(employee__id=employee.id, establishment__id=establishment.id)
            except EstablishmentManager.DoesNotExist:
                EstablishmentManager.objects.create(
                        establishment=establishment,
                        employee=employee,
                        creator=creator
                    )

        establishment.save()

        for item in activity_authorizations:
            document = item.pop("document") if "document" in item else None
            activity_authorization = ActivityAuthorization(**item)
            activity_authorization.establishment = establishment
            if document and isinstance(document, UploadedFile):
                document_file = activity_authorization.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                activity_authorization.document = document_file
            activity_authorization.save()
        return CreateEstablishment(establishment=establishment)

class UpdateEstablishment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        establishment_data = EstablishmentInput(required=True)
        logo = Upload(required=False)
        cover_image = Upload(required=False)

    establishment = graphene.Field(EstablishmentType)

    def mutate(root, info, id, logo=None, cover_image=None,  establishment_data=None):
        creator = info.context.user
        establishment_childs_ids = establishment_data.pop("establishment_childs")
        managers_ids = establishment_data.pop("managers")
        activity_authorizations = establishment_data.pop("activity_authorizations")
        establishment_childs = Establishment.objects.filter(id__in=establishment_childs_ids)
        Establishment.objects.filter(pk=id).update(**establishment_data)
        establishment = Establishment.objects.get(pk=id)
        if not establishment.folder or establishment.folder is None:
            folder = Folder.objects.create(name=str(establishment.id)+'_'+establishment.name,creator=creator)
            Establishment.objects.filter(pk=id).update(folder=folder)
        if not logo and establishment.logo:
            logo_file = establishment.logo
            logo_file.delete()
        if not cover_image and establishment.cover_image:
            cover_image_file = establishment.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if logo and isinstance(logo, UploadedFile):
                logo_file = establishment.logo
                if not logo_file:
                    logo_file = File()
                    logo_file.creator = creator
                logo_file.image = logo
                logo_file.save()
                establishment.logo = logo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = establishment.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                establishment.cover_image = cover_image_file
            establishment.save()
        establishment.establishment_childs.set(establishment_childs)

        EstablishmentManager.objects.filter(establishment=establishment).exclude(employee__id__in=managers_ids).delete()
        employees = Employee.objects.filter(id__in=managers_ids)
        for employee in employees:
            try:
                establishment_manager = EstablishmentManager.objects.get(employee__id=employee.id, establishment__id=establishment.id)
            except EstablishmentManager.DoesNotExist:
                EstablishmentManager.objects.create(
                        establishment=establishment,
                        employee=employee,
                        creator=creator
                    )

        activity_authorization_ids = [item.id for item in activity_authorizations if item.id is not None]
        ActivityAuthorization.objects.filter(establishment=establishment).exclude(id__in=activity_authorization_ids).delete()
        for item in activity_authorizations:
            document = item.pop("document") if "document" in item else None
            if id in item or 'id' in item:
                ActivityAuthorization.objects.filter(pk=item.id).update(**item)
                activity_authorization = ActivityAuthorization.objects.get(pk=item.id)
            else:
                activity_authorization = ActivityAuthorization(**item)
                activity_authorization.establishment = establishment
                activity_authorization.save()
            if not document and activity_authorization.document:
                document_file = activity_authorization.document
                document_file.delete()
            if document and isinstance(document, UploadedFile):
                document_file = activity_authorization.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                activity_authorization.document = document_file
                activity_authorization.save()
        establishment = Establishment.objects.get(pk=id)
        return UpdateEstablishment(establishment=establishment)
        
class UpdateEstablishmentState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    establishment = graphene.Field(EstablishmentType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, establishment_fields=None):
        creator = info.context.user
        done = True
        success = True
        establishment = None
        message = ''
        try:
            establishment = Establishment.objects.get(pk=id)
            Establishment.objects.filter(pk=id).update(is_active=not establishment.is_active)
            establishment.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            establishment=None
            message = "Une erreur s'est produite."
        return UpdateEstablishmentState(done=done, success=success, message=message,establishment=establishment)

class DeleteEstablishment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    establishment = graphene.Field(EstablishmentType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        if current_user.is_superuser:
            establishment = Establishment.objects.get(pk=id)
            establishment.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEstablishment(deleted=deleted, success=success, message=message, id=id)

        
#*************************************************************************#

class CompanyMutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    update_company = UpdateCompany.Field()
    delete_company = DeleteCompany.Field()

    create_establishment = CreateEstablishment.Field()
    update_establishment = UpdateEstablishment.Field()
    update_establishment_state = UpdateEstablishmentState.Field()
    delete_establishment = DeleteEstablishment.Field()