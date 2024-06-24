import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from administratives.models import Call, Caller, CallEstablishment, CallEmployee, CallBeneficiary, Letter, LetterEstablishment, LetterEmployee, LetterBeneficiary, Meeting, MeetingEstablishment, MeetingParticipant,  MeetingBeneficiary, MeetingDecision, MeetingReviewPoint
from data_management.models import MeetingReason, TypeMeeting
from medias.models import Folder, File
from companies.models import Establishment
from human_ressources.models import Employee, Beneficiary

class CallEstablishmentType(DjangoObjectType):
    class Meta:
        model = CallEstablishment
        fields = "__all__"
class CallEmployeeType(DjangoObjectType):
    class Meta:
        model = CallEmployee
        fields = "__all__"
class CallBeneficiaryType(DjangoObjectType):
    class Meta:
        model = CallBeneficiary
        fields = "__all__"

class CallerType(DjangoObjectType):
    class Meta:
        model = Caller
        fields = "__all__"

class CallType(DjangoObjectType):
    class Meta:
        model = Call
        fields = "__all__"
    image = graphene.String()
    caller = graphene.Field(CallerType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_caller(instance, info, **kwargs):
        return instance.callers.all().first()

class CallNodeType(graphene.ObjectType):
    nodes = graphene.List(CallType)
    total_count = graphene.Int()

class CallFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class LetterEstablishmentType(DjangoObjectType):
    class Meta:
        model = LetterEstablishment
        fields = "__all__"
class LetterEmployeeType(DjangoObjectType):
    class Meta:
        model = LetterEmployee
        fields = "__all__"

class LetterBeneficiaryType(DjangoObjectType):
    class Meta:
        model = LetterBeneficiary
        fields = "__all__"

class LetterType(DjangoObjectType):
    class Meta:
        model = Letter
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class LetterNodeType(graphene.ObjectType):
    nodes = graphene.List(LetterType)
    total_count = graphene.Int()

class LetterFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class MeetingEstablishmentType(DjangoObjectType):
    class Meta:
        model = MeetingEstablishment
        fields = "__all__"

class MeetingParticipantType(DjangoObjectType):
    class Meta:
        model = MeetingParticipant
        fields = "__all__"

class MeetingBeneficiaryType(DjangoObjectType):
    class Meta:
        model = MeetingBeneficiary
        fields = "__all__"

class MeetingDecisionType(DjangoObjectType):
    class Meta:
        model = MeetingDecision
        fields = "__all__"

class MeetingReviewPointType(DjangoObjectType):
    class Meta:
        model = MeetingReviewPoint
        fields = "__all__"

class MeetingType(DjangoObjectType):
    class Meta:
        model = Meeting
        fields = "__all__"

class MeetingNodeType(graphene.ObjectType):
    nodes = graphene.List(MeetingType)
    total_count = graphene.Int()

class MeetingFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    meeting_mode = graphene.String(required=False)

class CallerInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    name = graphene.String(required=False)
    phone = graphene.String(required=False)
    caller_type = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    partner_id = graphene.Int(name="partner", required=False)
    supplier_id = graphene.Int(name="supplier", required=False)
    client_id = graphene.Int(name="client", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)
    phone_number_id = graphene.Int(name="phoneNumber", required=False)

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
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    caller = CallerInput(required=False)

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
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class MeetingDecisionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    decision = graphene.String(required=False)
    due_date = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)
    for_voters = graphene.List(graphene.Int, required=False)
    against_voters = graphene.List(graphene.Int, required=False)

class MeetingReviewPointInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    point_to_review = graphene.String(required=False)
    
class MeetingInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=False)
    topic = graphene.String(required=False)
    meeting_mode = graphene.String(required=False)
    video_call_link = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    notes = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    employee_id = graphene.Int(name="employee", required=False)
    participants = graphene.List(graphene.Int, required=False)
    absent_participants = graphene.List(graphene.Int, required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)
    meeting_types = graphene.List(graphene.Int, required=False)
    reasons = graphene.List(graphene.Int, required=False)
    other_reasons = graphene.String(required=False)
    meeting_decisions = graphene.List(MeetingDecisionInput, required=False)
    meeting_review_points = graphene.List(MeetingReviewPointInput, required=False)
    
