import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from decimal import Decimal

from django.db.models import Q

from finance.models import DecisionDocument, DecisionDocumentItem, BankAccount, Balance
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

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )


class DecisionDocumentNodeType(graphene.ObjectType):
    nodes = graphene.List(DecisionDocumentType)
    total_count = graphene.Int()


class DecisionDocumentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class BankAccountType(DjangoObjectType):
    class Meta:
        model = BankAccount
        fields = "__all__"

    image = graphene.String()
    balance = graphene.Decimal()

    def resolve_image(instance, info, **kwargs):
        return instance.image and info.context.build_absolute_uri(
            instance.image.image.url
        )

    def resolve_balance(instance, info, **kwargs):
        return instance.current_balance


class BankAccountNodeType(graphene.ObjectType):
    nodes = graphene.List(BankAccountType)
    total_count = graphene.Int()


class BankAccountFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class BalanceType(DjangoObjectType):
    class Meta:
        model = Balance
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )


class BalanceNodeType(graphene.ObjectType):
    nodes = graphene.List(BalanceType)
    total_count = graphene.Int()


class BalanceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)


class DecisionDocumentItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    price = graphene.Decimal(required=False)
    endowment = graphene.Decimal(required=False)
    occupancy_rate = graphene.Float(required=False)
    theoretical_number_unit_work = graphene.Float(required=False)
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
    financier_id = graphene.Int(name="financier", required=False)
    decision_document_items = graphene.List(DecisionDocumentItemInput, required=False)


class BankAccountInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    account_number = graphene.String(required=False)
    account_type = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    opening_date = graphene.DateTime(required=False)
    closing_date = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)


class BalanceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    date = graphene.DateTime(required=False)
    amount = graphene.Decimal(required=False)
    bank_account_id = graphene.Int(name="bankAccount", required=False)


