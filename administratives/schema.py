import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from administratives.models import Call, CallBeneficiary, Letter, LetterBeneficiary, Meeting, ParticipantMeetingItem,  BeneficiaryMeetingItem
from data_management.models import MeetingReason
from medias.models import Folder, File
from human_ressources.models import Employee, Beneficiary

class CallBeneficiaryType(DjangoObjectType):
    class Meta:
        model = CallBeneficiary
        fields = "__all__"

class CallType(DjangoObjectType):
    class Meta:
        model = Call
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(CallBeneficiaryType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.callbeneficiary_set.all()

class CallNodeType(graphene.ObjectType):
    nodes = graphene.List(CallType)
    total_count = graphene.Int()

class CallFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class LetterBeneficiaryType(DjangoObjectType):
    class Meta:
        model = LetterBeneficiary
        fields = "__all__"

class LetterType(DjangoObjectType):
    class Meta:
        model = Letter
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(LetterBeneficiaryType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.letterbeneficiary_set.all()

class LetterNodeType(graphene.ObjectType):
    nodes = graphene.List(LetterType)
    total_count = graphene.Int()

class LetterFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class ParticipantMeetingItemType(DjangoObjectType):
    class Meta:
        model = ParticipantMeetingItem
        fields = "__all__"

class BeneficiaryMeetingItemType(DjangoObjectType):
    class Meta:
        model = BeneficiaryMeetingItem
        fields = "__all__"

class MeetingType(DjangoObjectType):
    class Meta:
        model = Meeting
        fields = "__all__"
    participants = graphene.List(ParticipantMeetingItemType)
    beneficiaries = graphene.List(BeneficiaryMeetingItemType)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.beneficiarymeetingitem_set.all()
    def resolve_participants( instance, info, **kwargs ):
        return instance.participantmeetingitem_set.all()

class MeetingNodeType(graphene.ObjectType):
    nodes = graphene.List(MeetingType)
    total_count = graphene.Int()

class MeetingFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class CallInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    call_type = graphene.String(required=True)
    entry_date_time = graphene.DateTime(required=False)
    duration = graphene.Float(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class LetterInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    letter_type = graphene.String(required=True)
    entry_date_time = graphene.DateTime(required=False)
    duration = graphene.Float(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    
class MeetingInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    video_call_link = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    participants = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    reasons = graphene.List(graphene.Int, required=False)
    other_reasons = graphene.String(required=False)

class AdministrativesQuery(graphene.ObjectType):
    calls = graphene.Field(CallNodeType, call_filter= CallFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    call = graphene.Field(CallType, id = graphene.ID())
    letters = graphene.Field(LetterNodeType, letter_filter= LetterFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    letter = graphene.Field(LetterType, id = graphene.ID())
    meetings = graphene.Field(MeetingNodeType, meeting_filter= MeetingFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    meeting = graphene.Field(MeetingType, id = graphene.ID())
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
                calls = calls.filter(entry_date_time__gte=starting_date_time)
            if ending_date_time:
                calls = calls.filter(entry_date_time__lte=ending_date_time)
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
    def resolve_letters(root, info, letter_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        letters = Letter.objects.all()
        if letter_filter:
            keyword = letter_filter.get('keyword', '')
            starting_date_time = letter_filter.get('starting_date_time')
            ending_date_time = letter_filter.get('ending_date_time')
            if keyword:
                letters = letters.filter(Q(title__icontains=keyword))
            if starting_date_time:
                letters = letters.filter(entry_date_time__gte=starting_date_time)
            if ending_date_time:
                letters = letters.filter(entry_date_time__lte=ending_date_time)
        letters = letters.order_by('-created_at')
        total_count = letters.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            letters = letters[offset:offset + limit]
        return LetterNodeType(nodes=letters, total_count=total_count)

    def resolve_letter(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            letter = Letter.objects.get(pk=id)
        except Letter.DoesNotExist:
            letter = None
        return letter

    def resolve_meetings(root, info, meeting_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        meetings = Meeting.objects.all()
        if meeting_filter:
            keyword = meeting_filter.get('keyword', '')
            starting_date_time = meeting_filter.get('starting_date_time')
            ending_date_time = meeting_filter.get('ending_date_time')
            if keyword:
                meetings = meetings.filter(Q(title__icontains=keyword))
            if starting_date_time:
                meetings = meetings.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                meetings = meetings.filter(starting_date_time__lte=ending_date_time)
        meetings = meetings.order_by('-created_at')
        total_count = meetings.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            meetings = meetings[offset:offset + limit]
        return MeetingNodeType(nodes=meetings, total_count=total_count)

    def resolve_meeting(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            meeting = Meeting.objects.get(pk=id)
        except Meeting.DoesNotExist:
            meeting = None
        return meeting

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

        
#*************************************************************************#
#************************************************************************

class CreateLetter(graphene.Mutation):
    class Arguments:
        letter_data = LetterInput(required=True)
        image = Upload(required=False)

    letter = graphene.Field(LetterType)

    def mutate(root, info, image=None, letter_data=None):
        creator = info.context.user
        beneficiary_ids = letter_data.pop("beneficiaries")
        letter = Letter(**letter_data)
        letter.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = letter.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                letter.image = image_file
        letter.save()
        folder = Folder.objects.create(name=str(letter.id)+'_'+letter.title,creator=creator)
        letter.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                letter_beneficiary = LetterBeneficiary.objects.get(beneficiary__id=beneficiary.id, letter__id=letter.id)
            except LetterBeneficiary.DoesNotExist:
                LetterBeneficiary.objects.create(
                        letter=letter,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        letter.save()
        return CreateLetter(letter=letter)

class UpdateLetter(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        letter_data = LetterInput(required=True)
        image = Upload(required=False)

    letter = graphene.Field(LetterType)

    def mutate(root, info, id, image=None, letter_data=None):
        creator = info.context.user
        beneficiary_ids = letter_data.pop("beneficiaries")
        Letter.objects.filter(pk=id).update(**letter_data)
        letter = Letter.objects.get(pk=id)
        if not letter.folder or letter.folder is None:
            folder = Folder.objects.create(name=str(letter.id)+'_'+letter.title,creator=creator)
            Letter.objects.filter(pk=id).update(folder=folder)
        if not image and letter.image:
            image_file = letter.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = letter.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                letter.image = image_file
            letter.save()
        LetterBeneficiary.objects.filter(letter=letter).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                letter_beneficiary = LetterBeneficiary.objects.get(beneficiary__id=beneficiary.id, letter__id=letter.id)
            except LetterBeneficiary.DoesNotExist:
                LetterBeneficiary.objects.create(
                        letter=letter,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateLetter(letter=letter)

class UpdateLetterState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    letter = graphene.Field(LetterType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, letter_fields=None):
        creator = info.context.user
        done = True
        success = True
        letter = None
        message = ''
        try:
            letter = Letter.objects.get(pk=id)
            Letter.objects.filter(pk=id).update(is_active=not letter.is_active)
            letter.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            letter=None
            message = "Une erreur s'est produite."
        return UpdateLetterState(done=done, success=success, message=message,letter=letter)


class DeleteLetter(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    letter = graphene.Field(LetterType)
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
            letter = Letter.objects.get(pk=id)
            letter.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteLetter(deleted=deleted, success=success, message=message, id=id)

        
#*************************************************************************#
#************************************************************************

class CreateMeeting(graphene.Mutation):
    class Arguments:
        meeting_data = MeetingInput(required=True)

    meeting = graphene.Field(MeetingType)

    def mutate(root, info, meeting_data=None):
        creator = info.context.user
        beneficiary_ids = meeting_data.pop("beneficiaries")
        participants_ids = meeting_data.pop("participants")
        reason_ids = meeting_data.pop("reasons")
        meeting = Meeting(**meeting_data)
        meeting.creator = creator
        meeting.save()
        folder = Folder.objects.create(name=str(meeting.id)+'_'+meeting.title,creator=creator)
        meeting.folder = folder
        if not meeting.employee:
            meeting.employee = creator.employee
        if reason_ids and reason_ids is not None:
            reasons = MeetingReason.objects.filter(id__in=reason_ids)
            meeting.reasons.set(reasons)
        employees = Employee.objects.filter(id__in=participants_ids)
        for employee in employees:
            try:
                participant_meeting_items = ParticipantMeetingItem.objects.get(employee__id=employee.id, meeting__id=meeting.id)
            except ParticipantMeetingItem.DoesNotExist:
                ParticipantMeetingItem.objects.create(
                        meeting=meeting,
                        employee=employee,
                        creator=creator
                    )
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_meeting_items = BeneficiaryMeetingItem.objects.get(beneficiary__id=beneficiary.id, meeting__id=meeting.id)
            except BeneficiaryMeetingItem.DoesNotExist:
                BeneficiaryMeetingItem.objects.create(
                        meeting=meeting,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        meeting.save()
        return CreateMeeting(meeting=meeting)

class UpdateMeeting(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        meeting_data = MeetingInput(required=True)

    meeting = graphene.Field(MeetingType)

    def mutate(root, info, id, image=None, meeting_data=None):
        creator = info.context.user
        beneficiary_ids = meeting_data.pop("beneficiaries")
        participants_ids = meeting_data.pop("participants")
        reason_ids = meeting_data.pop("reasons")
        Meeting.objects.filter(pk=id).update(**meeting_data)
        meeting = Meeting.objects.get(pk=id)
        if not meeting.folder or meeting.folder is None:
            folder = Folder.objects.create(name=str(meeting.id)+'_'+meeting.title,creator=creator)
            Meeting.objects.filter(pk=id).update(folder=folder)
        if not meeting.employee:
            meeting.employee = creator.employee
            meeting.save()

        if reason_ids and reason_ids is not None:
            reasons = MeetingReason.objects.filter(id__in=reason_ids)
            meeting.reasons.set(reasons)

        ParticipantMeetingItem.objects.filter(meeting=meeting).exclude(employee__id__in=participants_ids).delete()
        employees = Employee.objects.filter(id__in=participants_ids)
        for employee in employees:
            try:
                participant_meeting_items = ParticipantMeetingItem.objects.get(employee__id=employee.id, meeting__id=meeting.id)
            except ParticipantMeetingItem.DoesNotExist:
                ParticipantMeetingItem.objects.create(
                        meeting=meeting,
                        employee=employee,
                        creator=creator
                    )
        BeneficiaryMeetingItem.objects.filter(meeting=meeting).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_meeting_items = BeneficiaryMeetingItem.objects.get(beneficiary__id=beneficiary.id, meeting__id=meeting.id)
            except BeneficiaryMeetingItem.DoesNotExist:
                BeneficiaryMeetingItem.objects.create(
                        meeting=meeting,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateMeeting(meeting=meeting)

class DeleteMeeting(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    meeting = graphene.Field(MeetingType)
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
            meeting = Meeting.objects.get(pk=id)
            meeting.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteMeeting(deleted=deleted, success=success, message=message, id=id)
        
#*************************************************************************#

class AdministrativesMutation(graphene.ObjectType):
    create_call = CreateCall.Field()
    update_call = UpdateCall.Field()
    update_call_state = UpdateCallState.Field()
    delete_call = DeleteCall.Field()

    create_letter = CreateLetter.Field()
    update_letter = UpdateLetter.Field()
    update_letter_state = UpdateLetterState.Field()
    delete_letter = DeleteLetter.Field()

    create_meeting = CreateMeeting.Field()
    update_meeting = UpdateMeeting.Field()
    delete_meeting = DeleteMeeting.Field()