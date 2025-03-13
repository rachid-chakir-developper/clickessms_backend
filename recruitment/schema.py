import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from recruitment.models import JobPosition, JobPosting, JobPostingPlatform, JobCandidate, JobCandidateApplication
from medias.models import Folder, File
from medias.schema import MediaInput

class JobPositionType(DjangoObjectType):
    class Meta:
        model = JobPosition
        fields = "__all__"

class JobPositionNodeType(graphene.ObjectType):
    nodes = graphene.List(JobPositionType)
    total_count = graphene.Int()


class JobPostingPlatformType(DjangoObjectType):
    class Meta:
        model = JobPostingPlatform
        fields = "__all__"

class JobPostingType(DjangoObjectType):
    class Meta:
        model = JobPosting
        fields = "__all__"

class JobPostingNodeType(graphene.ObjectType):
    nodes = graphene.List(JobPostingType)
    total_count = graphene.Int()

class JobCandidateType(DjangoObjectType):
    class Meta:
        model = JobCandidate
        fields = "__all__"

    cv = graphene.String()
    cover_letter = graphene.String()

    def resolve_cv(instance, info, **kwargs):
        return instance.cv and info.context.build_absolute_uri(
            instance.cv.file.url
        )

    def resolve_cover_letter(instance, info, **kwargs):
        return instance.cover_letter and info.context.build_absolute_uri(
            instance.cover_letter.file.url
        )

class JobCandidateNodeType(graphene.ObjectType):
    nodes = graphene.List(JobCandidateType)
    total_count = graphene.Int()

class JobCandidateApplicationType(DjangoObjectType):
    class Meta:
        model = JobCandidateApplication
        fields = "__all__"

    cv = graphene.String()
    cover_letter = graphene.String()

    def resolve_cv(instance, info, **kwargs):
        return instance.cv and info.context.build_absolute_uri(
            instance.cv.file.url
        )

    def resolve_cover_letter(instance, info, **kwargs):
        return instance.cover_letter and info.context.build_absolute_uri(
            instance.cover_letter.file.url
        )

class JobCandidateApplicationNodeType(graphene.ObjectType):
    nodes = graphene.List(JobCandidateApplicationType)
    total_count = graphene.Int()

class JobPositionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    order_by = graphene.String(required=False)

class JobPositionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    sector = graphene.String(required=True)
    contract_type = graphene.String(required=True)
    hiring_date = graphene.DateTime(required=False)
    duration = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class JobPostingFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    job_positions = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class JobPostingPlatformInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    post_link= graphene.String(required=False)
    job_platform_id = graphene.Int(name="jobPlatform", required=False)
    job_posting_id = graphene.Int(name="jobPosting", required=False)

class JobPostingInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    publication_date = graphene.DateTime()
    expiration_date = graphene.DateTime()
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    job_position_id = graphene.Int(name="jobPosition", required=False)
    job_platforms = graphene.List(JobPostingPlatformInput, required=False)

class JobCandidateFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    job_positions = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class JobCandidateInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    gender = graphene.String(required=False)
    preferred_name = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)
    job_title = graphene.String(required=True)
    availability_date = graphene.DateTime(required=False)
    job_platform_id = graphene.Int(name="jobPlatform", required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    rating = graphene.Int(required=False)
    is_active = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)

class JobCandidateApplicationFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    job_positions = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class JobCandidateApplicationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    gender = graphene.String(required=False)
    preferred_name = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)
    job_title = graphene.String(required=True)
    availability_date = graphene.DateTime(required=False)
    job_platform_id = graphene.Int(name="jobPlatform", required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    rating = graphene.Int(required=False)
    status = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    job_candidate_id = graphene.Int(name="jobCandidate", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    job_position_id = graphene.Int(name="jobPosition", required=False)

class JobCandidateApplicationFieldInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)

class JobCandidateApplicationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)
    job_title = graphene.String(required=True)
    availability_date = graphene.DateTime(required=False)
    job_platform_id = graphene.Int(name="jobPlatform", required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    rating = graphene.Int(required=False)
    status = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    job_candidate_id = graphene.Int(name="jobCandidate", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    job_position_id = graphene.Int(name="jobPosition", required=False)

class GenerateJobCandidateApplicationInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    phone = graphene.String(required=False)
    job_title = graphene.String(required=False)
    availability_date = graphene.DateTime(required=False)
    job_platform_id = graphene.Int(name="jobPlatform", required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    rating = graphene.Int(required=False)
    status = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    job_candidate_id = graphene.Int(name="jobCandidate", required=True)
    employee_id = graphene.Int(name="employee", required=False)
    job_positions = graphene.List(graphene.Int, required=True)

class RecruitmentQuery(graphene.ObjectType):
    job_positions = graphene.Field(JobPositionNodeType, job_position_filter= JobPositionFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    job_position = graphene.Field(JobPositionType, id = graphene.ID())
    job_postings = graphene.Field(JobPostingNodeType, job_posting_filter= JobPostingFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    job_posting = graphene.Field(JobPostingType, id = graphene.ID())
    job_candidates = graphene.Field(JobCandidateNodeType, job_candidate_filter= JobCandidateFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    job_candidate = graphene.Field(JobCandidateType, id = graphene.ID())
    job_candidate_applications = graphene.Field(JobCandidateApplicationNodeType, job_candidate_application_filter= JobCandidateApplicationFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    job_candidate_application = graphene.Field(JobCandidateApplicationType, id = graphene.ID())
    def resolve_job_positions(root, info, job_position_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        job_positions = JobPosition.objects.filter(company__id=id_company) if id_company else JobPosition.objects.filter(company=company)
        the_order_by = '-created_at'
        if job_position_filter:
            keyword = job_position_filter.get('keyword', '')
            starting_date_time = job_position_filter.get('starting_date_time')
            ending_date_time = job_position_filter.get('ending_date_time')
            order_by = job_position_filter.get('order_by')
            if keyword:
                job_positions = job_positions.filter(Q(title__icontains=keyword))
            if starting_date_time:
                job_positions = job_positions.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                job_positions = job_positions.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        job_positions = job_positions.order_by(the_order_by).distinct()
        total_count = job_positions.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            job_positions = job_positions[offset:offset + limit]
        return JobPositionNodeType(nodes=job_positions, total_count=total_count)

    def resolve_job_position(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            job_position = JobPosition.objects.get(pk=id)
        except JobPosition.DoesNotExist:
            job_position = None
        return job_position
    def resolve_job_postings(root, info, job_posting_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        job_postings = JobPosting.objects.filter(company__id=id_company) if id_company else JobPosting.objects.filter(company=company)
        the_order_by = '-created_at'
        if job_posting_filter:
            keyword = job_posting_filter.get('keyword', '')
            starting_date_time = job_posting_filter.get('starting_date_time')
            ending_date_time = job_posting_filter.get('ending_date_time')
            job_positions = job_posting_filter.get('job_positions')
            order_by = job_posting_filter.get('order_by')
            if keyword:
                job_postings = job_postings.filter(Q(title__icontains=keyword))
            if job_positions:
                job_postings = job_postings.filter(job_position__id__in=job_positions)
            if starting_date_time:
                job_postings = job_postings.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                job_postings = job_postings.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        job_postings = job_postings.order_by(the_order_by).distinct()
        total_count = job_postings.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            job_postings = job_postings[offset:offset + limit]
        return JobPostingNodeType(nodes=job_postings, total_count=total_count)

    def resolve_job_posting(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            job_posting = JobPosting.objects.get(pk=id)
        except JobPosting.DoesNotExist:
            job_posting = None
        return job_posting
    def resolve_job_candidates(root, info, job_candidate_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        job_candidates = JobCandidate.objects.filter(company__id=id_company) if id_company else JobCandidate.objects.filter(company=company)
        the_order_by = '-created_at'
        if job_candidate_filter:
            keyword = job_candidate_filter.get('keyword', '')
            starting_date_time = job_candidate_filter.get('starting_date_time')
            ending_date_time = job_candidate_filter.get('ending_date_time')
            job_positions = job_candidate_filter.get('job_positions')
            order_by = job_candidate_filter.get('order_by')
            if keyword:
                job_candidates = job_candidates.filter(
                    Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | 
                    Q(preferred_name__icontains=keyword) | Q(email__icontains=keyword) | 
                    Q(phone__icontains=keyword) | Q(job_title__icontains=keyword)
                )
            if job_positions:
                job_candidates = job_candidates.filter(job_candidate_applications__job_position__id__in=job_positions)
            if starting_date_time:
                job_candidates = job_candidates.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                job_candidates = job_candidates.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        job_candidates = job_candidates.order_by(the_order_by).distinct()
        total_count = job_candidates.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            job_candidates = job_candidates[offset:offset + limit]
        return JobCandidateNodeType(nodes=job_candidates, total_count=total_count)

    def resolve_job_candidate(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            job_candidate = JobCandidate.objects.get(pk=id)
        except JobCandidate.DoesNotExist:
            job_candidate = None
        return job_candidate
    def resolve_job_candidate_applications(root, info, job_candidate_application_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        job_candidate_applications = JobCandidateApplication.objects.filter(company__id=id_company) if id_company else JobCandidateApplication.objects.filter(company=company)
        the_order_by = '-created_at'
        if job_candidate_application_filter:
            keyword = job_candidate_application_filter.get('keyword', '')
            starting_date_time = job_candidate_application_filter.get('starting_date_time')
            ending_date_time = job_candidate_application_filter.get('ending_date_time')
            job_positions = job_candidate_application_filter.get('job_positions')
            order_by = job_candidate_application_filter.get('order_by')
            if keyword:
                job_candidate_applications = job_candidate_applications.filter(
                    Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | 
                    Q(preferred_name__icontains=keyword) | Q(email__icontains=keyword) | 
                    Q(phone__icontains=keyword) | Q(job_title__icontains=keyword)
                )
            if job_positions:
                job_candidate_applications = job_candidate_applications.filter(job_position__id__in=job_positions)
            if starting_date_time:
                job_candidate_applications = job_candidate_applications.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                job_candidate_applications = job_candidate_applications.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        job_candidate_applications = job_candidate_applications.order_by(the_order_by).distinct()
        total_count = job_candidate_applications.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            job_candidate_applications = job_candidate_applications[offset:offset + limit]
        return JobCandidateApplicationNodeType(nodes=job_candidate_applications, total_count=total_count)

    def resolve_job_candidate_application(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            job_candidate_application = JobCandidateApplication.objects.get(pk=id)
        except JobCandidateApplication.DoesNotExist:
            job_candidate_application = None
        return job_candidate_application

#***************************************************************************

class CreateJobPosition(graphene.Mutation):
    class Arguments:
        job_position_data = JobPositionInput(required=True)

    job_position = graphene.Field(JobPositionType)

    def mutate(root, info, job_position_data=None):
        creator = info.context.user
        job_position = JobPosition(**job_position_data)
        job_position.creator = creator
        job_position.company = creator.the_current_company
        folder = Folder.objects.create(name=str(job_position.id)+'_'+job_position.title,creator=creator)
        job_position.folder = folder
        job_position.save()
        if not job_position.employee:
            job_position.employee = creator.get_employee_in_company()
        job_position.save()
        return CreateJobPosition(job_position=job_position)

class UpdateJobPosition(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_position_data = JobPositionInput(required=True)

    job_position = graphene.Field(JobPositionType)

    def mutate(root, info, id, job_position_data=None):
        creator = info.context.user
        JobPosition.objects.filter(pk=id).update(**job_position_data)
        job_position = JobPosition.objects.get(pk=id)
        if not job_position.folder or job_position.folder is None:
            folder = Folder.objects.create(name=str(job_position.id)+'_'+job_position.title,creator=creator)
            JobPosition.objects.filter(pk=id).update(folder=folder)
        if not job_position.employee:
            job_position.employee = creator.get_employee_in_company()
            job_position.save()
        return UpdateJobPosition(job_position=job_position)

class DeleteJobPosition(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    job_position = graphene.Field(JobPositionType)
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
            job_position = JobPosition.objects.get(pk=id)
            job_position.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteJobPosition(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#***************************************************************************

class CreateJobPosting(graphene.Mutation):
    class Arguments:
        job_posting_data = JobPostingInput(required=True)

    job_posting = graphene.Field(JobPostingType)

    def mutate(root, info, job_posting_data=None):
        creator = info.context.user
        job_platforms = job_posting_data.pop("job_platforms", None)
        job_posting = JobPosting(**job_posting_data)
        job_posting.creator = creator
        job_posting.company = creator.the_current_company
        folder = Folder.objects.create(name=str(job_posting.id)+'_'+job_posting.title,creator=creator)
        job_posting.folder = folder
        job_posting.save()
        if not job_posting.employee:
            job_posting.employee = creator.get_employee_in_company()
        for item in job_platforms:
            job_platform = JobPostingPlatform(**item)
            job_platform.creator = creator
            job_platform.job_posting = job_posting
            job_platform.save()
        job_posting.save()
        return CreateJobPosting(job_posting=job_posting)

class UpdateJobPosting(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_posting_data = JobPostingInput(required=True)

    job_posting = graphene.Field(JobPostingType)

    def mutate(root, info, id, job_posting_data=None):
        creator = info.context.user
        job_platforms = job_posting_data.pop("job_platforms", None)
        JobPosting.objects.filter(pk=id).update(**job_posting_data)
        job_posting = JobPosting.objects.get(pk=id)
        if not job_posting.folder or job_posting.folder is None:
            folder = Folder.objects.create(name=str(job_posting.id)+'_'+job_posting.title,creator=creator)
            JobPosting.objects.filter(pk=id).update(folder=folder)
        if not job_posting.employee:
            job_posting.employee = creator.get_employee_in_company()
            job_posting.save()
        job_platform_ids = [item.id for item in job_platforms if item.id is not None]
        JobPostingPlatform.objects.filter(job_posting=job_posting).exclude(id__in=job_platform_ids).delete()
        for item in job_platforms:
            if id in item or 'id' in item:
                JobPostingPlatform.objects.filter(pk=item.id).update(**item)
                job_platform = JobPostingPlatform.objects.get(pk=item.id)
            else:
                job_platform = JobPostingPlatform(**item)
                job_platform.creator = creator
                job_platform.job_posting = job_posting
                job_platform.save()
        return UpdateJobPosting(job_posting=job_posting)

class DeleteJobPosting(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    job_posting = graphene.Field(JobPostingType)
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
            job_posting = JobPosting.objects.get(pk=id)
            job_posting.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteJobPosting(deleted=deleted, success=success, message=message, id=id)

#************************************************************************
#***************************************************************************

#***************************************************************************

class CreateJobCandidate(graphene.Mutation):
    class Arguments:
        job_candidate_data = JobCandidateInput(required=True)
        cv = Upload(required=False)
        cover_letter = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    job_candidate = graphene.Field(JobCandidateType)

    def mutate(root, info, cv=None, cover_letter=None, files=None, job_candidate_data=None):
        creator = info.context.user
        job_candidate = JobCandidate(**job_candidate_data)
        job_candidate.creator = creator
        job_candidate.company = creator.the_current_company
        folder = Folder.objects.create(name=str(job_candidate.id)+'_'+job_candidate.first_name,creator=creator)
        job_candidate.folder = folder
        job_candidate.save()
        if not job_candidate.employee:
            job_candidate.employee = creator.get_employee_in_company()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if cv and isinstance(cv, UploadedFile):
                cv_file = job_candidate.cv
                if not cv_file:
                    cv_file = File()
                    cv_file.creator = creator
                    cv_file.folder = job_candidate.folder
                cv_file.file = cv
                cv_file.save()
                job_candidate.cv = cv_file
            # file1 = info.context.FILES['1']
            if cover_letter and isinstance(cover_letter, UploadedFile):
                cover_letter_file = job_candidate.cover_letter
                if not cover_letter_file:
                    cover_letter_file = File()
                    cover_letter_file.creator = creator
                    cover_letter_file.folder = job_candidate.folder
                cover_letter_file.file = cover_letter
                cover_letter_file.save()
                job_candidate.cover_letter = cover_letter_file
        if not files:
            files = []
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = job_candidate.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            job_candidate.files.add(file_file)
        job_candidate.save()
        return CreateJobCandidate(job_candidate=job_candidate)

class UpdateJobCandidate(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_candidate_data = JobCandidateInput(required=True)
        cv = Upload(required=False)
        cover_letter = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    job_candidate = graphene.Field(JobCandidateType)

    def mutate(root, info, id, cv=None, cover_letter=None, files=None, job_candidate_data=None):
        creator = info.context.user
        JobCandidate.objects.filter(pk=id).update(**job_candidate_data)
        job_candidate = JobCandidate.objects.get(pk=id)
        if not job_candidate.folder or job_candidate.folder is None:
            folder = Folder.objects.create(name=str(job_candidate.id)+'_'+job_candidate.first_name,creator=creator)
            UpdateJob.objects.filter(pk=id).update(folder=folder)
        if not job_candidate.employee:
            job_candidate.employee = creator.get_employee_in_company()
            job_candidate.save()
        if not cv and job_candidate.cv:
            cv_file = job_candidate.cv
            cv_file.delete()
        if not cover_letter and job_candidate.cover_letter:
            cover_letter_file = job_candidate.cover_letter
            cover_letter_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if cv and isinstance(cv, UploadedFile):
                cv_file = job_candidate.cv
                if not cv_file:
                    cv_file = File()
                    cv_file.creator = creator
                    cv_file.folder = job_candidate.folder
                cv_file.file = cv
                cv_file.save()
                job_candidate.cv = cv_file
            # file1 = info.context.FILES['1']
            if cover_letter and isinstance(cover_letter, UploadedFile):
                cover_letter_file = job_candidate.cover_letter
                if not cover_letter_file:
                    cover_letter_file = File()
                    cover_letter_file.creator = creator
                    cover_letter_file.folder = job_candidate.folder
                cover_letter_file.file = cover_letter
                cover_letter_file.save()
                job_candidate.cover_letter = cover_letter_file
        if not files:
            files = []
        else:
            file_ids = [item.id for item in files if item.id is not None]
            File.objects.filter(file_job_candidates=job_candidate).exclude(id__in=file_ids).delete()
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = job_candidate.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            job_candidate.files.add(file_file)
        job_candidate.save()
        return UpdateJobCandidate(job_candidate=job_candidate)

class DeleteJobCandidate(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    job_candidate = graphene.Field(JobCandidateType)
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
            job_candidate = JobCandidate.objects.get(pk=id)
            job_candidate.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteJobCandidate(deleted=deleted, success=success, message=message, id=id)
        
#*******************************************************************************************************************************

#***************************************************************************

class CreateJobCandidateApplication(graphene.Mutation):
    class Arguments:
        job_candidate_application_data = JobCandidateApplicationInput(required=True)
        cv = Upload(required=False)
        cover_letter = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    job_candidate_application = graphene.Field(JobCandidateApplicationType)

    def mutate(root, info, cv=None, cover_letter=None, files=None, job_candidate_application_data=None):
        creator = info.context.user
        job_candidate_application = JobCandidateApplication(**job_candidate_application_data)
        job_candidate_application.creator = creator
        job_candidate_application.company = creator.the_current_company
        folder = Folder.objects.create(name=str(job_candidate_application.id)+'_'+job_candidate_application.first_name,creator=creator)
        job_candidate_application.folder = folder
        job_candidate_application.save()
        if not job_candidate_application.employee:
            job_candidate_application.employee = creator.get_employee_in_company()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if cv and isinstance(cv, UploadedFile):
                cv_file = job_candidate_application.cv
                if not cv_file:
                    cv_file = File()
                    cv_file.creator = creator
                    cv_file.folder = job_candidate_application.folder
                cv_file.file = cv
                cv_file.save()
                job_candidate_application.cv = cv_file
            # file1 = info.context.FILES['1']
            if cover_letter and isinstance(cover_letter, UploadedFile):
                cover_letter_file = job_candidate_application.cover_letter
                if not cover_letter_file:
                    cover_letter_file = File()
                    cover_letter_file.creator = creator
                    cover_letter_file.folder = job_candidate_application.folder
                cover_letter_file.file = cover_letter
                cover_letter_file.save()
                job_candidate_application.cover_letter = cover_letter_file
        job_candidate_application.save()
        return CreateJobCandidateApplication(job_candidate_application=job_candidate_application)

class UpdateJobCandidateApplication(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_candidate_application_data = JobCandidateApplicationInput(required=True)
        cv = Upload(required=False)
        cover_letter = Upload(required=False)
        files = graphene.List(MediaInput, required=False)

    job_candidate_application = graphene.Field(JobCandidateApplicationType)

    def mutate(root, info, id, cv=None, cover_letter=None, files=None, job_candidate_application_data=None):
        creator = info.context.user
        JobCandidateApplication.objects.filter(pk=id).update(**job_candidate_application_data)
        job_candidate_application = JobCandidateApplication.objects.get(pk=id)
        if not job_candidate_application.folder or job_candidate_application.folder is None:
            folder = Folder.objects.create(name=str(job_candidate_application.id)+'_'+job_candidate_application.first_name,creator=creator)
            UpdateJob.objects.filter(pk=id).update(folder=folder)
        if not job_candidate_application.employee:
            job_candidate_application.employee = creator.get_employee_in_company()
            job_candidate_application.save()
        if not cv and job_candidate_application.cv:
            cv_file = job_candidate_application.cv
            cv_file.delete()
        if not cover_letter and job_candidate_application.cover_letter:
            cover_letter_file = job_candidate_application.cover_letter
            cover_letter_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if cv and isinstance(cv, UploadedFile):
                cv_file = job_candidate_application.cv
                if not cv_file:
                    cv_file = File()
                    cv_file.creator = creator
                    cv_file.folder = job_candidate_application.folder
                cv_file.file = cv
                cv_file.save()
                job_candidate_application.cv = cv_file
            # file1 = info.context.FILES['1']
            if cover_letter and isinstance(cover_letter, UploadedFile):
                cover_letter_file = job_candidate_application.cover_letter
                if not cover_letter_file:
                    cover_letter_file = File()
                    cover_letter_file.creator = creator
                    cover_letter_file.folder = job_candidate_application.folder
                cover_letter_file.file = cover_letter
                cover_letter_file.save()
                job_candidate_application.cover_letter = cover_letter_file
        job_candidate_application.save()
        return UpdateJobCandidateApplication(job_candidate_application=job_candidate_application)

class UpdateJobCandidateApplicationFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_candidate_application_data = JobCandidateApplicationFieldInput(required=True)

    job_candidate_application = graphene.Field(JobCandidateApplicationType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, job_candidate_application_data=None):
        creator = info.context.user
        done = True
        success = True
        job_candidate_application = None
        message = ''
        try:
            job_candidate_application = JobCandidateApplication.objects.get(pk=id)
            JobCandidateApplication.objects.filter(pk=id).update(**job_candidate_application_data)
            job_candidate_application.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            job_candidate_application=None
            message = "Une erreur s'est produite."
        return UpdateJobCandidateApplicationFields(done=done, success=success, message=message, job_candidate_application=job_candidate_application)

class GenerateJobCandidateApplication(graphene.Mutation):
    class Arguments:
        generate_job_candidate_application_data = GenerateJobCandidateApplicationInput(required=True)

    job_candidate_applications = graphene.List(JobCandidateApplicationType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, generate_job_candidate_application_data=None):
        creator = info.context.user
        company = creator.the_current_company
        job_candidate_id = generate_job_candidate_application_data.pop("job_candidate_id", None)
        job_position_ids = generate_job_candidate_application_data.pop("job_positions", None)
        job_candidate_applications = []
        try:
            # Vérifier si le candidat existe
            try:
                job_candidate = JobCandidate.objects.get(id=job_candidate_id, is_deleted=False)
            except JobCandidate.DoesNotExist:
                return GenerateJobCandidateApplication(job_candidate_applications=job_candidate_applications, success=False, message="Candidat non trouvé.")

            # Vérifier si les postes existent
            job_positions = JobPosition.objects.filter(id__in=job_position_ids)
            if not job_positions.exists():
                return GenerateJobCandidateApplication(job_candidate_applications=job_candidate_applications, success=False, message="Fiche(s) non trouvée(s).")

            # Vérifier et mettre à jour les candidatures existantes
            existing_applications = JobCandidateApplication.objects.filter(
                job_candidate=job_candidate, 
                job_position__in=job_positions
            )

            # Mise à jour des candidatures existantes
            if existing_applications.exists():
                existing_applications.update(**generate_job_candidate_application_data)

            # Créer les nouvelles candidatures
            existing_positions = set(existing_applications.values_list("job_position_id", flat=True))

            new_applications = [
                JobCandidateApplication(
                    gender=job_candidate.gender,
                    preferred_name=job_candidate.preferred_name,
                    first_name=job_candidate.first_name,
                    last_name=job_candidate.last_name,
                    email=job_candidate.email,
                    phone=job_candidate.phone,
                    job_title=job_candidate.job_title,
                    availability_date=job_candidate.availability_date,
                    job_candidate=job_candidate,
                    job_platform=job_candidate.job_platform,
                    cv=job_candidate.cv,
                    cover_letter=job_candidate.cover_letter,
                    description=job_candidate.description,
                    observation=job_candidate.observation,
                    rating=job_candidate.rating,
                    job_position=job_position,
                    employee=job_candidate.employee,
                    company=job_candidate.company,
                    creator=creator,
                )
                for job_position in job_positions if job_position.id not in existing_positions
            ]

            if new_applications:
                JobCandidateApplication.objects.bulk_create(new_applications)

            # Combiner les candidatures existantes et les nouvelles
            job_candidate_applications = JobCandidateApplication.objects.filter(
                job_candidate=job_candidate, 
                job_position__in=job_positions
            )

            return GenerateJobCandidateApplication(
                job_candidate_applications=job_candidate_applications,
                success=True,
                message="Candidature(s) générée(s) avec succès."
            )

        except Exception as e:
            return GenerateJobCandidateApplication(job_candidate_applications=job_candidate_applications, success=False, message=f"Une erreur s'est produite : {str(e)}")

class DeleteJobCandidateApplication(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    job_candidate_application = graphene.Field(JobCandidateApplicationType)
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
            job_candidate_application = JobCandidateApplication.objects.get(pk=id)
            job_candidate_application.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteJobCandidateApplication(deleted=deleted, success=success, message=message, id=id)
        
#*******************************************************************************************************************************
class RecruitmentMutation(graphene.ObjectType):
    create_job_position = CreateJobPosition.Field()
    update_job_position = UpdateJobPosition.Field()
    delete_job_position = DeleteJobPosition.Field()

    create_job_posting = CreateJobPosting.Field()
    update_job_posting = UpdateJobPosting.Field()
    delete_job_posting = DeleteJobPosting.Field()

    create_job_candidate = CreateJobCandidate.Field()
    update_job_candidate = UpdateJobCandidate.Field()
    delete_job_candidate = DeleteJobCandidate.Field()

    create_job_candidate_application = CreateJobCandidateApplication.Field()
    update_job_candidate_application = UpdateJobCandidateApplication.Field()
    update_job_candidate_application_fields = UpdateJobCandidateApplicationFields.Field()
    generate_job_candidate_application = GenerateJobCandidateApplication.Field()
    delete_job_candidate_application = DeleteJobCandidateApplication.Field()
    