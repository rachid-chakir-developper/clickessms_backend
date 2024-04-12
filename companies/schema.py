import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from companies.models import Company, Establishment, EstablishmentService
from medias.models import File, Folder

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

class EstablishmentType(DjangoObjectType):
    class Meta:
        model = Establishment
        fields = "__all__"
    logo = graphene.String()
    cover_image = graphene.String()
    def resolve_logo( instance, info, **kwargs ):
        return instance.logo and info.context.build_absolute_uri(instance.logo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class EstablishmentNodeType(graphene.ObjectType):
    nodes = graphene.List(EstablishmentType)
    total_count = graphene.Int()

class EstablishmentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class EstablishmentServiceType(DjangoObjectType):
    class Meta:
        model = EstablishmentService
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class EstablishmentServiceNodeType(graphene.ObjectType):
    nodes = graphene.List(EstablishmentServiceType)
    total_count = graphene.Int()

class EstablishmentServiceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

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

class EstablishmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    siret = graphene.String(required=True)
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
    establishment_type_id = graphene.Int(name="establishmentType", required=False)
    establishment_parent_id = graphene.Int(name="establishmentParent", required=False)
    establishment_childs = graphene.List(graphene.Int, required=False)

class EstablishmentServiceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    siret = graphene.String(required=True)
    establishment_service_type = graphene.String(required=True)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)
    establishment_service_parent_id = graphene.Int(name="establishmentServiceParent", required=False)
    establishment_service_childs = graphene.List(graphene.Int, required=False)

class CompanyQuery(graphene.ObjectType):
    companies = graphene.Field(CompanyNodeType, offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    company = graphene.Field(CompanyType, id = graphene.ID(required=False))
    establishments = graphene.Field(EstablishmentNodeType, establishment_filter= EstablishmentFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    establishment = graphene.Field(EstablishmentType, id = graphene.ID())
    establishment_services = graphene.Field(EstablishmentServiceNodeType, establishment_service_filter= EstablishmentServiceFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    establishment_service = graphene.Field(EstablishmentServiceType, id = graphene.ID())

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

    def resolve_establishments(root, info, establishment_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        establishments = Establishment.objects.all()
        if establishment_filter:
            keyword = establishment_filter.get('keyword', '')
            starting_date_time = establishment_filter.get('starting_date_time')
            ending_date_time = establishment_filter.get('ending_date_time')
            if keyword:
                establishments = establishments.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                establishments = establishments.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                establishments = establishments.filter(created_at__lte=ending_date_time)
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

    def resolve_establishment_services(root, info, establishment_service_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        establishment_services = EstablishmentService.objects.all()
        if establishment_service_filter:
            keyword = establishment_service_filter.get('keyword', '')
            starting_date_time = establishment_service_filter.get('starting_date_time')
            ending_date_time = establishment_service_filter.get('ending_date_time')
            if keyword:
                establishment_services = establishment_services.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                establishment_services = establishment_services.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                establishment_services = establishment_services.filter(created_at__lte=ending_date_time)
        establishment_services = establishment_services.order_by('-created_at')
        total_count = establishment_services.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            establishment_services = establishment_services[offset:offset + limit]
        return EstablishmentServiceNodeType(nodes=establishment_services, total_count=total_count)

    def resolve_establishment_service(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            establishment_service = EstablishmentService.objects.get(pk=id)
        except EstablishmentService.DoesNotExist:
            establishment_service = None
        return establishment_service


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
        company = creator.company
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
        establishment_childs = Establishment.objects.filter(id__in=establishment_childs_ids)
        establishment = Establishment(**establishment_data)
        establishment.creator = creator
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
        establishment.save()
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
#************************************************************************

class CreateEstablishmentService(graphene.Mutation):
    class Arguments:
        establishment_service_data = EstablishmentServiceInput(required=True)
        image = Upload(required=False)

    establishment_service = graphene.Field(EstablishmentServiceType)

    def mutate(root, info, image=None, establishment_service_data=None):
        creator = info.context.user
        establishment_service_childs_ids = establishment_service_data.pop("establishment_service_childs")
        establishment_service_childs = EstablishmentService.objects.filter(id__in=establishment_service_childs_ids)
        establishment_service = EstablishmentService(**establishment_service_data)
        establishment_service.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = establishment_service.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                establishment_service.image = image_file
        establishment_service.save()
        folder = Folder.objects.create(name=str(establishment_service.id)+'_'+establishment_service.name,creator=creator)
        establishment_service.folder = folder
        establishment_service.establishment_service_childs.set(establishment_service_childs)
        establishment_service.save()
        return CreateEstablishmentService(establishment_service=establishment_service)

class UpdateEstablishmentService(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        establishment_service_data = EstablishmentServiceInput(required=True)
        image = Upload(required=False)
        cover_image = Upload(required=False)

    establishment_service = graphene.Field(EstablishmentServiceType)

    def mutate(root, info, id, image=None, cover_image=None,  establishment_service_data=None):
        creator = info.context.user
        establishment_service_childs_ids = establishment_service_data.pop("establishment_service_childs")
        establishment_service_childs = EstablishmentService.objects.filter(id__in=establishment_service_childs_ids)
        EstablishmentService.objects.filter(pk=id).update(**establishment_service_data)
        establishment_service = EstablishmentService.objects.get(pk=id)
        if not establishment_service.folder or establishment_service.folder is None:
            folder = Folder.objects.create(name=str(establishment_service.id)+'_'+establishment_service.name,creator=creator)
            EstablishmentService.objects.filter(pk=id).update(folder=folder)
        if not image and establishment_service.image:
            image_file = establishment_service.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = establishment_service.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                establishment_service.image = image_file
            establishment_service.save()
        establishment_service.establishment_service_childs.set(establishment_service_childs)
        establishment_service = EstablishmentService.objects.get(pk=id)
        return UpdateEstablishmentService(establishment_service=establishment_service)
        
class UpdateEstablishmentServiceState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    establishment_service = graphene.Field(EstablishmentServiceType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, establishment_service_fields=None):
        creator = info.context.user
        done = True
        success = True
        establishment_service = None
        message = ''
        try:
            establishment_service = EstablishmentService.objects.get(pk=id)
            EstablishmentService.objects.filter(pk=id).update(is_active=not establishment_service.is_active)
            establishment_service.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            establishment_service=None
            message = "Une erreur s'est produite."
        return UpdateEstablishmentServiceState(done=done, success=success, message=message,establishment_service=establishment_service)

class DeleteEstablishmentService(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    establishment_service = graphene.Field(EstablishmentServiceType)
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
            establishment_service = EstablishmentService.objects.get(pk=id)
            establishment_service.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEstablishmentService(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#

class CompanyMutation(graphene.ObjectType):
    create_company = CreateCompany.Field()
    update_company = UpdateCompany.Field()
    delete_company = DeleteCompany.Field()

    create_establishment = CreateEstablishment.Field()
    update_establishment = UpdateEstablishment.Field()
    update_establishment_state = UpdateEstablishmentState.Field()
    delete_establishment = DeleteEstablishment.Field()

    create_establishment_service = CreateEstablishmentService.Field()
    update_establishment_service = UpdateEstablishmentService.Field()
    update_establishment_service_state = UpdateEstablishmentServiceState.Field()
    delete_establishment_service = DeleteEstablishmentService.Field()