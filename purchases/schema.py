import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q
from datetime import datetime, timedelta

from purchases.models import Supplier, PurchaseContract, Expense, ExpenseItem, PurchaseOrder, PurchaseOrderItem, ExpenseReport
from companies.models import Establishment
from medias.models import Folder, File
from accounts.models import User
from medias.schema import MediaInput

from notifications.notificator import notify_expense, notify_expense_report


class SupplierType(DjangoObjectType):
    class Meta:
        model = Supplier
        fields = "__all__"
    photo = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class SupplierNodeType(graphene.ObjectType):
    nodes = graphene.List(SupplierType)
    total_count = graphene.Int()

class SupplierFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    is_verified = graphene.Boolean(required=False)

class SupplierInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    external_number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    supplier_type = graphene.String(required=True)
    manager_name = graphene.String(required=True)
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
    is_verified = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class PurchaseContractType(DjangoObjectType):
    class Meta:
        model = PurchaseContract
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )

class PurchaseContractNodeType(graphene.ObjectType):
    nodes = graphene.List(PurchaseContractType)
    total_count = graphene.Int()

class PurchaseContractFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    suppliers = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class PurchaseContractInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    contract_number = graphene.String(required=False)
    title = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    supplier_id = graphene.Int(name="supplier", required=False)

class ExpenseItemType(DjangoObjectType):
    class Meta:
        model = ExpenseItem
        fields = "__all__"

class ExpenseType(DjangoObjectType):
    class Meta:
        model = Expense
        fields = "__all__"


class ExpenseNodeType(graphene.ObjectType):
    nodes = graphene.List(ExpenseType)
    total_count = graphene.Int()


class ExpenseFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    statuses = graphene.List(graphene.String, required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class ExpenseExpenseItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    quantity = graphene.Float(required=False)
    amount = graphene.Decimal(required=False)
    expense_date_time = graphene.DateTime(required=False)
    status = graphene.String(required=False)
    description = graphene.String(required=False)
    comment = graphene.String(required=False)
    accounting_nature_id = graphene.Int(name="accountingNature", required=False)

class ExpenseInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    total_amount = graphene.Decimal(required=False)
    expense_date_time = graphene.DateTime(required=False)
    payment_method = graphene.String(required=False)
    check_number = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    expense_type = graphene.String(required=False)
    description = graphene.String(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    status = graphene.String(required=False)
    is_amount_accurate = graphene.Boolean(required=False)
    is_planned_in_budget = graphene.Boolean(required=False)
    is_active = graphene.Boolean(required=False)
    expense_items = graphene.List(ExpenseExpenseItemInput, required=False)
    supplier_id = graphene.Int(name="supplier", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)
    bank_card_id = graphene.Int(name="bankCard", required=False)
    cash_register_id = graphene.Int(name="cashRegister", required=False)

class PurchaseOrderItemType(DjangoObjectType):
    class Meta:
        model = PurchaseOrderItem
        fields = "__all__"

class PurchaseOrderType(DjangoObjectType):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"


class PurchaseOrderNodeType(graphene.ObjectType):
    nodes = graphene.List(PurchaseOrderType)
    total_count = graphene.Int()


class PurchaseOrderFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    statuses = graphene.List(graphene.String, required=False)
    order_by = graphene.String(required=False)

class PurchaseOrderPurchaseOrderItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    quantity = graphene.Float(required=False)
    amount = graphene.Decimal(required=False)
    description = graphene.String(required=False)
    comment = graphene.String(required=False)

class PurchaseOrderInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    total_ttc = graphene.Decimal(required=False)
    order_date_time = graphene.DateTime(required=False)
    validity_end_date = graphene.DateTime(required=False)
    payment_method = graphene.String(required=False)
    description = graphene.String(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    status = graphene.String(required=False)
    purchase_order_items = graphene.List(PurchaseOrderPurchaseOrderItemInput, required=False)
    supplier_id = graphene.Int(name="supplier", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class ExpenseReportType(DjangoObjectType):
    class Meta:
        model = ExpenseReport
        fields = "__all__"

class ExpenseReportNodeType(graphene.ObjectType):
    nodes = graphene.List(ExpenseReportType)
    total_count = graphene.Int()


class ExpenseReportFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    statuses = graphene.List(graphene.String, required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class ExpenseReportInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    total_amount = graphene.Decimal(required=False)
    expense_date_time = graphene.DateTime(required=False)
    payment_method = graphene.String(required=False)
    description = graphene.String(required=False)
    comment = graphene.String(required=False)
    observation = graphene.String(required=False)
    status = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishment_id = graphene.Int(name="establishment", required=False)

class PurchasesQuery(graphene.ObjectType):
    suppliers = graphene.Field(SupplierNodeType, supplier_filter= SupplierFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    supplier = graphene.Field(SupplierType, id = graphene.ID())
    expenses = graphene.Field(
        ExpenseNodeType,
        expense_filter=ExpenseFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    expense = graphene.Field(ExpenseType, id=graphene.ID())
    purchase_orders = graphene.Field(
        PurchaseOrderNodeType,
        purchase_order_filter=PurchaseOrderFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    purchase_order = graphene.Field(PurchaseOrderType, id=graphene.ID())
    expense_reports = graphene.Field(
        ExpenseReportNodeType,
        expense_report_filter=ExpenseReportFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    expense_report = graphene.Field(ExpenseReportType, id=graphene.ID())
    def resolve_suppliers(root, info, supplier_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        suppliers = Supplier.objects.filter(company__id=id_company, is_deleted=False) if id_company else Supplier.objects.filter(company=company, is_deleted=False)
        if supplier_filter:
            keyword = supplier_filter.get('keyword', '')
            starting_date_time = supplier_filter.get('starting_date_time')
            ending_date_time = supplier_filter.get('ending_date_time')
            is_verified = supplier_filter.get('is_verified')
            if is_verified:
                suppliers = suppliers.filter(is_verified=is_verified)
            if keyword:
                suppliers = suppliers.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                suppliers = suppliers.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                suppliers = suppliers.filter(created_at__lte=ending_date_time)
        suppliers = suppliers.order_by('-created_at')
        total_count = suppliers.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            suppliers = suppliers[offset:offset + limit]
        return SupplierNodeType(nodes=suppliers, total_count=total_count)

    def resolve_supplier(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            supplier = Supplier.objects.get(pk=id, company=company)
        except Supplier.DoesNotExist:
            supplier = None
        return supplier

    def resolve_expenses(
        root, info, expense_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        expenses = Expense.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_finance():
            if user.is_manager():
                expenses = expenses.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                expenses = expenses.filter(creator=user)
        the_order_by = '-created_at'
        if expense_filter:
            keyword = expense_filter.get("keyword", "")
            starting_date_time = expense_filter.get("starting_date_time")
            ending_date_time = expense_filter.get("ending_date_time")
            establishments = expense_filter.get('establishments')
            statuses = expense_filter.get('statuses')
            list_type = expense_filter.get('list_type') # ALL_EXPENSE_REQUESTS / MY_EXPENSES / MY_EXPENSE_REQUESTS / ALL
            order_by = expense_filter.get('order_by')
            if establishments:
                expenses = expenses.filter(establishment__id__in=establishments)
            if list_type:
                if list_type == 'MY_EXPENSES':
                    expenses = expenses.filter(creator=user)
                elif list_type == 'MY_EXPENSE_REQUESTS':
                    expenses = expenses.filter(creator=user)
                elif list_type == 'ALL':
                    pass
            if keyword:
                expenses = expenses.filter(
                    Q(name__icontains=keyword)
                )
            if starting_date_time:
                expenses = expenses.filter(starting_date__gte=starting_date_time)
            if ending_date_time:
                expenses = expenses.filter(starting_date__lte=ending_date_time)
            if statuses:
                expenses = expenses.filter(status__in=statuses)
            if order_by:
                the_order_by = order_by
        expenses = expenses.order_by(the_order_by).distinct()
        total_count = expenses.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            expenses = expenses[offset : offset + limit]
        return ExpenseNodeType(nodes=expenses, total_count=total_count)

    def resolve_expense(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            expense = Expense.objects.get(pk=id, company=company)
        except Expense.DoesNotExist:
            expense = None
        return expense

    def resolve_purchase_orders(
        root, info, purchase_order_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        purchase_orders = PurchaseOrder.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_finance():
            if user.is_manager():
                purchase_orders = purchase_orders.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user) | Q(expense__creator=user))
            else:
                purchase_orders = purchase_orders.filter(Q(creator=user) | Q(expense__creator=user))
        the_order_by = '-created_at'
        if purchase_order_filter:
            keyword = purchase_order_filter.get("keyword", "")
            starting_date_time = purchase_order_filter.get("starting_date_time")
            ending_date_time = purchase_order_filter.get("ending_date_time")
            establishments = purchase_order_filter.get('establishments')
            statuses = purchase_order_filter.get('statuses')
            order_by = purchase_order_filter.get('order_by')
            if establishments:
                purchase_orders = purchase_orders.filter(establishment__id__in=establishments)
            if keyword:
                purchase_orders = purchase_orders.filter(
                    Q(name__icontains=keyword)
                )
            if starting_date_time:
                purchase_orders = purchase_orders.filter(starting_date__gte=starting_date_time)
            if ending_date_time:
                purchase_orders = purchase_orders.filter(starting_date__lte=ending_date_time)
            if statuses:
                purchase_orders = purchase_orders.filter(status__in=statuses)
            if order_by:
                the_order_by = order_by
        purchase_orders = purchase_orders.order_by(the_order_by).distinct()
        total_count = purchase_orders.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            purchase_orders = purchase_orders[offset : offset + limit]
        return PurchaseOrderNodeType(nodes=purchase_orders, total_count=total_count)

    def resolve_purchase_order(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            purchase_order = PurchaseOrder.objects.get(pk=id, company=company)
        except PurchaseOrder.DoesNotExist:
            purchase_order = None
        return purchase_order

    def resolve_expense_reports(
        root, info, expense_report_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        expense_reports = ExpenseReport.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_finance():
            if user.is_manager():
                expense_reports = expense_reports.filter(Q(establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                expense_reports = expense_reports.filter(creator=user)
        the_order_by = '-created_at'
        if expense_report_filter:
            keyword = expense_report_filter.get("keyword", "")
            starting_date_time = expense_report_filter.get("starting_date_time")
            ending_date_time = expense_report_filter.get("ending_date_time")
            establishments = expense_report_filter.get('establishments')
            statuses = expense_report_filter.get('statuses')
            list_type = expense_report_filter.get('list_type') # ALL_EXPENSE_REQUESTS / MY_EXPENSES / MY_EXPENSE_REQUESTS / ALL
            order_by = expense_report_filter.get('order_by')
            if establishments:
                expense_reports = expense_reports.filter(establishment__id__in=establishments)
            if list_type:
                if list_type == 'MY_EXPENSES':
                    expense_reports = expense_reports.filter(creator=user)
                elif list_type == 'MY_EXPENSE_REQUESTS':
                    expense_reports = expense_reports.filter(creator=user)
                elif list_type == 'ALL':
                    pass
            if keyword:
                expense_reports = expense_reports.filter(
                    Q(name__icontains=keyword)
                )
            if starting_date_time:
                expense_reports = expense_reports.filter(starting_date__gte=starting_date_time)
            if ending_date_time:
                expense_reports = expense_reports.filter(starting_date__lte=ending_date_time)
            if statuses:
                expense_reports = expense_reports.filter(status__in=statuses)
            if order_by:
                the_order_by = order_by
        expense_reports = expense_reports.order_by(the_order_by).distinct()
        total_count = expense_reports.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            expense_reports = expense_reports[offset : offset + limit]
        return ExpenseReportNodeType(nodes=expense_reports, total_count=total_count)

    def resolve_expense_report(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            expense_report = ExpenseReport.objects.get(pk=id, company=company)
        except ExpenseReport.DoesNotExist:
            expense_report = None
        return expense_report

#*******************************************************************************************************************************
#*******************************************************************************************************************************

class CreateSupplier(graphene.Mutation):
    class Arguments:
        supplier_data = SupplierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    supplier = graphene.Field(SupplierType)

    def mutate(root, info, photo=None, cover_image=None,  supplier_data=None):
        creator = info.context.user
        supplier = Supplier(**supplier_data)
        supplier.creator = creator
        supplier.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = supplier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                supplier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = supplier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                supplier.cover_image = cover_image_file
        supplier.save()
        folder = Folder.objects.create(name=str(supplier.id)+'_'+supplier.name,creator=creator)
        supplier.folder = folder
        supplier.save()
        return CreateSupplier(supplier=supplier)

class UpdateSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        supplier_data = SupplierInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    supplier = graphene.Field(SupplierType)

    def mutate(root, info, id, photo=None, cover_image=None,  supplier_data=None):
        creator = info.context.user
        try:
            supplier = Supplier.objects.get(pk=id, company=creator.the_current_company)
        except Supplier.DoesNotExist:
            raise e
        Supplier.objects.filter(pk=id).update(**supplier_data)
        supplier.refresh_from_db()
        if not supplier.folder or supplier.folder is None:
            folder = Folder.objects.create(name=str(supplier.id)+'_'+supplier.name,creator=creator)
            Supplier.objects.filter(pk=id).update(folder=folder)
        if not photo and supplier.photo:
            photo_file = supplier.photo
            photo_file.delete()
        if not cover_image and supplier.cover_image:
            cover_image_file = supplier.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = supplier.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                supplier.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = supplier.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                supplier.cover_image = cover_image_file
            supplier.save()
        supplier = Supplier.objects.get(pk=id)
        return UpdateSupplier(supplier=supplier)
        
class UpdateSupplierState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    supplier = graphene.Field(SupplierType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, supplier_fields=None):
        creator = info.context.user
        try:
            supplier = Supplier.objects.get(pk=id, company=creator.the_current_company)
        except Supplier.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            Supplier.objects.filter(pk=id).update(is_active=not supplier.is_active)
            supplier.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            supplier=None
            message = "Une erreur s'est produite."
        return UpdateSupplierState(done=done, success=success, message=message,supplier=supplier)

class DeleteSupplier(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    supplier = graphene.Field(SupplierType)
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
            supplier = Supplier.objects.get(pk=id, company=current_user.the_current_company)
        except Supplier.DoesNotExist:
            raise e
        if current_user.is_superuser or supplier.creator==current_user:
            supplier = Supplier.objects.get(pk=id)
            supplier.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteSupplier(deleted=deleted, success=success, message=message, id=id)

# ************************************************************************
#*****************************************************************************************************************

class CreatePurchaseContract(graphene.Mutation):
    class Arguments:
        purchase_contract_data = PurchaseContractInput(required=True)
        document = Upload(required=False)

    purchase_contract = graphene.Field(PurchaseContractType)

    def mutate(root, info, document=None, purchase_contract_data=None):
        creator = info.context.user
        purchase_contract = PurchaseContract(**purchase_contract_data)
        purchase_contract.creator = creator
        purchase_contract.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = purchase_contract.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                purchase_contract.document = document_file
        purchase_contract.save()
        folder = Folder.objects.create(
            name=str(purchase_contract.id) + "_" + purchase_contract.name,
            creator=creator,
        )
        purchase_contract.folder = folder
        purchase_contract.save()
        return CreatePurchaseContract(purchase_contract=purchase_contract)

class UpdatePurchaseContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        purchase_contract_data = PurchaseContractInput(required=True)
        document = Upload(required=False)

    purchase_contract = graphene.Field(PurchaseContractType)

    def mutate(root, info, id, document=None, purchase_contract_data=None):
        creator = info.context.user
        try:
            purchase_contract = PurchaseContract.objects.get(pk=id, company=creator.the_current_company)
        except PurchaseContract.DoesNotExist:
            raise e
        PurchaseContract.objects.filter(pk=id).update(**purchase_contract_data)
        purchase_contract.refresh_from_db()
        if not purchase_contract.folder or purchase_contract.folder is None:
            folder = Folder.objects.create(
                name=str(purchase_contract.id) + "_" + purchase_contract.name,
                creator=creator,
            )
            PurchaseContract.objects.filter(pk=id).update(folder=folder)
        if not document and purchase_contract.document:
            document_file = purchase_contract.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = purchase_contract.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                purchase_contract.document = document_file
        purchase_contract.save()
        return UpdatePurchaseContract(purchase_contract=purchase_contract)

class UpdatePurchaseContractState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    purchase_contract = graphene.Field(PurchaseContractType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, purchase_contract_fields=None):
        creator = info.context.user
        try:
            purchase_contract = PurchaseContract.objects.get(pk=id, company=creator.the_current_company)
        except PurchaseContract.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            PurchaseContract.objects.filter(pk=id).update(is_active=not purchase_contract.is_active)
            purchase_contract.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            purchase_contract=None
            message = "Une erreur s'est produite."
        return UpdatePurchaseContractState(done=done, success=success, message=message,purchase_contract=purchase_contract)

class DeletePurchaseContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    purchase_contract = graphene.Field(PurchaseContractType)
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
            purchase_contract = PurchaseContract.objects.get(pk=id, company=current_user.the_current_company)
        except PurchaseContract.DoesNotExist:
            raise e
        if current_user.is_superuser or purchase_contract.creator==current_user:
            purchase_contract = PurchaseContract.objects.get(pk=id)
            purchase_contract.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeletePurchaseContract(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#*******************************************************************************************************************************

class CreateExpense(graphene.Mutation):
    class Arguments:
        expense_data = ExpenseInput(required=True)
        files = graphene.List(MediaInput, required=False)

    expense = graphene.Field(ExpenseType)

    def mutate(root, info, files=None, expense_data=None):
        creator = info.context.user
        expense_items = expense_data.pop("expense_items")
        expense = Expense(**expense_data)
        expense.creator = creator
        expense.company = creator.the_current_company
        expense.save()
        folder = Folder.objects.create(name=str(expense.id)+'_'+expense.label,creator=creator)
        expense.folder = folder
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
                file_file.folder = expense.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            expense.files.add(file_file)
        expense.save()
        if not expense.employee:
            expense.employee = creator.get_employee_in_company()
            expense.save()
        for item in expense_items:
            expense_item = ExpenseItem(**item)
            expense_item.expense = expense
            expense_item.creator = creator
            expense_item.save()

        if expense.status == 'PENDING':
            finance_managers = User.get_finance_managers_in_user_company(user=creator)
            for finance_manager in finance_managers:
                notify_expense(sender=creator, recipient=finance_manager, expense=expense, action='ADDED')
        return CreateExpense(expense=expense)


class UpdateExpense(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        expense_data = ExpenseInput(required=True)
        files = graphene.List(MediaInput, required=False)

    expense = graphene.Field(ExpenseType)

    def mutate(root, info, id, files=None, expense_data=None):
        creator = info.context.user
        try:
            expense = Expense.objects.get(pk=id, company=creator.the_current_company)
        except Expense.DoesNotExist:
            raise e
        expense_items = expense_data.pop("expense_items")
        Expense.objects.filter(pk=id).update(**expense_data)
        expense.refresh_from_db()
        if not expense.folder or expense.folder is None:
            folder = Folder.objects.create(name=str(expense.id)+'_'+expense.label,creator=creator)
            Expense.objects.filter(pk=id).update(folder=folder)
            expense.refresh_from_db()
        if not expense.employee:
            expense.employee = creator.get_employee_in_company()
            expense.save()
        if not files:
            files = []
        else:
            file_ids = [item.id for item in files if item.id is not None]
            File.objects.filter(file_expenses=expense).exclude(id__in=file_ids).delete()
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = expense.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            expense.files.add(file_file)
        expense.save()
        expense_item_ids = [
            item.id for item in expense_items if item.id is not None
        ]
        ExpenseItem.objects.filter(
            expense=expense
        ).exclude(id__in=expense_item_ids).delete()
        for item in expense_items:
            if id in item or "id" in item:
                ExpenseItem.objects.filter(pk=item.id).update(**item)
            else:
                expense_item = ExpenseItem(**item)
                expense_item.expense = expense
                expense_item.creator = creator
                expense_item.save()
        is_draft = True if expense.status == 'DRAFT' else False
        if is_draft:
            Expense.objects.filter(pk=id).update(status='PENDING')
            expense.refresh_from_db()
        notify_expense(sender=creator, recipient=expense.creator, expense=expense, action='UPDATED')
        return UpdateExpense(expense=expense)


class UpdateExpenseState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    expense = graphene.Field(ExpenseType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, expense_fields=None):
        creator = info.context.user
        try:
            expense = Expense.objects.get(pk=id, company=creator.the_current_company)
        except Expense.DoesNotExist:
            raise e
        done = True
        success = True
        message = ""
        try:
            Expense.objects.filter(pk=id).update(
                is_active=not expense.is_active
            )
            expense.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            expense = None
            message = "Une erreur s'est produite."
        return UpdateExpenseState(
            done=done, success=success, message=message, expense=expense
        )

class UpdateExpenseFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        expense_data = ExpenseInput(required=True)

    expense = graphene.Field(ExpenseType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, expense_data=None):
        creator = info.context.user
        try:
            expense = Expense.objects.get(pk=id, company=creator.the_current_company)
        except Expense.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            Expense.objects.filter(pk=id).update(**expense_data)
            expense.refresh_from_db()
            if 'status' in expense_data:
                if creator.can_manage_finance() or creator.is_manager():
                    employee_user = expense.employee.user if expense.employee else expense.creator
                    if employee_user:
                        notify_expense(sender=creator, recipient=employee_user, expense=expense)
                else:
                    finance_managers = User.get_finance_managers_in_user_company(user=creator)
                    for finance_manager in finance_managers:
                        notify_expense(sender=creator, recipient=finance_manager, expense=expense)
                expense.refresh_from_db()
        except Exception as e:
            print(e)
            done = False
            success = False
            expense=None
            message = "Une erreur s'est produite."
        return UpdateExpenseFields(done=done, success=success, message=message, expense=expense)


class DeleteExpense(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    expense = graphene.Field(ExpenseType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        try:
            expense = Expense.objects.get(pk=id, company=current_user.the_current_company)
        except Expense.DoesNotExist:
            raise e
        if current_user.is_superuser or expense.creator==current_user:
            expense = Expense.objects.get(pk=id)
            expense.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteExpense(
            deleted=deleted, success=success, message=message, id=id
        )
# *****************************************************************************

class GeneratePurchaseOrder(graphene.Mutation):
    class Arguments:
        id_expense = graphene.ID(required=True)
        id_purchase_order = graphene.ID(required=False)

    success = graphene.Boolean()
    message = graphene.String()
    purchase_order = graphene.Field(PurchaseOrderType)

    def mutate(self, info, id_expense, id_purchase_order=None):
        creator = info.context.user
        # Vérifier si la dépense existe
        try:
            expense = Expense.objects.get(id=id_expense, company=creator.the_current_company)
        except Expense.DoesNotExist:
            return GeneratePurchaseOrder(success=False, message="Dépense introuvable.")

        # Si un ID de bon est fourni, vérifier son existence
        if id_purchase_order:
            try:
                purchase_order = PurchaseOrder.objects.get(id=id_purchase_order)
                purchase_order.purchase_order_items.all().delete()
                return GeneratePurchaseOrder(
                    success=True,
                    message="Bon de commande mis à jour avec succès.",
                    purchase_order=purchase_order,
                )
            except PurchaseOrder.DoesNotExist:
                return GeneratePurchaseOrder(success=False, message="Bon de commande introuvable.")
        else:
            # Créer un nouvel purchase_order
            purchase_order = PurchaseOrder(creator=creator, generator=creator.get_employee_in_company())

        # Populate or update invoice fields from quote
        validity_end_date = datetime.now() + timedelta(days=30)
        if validity_end_date.weekday() == 5:
            validity_end_date += timedelta(days=2)
        elif validity_end_date.weekday() == 6:
            validity_end_date += timedelta(days=1)

        purchase_order_fields = {
            'expense': expense,
            'label': expense.label,
            'description':expense. description,
            'total_ttc': expense.total_amount,
            'order_date_time': datetime.now(),
            'validity_end_date': validity_end_date,
            'payment_method':expense.payment_method,
            'supplier': expense.supplier,
            'establishment': expense.establishment,
            'employee': expense.employee,
            'company': expense.company,
            'status': 'APPROVED',
        }

        for field, value in purchase_order_fields.items():
            setattr(purchase_order, field, value)
        purchase_order.save()

        purchase_order_items = []
        for expense_item in expense.expense_items.all():
            purchase_order_item = PurchaseOrderItem(
                purchase_order=purchase_order,
                description=expense_item.description,
                quantity=expense_item.quantity,
                amount_ttc=expense_item.amount,
            )
            purchase_order_items.append(purchase_order_item)
        PurchaseOrderItem.objects.bulk_create(purchase_order_items)
        return GeneratePurchaseOrder(
            success=True,
            message="Bon de commande créé avec succès.",
            purchase_order=purchase_order,
        )


# *************************************************************************#

class CreatePurchaseOrder(graphene.Mutation):
    class Arguments:
        purchase_order_data = PurchaseOrderInput(required=True)
        files = graphene.List(MediaInput, required=False)

    purchase_order = graphene.Field(PurchaseOrderType)

    def mutate(root, info, files=None, purchase_order_data=None):
        creator = info.context.user
        purchase_order_items = purchase_order_data.pop("purchase_order_items")
        purchase_order = PurchaseOrder(**purchase_order_data)
        purchase_order.creator = creator
        purchase_order.company = creator.the_current_company
        purchase_order.save()
        if not purchase_order.employee:
            purchase_order.employee = creator.get_employee_in_company()
            purchase_order.save()
        for item in purchase_order_items:
            purchase_order_item = PurchaseOrderItem(**item)
            purchase_order_item.purchase_order = purchase_order
            purchase_order_item.creator = creator
            purchase_order_item.save()
        return CreatePurchaseOrder(purchase_order=purchase_order)


class UpdatePurchaseOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        purchase_order_data = PurchaseOrderInput(required=True)
        files = graphene.List(MediaInput, required=False)

    purchase_order = graphene.Field(PurchaseOrderType)

    def mutate(root, info, id, files=None, purchase_order_data=None):
        creator = info.context.user
        try:
            purchase_order = PurchaseOrder.objects.get(pk=id, company=creator.the_current_company)
        except PurchaseOrder.DoesNotExist:
            raise e
        purchase_order_items = purchase_order_data.pop("purchase_order_items")
        PurchaseOrder.objects.filter(pk=id).update(**purchase_order_data)
        purchase_order.refresh_from_db()
        if not purchase_order.employee:
            purchase_order.employee = creator.get_employee_in_company()
            purchase_order.save()
        purchase_order_item_ids = [
            item.id for item in purchase_order_items if item.id is not None
        ]
        PurchaseOrderItem.objects.filter(
            purchase_order=purchase_order
        ).exclude(id__in=purchase_order_item_ids).delete()
        for item in purchase_order_items:
            if id in item or "id" in item:
                PurchaseOrderItem.objects.filter(pk=item.id).update(**item)
            else:
                purchase_order_item = PurchaseOrderItem(**item)
                purchase_order_item.purchase_order = purchase_order
                purchase_order_item.creator = creator
                purchase_order_item.save()
        return UpdatePurchaseOrder(purchase_order=purchase_order)


class UpdatePurchaseOrderState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    purchase_order = graphene.Field(PurchaseOrderType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, purchase_order_fields=None):
        creator = info.context.user
        try:
            purchase_order = PurchaseOrder.objects.get(pk=id, company=creator.the_current_company)
        except PurchaseOrder.DoesNotExist:
            raise e
        done = True
        success = True
        message = ""
        try:
            PurchaseOrder.objects.filter(pk=id).update(
                is_active=not purchase_order.is_active
            )
            purchase_order.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            purchase_order = None
            message = "Une erreur s'est produite."
        return UpdatePurchaseOrderState(
            done=done, success=success, message=message, purchase_order=purchase_order
        )

class UpdatePurchaseOrderFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        purchase_order_data = PurchaseOrderInput(required=True)

    purchase_order = graphene.Field(PurchaseOrderType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, purchase_order_data=None):
        creator = info.context.user
        try:
            purchase_order = PurchaseOrder.objects.get(pk=id, company=creator.the_current_company)
        except PurchaseOrder.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            PurchaseOrder.objects.filter(pk=id).update(**purchase_order_data)
            purchase_order.refresh_from_db()
        except Exception as e:
            print(e)
            done = False
            success = False
            purchase_order=None
            message = "Une erreur s'est produite."
        return UpdatePurchaseOrderFields(done=done, success=success, message=message, purchase_order=purchase_order)


class DeletePurchaseOrder(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    purchase_order = graphene.Field(PurchaseOrderType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        try:
            purchase_order = PurchaseOrder.objects.get(pk=id, company=current_user.the_current_company)
        except PurchaseOrder.DoesNotExist:
            raise e
        if current_user.is_superuser or purchase_order.creator==current_user:
            purchase_order = PurchaseOrder.objects.get(pk=id)
            purchase_order.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeletePurchaseOrder(
            deleted=deleted, success=success, message=message, id=id
        )


# *************************************************************************************************#
# *************************************************************************************************#

class CreateExpenseReport(graphene.Mutation):
    class Arguments:
        expense_report_data = ExpenseReportInput(required=True)
        files = graphene.List(MediaInput, required=False)

    expense_report = graphene.Field(ExpenseReportType)

    def mutate(root, info, files=None, expense_report_data=None):
        creator = info.context.user
        expense_report = ExpenseReport(**expense_report_data)
        expense_report.creator = creator
        expense_report.company = creator.the_current_company
        expense_report.save()
        folder = Folder.objects.create(name=str(expense_report.id)+'_'+expense_report.label,creator=creator)
        expense_report.folder = folder
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
                file_file.folder = expense_report.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            expense_report.files.add(file_file)
        expense_report.save()
        if not expense_report.employee:
            expense_report.employee = creator.get_employee_in_company()
            expense_report.save()
        if expense_report.status == 'PENDING':
            finance_managers = User.get_finance_managers_in_user_company(user=creator)
            for finance_manager in finance_managers:
                notify_expense_report(sender=creator, recipient=finance_manager, expense_report=expense_report, action='ADDED')
        return CreateExpenseReport(expense_report=expense_report)


class UpdateExpenseReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        expense_report_data = ExpenseReportInput(required=True)
        files = graphene.List(MediaInput, required=False)

    expense_report = graphene.Field(ExpenseReportType)

    def mutate(root, info, id, files=None, expense_report_data=None):
        creator = info.context.user
        try:
            expense_report = ExpenseReport.objects.get(pk=id, company=creator.the_current_company)
        except ExpenseReport.DoesNotExist:
            raise e
        ExpenseReport.objects.filter(pk=id).update(**expense_report_data)
        expense_report.refresh_from_db()
        if not expense_report.folder or expense_report.folder is None:
            folder = Folder.objects.create(name=str(expense_report.id)+'_'+expense_report.label,creator=creator)
            ExpenseReport.objects.filter(pk=id).update(folder=folder)
            expense_report.refresh_from_db()
        if not expense_report.employee:
            expense_report.employee = creator.get_employee_in_company()
            expense_report.save()
        if not files:
            files = []
        else:
            file_ids = [item.id for item in files if item.id is not None]
            File.objects.filter(file_expense_reports=expense_report).exclude(id__in=file_ids).delete()
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = expense_report.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            expense_report.files.add(file_file)
        expense_report.save()
        is_draft = True if expense_report.status == 'DRAFT' else False
        if is_draft:
            ExpenseReport.objects.filter(pk=id).update(status='PENDING')
            expense_report.refresh_from_db()
        notify_expense_report(sender=creator, recipient=expense_report.creator, expense_report=expense_report, action='UPDATED')
        return UpdateExpenseReport(expense_report=expense_report)


class UpdateExpenseReportState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    expense_report = graphene.Field(ExpenseReportType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, expense_report_fields=None):
        creator = info.context.user
        try:
            expense_report = ExpenseReport.objects.get(pk=id, company=creator.the_current_company)
        except ExpenseReport.DoesNotExist:
            raise e
        done = True
        success = True
        message = ""
        try:
            ExpenseReport.objects.filter(pk=id).update(
                is_active=not expense_report.is_active
            )
            expense_report.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            expense_report = None
            message = "Une erreur s'est produite."
        return UpdateExpenseReportState(
            done=done, success=success, message=message, expense_report=expense_report
        )

class UpdateExpenseReportFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        expense_report_data = ExpenseReportInput(required=True)

    expense_report = graphene.Field(ExpenseReportType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, expense_report_data=None):
        creator = info.context.user
        try:
            expense_report = ExpenseReport.objects.get(pk=id, company=creator.the_current_company)
        except ExpenseReport.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            ExpenseReport.objects.filter(pk=id).update(**expense_report_data)
            expense_report.refresh_from_db()
            if 'status' in expense_report_data:
                if creator.can_manage_finance() or creator.is_manager():
                    employee_user = expense_report.employee.user if expense_report.employee else expense_report.creator
                    if employee_user:
                        notify_expense_report(sender=creator, recipient=employee_user, expense_report=expense_report)
                else:
                    finance_managers = User.get_finance_managers_in_user_company(user=creator)
                    for finance_manager in finance_managers:
                        notify_expense_report(sender=creator, recipient=finance_manager, expense_report=expense_report)
                expense_report.refresh_from_db()
        except Exception as e:
            print(e)
            done = False
            success = False
            expense_report=None
            message = "Une erreur s'est produite."
        return UpdateExpenseReportFields(done=done, success=success, message=message, expense_report=expense_report)


class DeleteExpenseReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    expense_report = graphene.Field(ExpenseReportType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ""
        current_user = info.context.user
        try:
            expense_report = ExpenseReport.objects.get(pk=id, company=current_user.the_current_company)
        except ExpenseReport.DoesNotExist:
            raise e
        if current_user.is_superuser or expense_report.creator==current_user:
            expense_report = ExpenseReport.objects.get(pk=id)
            expense_report.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteExpenseReport(
            deleted=deleted, success=success, message=message, id=id
        )
# *************************************************************************#
# *************************************************************************#

class PurchasesMutation(graphene.ObjectType):
    create_supplier = CreateSupplier.Field()
    update_supplier = UpdateSupplier.Field()
    update_supplier_state = UpdateSupplierState.Field()
    delete_supplier = DeleteSupplier.Field()

    create_purchase_contract = CreatePurchaseContract.Field()
    update_purchase_contract = UpdatePurchaseContract.Field()
    update_purchase_contract_state = UpdatePurchaseContractState.Field()
    delete_purchase_contract = DeletePurchaseContract.Field()

    create_expense = CreateExpense.Field()
    update_expense = UpdateExpense.Field()
    update_expense_state = UpdateExpenseState.Field()
    update_expense_fields = UpdateExpenseFields.Field()
    delete_expense = DeleteExpense.Field()

    generate_purchase_order = GeneratePurchaseOrder.Field()

    create_purchase_order = CreatePurchaseOrder.Field()
    update_purchase_order = UpdatePurchaseOrder.Field()
    update_purchase_order_state = UpdatePurchaseOrderState.Field()
    update_purchase_order_fields = UpdatePurchaseOrderFields.Field()
    delete_purchase_order = DeletePurchaseOrder.Field()

    create_expense_report = CreateExpenseReport.Field()
    update_expense_report = UpdateExpenseReport.Field()
    update_expense_report_state = UpdateExpenseReportState.Field()
    update_expense_report_fields = UpdateExpenseReportFields.Field()
    delete_expense_report = DeleteExpenseReport.Field()