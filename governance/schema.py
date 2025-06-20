import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from django.core.exceptions import PermissionDenied
import datetime

from django.db.models import Q

from graphene.types.generic import GenericScalar
from governance.utils import build_governance_organization_tree

from governance.models import GovernanceMember, GovernanceMemberRole
from medias.models import Folder, File
from companies.schema import CompanyType

class GovernanceMemberRoleType(DjangoObjectType):
    class Meta:
        model = GovernanceMemberRole
        fields = "__all__"

class GovernanceMemberType(DjangoObjectType):
    class Meta:
        model = GovernanceMember
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    governance_roles = graphene.List(graphene.String)
    role = graphene.String()
    last_governance_member_role = graphene.Field(GovernanceMemberRoleType)
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)
    def resolve_governance_roles( instance, info, **kwargs ):
        return instance.governance_roles
    def resolve_role( instance, info, **kwargs ):
        return instance.current_role
    def resolve_last_governance_member_role( instance, info, **kwargs ):
        return instance.last_governance_member_role

class GovernanceMemberNodeType(graphene.ObjectType):
    nodes = graphene.List(GovernanceMemberType)
    total_count = graphene.Int()

class OrganizationInfosType(graphene.ObjectType):
    organization_tree = GenericScalar()
    current_date = graphene.DateTime(required=False)
    company = graphene.Field(CompanyType)
    def resolve_organization_tree( instance, info, **kwargs ):
        return build_governance_organization_tree(info)
    def resolve_current_date( instance, info, **kwargs ):
        return datetime.datetime.now()
    def resolve_company( instance, info, **kwargs ):
        user = info.context.user
        return user.the_current_company if user else None

class GovernanceMemberFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class GovernanceMemberRoleInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    role = graphene.String(required=False)
    other_role = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    is_active = graphene.Boolean(required=False)
    governance_member_id = graphene.Int(name="governanceMember", required=False)

class GovernanceMemberInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    role = graphene.String(required=False)
    birth_date = graphene.DateTime(required=False)
    hiring_date = graphene.DateTime(required=False)
    probation_end_date = graphene.DateTime(required=False)
    work_end_date = graphene.DateTime(required=False)
    starting_salary = graphene.Float(required=False)
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
    is_archived = graphene.Boolean(required=False)
    governance_member_roles = graphene.List(GovernanceMemberRoleInput, required=False)

