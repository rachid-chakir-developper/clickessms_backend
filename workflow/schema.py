import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required

from django.db.models import Q

from workflow.models import ValidationWorkflow, ValidationStep, ValidationRule, FallbackRule

class ValidationStepType(DjangoObjectType):
    class Meta:
        model = ValidationStep
        fields = "__all__"

class ValidationRuleType(DjangoObjectType):
    class Meta:
        model = ValidationRule
        fields = "__all__"


class FallbackRuleType(DjangoObjectType):
    class Meta:
        model = FallbackRule
        fields = "__all__"

class ValidationWorkflowType(DjangoObjectType):
    class Meta:
        model = ValidationWorkflow
        fields = "__all__"

class ValidationWorkflowNodeType(graphene.ObjectType):
    nodes = graphene.List(ValidationWorkflowType)
    total_count = graphene.Int()

class ValidationWorkflowFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class ValidationWorkflowInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    request_type = graphene.String(required=True)
    description = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)

class WorkflowQuery(graphene.ObjectType):
    validation_workflows = graphene.Field(ValidationWorkflowNodeType, validation_workflow_filter= ValidationWorkflowFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    validation_workflow = graphene.Field(ValidationWorkflowType, id = graphene.ID())
    def resolve_validation_workflows(root, info, validation_workflow_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        validation_workflows = ValidationWorkflow.objects.filter(company=company, is_deleted=False)
        if validation_workflow_filter:
            keyword = validation_workflow_filter.get('keyword', '')
            starting_date_time = validation_workflow_filter.get('starting_date_time')
            ending_date_time = validation_workflow_filter.get('ending_date_time')
            if keyword:
                validation_workflows = validation_workflows.filter(Q(request_type__icontains=keyword))
            if starting_date_time:
                validation_workflows = validation_workflows.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                validation_workflows = validation_workflows.filter(created_at__lte=ending_date_time)
        validation_workflows = validation_workflows.order_by('-created_at')
        total_count = validation_workflows.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            validation_workflows = validation_workflows[offset:offset + limit]
        return ValidationWorkflowNodeType(nodes=validation_workflows, total_count=total_count)

    def resolve_validation_workflow(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            validation_workflow = ValidationWorkflow.objects.get(pk=id, company=company)
        except ValidationWorkflow.DoesNotExist:
            validation_workflow = None
        return validation_workflow

#***************************************************************************

class CreateValidationWorkflow(graphene.Mutation):
    class Arguments:
        validation_workflow_data = ValidationWorkflowInput(required=True)

    validation_workflow = graphene.Field(ValidationWorkflowType) 

    def mutate(root, info, validation_workflow_data=None):
        creator = info.context.user
        if not creator.is_admin() and not creator.is_superuser:
            raise ValueError("Vous n'avez pas les droits nécessairespour effectuer cette action.")
        validation_workflow = ValidationWorkflow(**validation_workflow_data)
        validation_workflow.creator = creator
        validation_workflow.company = creator.the_current_company
        validation_workflow.save()
        return CreateValidationWorkflow(validation_workflow=validation_workflow)

class UpdateValidationWorkflow(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        validation_workflow_data = ValidationWorkflowInput(required=True)

    validation_workflow = graphene.Field(ValidationWorkflowType)

    def mutate(root, info, id, validation_workflow_data=None):
        creator = info.context.user
        try:
            validation_workflow = ValidationWorkflow.objects.get(pk=id, company=creator.the_current_company)
        except ValidationWorkflow.DoesNotExist as e:
            raise e
        if not creator.is_admin() and not creator.is_superuser:
            raise ValueError("Vous n'avez pas les droits nécessairespour effectuer cette action.")
        ValidationWorkflow.objects.filter(pk=id).update(**validation_workflow_data)
        validation_workflow.refresh_from_db()
        return UpdateValidationWorkflow(validation_workflow=validation_workflow)

class DeleteValidationWorkflow(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    validation_workflow = graphene.Field(ValidationWorkflowType)
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
            validation_workflow = ValidationWorkflow.objects.get(pk=id, company=current_user.the_current_company)
        except ValidationWorkflow.DoesNotExist:
            raise e
        if current_user.is_superuser or current_user.is_admin() or (validation_workflow.creator == current_user):
            # validation_workflow = ValidationWorkflow.objects.get(pk=id)
            # validation_workflow.delete()
            ValidationWorkflow.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteValidationWorkflow(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class WorkflowMutation(graphene.ObjectType):
    create_validation_workflow = CreateValidationWorkflow.Field()
    update_validation_workflow = UpdateValidationWorkflow.Field()
    delete_validation_workflow = DeleteValidationWorkflow.Field()
    