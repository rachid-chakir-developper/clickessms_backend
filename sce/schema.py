import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from sce.models import SceMember, SceBenefit
from medias.models import Folder, File

class SceMemberType(DjangoObjectType):
    class Meta:
        model = SceMember
        fields = "__all__"

class SceMemberNodeType(graphene.ObjectType):
    nodes = graphene.List(SceMemberType)
    total_count = graphene.Int()

class SceMemberFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class SceMemberInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    role = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)

class SceBenefitType(DjangoObjectType):
    class Meta:
        model = SceBenefit
        fields = "__all__"

class SceBenefitNodeType(graphene.ObjectType):
    nodes = graphene.List(SceBenefitType)
    total_count = graphene.Int()

class SceBenefitFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class SceBenefitInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    content = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class SceQuery(graphene.ObjectType):
    sce_members = graphene.Field(SceMemberNodeType, sce_member_filter= SceMemberFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    sce_member = graphene.Field(SceMemberType, id = graphene.ID())
    sce_benefits = graphene.Field(SceBenefitNodeType, sce_benefit_filter= SceBenefitFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    sce_benefit = graphene.Field(SceBenefitType, id = graphene.ID())
    def resolve_sce_members(root, info, sce_member_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        sce_members = SceMember.objects.filter(company__id=id_company) if id_company else SceMember.objects.filter(company=company)
        if sce_member_filter:
            keyword = sce_member_filter.get('keyword', '')
            starting_date_time = sce_member_filter.get('starting_date_time')
            ending_date_time = sce_member_filter.get('ending_date_time')
            if keyword:
                sce_members = sce_members.filter(Q(employee__first_name__icontains=keyword) | Q(employee__last_name__icontains=keyword) | Q(employee__email__icontains=keyword))
            if starting_date_time:
                sce_members = sce_members.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                sce_members = sce_members.filter(created_at__lte=ending_date_time)
        sce_members = sce_members.order_by('-created_at')
        total_count = sce_members.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            sce_members = sce_members[offset:offset + limit]
        return SceMemberNodeType(nodes=sce_members, total_count=total_count)

    def resolve_sce_member(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            sce_member = SceMember.objects.get(pk=id)
        except SceMember.DoesNotExist:
            sce_member = None
        return sce_member
    def resolve_sce_benefits(root, info, sce_benefit_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        sce_benefits = SceBenefit.objects.filter(company__id=id_company) if id_company else SceBenefit.objects.filter(company=company)
        if sce_benefit_filter:
            keyword = sce_benefit_filter.get('keyword', '')
            starting_date_time = sce_benefit_filter.get('starting_date_time')
            ending_date_time = sce_benefit_filter.get('ending_date_time')
            if keyword:
                sce_benefits = sce_benefits.filter(Q(title__icontains=keyword))
            if starting_date_time:
                sce_benefits = sce_benefits.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                sce_benefits = sce_benefits.filter(created_at__lte=ending_date_time)
        sce_benefits = sce_benefits.order_by('-created_at')
        total_count = sce_benefits.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            sce_benefits = sce_benefits[offset:offset + limit]
        return SceBenefitNodeType(nodes=sce_benefits, total_count=total_count)

    def resolve_sce_benefit(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            sce_benefit = SceBenefit.objects.get(pk=id)
        except SceBenefit.DoesNotExist:
            sce_benefit = None
        return sce_benefit

class CreateSceMember(graphene.Mutation):
    class Arguments:
        sce_member_data = SceMemberInput(required=True)

    sce_member = graphene.Field(SceMemberType)

    def mutate(root, info, sce_member_data=None):
        creator = info.context.user
        sce_member = None
        try:
            sce_member = SceMember.objects.get(employee__id=sce_member_data.employee_id)
            sce_member = None
        except SceMember.DoesNotExist:
            sce_member = SceMember(**sce_member_data)
            sce_member.creator = creator
            sce_member.company = creator.current_company if creator.current_company is not None else creator.company
            sce_member.save()
            folder = Folder.objects.create(name=str(sce_member.id)+'_'+sce_member.employee.first_name+'-'+sce_member.employee.last_name,creator=creator)
            sce_member.folder = folder
            sce_member.save()
        return CreateSceMember(sce_member=sce_member)

class UpdateSceMember(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        sce_member_data = SceMemberInput(required=True)

    sce_member = graphene.Field(SceMemberType)

    def mutate(root, info, id, sce_member_data=None):
        creator = info.context.user
        SceMember.objects.filter(pk=id).update(**sce_member_data)
        sce_member = SceMember.objects.get(pk=id)
        if not sce_member.folder or sce_member.folder is None:
            folder = Folder.objects.create(name=str(sce_member.id)+'_'+sce_member.employee.first_name+'-'+sce_member.employee.last_name,creator=creator)
            SceMember.objects.filter(pk=id).update(folder=folder)
        sce_member = SceMember.objects.get(pk=id)
        return UpdateSceMember(sce_member=sce_member)

class UpdateSceMemberState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    sce_member = graphene.Field(SceMemberType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, sce_member_fields=None):
        creator = info.context.user
        done = True
        success = True
        sce_member = None
        message = ''
        try:
            sce_member = SceMember.objects.get(pk=id)
            SceMember.objects.filter(pk=id).update(is_active=not sce_member.is_active)
            sce_member.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            sce_member=None
            message = "Une erreur s'est produite."
        return UpdateSceMemberState(done=done, success=success, message=message,sce_member=sce_member)

class DeleteSceMember(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    sce_member = graphene.Field(SceMemberType)
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
            sce_member = SceMember.objects.get(pk=id)
            sce_member.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteSceMember(deleted=deleted, success=success, message=message, id=id)

#************************************************************************


class CreateSceBenefit(graphene.Mutation):
    class Arguments:
        sce_benefit_data = SceBenefitInput(required=True)

    sce_benefit = graphene.Field(SceBenefitType)

    def mutate(root, info, sce_benefit_data=None):
        creator = info.context.user
        sce_benefit = SceBenefit(**sce_benefit_data)
        sce_benefit.creator = creator
        sce_benefit.company = creator.current_company if creator.current_company is not None else creator.company
        sce_benefit.save()
        folder = Folder.objects.create(name=str(sce_benefit.id)+'_'+sce_benefit.title+'-'+sce_benefit.title,creator=creator)
        sce_benefit.folder = folder
        sce_benefit.save()
        return CreateSceBenefit(sce_benefit=sce_benefit)

class UpdateSceBenefit(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        sce_benefit_data = SceBenefitInput(required=True)

    sce_benefit = graphene.Field(SceBenefitType)

    def mutate(root, info, id, sce_benefit_data=None):
        creator = info.context.user
        SceBenefit.objects.filter(pk=id).update(**sce_benefit_data)
        sce_benefit = SceBenefit.objects.get(pk=id)
        if not sce_benefit.folder or sce_benefit.folder is None:
            folder = Folder.objects.create(name=str(sce_benefit.id)+'_'+sce_benefit.title+'-'+sce_benefit.title,creator=creator)
            SceBenefit.objects.filter(pk=id).update(folder=folder)
        sce_benefit = SceBenefit.objects.get(pk=id)
        return UpdateSceBenefit(sce_benefit=sce_benefit)

class UpdateSceBenefitState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    sce_benefit = graphene.Field(SceBenefitType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, sce_benefit_fields=None):
        creator = info.context.user
        done = True
        success = True
        sce_benefit = None
        message = ''
        try:
            sce_benefit = SceBenefit.objects.get(pk=id)
            SceBenefit.objects.filter(pk=id).update(is_active=not sce_benefit.is_active)
            sce_benefit.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            sce_benefit=None
            message = "Une erreur s'est produite."
        return UpdateSceBenefitState(done=done, success=success, message=message,sce_benefit=sce_benefit)

class DeleteSceBenefit(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    sce_benefit = graphene.Field(SceBenefitType)
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
            sce_benefit = SceBenefit.objects.get(pk=id)
            sce_benefit.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteSceBenefit(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class SceMutation(graphene.ObjectType):
    create_sce_member = CreateSceMember.Field()
    update_sce_member = UpdateSceMember.Field()
    update_sce_member_state = UpdateSceMemberState.Field()
    delete_sce_member = DeleteSceMember.Field()

    create_sce_benefit = CreateSceBenefit.Field()
    update_sce_benefit = UpdateSceBenefit.Field()
    update_sce_benefit_state = UpdateSceBenefitState.Field()
    delete_sce_benefit = DeleteSceBenefit.Field()
    