class GovernanceQuery(graphene.ObjectType):
    governance_members = graphene.Field(GovernanceMemberNodeType, governance_member_filter= GovernanceMemberFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    governance_member = graphene.Field(GovernanceMemberType, id = graphene.ID())
    governance_organization = graphene.Field(OrganizationInfosType)
    def resolve_governance_members(root, info, governance_member_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        governance_members = GovernanceMember.objects.filter(company=company, is_deleted=False)
        the_order_by = '-created_at'
        is_archived=False
        if governance_member_filter:
            keyword = governance_member_filter.get('keyword', '')
            starting_date_time = governance_member_filter.get('starting_date_time')
            ending_date_time = governance_member_filter.get('ending_date_time')
            list_type = governance_member_filter.get('list_type') # ALL / GOVERNANCE_MEMBER_ACTIONS / GOVERNANCE_MEMBER_ARCHIVED
            order_by = governance_member_filter.get('order_by')
            if list_type:
                if list_type == 'GOVERNANCE_MEMBER_ARCHIVED':
                    is_archived=True
                elif list_type == 'ALL':
                    pass
            if keyword:
                governance_members = governance_members.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                governance_members = governance_members.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                governance_members = governance_members.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        governance_members = governance_members.filter(is_archived=is_archived)
        governance_members = governance_members.order_by(the_order_by).distinct()
        total_count = governance_members.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            governance_members = governance_members[offset:offset + limit]
        return GovernanceMemberNodeType(nodes=governance_members, total_count=total_count)

    def resolve_governance_member(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            governance_member = GovernanceMember.objects.get(pk=id, company=company)
        except GovernanceMember.DoesNotExist:
            governance_member = None
        return governance_member

    def resolve_governance_organization(root, info):
        # Logique pour récupérer l'organisation
        user = info.context.user
        company = user.the_current_company
        return OrganizationInfosType()

class CreateGovernanceMember(graphene.Mutation):
    class Arguments:
        governance_member_data = GovernanceMemberInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    governance_member = graphene.Field(GovernanceMemberType)

    def mutate(root, info, photo=None, cover_image=None,  governance_member_data=None):
        creator = info.context.user
        if not creator.can_manage_governance():
            raise PermissionDenied("Impossible de modifier : vous n'avez pas les droits nécessaires.")
        governance_member_roles = governance_member_data.pop("governance_member_roles", None)
        governance_member = GovernanceMember(**governance_member_data)
        governance_member.creator = creator
        governance_member.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = governance_member.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                governance_member.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = governance_member.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                governance_member.cover_image = cover_image_file
        governance_member.save()
        folder = Folder.objects.create(name=str(governance_member.id)+'_'+governance_member.first_name+'-'+governance_member.last_name,creator=creator)
        governance_member.folder = folder
        governance_member.save()
        if governance_member_roles is not None:
            for item in governance_member_roles:
                GovernanceMemberRole.objects.create(
                    governance_member=governance_member,
                    **item
                )
        return CreateGovernanceMember(governance_member=governance_member)

class UpdateGovernanceMember(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        governance_member_data = GovernanceMemberInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    governance_member = graphene.Field(GovernanceMemberType)

    def mutate(root, info, id, photo=None, cover_image=None,  governance_member_data=None):
        creator = info.context.user
        if not creator.can_manage_governance():
            raise PermissionDenied("Impossible de modifier : vous n'avez pas les droits nécessaires.")
        try:
            governance_member = GovernanceMember.objects.get(pk=id, company=creator.the_current_company)
        except GovernanceMember.DoesNotExist:
            raise e
        governance_member_roles = governance_member_data.pop("governance_member_roles", None)
        GovernanceMember.objects.filter(pk=id).update(**governance_member_data)
        governance_member.refresh_from_db()
        if not governance_member.folder or governance_member.folder is None:
            folder = Folder.objects.create(name=str(governance_member.id)+'_'+governance_member.first_name+'-'+governance_member.last_name,creator=creator)
            GovernanceMember.objects.filter(pk=id).update(folder=folder)
        if not photo and governance_member.photo:
            photo_file = governance_member.photo
            photo_file.delete()
        if not cover_image and governance_member.cover_image:
            cover_image_file = governance_member.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = governance_member.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                governance_member.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = governance_member.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                governance_member.cover_image = cover_image_file
            governance_member.save()
        if governance_member_roles is not None:
            governance_member_role_ids = [item.id for item in governance_member_roles if item.id is not None]
            GovernanceMemberRole.objects.filter(governance_member=governance_member).exclude(id__in=governance_member_role_ids).delete()
            for item in governance_member_roles:
                if id in item or 'id' in item:
                    GovernanceMemberRole.objects.filter(pk=item.id).update(**item)
                else:
                    GovernanceMemberRole.objects.create(
                        governance_member=governance_member,
                        **item
                    )
        governance_member.refresh_from_db()
        return UpdateGovernanceMember(governance_member=governance_member)

class UpdateGovernanceMemberState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    governance_member = graphene.Field(GovernanceMemberType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, governance_member_fields=None):
        creator = info.context.user
        if not creator.can_manage_governance():
            raise PermissionDenied("Impossible de modifier : vous n'avez pas les droits nécessaires.")
        try:
            governance_member = GovernanceMember.objects.get(pk=id, company=creator.the_current_company)
        except GovernanceMember.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            GovernanceMember.objects.filter(pk=id).update(is_active=not governance_member.is_active)
            governance_member.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            governance_member=None
            message = "Une erreur s'est produite."
        return UpdateGovernanceMemberState(done=done, success=success, message=message,governance_member=governance_member)

class UpdateGovernanceMemberFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        governance_member_data = GovernanceMemberInput(required=True)

    governance_member = graphene.Field(GovernanceMemberType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, governance_member_data=None):
        creator = info.context.user
        if not creator.can_manage_governance():
            raise PermissionDenied("Impossible de modifier : vous n'avez pas les droits nécessaires.")
        try:
            governance_member = GovernanceMember.objects.get(pk=id, company=creator.the_current_company)
        except GovernanceMember.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            GovernanceMember.objects.filter(pk=id).update(**governance_member_data)
            governance_member.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            governance_member=None
            message = "Une erreur s'est produite."
        return UpdateGovernanceMemberFields(done=done, success=success, message=message, governance_member=governance_member)

class DeleteGovernanceMember(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    governance_member = graphene.Field(GovernanceMemberType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        try:
            governance_member = GovernanceMember.objects.get(pk=id, company=current_user.the_current_company)
        except GovernanceMember.DoesNotExist:
            raise e
        if current_user.is_superuser or current_user.can_manage_governance() or governance_member.creator==current_user:
            governance_member = GovernanceMember.objects.get(pk=id)
            governance_member.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteGovernanceMember(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class GovernanceMutation(graphene.ObjectType):
    create_governance_member = CreateGovernanceMember.Field()
    update_governance_member = UpdateGovernanceMember.Field()
    update_governance_member_state = UpdateGovernanceMemberState.Field()
    update_governance_member_fields = UpdateGovernanceMemberFields.Field()
    delete_governance_member = DeleteGovernanceMember.Field()