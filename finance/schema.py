import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from finance.models import DecisionDocument, DecisionDocumentItem
from medias.models import Folder, File

class DecisionDocumentItemType(DjangoObjectType):
    class Meta:
        model = DecisionDocumentItem
        fields = "__all__"

class DecisionDocumentType(DjangoObjectType):
    class Meta:
        model = DecisionDocument
        fields = "__all__"
    document = graphene.String()
    decision_document_items = graphene.List(DecisionDocumentItemType)
    def resolve_document( instance, info, **kwargs ):
        return instance.document and info.context.build_absolute_uri(instance.document.file.url)
    def resolve_decision_document_items( instance, info, **kwargs ):
        return instance.decisiondocumentitem_set.all()

class DecisionDocumentNodeType(graphene.ObjectType):
    nodes = graphene.List(DecisionDocumentType)
    total_count = graphene.Int()

class DecisionDocumentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class DecisionDocumentItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    price = graphene.Float(required=False)
    endowment = graphene.Float(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class DecisionDocumentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    decision_date = graphene.DateTime(required=False)
    reception_date_time = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    decision_document_items = graphene.List(DecisionDocumentItemInput, required=False)

class FinanceQuery(graphene.ObjectType):
    decision_documents = graphene.Field(DecisionDocumentNodeType, decision_document_filter= DecisionDocumentFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    decision_document = graphene.Field(DecisionDocumentType, id = graphene.ID())
    def resolve_decision_documents(root, info, decision_document_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        decision_documents = DecisionDocument.objects.all()
        if decision_document_filter:
            keyword = decision_document_filter.get('keyword', '')
            starting_date_time = decision_document_filter.get('starting_date_time')
            ending_date_time = decision_document_filter.get('ending_date_time')
            if keyword:
                decision_documents = decision_documents.filter(Q(name__icontains=keyword) | Q(establishment__name__icontains=keyword))
            if starting_date_time:
                decision_documents = decision_documents.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                decision_documents = decision_documents.filter(created_at__lte=ending_date_time)
        decision_documents = decision_documents.order_by('-created_at')
        total_count = decision_documents.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            decision_documents = decision_documents[offset:offset + limit]
        return DecisionDocumentNodeType(nodes=decision_documents, total_count=total_count)

    def resolve_decision_document(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            decision_document = DecisionDocument.objects.get(pk=id)
        except DecisionDocument.DoesNotExist:
            decision_document = None
        return decision_document

#************************************************************************

class CreateDecisionDocument(graphene.Mutation):
    class Arguments:
        decision_document_data = DecisionDocumentInput(required=True)
        document = Upload(required=False)

    decision_document = graphene.Field(DecisionDocumentType)

    def mutate(root, info, document=None, decision_document_data=None):
        creator = info.context.user
        decision_document_items = task_data.pop("decision_document_items")
        decision_document = DecisionDocument(**decision_document_data)
        decision_document.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = decision_document.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                decision_document.document = document_file
        decision_document.save()
        folder = Folder.objects.create(name=str(decision_document.id)+'_'+decision_document.name,creator=creator)
        decision_document.folder = folder
        decision_document.save()
        for item in decision_document_items:
            decision_document_item = DecisionDocumentItem(**item)
            decision_document_item.decision_document = decision_document
            decision_document_item.save()
        return CreateDecisionDocument(decision_document=decision_document)

class UpdateDecisionDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        decision_document_data = DecisionDocumentInput(required=True)
        document = Upload(required=False)

    decision_document = graphene.Field(DecisionDocumentType)

    def mutate(root, info, id, document=None, decision_document_data=None):
        creator = info.context.user
        decision_document_items = task_data.pop("decision_document_items")
        DecisionDocument.objects.filter(pk=id).update(**decision_document_data)
        decision_document = DecisionDocument.objects.get(pk=id)
        if not decision_document.folder or decision_document.folder is None:
            folder = Folder.objects.create(name=str(decision_document.id)+'_'+decision_document.name,creator=creator)
            DecisionDocument.objects.filter(pk=id).update(folder=folder)
        if not document and decision_document.document:
            document_file = decision_document.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = decision_document.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                decision_document.document = document_file
            decision_document.save()

        decision_document_item_ids = [item.id for item in decision_document_items if item.id is not None]
        DecisionDocumentItem.objects.filter(decision_document=decision_document).exclude(id__in=decision_document_item_ids).delete()
        for item in decision_document_items:
            if id in item or 'id' in item:
                DecisionDocumentItem.objects.filter(pk=item.id).update(**item)
            else:
                decision_document_item = DecisionDocumentItem(**item)
                decision_document_item.decision_document = decision_document
                decision_document_item.save()
        return UpdateDecisionDocument(decision_document=decision_document)

class UpdateDecisionDocumentState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    decision_document = graphene.Field(DecisionDocumentType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, decision_document_fields=None):
        creator = info.context.user
        done = True
        success = True
        decision_document = None
        message = ''
        try:
            decision_document = DecisionDocument.objects.get(pk=id)
            DecisionDocument.objects.filter(pk=id).update(is_active=not decision_document.is_active)
            decision_document.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            decision_document=None
            message = "Une erreur s'est produite."
        return UpdateDecisionDocumentState(done=done, success=success, message=message,decision_document=decision_document)


class DeleteDecisionDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    decision_document = graphene.Field(DecisionDocumentType)
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
            decision_document = DecisionDocument.objects.get(pk=id)
            decision_document.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteDecisionDocument(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
class FinanceMutation(graphene.ObjectType):
    create_decision_document = CreateDecisionDocument.Field()
    update_decision_document = UpdateDecisionDocument.Field()
    update_decision_document_state = UpdateDecisionDocumentState.Field()
    delete_decision_document = DeleteDecisionDocument.Field()