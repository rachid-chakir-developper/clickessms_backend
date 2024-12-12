import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from partnerships.models import Partner, Financier
from medias.models import Folder, File

class PartnerType(DjangoObjectType):
    class Meta:
        model = Partner
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class PartnerNodeType(graphene.ObjectType):
    nodes = graphene.List(PartnerType)
    total_count = graphene.Int()

class FinancierType(DjangoObjectType):
    class Meta:
        model = Financier
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class FinancierNodeType(graphene.ObjectType):
    nodes = graphene.List(FinancierType)
    total_count = graphene.Int()

class PartnerFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class PartnerInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    partner_type = graphene.String(required=True)
    manager_name = graphene.String(required=True)
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
    position = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class FinancierFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class FinancierInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    external_number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    financier_type = graphene.String(required=True)
    manager_name = graphene.String(required=True)
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
    position = graphene.String(required=False)
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class PartnershipsQuery(graphene.ObjectType):
    partners = graphene.Field(PartnerNodeType, partner_filter= PartnerFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    partner = graphene.Field(PartnerType, id = graphene.ID())
    financiers = graphene.Field(FinancierNodeType, financier_filter= FinancierFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    financier = graphene.Field(FinancierType, id = graphene.ID())
    def resolve_partners(root, info, partner_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        partners = Partner.objects.filter(company__id=id_company) if id_company else Partner.objects.filter(company=company)
        if partner_filter:
            keyword = partner_filter.get('keyword', '')
            starting_date_time = partner_filter.get('starting_date_time')
            ending_date_time = partner_filter.get('ending_date_time')
            if keyword:
                partners = partners.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                partners = partners.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                partners = partners.filter(created_at__lte=ending_date_time)
        partners = partners.order_by('-created_at')
        total_count = partners.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            partners = partners[offset:offset + limit]
        return PartnerNodeType(nodes=partners, total_count=total_count)

    def resolve_partner(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            partner = Partner.objects.get(pk=id)
        except Partner.DoesNotExist:
            partner = None
        return partner
    def resolve_financiers(root, info, financier_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        financiers = Financier.objects.filter(company__id=id_company) if id_company else Financier.objects.filter(company=company)
        if financier_filter:
            keyword = financier_filter.get('keyword', '')
            starting_date_time = financier_filter.get('starting_date_time')
            ending_date_time = financier_filter.get('ending_date_time')
            if keyword:
                financiers = financiers.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                financiers = financiers.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                financiers = financiers.filter(created_at__lte=ending_date_time)
        financiers = financiers.order_by('-created_at')
        total_count = financiers.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            financiers = financiers[offset:offset + limit]
        return FinancierNodeType(nodes=financiers, total_count=total_count)

    def resolve_financier(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            financier = Financier.objects.get(pk=id)
        except Financier.DoesNotExist:
            financier = None
        return financier

class CreatePartner(graphene.Mutation):
    class Arguments:
        partner_data = PartnerInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    partner = graphene.Field(PartnerType)

    def mutate(root, info, photo=None, cover_image=None,  partner_data=None):
        creator = info.context.user
        partner = Partner(**partner_data)
        partner.creator = creator
        partner.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = partner.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                partner.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = partner.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                partner.cover_image = cover_image_file
        partner.save()
        folder = Folder.objects.create(name=str(partner.id)+'_'+partner.name,creator=creator)
        partner.folder = folder
        partner.save()
        return CreatePartner(partner=partner)

class UpdatePartner(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        partner_data = PartnerInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    partner = graphene.Field(PartnerType)

    def mutate(root, info, id, photo=None, cover_image=None,  partner_data=None):
        creator = info.context.user
        Partner.objects.filter(pk=id).update(**partner_data)
        partner = Partner.objects.get(pk=id)
        if not partner.folder or partner.folder is None:
            folder = Folder.objects.create(name=str(partner.id)+'_'+partner.name,creator=creator)
            Partner.objects.filter(pk=id).update(folder=folder)
        if not photo and partner.photo:
            photo_file = partner.photo
            photo_file.delete()
        if not cover_image and partner.cover_image:
            cover_image_file = partner.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = partner.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                partner.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = partner.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                partner.cover_image = cover_image_file
            partner.save()
        partner = Partner.objects.get(pk=id)
        return UpdatePartner(partner=partner)

class UpdatePartnerState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    partner = graphene.Field(PartnerType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, partner_fields=None):
        creator = info.context.user
        done = True
        success = True
        partner = None
        message = ''
        try:
            partner = Partner.objects.get(pk=id)
            Partner.objects.filter(pk=id).update(is_active=not partner.is_active)
            partner.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            partner=None
            message = "Une erreur s'est produite."
        return UpdatePartnerState(done=done, success=success, message=message,partner=partner)

class DeletePartner(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    partner = graphene.Field(PartnerType)
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
            partner = Partner.objects.get(pk=id)
            partner.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeletePartner(deleted=deleted, success=success, message=message, id=id)

#****************************************************************************************************************

class CreateFinancier(graphene.Mutation):
    class Arguments:
        financier_data = FinancierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    financier = graphene.Field(FinancierType)

    def mutate(root, info, photo=None, cover_image=None,  financier_data=None):
        creator = info.context.user
        financier = Financier(**financier_data)
        financier.creator = creator
        financier.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = financier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                financier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = financier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                financier.cover_image = cover_image_file
        financier.save()
        folder = Folder.objects.create(name=str(financier.id)+'_'+financier.name,creator=creator)
        financier.folder = folder
        financier.save()
        return CreateFinancier(financier=financier)

class UpdateFinancier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        financier_data = FinancierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    financier = graphene.Field(FinancierType)

    def mutate(root, info, id, photo=None, cover_image=None,  financier_data=None):
        creator = info.context.user
        Financier.objects.filter(pk=id).update(**financier_data)
        financier = Financier.objects.get(pk=id)
        if not financier.folder or financier.folder is None:
            folder = Folder.objects.create(name=str(financier.id)+'_'+financier.name,creator=creator)
            Financier.objects.filter(pk=id).update(folder=folder)
        if not photo and financier.photo:
            photo_file = financier.photo
            photo_file.delete()
        if not cover_image and financier.cover_image:
            cover_image_file = financier.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = financier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                financier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = financier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                financier.cover_image = cover_image_file
            financier.save()
        financier = Financier.objects.get(pk=id)
        return UpdateFinancier(financier=financier)
        
class UpdateFinancierState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    financier = graphene.Field(FinancierType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, financier_fields=None):
        creator = info.context.user
        done = True
        success = True
        financier = None
        message = ''
        try:
            financier = Financier.objects.get(pk=id)
            Financier.objects.filter(pk=id).update(is_active=not financier.is_active)
            financier.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            financier=None
            message = "Une erreur s'est produite."
        return UpdateFinancierState(done=done, success=success, message=message,financier=financier)

class DeleteFinancier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    financier = graphene.Field(FinancierType)
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
            financier = Financier.objects.get(pk=id)
            financier.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteFinancier(deleted=deleted, success=success, message=message, id=id)

#********************************************************************************************************************

class PartnershipsMutation(graphene.ObjectType):
    create_partner = CreatePartner.Field()
    update_partner = UpdatePartner.Field()
    update_partner_state = UpdatePartnerState.Field()
    delete_partner = DeletePartner.Field()
    
    create_financier = CreateFinancier.Field()
    update_financier = UpdateFinancier.Field()
    update_financier_state = UpdateFinancierState.Field()
    delete_financier = DeleteFinancier.Field()