class AdministrativesQuery(graphene.ObjectType):
    calls = graphene.Field(CallNodeType, call_filter= CallFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    call = graphene.Field(CallType, id = graphene.ID())
    letters = graphene.Field(LetterNodeType, letter_filter= LetterFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    letter = graphene.Field(LetterType, id = graphene.ID())
    meetings = graphene.Field(MeetingNodeType, meeting_filter= MeetingFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    meeting = graphene.Field(MeetingType, id = graphene.ID())
    def resolve_calls(root, info, call_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        calls = Call.objects.filter(company=company)
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
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        letters = Letter.objects.filter(company=company)
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
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        meetings = Meeting.objects.filter(company=company)
        if meeting_filter:
            keyword = meeting_filter.get('keyword', '')
            starting_date_time = meeting_filter.get('starting_date_time')
            ending_date_time = meeting_filter.get('ending_date_time')
            meeting_mode = meeting_filter.get('meeting_mode', 'SIMPLE')
            meetings = meetings.filter(meeting_mode=meeting_mode if meeting_mode else 'SIMPLE')
            if keyword:
                meetings = meetings.filter(Q(title__icontains=keyword))
            if starting_date_time:
                meetings = meetings.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                meetings = meetings.filter(starting_date_time__lte=ending_date_time)
        else:
            meetings = meetings.filter(Q(meeting_mode='SIMPLE') | Q(meeting_mode='') | Q(meeting_mode=None))
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
        establishment_ids = call_data.pop("establishments")
        employee_ids = call_data.pop("employees")
        beneficiary_ids = call_data.pop("beneficiaries")
        caller_data = call_data.pop("caller")
        call = Call(**call_data)
        call.creator = creator
        call.company = creator.current_company if creator.current_company is not None else creator.company
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
        if call_data:
            call.setCaller(caller_data=caller_data, creator=creator)
        folder = Folder.objects.create(name=str(call.id)+'_'+call.title,creator=creator)
        call.folder = folder
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                call_establishment = CallEstablishment.objects.get(establishment__id=establishment.id, call__id=call.id)
            except CallEstablishment.DoesNotExist:
                CallEstablishment.objects.create(
                        call=call,
                        establishment=establishment,
                        creator=creator
                    )
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                call_employee = CallEmployee.objects.get(employee__id=employee.id, call__id=call.id)
            except CallEmployee.DoesNotExist:
                CallEmployee.objects.create(
                        call=call,
                        employee=employee,
                        creator=creator
                    )
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
        establishment_ids = call_data.pop("establishments")
        employee_ids = call_data.pop("employees")
        beneficiary_ids = call_data.pop("beneficiaries")
        caller_data = call_data.pop("caller")
        Call.objects.filter(pk=id).update(**call_data)
        call = Call.objects.get(pk=id)
        if call_data:
            call.setCaller(caller_data=caller_data, creator=creator)
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
        CallEstablishment.objects.filter(call=call).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                call_establishment = CallEstablishment.objects.get(establishment__id=establishment.id, call__id=call.id)
            except CallEstablishment.DoesNotExist:
                CallEstablishment.objects.create(
                        call=call,
                        establishment=establishment,
                        creator=creator
                    )
        CallEmployee.objects.filter(call=call).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                call_employee = CallEmployee.objects.get(employee__id=employee.id, call__id=call.id)
            except CallEmployee.DoesNotExist:
                CallEmployee.objects.create(
                        call=call,
                        employee=employee,
                        creator=creator
                    )
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
        establishment_ids = letter_data.pop("establishments")
        employee_ids = letter_data.pop("employees")
        beneficiary_ids = letter_data.pop("beneficiaries")
        letter = Letter(**letter_data)
        letter.creator = creator
        letter.company = creator.current_company if creator.current_company is not None else creator.company
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
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                letter_establishment = LetterEstablishment.objects.get(establishment__id=establishment.id, letter__id=letter.id)
            except LetterEstablishment.DoesNotExist:
                LetterEstablishment.objects.create(
                        letter=letter,
                        establishment=establishment,
                        creator=creator
                    )
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                letter_employee = LetterEmployee.objects.get(employee__id=employee.id, letter__id=letter.id)
            except LetterEmployee.DoesNotExist:
                LetterEmployee.objects.create(
                        letter=letter,
                        employee=employee,
                        creator=creator
                    )
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
        establishment_ids = letter_data.pop("establishments")
        employee_ids = letter_data.pop("employees")
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
        LetterEstablishment.objects.filter(letter=letter).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                letter_establishment = LetterEstablishment.objects.get(establishment__id=establishment.id, letter__id=letter.id)
            except LetterEstablishment.DoesNotExist:
                LetterEstablishment.objects.create(
                        letter=letter,
                        establishment=establishment,
                        creator=creator
                    )
        LetterEmployee.objects.filter(letter=letter).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                letter_employee = LetterEmployee.objects.get(employee__id=employee.id, letter__id=letter.id)
            except LetterEmployee.DoesNotExist:
                LetterEmployee.objects.create(
                        letter=letter,
                        employee=employee,
                        creator=creator
                    )
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
        establishment_ids = meeting_data.pop("establishments")
        beneficiary_ids = meeting_data.pop("beneficiaries")
        participants_ids = meeting_data.pop("participants")
        absent_participants_ids = meeting_data.pop("absent_participants")
        reason_ids = meeting_data.pop("reasons") if 'reasons' in meeting_data else None
        meeting_type_ids = meeting_data.pop("meeting_types")
        meeting_decisions = meeting_data.pop("meeting_decisions")
        meeting_review_points = meeting_data.pop("meeting_review_points")
        meeting = Meeting(**meeting_data)
        meeting.creator = creator
        meeting.company = creator.current_company if creator.current_company is not None else creator.company
        meeting.save()
        folder = Folder.objects.create(name=str(meeting.id)+'_'+meeting.title,creator=creator)
        meeting.folder = folder
        if not meeting.employee:
            meeting.employee = creator.getEmployeeInCompany()
        if reason_ids and reason_ids is not None:
            meeting.reasons.set(reason_ids)
        if absent_participants_ids and absent_participants_ids is not None:
            meeting.absent_participants.set(absent_participants_ids)

        if meeting_type_ids and meeting_type_ids is not None:
            meeting_types = TypeMeeting.objects.filter(id__in=meeting_type_ids)
            meeting.meeting_types.set(meeting_types)
        
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                meeting_establishment = MeetingEstablishment.objects.get(establishment__id=establishment.id, meeting__id=meeting.id)
            except MeetingEstablishment.DoesNotExist:
                MeetingEstablishment.objects.create(
                        meeting=meeting,
                        establishment=establishment,
                        creator=creator
                    )

        employees = Employee.objects.filter(id__in=participants_ids)
        for employee in employees:
            try:
                meeting_participant = MeetingParticipant.objects.get(employee__id=employee.id, meeting__id=meeting.id)
            except MeetingParticipant.DoesNotExist:
                MeetingParticipant.objects.create(
                        meeting=meeting,
                        employee=employee,
                        creator=creator
                    )
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                meeting_beneficiaries = MeetingBeneficiary.objects.get(beneficiary__id=beneficiary.id, meeting__id=meeting.id)
            except MeetingBeneficiary.DoesNotExist:
                MeetingBeneficiary.objects.create(
                        meeting=meeting,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        for item in meeting_decisions:
            employees_ids = item.pop("employees") if "employees" in item else None
            for_voters_ids = item.pop("for_voters") if "for_voters" in item else None
            against_voters_ids = item.pop("against_voters") if "against_voters" in item else None
            meeting_decision = MeetingDecision(**item)
            meeting_decision.meeting = meeting
            meeting_decision.save()
            if employees_ids and employees_ids is not None:
                meeting_decision.employees.set(employees_ids)
            if for_voters_ids and for_voters_ids is not None:
                meeting_decision.for_voters.set(for_voters_ids)
            if against_voters_ids and against_voters_ids is not None:
                meeting_decision.against_voters.set(against_voters_ids)

        for item in meeting_review_points:
            meeting_review_point = MeetingReviewPoint(**item)
            meeting_review_point.meeting = meeting
            meeting_review_point.save()

        meeting.save()
        return CreateMeeting(meeting=meeting)

class UpdateMeeting(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        meeting_data = MeetingInput(required=True)

    meeting = graphene.Field(MeetingType)

    def mutate(root, info, id, image=None, meeting_data=None):
        creator = info.context.user
        establishment_ids = meeting_data.pop("establishments")
        beneficiary_ids = meeting_data.pop("beneficiaries")
        participants_ids = meeting_data.pop("participants")
        absent_participants_ids = meeting_data.pop("absent_participants")
        reason_ids = meeting_data.pop("reasons") if 'reasons' in meeting_data else None
        meeting_type_ids = meeting_data.pop("meeting_types")
        meeting_decisions = meeting_data.pop("meeting_decisions")
        meeting_review_points = meeting_data.pop("meeting_review_points")
        Meeting.objects.filter(pk=id).update(**meeting_data)
        meeting = Meeting.objects.get(pk=id)
        if not meeting.folder or meeting.folder is None:
            folder = Folder.objects.create(name=str(meeting.id)+'_'+meeting.title,creator=creator)
            Meeting.objects.filter(pk=id).update(folder=folder)
        if not meeting.employee:
            meeting.employee = creator.getEmployeeInCompany()
            meeting.save()
        if absent_participants_ids and absent_participants_ids is not None:
            meeting.absent_participants.set(absent_participants_ids)
            
        if reason_ids and reason_ids is not None:
            reasons = MeetingReason.objects.filter(id__in=reason_ids)
            meeting.reasons.set(reasons)
            
        if meeting_type_ids and meeting_type_ids is not None:
            meeting_types = TypeMeeting.objects.filter(id__in=meeting_type_ids)
            meeting.meeting_types.set(meeting_types)

        MeetingEstablishment.objects.filter(meeting=meeting).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                meeting_establishment = MeetingEstablishment.objects.get(establishment__id=establishment.id, meeting__id=meeting.id)
            except MeetingEstablishment.DoesNotExist:
                MeetingEstablishment.objects.create(
                        meeting=meeting,
                        establishment=establishment,
                        creator=creator
                    )

        MeetingParticipant.objects.filter(meeting=meeting).exclude(employee__id__in=participants_ids).delete()
        employees = Employee.objects.filter(id__in=participants_ids)
        for employee in employees:
            try:
                meeting_participant = MeetingParticipant.objects.get(employee__id=employee.id, meeting__id=meeting.id)
            except MeetingParticipant.DoesNotExist:
                MeetingParticipant.objects.create(
                        meeting=meeting,
                        employee=employee,
                        creator=creator
                    )
        MeetingBeneficiary.objects.filter(meeting=meeting).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                meeting_beneficiaries = MeetingBeneficiary.objects.get(beneficiary__id=beneficiary.id, meeting__id=meeting.id)
            except MeetingBeneficiary.DoesNotExist:
                MeetingBeneficiary.objects.create(
                        meeting=meeting,
                        beneficiary=beneficiary,
                        creator=creator
                    )

        meeting_decision_ids = [item.id for item in meeting_decisions if item.id is not None]
        MeetingDecision.objects.filter(meeting=meeting).exclude(id__in=meeting_decision_ids).delete()
        for item in meeting_decisions:
            employees_ids = item.pop("employees") if "employees" in item else None
            for_voters_ids = item.pop("for_voters") if "for_voters" in item else None
            against_voters_ids = item.pop("against_voters") if "against_voters" in item else None
            if id in item or 'id' in item:
                MeetingDecision.objects.filter(pk=item.id).update(**item)
                meeting_decision = MeetingDecision.objects.get(pk=item.id)
            else:
                meeting_decision = MeetingDecision(**item)
                meeting_decision.meeting = meeting
                meeting_decision.save()
            if employees_ids and employees_ids is not None:
                meeting_decision.employees.set(employees_ids)
            if for_voters_ids and for_voters_ids is not None:
                meeting_decision.for_voters.set(for_voters_ids)
            if against_voters_ids and against_voters_ids is not None:
                meeting_decision.against_voters.set(against_voters_ids)

        meeting_review_point_ids = [item.id for item in meeting_review_points if item.id is not None]
        MeetingReviewPoint.objects.filter(meeting=meeting).exclude(id__in=meeting_review_point_ids).delete()
        for item in meeting_review_points:
            if id in item or 'id' in item:
                MeetingReviewPoint.objects.filter(pk=item.id).update(**item)
            else:
                meeting_review_point = MeetingReviewPoint(**item)
                meeting_review_point.meeting = meeting
                meeting_review_point.save()

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

#************************************************************************

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