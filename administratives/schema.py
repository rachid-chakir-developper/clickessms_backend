import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from administratives.models import Call, CallBeneficiary, CallBeneficiaryAbsence
from medias.models import Folder, File
from human_ressources.models import Beneficiary

class CallBeneficiaryType(DjangoObjectType):
    class Meta:
        model = CallBeneficiary
        fields = "__all__"

class CallBeneficiaryAbsenceType(DjangoObjectType):
    class Meta:
        model = CallBeneficiaryAbsence
        fields = "__all__"

class CallBeneficiaryAbsenceNodeType(graphene.ObjectType):
    nodes = graphene.List(CallBeneficiaryAbsenceType)
    total_count = graphene.Int()

class CallBeneficiaryAbsenceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class CallType(DjangoObjectType):
    class Meta:
        model = Call
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(CallBeneficiaryType)
    absences = graphene.List(CallBeneficiaryAbsenceType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.callbeneficiary_set.all()
    def resolve_absences( instance, info, **kwargs ):
        return instance.callbeneficiaryabsence_set.all()

class CallNodeType(graphene.ObjectType):
    nodes = graphene.List(CallType)
    total_count = graphene.Int()

class CallFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class CallInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    entry_date_time = graphene.DateTime(required=False)
    duration = graphene.Float(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class CallBeneficiaryAbsenceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class AdministrativesQuery(graphene.ObjectType):
    calls = graphene.Field(CallNodeType, call_filter= CallFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    call = graphene.Field(CallType, id = graphene.ID())
    call_beneficiary_absences = graphene.Field(CallBeneficiaryAbsenceNodeType, call_beneficiary_absence_filter= CallBeneficiaryAbsenceFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    call_beneficiary_absence = graphene.Field(CallBeneficiaryAbsenceType, id = graphene.ID())
    def resolve_calls(root, info, call_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        calls = Call.objects.all()
        if call_filter:
            keyword = call_filter.get('keyword', '')
            starting_date_time = call_filter.get('starting_date_time')
            ending_date_time = call_filter.get('ending_date_time')
            if keyword:
                calls = calls.filter(Q(title__icontains=keyword))
            if starting_date_time:
                calls = calls.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                calls = calls.filter(starting_date_time__lte=ending_date_time)
        calls = calls.order_by('-created_at')
        total_count = calls.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            calls = calls[offset:offset + limit]
        return CallNodeType(nodes=calls, total_count=total_count)

    def resolve_call(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            call = Call.objects.get(pk=id)
        except Call.DoesNotExist:
            call = None
        return call

    def resolve_call_beneficiary_absences(root, info, call_beneficiary_absence_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        call_beneficiary_absences = CallBeneficiaryAbsence.objects.all()
        if call_beneficiary_absence_filter:
            keyword = call_beneficiary_absence_filter.get('keyword', '')
            starting_date_time = call_beneficiary_absence_filter.get('starting_date_time')
            ending_date_time = call_beneficiary_absence_filter.get('ending_date_time')
            if keyword:
                call_beneficiary_absences = call_beneficiary_absences.filter(Q(title__icontains=keyword))
            if starting_date_time:
                call_beneficiary_absences = call_beneficiary_absences.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                call_beneficiary_absences = call_beneficiary_absences.filter(starting_date_time__lte=ending_date_time)
        call_beneficiary_absences = call_beneficiary_absences.order_by('-created_at')
        total_count = call_beneficiary_absences.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            call_beneficiary_absences = call_beneficiary_absences[offset:offset + limit]
        return CallBeneficiaryAbsenceNodeType(nodes=call_beneficiary_absences, total_count=total_count)

    def resolve_call_beneficiary_absence(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            call_beneficiary_absence = CallBeneficiaryAbsence.objects.get(pk=id)
        except CallBeneficiaryAbsence.DoesNotExist:
            call_beneficiary_absence = None
        return call_beneficiary_absence

#************************************************************************

class CreateCall(graphene.Mutation):
    class Arguments:
        call_data = CallInput(required=True)
        image = Upload(required=False)

    call = graphene.Field(CallType)

    def mutate(root, info, image=None, call_data=None):
        creator = info.context.user
        beneficiary_ids = call_data.pop("beneficiaries")
        call = Call(**call_data)
        call.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = call.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                call.image = image_file
        call.save()
        folder = Folder.objects.create(name=str(call.id)+'_'+call.title,creator=creator)
        call.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                call_beneficiary = CallBeneficiary.objects.get(beneficiary__id=beneficiary.id, call__id=call.id)
            except CallBeneficiary.DoesNotExist:
                CallBeneficiary.objects.create(
                        call=call,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        call.save()
        return CreateCall(call=call)

class UpdateCall(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        call_data = CallInput(required=True)
        image = Upload(required=False)

    call = graphene.Field(CallType)

    def mutate(root, info, id, image=None, call_data=None):
        creator = info.context.user
        beneficiary_ids = call_data.pop("beneficiaries")
        Call.objects.filter(pk=id).update(**call_data)
        call = Call.objects.get(pk=id)
        if not call.folder or call.folder is None:
            folder = Folder.objects.create(name=str(call.id)+'_'+call.title,creator=creator)
            Call.objects.filter(pk=id).update(folder=folder)
        if not image and call.image:
            image_file = call.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = call.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                call.image = image_file
            call.save()
        CallBeneficiary.objects.filter(call=call).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                call_beneficiary = CallBeneficiary.objects.get(beneficiary__id=beneficiary.id, call__id=call.id)
            except CallBeneficiary.DoesNotExist:
                CallBeneficiary.objects.create(
                        call=call,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateCall(call=call)

class UpdateCallState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    call = graphene.Field(CallType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, call_fields=None):
        creator = info.context.user
        done = True
        success = True
        call = None
        message = ''
        try:
            call = Call.objects.get(pk=id)
            Call.objects.filter(pk=id).update(is_active=not call.is_active)
            call.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            call=None
            message = "Une erreur s'est produite."
        return UpdateCallState(done=done, success=success, message=message,call=call)


class DeleteCall(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    call = graphene.Field(CallType)
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
            call = Call.objects.get(pk=id)
            call.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteCall(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

class CreateCallBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        call_beneficiary_absence_data = CallBeneficiaryAbsenceInput(required=True)

    call_beneficiary_absence = graphene.Field(CallBeneficiaryAbsenceType)

    def mutate(root, info, call_beneficiary_absence_data=None):
        creator = info.context.user
        beneficiary_ids = call_beneficiary_absence_data.pop("beneficiaries")
        call_beneficiary_absence = CallBeneficiaryAbsence(**call_beneficiary_absence_data)
        call_beneficiary_absence.creator = creator
        folder = Folder.objects.create(name=str(call_beneficiary_absence.id)+'_'+call_beneficiary_absence.title,creator=creator)
        call_beneficiary_absence.folder = folder
        call_beneficiary_absence.save()
        return CreateCallBeneficiaryAbsence(call_beneficiary_absence=call_beneficiary_absence)

class UpdateCallBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        call_beneficiary_absence_data = CallBeneficiaryAbsenceInput(required=True)

    call_beneficiary_absence = graphene.Field(CallBeneficiaryAbsenceType)

    def mutate(root, info, id, image=None, call_beneficiary_absence_data=None):
        creator = info.context.user
        beneficiary_ids = call_beneficiary_absence_data.pop("beneficiaries")
        CallBeneficiaryAbsence.objects.filter(pk=id).update(**call_beneficiary_absence_data)
        call_beneficiary_absence = CallBeneficiaryAbsence.objects.get(pk=id)
        if not call_beneficiary_absence.folder or call_beneficiary_absence.folder is None:
            folder = Folder.objects.create(name=str(call_beneficiary_absence.id)+'_'+call_beneficiary_absence.title,creator=creator)
            CallBeneficiaryAbsence.objects.filter(pk=id).update(folder=folder)
        return UpdateCallBeneficiaryAbsence(call_beneficiary_absence=call_beneficiary_absence)

class DeleteCallBeneficiaryAbsence(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    call_beneficiary_absence = graphene.Field(CallBeneficiaryAbsenceType)
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
            call_beneficiary_absence = CallBeneficiaryAbsence.objects.get(pk=id)
            call_beneficiary_absence.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteCallBeneficiaryAbsence(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#
class AdministrativesMutation(graphene.ObjectType):
    create_call = CreateCall.Field()
    update_call = UpdateCall.Field()
    update_call_state = UpdateCallState.Field()
    delete_call = DeleteCall.Field()
    create_call_beneficiary_absence = CreateCallBeneficiaryAbsence.Field()
    update_call_beneficiary_absence = UpdateCallBeneficiaryAbsence.Field()
    delete_call_beneficiary_absence = DeleteCallBeneficiaryAbsence.Field()