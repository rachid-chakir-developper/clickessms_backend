import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload
from decimal import Decimal

from django.db.models import Q

from finance.models import DecisionDocument, DecisionDocumentItem, BankAccount, Balance, CashRegister, CashRegisterEstablishment, CashRegisterManager, CashRegisterTransaction, Budget, BudgetAccountingNature, Endowment
from data_management.models import AccountingNature
from medias.models import Folder, File
from companies.models import Establishment
from human_ressources.models import Employee


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


class BudgetAccountingNatureType(DjangoObjectType):
    class Meta:
        model = BudgetAccountingNature
        fields = "__all__"

class BudgetType(DjangoObjectType):
    class Meta:
        model = Budget
        fields = "__all__"


class BudgetNodeType(graphene.ObjectType):
    nodes = graphene.List(BudgetType)
    total_count = graphene.Int()


class BudgetFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class BudgetAccountingNatureInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    amount_allocated = graphene.Decimal(required=False)
    budget_id = graphene.Int(name="budget", required=False)
    accounting_nature_id = graphene.Int(name="accountingNature", required=False)
    managers = graphene.List(graphene.Int, required=False)

class BudgetInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    amount_allocated = graphene.Decimal(required=False)
    amount_spent = graphene.Decimal(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)


class CashRegisterEstablishmentType(DjangoObjectType):
    class Meta:
        model = CashRegisterEstablishment
        fields = "__all__"

class CashRegisterManagerType(DjangoObjectType):
    class Meta:
        model = CashRegisterManager
        fields = "__all__"

class CashRegisterType(DjangoObjectType):
    class Meta:
        model = CashRegister
        fields = "__all__"

    balance = graphene.Decimal()
    def resolve_balance(instance, info, **kwargs):
        return instance.current_balance


class CashRegisterNodeType(graphene.ObjectType):
    nodes = graphene.List(CashRegisterType)
    total_count = graphene.Int()

class CashRegisterFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class CashRegisterInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    opening_date = graphene.DateTime(required=False)
    closing_date = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    managers = graphene.List(graphene.Int, required=False)

class CashRegisterTransactionType(DjangoObjectType):
    class Meta:
        model = CashRegisterTransaction
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )


class CashRegisterTransactionNodeType(graphene.ObjectType):
    nodes = graphene.List(CashRegisterTransactionType)
    total_count = graphene.Int()


class CashRegisterTransactionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    cash_registers = graphene.List(graphene.Int, required=False)

class CashRegisterTransactionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    comment = graphene.String(required=False)
    description = graphene.String(required=False)
    date = graphene.DateTime(required=False)
    amount = graphene.Decimal(required=False)
    transaction_type = graphene.String(required=False)
    cash_register_id = graphene.Int(name="cashRegister", required=True)

class EndowmentType(DjangoObjectType):
    class Meta:
        model = Endowment
        fields = "__all__"

class EndowmentNodeType(graphene.ObjectType):
    nodes = graphene.List(EndowmentType)
    total_count = graphene.Int()

class EndowmentFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class EndowmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    amount_allocated = graphene.Decimal(required=True)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    gender = graphene.String(required=False)
    age_min = graphene.Float(required=False)
    age_max = graphene.Float(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    endowment_type_id = graphene.Int(name="endowmentType", required=True)
    accounting_nature_id = graphene.Int(name="accountingNature", required=True)
    professional_status_id = graphene.Int(name="professionalStatus", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

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
    cash_registers = graphene.Field(
        CashRegisterNodeType,
        cash_register_filter=CashRegisterFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    cash_register = graphene.Field(CashRegisterType, id=graphene.ID())
    cash_register_transactions = graphene.Field(
        CashRegisterTransactionNodeType,
        cash_register_transaction_filter=CashRegisterTransactionFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    cash_register_transaction = graphene.Field(CashRegisterTransactionType, id=graphene.ID())
    budgets = graphene.Field(
        BudgetNodeType,
        budget_filter=BudgetFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    budget = graphene.Field(BudgetType, id=graphene.ID())
    endowments = graphene.Field(EndowmentNodeType, endowment_filter= EndowmentFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    endowment = graphene.Field(EndowmentType, id = graphene.ID())

    def resolve_decision_documents(
        root, info, decision_document_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
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
        decision_documents = decision_documents.order_by("-created_at").distinct()
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
        company = user.the_current_company
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
        bank_accounts = bank_accounts.order_by("-created_at").distinct()
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
        company = user.the_current_company
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
        balances = balances.order_by("-created_at").distinct()
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
    def resolve_cash_registers(
        root, info, cash_register_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        cash_registers = CashRegister.objects.filter(company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                cash_registers = cash_registers.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                cash_registers = cash_registers.filter(creator=user)
        if cash_register_filter:
            keyword = cash_register_filter.get("keyword", "")
            starting_date_time = cash_register_filter.get("starting_date_time")
            ending_date_time = cash_register_filter.get("ending_date_time")
            if keyword:
                cash_registers = cash_registers.filter(
                    Q(name__icontains=keyword)
                    | Q(registration_number__icontains=keyword)
                    | Q(driver_name__icontains=keyword)
                )
            if starting_date_time:
                cash_registers = cash_registers.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                cash_registers = cash_registers.filter(created_at__lte=ending_date_time)
        cash_registers = cash_registers.order_by("-created_at").distinct()
        total_count = cash_registers.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            cash_registers = cash_registers[offset : offset + limit]
        return CashRegisterNodeType(nodes=cash_registers, total_count=total_count)

    def resolve_cash_register(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            cash_register = CashRegister.objects.get(pk=id)
        except CashRegister.DoesNotExist:
            cash_register = None
        return cash_register

    def resolve_cash_register_transactions(
        root, info, cash_register_transaction_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        cash_register_transactions = CashRegisterTransaction.objects.filter(cash_register__company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                cash_register_transactions = cash_register_transactions.filter(Q(cash_register__establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                cash_register_transactions = cash_register_transactions.filter(creator=user)
        if cash_register_transaction_filter:
            keyword = cash_register_transaction_filter.get("keyword", "")
            starting_date_time = cash_register_transaction_filter.get("starting_date_time")
            ending_date_time = cash_register_transaction_filter.get("ending_date_time")
            cash_registers = cash_register_transaction_filter.get("cash_registers")
            if cash_registers:
                cash_register_transactions = cash_register_transactions.filter(cash_register__id__in=cash_registers)
            if keyword:
                cash_register_transactions = cash_register_transactions.filter(
                    Q(name__icontains=keyword)
                    | Q(description__icontains=keyword)
                )
            if starting_date_time:
                cash_register_transactions = cash_register_transactions.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                cash_register_transactions = cash_register_transactions.filter(created_at__lte=ending_date_time)
        cash_register_transactions = cash_register_transactions.order_by("-created_at").distinct()
        total_count = cash_register_transactions.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            cash_register_transactions = cash_register_transactions[offset : offset + limit]
        return CashRegisterTransactionNodeType(nodes=cash_register_transactions, total_count=total_count)

    def resolve_cash_register_transaction(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            cash_register_transaction = CashRegisterTransaction.objects.get(pk=id)
        except CashRegisterTransaction.DoesNotExist:
            cash_register_transaction = None
        return cash_register_transaction 

    def resolve_budgets(
        root, info, budget_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        budgets = Budget.objects.filter(company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                budgets = budgets.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                budgets = budgets.filter(creator=user)
        the_order_by = '-created_at'
        if budget_filter:
            keyword = budget_filter.get("keyword", "")
            starting_date_time = budget_filter.get("starting_date_time")
            ending_date_time = budget_filter.get("ending_date_time")
            establishments = budget_filter.get('establishments')
            order_by = budget_filter.get('order_by')
            if establishments:
                budgets = budgets.filter(establishment__id__in=establishments)
            if keyword:
                budgets = budgets.filter(
                    Q(name__icontains=keyword)
                )
            if starting_date_time:
                budgets = budgets.filter(starting_date__gte=starting_date_time)
            if ending_date_time:
                budgets = budgets.filter(starting_date__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        budgets = budgets.order_by(the_order_by).distinct()
        total_count = budgets.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            budgets = budgets[offset : offset + limit]
        return BudgetNodeType(nodes=budgets, total_count=total_count)

    def resolve_budget(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            budget = Budget.objects.get(pk=id)
        except Budget.DoesNotExist:
            budget = None
        return budget

    def resolve_endowments(root, info, endowment_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        endowments = Endowment.objects.filter(company=company)
        if not user.can_manage_finance():
            if user.is_manager():
                endowments = endowments.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                endowments = endowments.filter(creator=user)
        the_order_by = '-created_at'
        if endowment_filter:
            keyword = endowment_filter.get('keyword', '')
            starting_date_time = endowment_filter.get('starting_date_time')
            ending_date_time = endowment_filter.get('ending_date_time')
            establishments = endowment_filter.get('establishments')
            order_by = endowment_filter.get('order_by')
            if establishments:
                endowments = endowments.filter(establishment__id__in=establishments)
            if keyword:
                endowments = endowments.filter(Q(label__icontains=keyword) | Q(endowment_type__name__icontains=keyword))
            if starting_date_time:
                endowments = endowments.filter(starting_date_time__gte=starting_date_time)
            if ending_date_time:
                endowments = endowments.filter(starting_date_time__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        endowments = endowments.order_by(the_order_by).distinct()
        total_count = endowments.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            endowments = endowments[offset:offset + limit]
        return EndowmentNodeType(nodes=endowments, total_count=total_count)

    def resolve_endowment(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            endowment = Endowment.objects.get(pk=id)
        except Endowment.DoesNotExist:
            endowment = None
        return endowment


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
        decision_document.company = creator.the_current_company
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
        bank_account.company = creator.the_current_company
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
        balance.company = creator.the_current_company
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

# ************************************************************************


class CreateCashRegister(graphene.Mutation):
    class Arguments:
        cash_register_data = CashRegisterInput(required=True)

    cash_register = graphene.Field(CashRegisterType)

    def mutate(root, info, cash_register_data=None):
        creator = info.context.user
        establishment_ids = cash_register_data.pop("establishments")
        manager_ids = cash_register_data.pop("managers")
        cash_register = CashRegister(**cash_register_data)
        cash_register.creator = creator
        cash_register.company = creator.the_current_company
        cash_register.save()
        folder = Folder.objects.create(
            name=str(cash_register.id) + "_" + cash_register.name, creator=creator
        )
        cash_register.folder = folder
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                cash_register_establishment = CashRegisterEstablishment.objects.get(establishment__id=establishment.id, cash_register__id=cash_register.id)
            except CashRegisterEstablishment.DoesNotExist:
                CashRegisterEstablishment.objects.create(
                        cash_register=cash_register,
                        establishment=establishment,
                        creator=creator
                    )
        employees = Employee.objects.filter(id__in=manager_ids)
        for employee in employees:
            try:
                cash_register_manager = CashRegisterManager.objects.get(employee__id=employee.id, cash_register__id=cash_register.id)
            except CashRegisterManager.DoesNotExist:
                CashRegisterManager.objects.create(
                        cash_register=cash_register,
                        employee=employee,
                        creator=creator
                    )
        cash_register.save()
        return CreateCashRegister(cash_register=cash_register)


class UpdateCashRegister(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        cash_register_data = CashRegisterInput(required=True)

    cash_register = graphene.Field(CashRegisterType)

    def mutate(root, info, id, cash_register_data=None):
        creator = info.context.user
        establishment_ids = cash_register_data.pop("establishments")
        manager_ids = cash_register_data.pop("managers")
        CashRegister.objects.filter(pk=id).update(**cash_register_data)
        cash_register = CashRegister.objects.get(pk=id)
        if not cash_register.folder or cash_register.folder is None:
            folder = Folder.objects.create(
                name=str(cash_register.id) + "_" + cash_register.name, creator=creator
            )
            CashRegister.objects.filter(pk=id).update(folder=folder)

        CashRegisterEstablishment.objects.filter(cash_register=cash_register).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                cash_register_establishment = CashRegisterEstablishment.objects.get(establishment__id=establishment.id, cash_register__id=cash_register.id)
            except CashRegisterEstablishment.DoesNotExist:
                CashRegisterEstablishment.objects.create(
                        cash_register=cash_register,
                        establishment=establishment,
                        creator=creator
                    )

        CashRegisterManager.objects.filter(cash_register=cash_register).exclude(employee__id__in=manager_ids).delete()
        employees = Employee.objects.filter(id__in=manager_ids)
        for employee in employees:
            try:
                cash_register_manager = CashRegisterManager.objects.get(employee__id=employee.id, cash_register__id=cash_register.id)
            except CashRegisterManager.DoesNotExist:
                CashRegisterManager.objects.create(
                        cash_register=cash_register,
                        employee=employee,
                        creator=creator
                    )
        return UpdateCashRegister(cash_register=cash_register)


class UpdateCashRegisterState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    cash_register = graphene.Field(CashRegisterType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, cash_register_fields=None):
        creator = info.context.user
        done = True
        success = True
        cash_register = None
        message = ""
        try:
            cash_register = CashRegister.objects.get(pk=id)
            CashRegister.objects.filter(pk=id).update(
                is_active=not cash_register.is_active
            )
            cash_register.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            cash_register = None
            message = "Une erreur s'est produite."
        return UpdateCashRegisterState(
            done=done, success=success, message=message, cash_register=cash_register
        )


class DeleteCashRegister(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    cash_register = graphene.Field(CashRegisterType)
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
            cash_register = CashRegister.objects.get(pk=id)
            cash_register.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteCashRegister(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************#
# ************************************************************************


class CreateCashRegisterTransaction(graphene.Mutation):
    class Arguments:
        cash_register_transaction_data = CashRegisterTransactionInput(required=True)
        document = Upload(required=False)

    cash_register_transaction = graphene.Field(CashRegisterTransactionType)

    def mutate(root, info, document=None, cash_register_transaction_data=None):
        creator = info.context.user
        # Vérification si le cash_register existe
        try:
            cash_register = CashRegister.objects.get(pk=cash_register_transaction_data.cash_register_id)
        except CashRegister.DoesNotExist:
            raise ValueError("Le registre de caisse spécifié n'existe pas.")
        cash_register_transaction = CashRegisterTransaction(**cash_register_transaction_data)
        cash_register_transaction.creator = creator
        cash_register_transaction.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = cash_register_transaction.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                cash_register_transaction.document = document_file
        cash_register_transaction.save()
        return CreateCashRegisterTransaction(cash_register_transaction=cash_register_transaction)


class UpdateCashRegisterTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        cash_register_transaction_data = CashRegisterTransactionInput(required=True)
        document = Upload(required=False)

    cash_register_transaction = graphene.Field(CashRegisterTransactionType)

    def mutate(root, info, id, document=None, cash_register_transaction_data=None):
        creator = info.context.user
        # Vérification si le cash_register existe
        try:
            cash_register = CashRegister.objects.get(pk=cash_register_transaction_data.cash_register_id)
        except CashRegister.DoesNotExist:
            raise ValueError("Le registre de caisse spécifié n'existe pas.")
        CashRegisterTransaction.objects.filter(pk=id).update(**cash_register_transaction_data)
        cash_register_transaction = CashRegisterTransaction.objects.get(pk=id)
        if not document and cash_register_transaction.document:
            document_file = cash_register_transaction.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = cash_register_transaction.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                cash_register_transaction.document = document_file
            cash_register_transaction.save()
        return UpdateCashRegisterTransaction(cash_register_transaction=cash_register_transaction)


class DeleteCashRegisterTransaction(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    cash_register_transaction = graphene.Field(CashRegisterTransactionType)
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
            cash_register_transaction = CashRegisterTransaction.objects.get(pk=id)
            cash_register_transaction.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteCashRegisterTransaction(deleted=deleted, success=success, message=message, id=id)


# *************************************************************************#
# ************************************************************************


class CreateBudget(graphene.Mutation):
    class Arguments:
        budget_data = BudgetInput(required=True)

    budget = graphene.Field(BudgetType)

    def mutate(root, info, budget_data=None):
        creator = info.context.user
        budget = Budget(**budget_data)
        budget.creator = creator
        budget.company = creator.the_current_company
        budget.save()
        folder = Folder.objects.create(
            name=str(budget.id) + "_" + budget.name, creator=creator
        )
        budget.folder = folder
        budget.save()
        return CreateBudget(budget=budget)


class UpdateBudget(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        budget_data = BudgetInput(required=True)

    budget = graphene.Field(BudgetType)

    def mutate(root, info, id, budget_data=None):
        creator = info.context.user
        Budget.objects.filter(pk=id).update(**budget_data)
        budget = Budget.objects.get(pk=id)
        is_draft = True if budget.status == 'DRAFT' else False
        if not budget.folder or budget.folder is None:
            folder = Folder.objects.create(
                name=str(budget.id) + "_" + budget.name, creator=creator
            )
            Budget.objects.filter(pk=id).update(folder=folder)
        if is_draft:
            Budget.objects.filter(pk=id).update(status='PENDING')
            budget.refresh_from_db()
        return UpdateBudget(budget=budget)

class UpdateBudgetAccountingNature(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        budget_accounting_nature_data = BudgetAccountingNatureInput(required=True)

    budget_accounting_nature = graphene.Field(BudgetAccountingNatureType)

    def mutate(root, info, id=None, budget_accounting_nature_data=None):
        creator = info.context.user
        managers_ids = budget_accounting_nature_data.pop("managers", None)
        budget_id = budget_accounting_nature_data.get("budget_id", None)
        accounting_nature_id = budget_accounting_nature_data.get("accounting_nature_id", None)

         # Vérifier que le budget existe
        try:
            budget = Budget.objects.get(pk=budget_id)
        except Budget.DoesNotExist:
            raise Exception(f"Aucun budget trouvé avec l'ID {budget_id}.")

        # Vérifier que la nature comptable existe
        try:
            accounting_nature = AccountingNature.objects.get(pk=accounting_nature_id)
        except AccountingNature.DoesNotExist:
            raise Exception(f"Aucune nature comptable trouvée avec l'ID {accounting_nature_id}.")

        # Rechercher un BudgetAccountingNature existant
        budget_accounting_nature = BudgetAccountingNature.objects.filter(
            budget_id=budget_id,
            accounting_nature_id=accounting_nature_id
        ).first()

        if budget_accounting_nature:
            # Mettre à jour les champs dynamiquement si l'objet existe
            for key, value in budget_accounting_nature_data.items():
                setattr(budget_accounting_nature, key, value)
            budget_accounting_nature.save()
        else:
            # Créer un nouvel objet si aucun n'existe
            budget_accounting_nature = BudgetAccountingNature.objects.create(
                budget=budget,
                accounting_nature=accounting_nature,
                creator=creator,
                **budget_accounting_nature_data
            )
        if managers_ids and managers_ids is not None:
            budget_accounting_nature.managers.set(managers_ids)

        return UpdateBudgetAccountingNature(budget_accounting_nature=budget_accounting_nature)

class UpdateBudgetState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    budget = graphene.Field(BudgetType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, budget_fields=None):
        creator = info.context.user
        done = True
        success = True
        budget = None
        message = ""
        try:
            budget = Budget.objects.get(pk=id)
            Budget.objects.filter(pk=id).update(
                is_active=not budget.is_active
            )
            budget.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            budget = None
            message = "Une erreur s'est produite."
        return UpdateBudgetState(
            done=done, success=success, message=message, budget=budget
        )

class UpdateBudgetFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        budget_data = BudgetInput(required=True)

    budget = graphene.Field(BudgetType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, budget_data=None):
        creator = info.context.user
        done = True
        success = True
        budget = None
        message = ''
        try:
            budget = Budget.objects.get(pk=id)
            Budget.objects.filter(pk=id).update(**budget_data)
            budget.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            budget=None
            message = "Une erreur s'est produite."
        return UpdateBudgetFields(done=done, success=success, message=message, budget=budget)

class DeleteBudget(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    budget = graphene.Field(BudgetType)
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
            budget = Budget.objects.get(pk=id)
            budget.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBudget(
            deleted=deleted, success=success, message=message, id=id
        )
#************************************************************************
#************************************************************************

class CreateEndowment(graphene.Mutation):
    class Arguments:
        endowment_data = EndowmentInput(required=True)

    endowment = graphene.Field(EndowmentType)

    def mutate(root, info, endowment_data=None):
        creator = info.context.user
        endowment = Endowment(**endowment_data)
        endowment.creator = creator
        endowment.company = creator.the_current_company
        endowment.save()
        return CreateEndowment(endowment=endowment)

class UpdateEndowment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        endowment_data = EndowmentInput(required=True)

    endowment = graphene.Field(EndowmentType)

    def mutate(root, info, id, endowment_data=None):
        creator = info.context.user
        Endowment.objects.filter(pk=id).update(**endowment_data)
        endowment = Endowment.objects.get(pk=id)
        return UpdateEndowment(endowment=endowment)
        
class UpdateEndowmentState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    endowment = graphene.Field(EndowmentType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, endowment_fields=None):
        creator = info.context.user
        done = True
        success = True
        endowment = None
        message = ''
        try:
            endowment = Endowment.objects.get(pk=id)
            Endowment.objects.filter(pk=id).update(is_active=not endowment.is_active)
            endowment.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            endowment=None
            message = "Une erreur s'est produite."
        return UpdateEndowmentState(done=done, success=success, message=message,endowment=endowment)


class DeleteEndowment(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    endowment = graphene.Field(EndowmentType)
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
            endowment = Endowment.objects.get(pk=id)
            endowment.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEndowment(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#

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

    create_cash_register = CreateCashRegister.Field()
    update_cash_register = UpdateCashRegister.Field()
    update_cash_register_state = UpdateCashRegisterState.Field()
    delete_cash_register = DeleteCashRegister.Field()

    create_cash_register_transaction = CreateCashRegisterTransaction.Field()
    update_cash_register_transaction = UpdateCashRegisterTransaction.Field()
    delete_cash_register_transaction = DeleteCashRegisterTransaction.Field()

    create_budget = CreateBudget.Field()
    update_budget = UpdateBudget.Field()
    update_budget_accounting_nature = UpdateBudgetAccountingNature.Field()
    update_budget_state = UpdateBudgetState.Field()
    update_budget_fields = UpdateBudgetFields.Field()
    delete_budget = DeleteBudget.Field()

    create_endowment = CreateEndowment.Field()
    update_endowment = UpdateEndowment.Field()
    update_endowment_state = UpdateEndowmentState.Field()
    delete_endowment = DeleteEndowment.Field()