class FinanceQuery(graphene.ObjectType):
    decision_documents = graphene.Field(
        DecisionDocumentNodeType,
        decision_document_filter=DecisionDocumentFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    decision_document = graphene.Field(DecisionDocumentType, id=graphene.ID())
    bank_accounts = graphene.Field(
        BankAccountNodeType,
        bank_account_filter=BankAccountFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    bank_account = graphene.Field(BankAccountType, id=graphene.ID())
    balances = graphene.Field(
        BalanceNodeType,
        balance_filter=BalanceFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    balance = graphene.Field(BalanceType, id=graphene.ID())

    def resolve_decision_documents(
        root, info, decision_document_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = (
            user.current_company if user.current_company is not None else user.company
        )
        total_count = 0
        decision_documents = DecisionDocument.objects.filter(company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                decision_documents = decision_documents.filter(Q(decision_document_items__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                decision_documents = decision_documents.filter(creator=user)
        if decision_document_filter:
            keyword = decision_document_filter.get("keyword", "")
            starting_date_time = decision_document_filter.get("starting_date_time")
            ending_date_time = decision_document_filter.get("ending_date_time")
            if keyword:
                decision_documents = decision_documents.filter(
                    Q(name__icontains=keyword)
                    | Q(establishment__name__icontains=keyword)
                )
            if starting_date_time:
                decision_documents = decision_documents.filter(
                    created_at__gte=starting_date_time
                )
            if ending_date_time:
                decision_documents = decision_documents.filter(
                    created_at__lte=ending_date_time
                )
        decision_documents = decision_documents.order_by("-created_at")
        total_count = decision_documents.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            decision_documents = decision_documents[offset : offset + limit]
        return DecisionDocumentNodeType(
            nodes=decision_documents, total_count=total_count
        )

    def resolve_decision_document(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            decision_document = DecisionDocument.objects.get(pk=id)
        except DecisionDocument.DoesNotExist:
            decision_document = None
        return decision_document

    def resolve_bank_accounts(
        root, info, bank_account_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = (
            user.current_company if user.current_company is not None else user.company
        )
        total_count = 0
        bank_accounts = BankAccount.objects.filter(company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                bank_accounts = bank_accounts.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                bank_accounts = bank_accounts.filter(creator=user)
        if bank_account_filter:
            keyword = bank_account_filter.get("keyword", "")
            starting_date_time = bank_account_filter.get("starting_date_time")
            ending_date_time = bank_account_filter.get("ending_date_time")
            if keyword:
                bank_accounts = bank_accounts.filter(
                    Q(name__icontains=keyword)
                    | Q(registration_number__icontains=keyword)
                    | Q(driver_name__icontains=keyword)
                )
            if starting_date_time:
                bank_accounts = bank_accounts.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                bank_accounts = bank_accounts.filter(created_at__lte=ending_date_time)
        bank_accounts = bank_accounts.order_by("-created_at")
        total_count = bank_accounts.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            bank_accounts = bank_accounts[offset : offset + limit]
        return BankAccountNodeType(nodes=bank_accounts, total_count=total_count)

    def resolve_bank_account(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            bank_account = BankAccount.objects.get(pk=id)
        except BankAccount.DoesNotExist:
            bank_account = None
        return bank_account

    def resolve_balances(
        root, info, balance_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = (
            user.current_company if user.current_company is not None else user.company
        )
        total_count = 0
        balances = Balance.objects.filter(bank_account__company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                balances = balances.filter(Q(bank_account__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                balances = balances.filter(creator=user)
        if balance_filter:
            keyword = balance_filter.get("keyword", "")
            starting_date_time = balance_filter.get("starting_date_time")
            ending_date_time = balance_filter.get("ending_date_time")
            if keyword:
                balances = balances.filter(
                    Q(name__icontains=keyword)
                    | Q(registration_number__icontains=keyword)
                    | Q(driver_name__icontains=keyword)
                )
            if starting_date_time:
                balances = balances.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                balances = balances.filter(created_at__lte=ending_date_time)
        balances = balances.order_by("-created_at")
        total_count = balances.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            balances = balances[offset : offset + limit]
        return BalanceNodeType(nodes=balances, total_count=total_count)

    def resolve_balance(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            balance = Balance.objects.get(pk=id)
        except Balance.DoesNotExist:
            balance = None
        return balance


# ************************************************************************


class CreateDecisionDocument(graphene.Mutation):
    class Arguments:
        decision_document_data = DecisionDocumentInput(required=True)
        document = Upload(required=False)

    decision_document = graphene.Field(DecisionDocumentType)

    def mutate(root, info, document=None, decision_document_data=None):
        creator = info.context.user
        decision_document_items = decision_document_data.pop("decision_document_items")
        decision_document = DecisionDocument(**decision_document_data)
        decision_document.creator = creator
        decision_document.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
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
        folder = Folder.objects.create(
            name=str(decision_document.id) + "_" + decision_document.name,
            creator=creator,
        )
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
        decision_document_items = decision_document_data.pop("decision_document_items")
        DecisionDocument.objects.filter(pk=id).update(**decision_document_data)
        decision_document = DecisionDocument.objects.get(pk=id)
        if not decision_document.folder or decision_document.folder is None:
            folder = Folder.objects.create(
                name=str(decision_document.id) + "_" + decision_document.name,
                creator=creator,
            )
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

        decision_document_item_ids = [
            item.id for item in decision_document_items if item.id is not None
        ]
        DecisionDocumentItem.objects.filter(
            decision_document=decision_document
        ).exclude(id__in=decision_document_item_ids).delete()
        for item in decision_document_items:
            if id in item or "id" in item:
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
        message = ""
        try:
            decision_document = DecisionDocument.objects.get(pk=id)
            DecisionDocument.objects.filter(pk=id).update(
                is_active=not decision_document.is_active
            )
            decision_document.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            decision_document = None
            message = "Une erreur s'est produite."
        return UpdateDecisionDocumentState(
            done=done,
            success=success,
            message=message,
            decision_document=decision_document,
        )


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
        message = ""
        current_user = info.context.user
        if current_user.is_superuser:
            decision_document = DecisionDocument.objects.get(pk=id)
            decision_document.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteDecisionDocument(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************#

# ************************************************************************


class CreateBankAccount(graphene.Mutation):
    class Arguments:
        bank_account_data = BankAccountInput(required=True)
        image = Upload(required=False)

    bank_account = graphene.Field(BankAccountType)

    def mutate(root, info, image=None, bank_account_data=None):
        creator = info.context.user
        bank_account = BankAccount(**bank_account_data)
        bank_account.creator = creator
        bank_account.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = bank_account.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                bank_account.image = image_file
        bank_account.save()
        folder = Folder.objects.create(
            name=str(bank_account.id) + "_" + bank_account.name, creator=creator
        )
        bank_account.folder = folder
        bank_account.save()
        return CreateBankAccount(bank_account=bank_account)


class UpdateBankAccount(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        bank_account_data = BankAccountInput(required=True)
        image = Upload(required=False)

    bank_account = graphene.Field(BankAccountType)

    def mutate(root, info, id, image=None, bank_account_data=None):
        creator = info.context.user
        BankAccount.objects.filter(pk=id).update(**bank_account_data)
        bank_account = BankAccount.objects.get(pk=id)
        if not bank_account.folder or bank_account.folder is None:
            folder = Folder.objects.create(
                name=str(bank_account.id) + "_" + bank_account.name, creator=creator
            )
            BankAccount.objects.filter(pk=id).update(folder=folder)
        if not image and bank_account.image:
            image_file = bank_account.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = bank_account.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                bank_account.image = image_file
            bank_account.save()
        return UpdateBankAccount(bank_account=bank_account)


class UpdateBankAccountState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    bank_account = graphene.Field(BankAccountType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, bank_account_fields=None):
        creator = info.context.user
        done = True
        success = True
        bank_account = None
        message = ""
        try:
            bank_account = BankAccount.objects.get(pk=id)
            BankAccount.objects.filter(pk=id).update(
                is_active=not bank_account.is_active
            )
            bank_account.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            bank_account = None
            message = "Une erreur s'est produite."
        return UpdateBankAccountState(
            done=done, success=success, message=message, bank_account=bank_account
        )


class DeleteBankAccount(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    bank_account = graphene.Field(BankAccountType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        if current_user.is_superuser:
            bank_account = BankAccount.objects.get(pk=id)
            bank_account.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBankAccount(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************#

# ************************************************************************


class CreateBalance(graphene.Mutation):
    class Arguments:
        balance_data = BalanceInput(required=True)
        document = Upload(required=False)

    balance = graphene.Field(BalanceType)

    def mutate(root, info, document=None, balance_data=None):
        creator = info.context.user
        balance = Balance(**balance_data)
        balance.creator = creator
        balance.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = balance.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                balance.document = document_file
        balance.save()
        return CreateBalance(balance=balance)


class UpdateBalance(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        balance_data = BalanceInput(required=True)
        document = Upload(required=False)

    balance = graphene.Field(BalanceType)

    def mutate(root, info, id, document=None, balance_data=None):
        creator = info.context.user
        Balance.objects.filter(pk=id).update(**balance_data)
        balance = Balance.objects.get(pk=id)
        if not document and balance.document:
            document_file = balance.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = balance.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                balance.document = document_file
            balance.save()
        return UpdateBalance(balance=balance)


class DeleteBalance(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    balance = graphene.Field(BalanceType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        if current_user.is_superuser:
            balance = Balance.objects.get(pk=id)
            balance.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBalance(deleted=deleted, success=success, message=message, id=id)


# *************************************************************************#


class FinanceMutation(graphene.ObjectType):
    create_decision_document = CreateDecisionDocument.Field()
    update_decision_document = UpdateDecisionDocument.Field()
    update_decision_document_state = UpdateDecisionDocumentState.Field()
    delete_decision_document = DeleteDecisionDocument.Field()

    create_bank_account = CreateBankAccount.Field()
    update_bank_account = UpdateBankAccount.Field()
    update_bank_account_state = UpdateBankAccountState.Field()
    delete_bank_account = DeleteBankAccount.Field()

    create_balance = CreateBalance.Field()
    update_balance = UpdateBalance.Field()
    delete_balance = DeleteBalance.Field()
