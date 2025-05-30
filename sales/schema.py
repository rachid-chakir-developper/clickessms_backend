import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.conf import settings

from django.db.models import Q
from datetime import datetime, timedelta

from sales.models import Client, Invoice, InvoiceEstablishment, InvoiceItem
from medias.models import Folder, File
from partnerships.models import Financier
from companies.models import Establishment

from sales.utils import calculate_amounts

class ClientType(DjangoObjectType):
    class Meta:
        model = Client
        fields = "__all__"
    monthText = graphene.String()
    cover_image = graphene.String()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)

class ClientNodeType(graphene.ObjectType):
    nodes = graphene.List(ClientType)
    total_count = graphene.Int()

class ClientFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class ClientInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    external_number = graphene.String(required=False)
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    client_type = graphene.String(required=True)
    manager_name = graphene.String(required=True)
    latitude = graphene.String(required=False)
    longitude = graphene.String(required=False)
    city = graphene.String(required=False)
    country = graphene.String(required=False)
    zip_code = graphene.String(required=False)
    address = graphene.String(required=False)
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
    description = graphene.String(required=False)
    observation = graphene.String(required=False)

class InvoiceEstablishmentType(DjangoObjectType):
    class Meta:
        model = InvoiceEstablishment
        fields = "__all__"

class InvoiceItemType(DjangoObjectType):
    class Meta:
        model = InvoiceItem
        fields = "__all__"

class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice
        fields = "__all__"
    month_text = graphene.String()
    def resolve_month_text( instance, info, **kwargs ):
        return instance.month_text

class InvoiceNodeType(graphene.ObjectType):
    nodes = graphene.List(InvoiceType)
    total_count = graphene.Int()

class InvoiceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    financiers = graphene.List(graphene.Int, required=False)
    statuses = graphene.List(graphene.String, required=False)
    establishments = graphene.List(graphene.Int, required=False)

class InvoiceItemInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    label = graphene.String(required=False)
    preferred_name = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    birth_date = graphene.DateTime(required=False)
    entry_date = graphene.DateTime(required=False)
    release_date = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    measurement_unit = graphene.String(required=False)
    unit_price = graphene.Decimal(required=False)
    quantity = graphene.Float(required=False)
    tva = graphene.Decimal(required=False)
    discount = graphene.Decimal(required=False)
    amount_ht = graphene.Decimal(required=False)
    amount_ttc = graphene.Decimal(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    invoice_establishment_id = graphene.Int(name="invoiceEstablishment", required=False)


class InvoiceEstablishmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    #********establishment*****************************************************
    establishment_number = graphene.String(required=False)
    establishment_name = graphene.String(required=False)
    establishment_siret = graphene.String(required=False)
    establishment_finess = graphene.String(required=False)
    establishment_ape_code = graphene.String(required=False)
    establishment_capacity = graphene.Float(required=False)
    establishment_unit_price = graphene.String(required=False)
    establishment_tva_number = graphene.String(required=False)
    establishment_infos = graphene.String(required=False)
    establishment_address = graphene.String(required=False)
    establishment_city = graphene.String(required=False)
    establishment_country = graphene.String(required=False)
    establishment_zip_code = graphene.String(required=False)
    establishment_mobile = graphene.String(required=False)
    establishment_fix = graphene.String(required=False)
    establishment_email = graphene.String(required=False)
    establishment_iban = graphene.String(required=False)
    establishment_bic = graphene.String(required=False)
    establishment_bank_name = graphene.String(required=False)

    #**************************************************************************
    comment = graphene.String(required=False)
    total_ht = graphene.Decimal(required=False)
    tva = graphene.Decimal(required=False)
    discount = graphene.Decimal(required=False)
    total_ttc = graphene.Decimal(required=False)
    payment_method = graphene.String(required=False)
    establishment_id = graphene.Int(name="establishment", required=False)
    invoice_items = graphene.List(InvoiceItemInput, required=False)

class InvoiceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    invoice_type = graphene.String(required=False)
    title = graphene.String(required=False)
    description = graphene.String(required=False)
    year = graphene.String(required=False)
    month = graphene.String(required=False)
    #********financier**********************************************************
    financier_infos = graphene.String(required=False)
    financier_number = graphene.String(required=False)
    financier_name = graphene.String(required=False)
    financier_tva_number = graphene.String(required=False)
    establishment_capacity = graphene.Float(required=False)
    establishment_unit_price = graphene.Decimal(required=False)
    financier_address = graphene.String(required=False)
    financier_city = graphene.String(required=False)
    financier_country = graphene.String(required=False)
    financier_zip_code = graphene.String(required=False)
    financier_mobile = graphene.String(required=False)
    financier_fix = graphene.String(required=False)
    financier_email = graphene.String(required=False)
    financier_iban = graphene.String(required=False)
    financier_bic = graphene.String(required=False)
    financier_bank_name = graphene.String(required=False)
    #****************************************************************************
    emission_date = graphene.DateTime(required=False)
    due_date = graphene.DateTime(required=False)
    payment_date = graphene.DateTime(required=False)
    comment = graphene.String(required=False)
    total_ht = graphene.Decimal(required=False)
    tva = graphene.Decimal(required=False)
    discount = graphene.Decimal(required=False)
    total_ttc = graphene.Decimal(required=False)
    payment_method = graphene.String(required=False)
    status = graphene.String(required=False)
    financier_id = graphene.Int(name="financier", required=False)
    invoice_establishments = graphene.List(InvoiceEstablishmentInput, required=False)

class GenerateInvoiceInput(graphene.InputObjectType):
    year = graphene.String(required=True)
    month = graphene.String(required=True)
    financier = graphene.Int(required=True)
    establishments = graphene.List(graphene.Int, required=False)

class SalesQuery(graphene.ObjectType):
    clients = graphene.Field(ClientNodeType, client_filter= ClientFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    client = graphene.Field(ClientType, id = graphene.ID())
    invoices = graphene.Field(
        InvoiceNodeType,
        invoice_filter=InvoiceFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    invoice = graphene.Field(InvoiceType, id=graphene.ID())

    def resolve_clients(root, info, client_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        clients = Client.objects.filter(company__id=id_company, is_deleted=False) if id_company else Client.objects.filter(company=company, is_deleted=False)
        if client_filter:
            keyword = client_filter.get('keyword', '')
            starting_date_time = client_filter.get('starting_date_time')
            ending_date_time = client_filter.get('ending_date_time')
            if keyword:
                clients = clients.filter(Q(name__icontains=keyword) | Q(manager_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                clients = clients.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                clients = clients.filter(created_at__lte=ending_date_time)
        clients = clients.order_by('-created_at')
        total_count = clients.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            clients = clients[offset:offset + limit]
        return ClientNodeType(nodes=clients, total_count=total_count)

    def resolve_client(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            client = Client.objects.get(pk=id, company=company)
        except Client.DoesNotExist:
            client = None
        return client

    def resolve_invoices(
        root, info, invoice_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        invoices = Invoice.objects.filter(company=company, is_deleted=False)
        if invoice_filter:
            keyword = invoice_filter.get("keyword", "")
            starting_date_time = invoice_filter.get("starting_date_time")
            ending_date_time = invoice_filter.get("ending_date_time")
            financiers = invoice_filter.get("financiers")
            statuses = invoice_filter.get("statuses")
            establishments = invoice_filter.get("establishments")
            if keyword:
                invoices = invoices.filter(
                    Q(title__icontains=keyword)
                    | Q(establishment__name__icontains=keyword)
                )
            if starting_date_time:
                invoices = invoices.filter(
                    emission_date__date__gte=starting_date_time.date()
                )
            if ending_date_time:
                invoices = invoices.filter(
                    emission_date__date__lte=ending_date_time.date()
                )
            if financiers:
                invoices = invoices.filter(financier__id__in=financiers)
            if establishments:
                invoices = invoices.filter(establishment__id__in=establishments)
            if statuses:
                invoices = invoices.filter(status__in=statuses)
        invoices = invoices.order_by("-created_at").distinct()
        total_count = invoices.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            invoices = invoices[offset : offset + limit]
        return InvoiceNodeType(
            nodes=invoices, total_count=total_count
        )

    def resolve_invoice(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            invoice = Invoice.objects.get(pk=id, company=company)
        except Invoice.DoesNotExist:
            invoice = None
        return invoice

class CreateClient(graphene.Mutation):
    class Arguments:
        client_data = ClientInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    client = graphene.Field(ClientType)

    def mutate(root, info, photo=None, cover_image=None,  client_data=None):
        creator = info.context.user
        client = Client(**client_data)
        client.creator = creator
        client.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = client.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                client.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = client.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                client.cover_image = cover_image_file
        client.save()
        folder = Folder.objects.create(name=str(client.id)+'_'+client.name,creator=creator)
        client.folder = folder
        client.save()
        return CreateClient(client=client)

class UpdateClient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        client_data = ClientInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    client = graphene.Field(ClientType)

    def mutate(root, info, id, photo=None, cover_image=None,  client_data=None):
        creator = info.context.user
        try:
            client = Client.objects.get(pk=id, company=creator.the_current_company)
        except Client.DoesNotExist:
            raise e
        Client.objects.filter(pk=id).update(**client_data)
        client.refresh_from_db()
        if not client.folder or client.folder is None:
            folder = Folder.objects.create(name=str(client.id)+'_'+client.name,creator=creator)
            Client.objects.filter(pk=id).update(folder=folder)
        if not photo and client.photo:
            photo_file = client.photo
            photo_file.delete()
        if not cover_image and client.cover_image:
            cover_image_file = client.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = client.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                client.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = client.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                client.cover_image = cover_image_file
            client.save()
        client = Client.objects.get(pk=id)
        return UpdateClient(client=client)

class UpdateClientState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    client = graphene.Field(ClientType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, client_fields=None):
        creator = info.context.user
        try:
            client = Client.objects.get(pk=id, company=creator.the_current_company)
        except Client.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            Client.objects.filter(pk=id).update(is_active=not client.is_active)
            client.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            client=None
            message = "Une erreur s'est produite."
        return UpdateClientState(done=done, success=success, message=message,client=client)

class DeleteClient(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    client = graphene.Field(ClientType)
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
            client = Client.objects.get(pk=id, company=current_user.the_current_company)
        except Client.DoesNotExist:
            raise e
        if current_user.is_superuser or client.creator==current_user:
            client = Client.objects.get(pk=id)
            client.delete()
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteClient(deleted=deleted, success=success, message=message, id=id)


#*************************************************************************#

# ************************************************************************


class CreateInvoice(graphene.Mutation):
    class Arguments:
        invoice_data = InvoiceInput(required=True)

    invoice = graphene.Field(InvoiceType)

    def mutate(root, info, invoice_data=None):
        creator = info.context.user
        invoice_items = invoice_data.pop("invoice_items")
        invoice = Invoice(**invoice_data)
        invoice.creator = creator
        invoice.company = creator.the_current_company
        invoice.save()
        if not invoice.employee:
            invoice.employee = creator.get_employee_in_company()
            invoice.save()
        for item in invoice_items:
            invoice_item = InvoiceItem(**item)
            invoice_item.invoice = invoice
            invoice_item.creator = creator
            invoice_item.save()
        return CreateInvoice(invoice=invoice)


class UpdateInvoice(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        invoice_data = InvoiceInput(required=True)
    invoice = graphene.Field(InvoiceType)

    def mutate(root, info, id, invoice_data=None):
        creator = info.context.user
        try:
            invoice = Invoice.objects.get(pk=id, company=creator.the_current_company)
        except Invoice.DoesNotExist:
            raise e
        invoice_establishments = invoice_data.pop("invoice_establishments", None)
        Invoice.objects.filter(pk=id).update(**invoice_data)
        invoice.refresh_from_db()
        if not invoice.employee:
            invoice.employee = creator.get_employee_in_company()
            invoice.save()

        if invoice_establishments is not None:
            invoice_establishment_ids = [
                item["id"] for item in invoice_establishments if "id" in item and item["id"] is not None
            ]

            # Supprime les établissements qui ne sont plus dans la liste
            InvoiceEstablishment.objects.filter(invoice=invoice).exclude(id__in=invoice_establishment_ids).delete()

            for item in invoice_establishments:
                invoice_items = item.pop("invoice_items", None)  # Récupère bien invoice_items à chaque itération
                
                if "id" in item and item["id"] is not None:
                    InvoiceEstablishment.objects.filter(pk=item["id"]).update(**item)
                    invoice_establishment = InvoiceEstablishment.objects.get(pk=item["id"])
                else:
                    invoice_establishment = InvoiceEstablishment.objects.create(
                        **item, invoice=invoice, creator=creator
                    )

                if invoice_items is not None:
                    invoice_item_ids = [
                        i_item["id"] for i_item in invoice_items if "id" in i_item and i_item["id"] is not None
                    ]

                    # Supprime les éléments non présents dans la liste
                    InvoiceItem.objects.filter(invoice_establishment=invoice_establishment).exclude(id__in=invoice_item_ids).delete()

                    for i_item in invoice_items:
                        if "id" in i_item and i_item["id"] is not None:
                            InvoiceItem.objects.filter(pk=i_item["id"]).update(**i_item)
                            invoice_item = InvoiceItem.objects.get(pk=i_item["id"])
                            invoice_item.update_totals()
                        else:
                            invoice_item = InvoiceItem.objects.create(
                                **i_item, invoice=invoice, invoice_establishment=invoice_establishment, creator=creator
                            )
        invoice = Invoice.objects.get(pk=id, company=creator.the_current_company)
        return UpdateInvoice(invoice=invoice)


class UpdateInvoiceFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        invoice_data = InvoiceInput(required=True)

    invoice = graphene.Field(InvoiceType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, invoice_data=None):
        creator = info.context.user
        try:
            invoice = Invoice.objects.get(pk=id, company=creator.the_current_company)
        except Invoice.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            for field, value in invoice_data.items():
                setattr(invoice, field, value)
            invoice.save()
            invoice.refresh_from_db()
            if 'status' in invoice_data:
                pass
        except Exception as e:
            done = False
            success = False
            invoice=None
            message = f"Une erreur s'est produite"
        return UpdateInvoiceFields(done=done, success=success, message=message, invoice=invoice)


class GenerateInvoice(graphene.Mutation):
    class Arguments:
        generate_invoice_data = GenerateInvoiceInput(required=True)

    invoice = graphene.Field(InvoiceType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, generate_invoice_data=None):
        creator = info.context.user
        company = creator.the_current_company
        year, month, financier_id, establishment_ids = map(
            lambda field: getattr(generate_invoice_data, field),
            ["year", "month", "financier", "establishments"],
        )
        invoice = None
        the_establishment=None
        the_parent_establishment=None
        children_establishments=[]
        managers = []
        try:
            try:
                establishments = Establishment.objects.filter(id__in=establishment_ids, company=creator.the_current_company, is_deleted=False)
                if not establishments:
                    return GenerateInvoice(invoice=invoice, success=False, message="Structures non trouvées.")
                establishment_parents = establishments.filter(establishment_parent__id=None)
                if establishment_parents:
                    for i, establishment_parent in enumerate(establishment_parents):
                        children_establishments += establishment_parent.get_all_children()
                    the_establishment=establishment_parents.first()
                    the_parent_establishment=the_establishment
                establishments = establishments | Establishment.objects.filter(id__in=[e.id for e in children_establishments])
                establishments = establishments.distinct()
                if not the_establishment:
                    the_establishment=establishments.first()
                financier = Financier.objects.get(pk=financier_id, company=creator.the_current_company)
            except Financier.DoesNotExist:
                return GenerateInvoice(invoice=invoice, success=False, message="Financeur non trouvé.")
            try:
                action_message = "mise à jour"
                invoice = Invoice.objects.get(establishment=the_establishment, financier=financier, year=year, month=month, status="DRAFT")
                # return GenerateInvoice(invoice=invoice, success=True, message=f"Facture {action_message} avec succée.")
            except Invoice.DoesNotExist:
                action_message = "créée"
                invoice = Invoice(creator=creator,
                        company=company,
                        establishment=the_establishment, financier=financier,
                        year=year,
                        month=month
                    )

            # Populate or update invoice fields from quote
            due_date = datetime.now() + timedelta(days=30)
            if due_date.weekday() == 5:
                due_date += timedelta(days=2)
            elif due_date.weekday() == 6:
                due_date += timedelta(days=1)

            the_capacity = the_establishment.get_monthly_capacity(year, month)
            the_unit_price = the_establishment.get_monthly_unit_price(year, month)
            # Construction de establishment_infos avec des retours à la ligne
            the_establishment_infos = "\n".join(filter(None, [
                the_establishment.address,  # Adresse principale
                the_establishment.additional_address,  # Complément d'adresse (si présent)
                f"{the_establishment.zip_code} {the_establishment.city}",  # Code postal + ville
                the_establishment.country,  # Pays
                f"{the_establishment.fix}" if the_establishment.fix else None,  # Téléphone fixe
                f"{the_establishment.mobile}" if the_establishment.mobile else None,  # Mobile
                f"{the_establishment.email}" if the_establishment.email else None,  # Email
            ]))

            company_infos = "\n".join(filter(None, [
                company.address,  # Adresse principale
                company.additional_address,  # Complément d'adresse (si présent)
                f"{company.zip_code} {company.city}",  # Code postal + ville
                company.country,  # Pays
                f"{company.fix}" if company.fix else None,  # Téléphone fixe
                f"{company.mobile}" if company.mobile else None,  # Mobile
                f"{company.email}" if company.email else None,  # Email
            ]))
            financier_infos = "\n".join(filter(None, [
                financier.address,  # Adresse principale
                financier.additional_address,  # Complément d'adresse (si présent)
                f"{financier.zip_code} {financier.city}",  # Code postal + ville
                financier.country,  # Pays
                f"{financier.fix}" if financier.fix else None,  # Téléphone fixe
                f"{financier.mobile}" if financier.mobile else None,  # Mobile
                f"{financier.email}" if financier.email else None,  # Email
            ]))
            invoice_fields = {
                'title': f"Facture du {int(month):02d}/{year}  pour {the_establishment.name}",
                'description': f"Facture du {int(month):02d}/{year}  pour {the_establishment.name}",

                'establishment_number': the_establishment.number,
                'establishment_name': the_establishment.name,
                'establishment_siret': the_establishment.siret,
                'establishment_finess': the_establishment.finess,
                'establishment_ape_code': the_establishment.ape_code,
                'establishment_capacity': the_capacity,
                'establishment_unit_price': the_unit_price,
                'establishment_tva_number': '',
                'establishment_infos': the_establishment_infos,
                'establishment_address': the_establishment.address,
                'establishment_city': the_establishment.city,
                'establishment_country': the_establishment.country,
                'establishment_zip_code': the_establishment.zip_code,
                'establishment_mobile': the_establishment.mobile,
                'establishment_fix': the_establishment.fix,
                'establishment_email': the_establishment.email,
                'establishment_iban': the_establishment.iban,
                'establishment_bic': the_establishment.bic,
                'establishment_bank_name': the_establishment.bank_name,

                'financier_number': financier.number,
                'financier_name': financier.name,
                'financier_tva_number': '',
                'financier_infos': financier_infos,
                'financier_address': financier.address,
                'financier_city': financier.city,
                'financier_country': financier.country,
                'financier_zip_code': financier.zip_code,
                'financier_mobile': financier.mobile,
                'financier_fix': financier.fix,
                'financier_email': financier.email,
                'financier_iban': financier.iban,
                'financier_bic': financier.bic,
                'financier_bank_name': financier.bank_name,

                'company_number': company.number,
                'company_name': company.name,
                'company_siret': company.siret,
                'company_finess': company.finess,
                'company_ape_code': company.ape_code,
                'company_approval_number': company.approval_number,
                'company_tva_number': '',
                'company_infos': company_infos,
                'company_address': company.address,
                'company_city': company.city,
                'company_country': company.country,
                'company_zip_code': company.zip_code,
                'company_mobile': company.mobile,
                'company_fix': company.fix,
                'company_email': company.email,
                'company_bank_code': company.bank_code,
                'company_branch_code': company.branch_code,
                'company_account_number': company.account_number,
                'company_rib_key': company.rib_key,
                'company_iban': company.iban,
                'company_bic': company.bic,
                'company_bank_name': company.bank_name,

                'emission_date': datetime.now(),
                'due_date': due_date,
                'employee': creator.get_employee_in_company(),
            }

            for field, value in invoice_fields.items():
                setattr(invoice, field, value)

            # Save the invoice to update changes
            invoice.save()
            for establishment in establishments:
                if establishment!=the_parent_establishment:
                    capacity = establishment.get_monthly_capacity(year, month)
                    unit_price = establishment.get_monthly_unit_price(year, month)
                    # Construction de establishment_infos avec des retours à la ligne
                    establishment_infos = "\n".join(filter(None, [
                        establishment.address,  # Adresse principale
                        establishment.additional_address,  # Complément d'adresse (si présent)
                        f"{establishment.zip_code} {establishment.city}",  # Code postal + ville
                        establishment.country,  # Pays
                        f"{establishment.fix}" if establishment.fix else None,  # Téléphone fixe
                        f"{establishment.mobile}" if establishment.mobile else None,  # Mobile
                        f"{establishment.email}" if establishment.email else None,  # Email
                    ]))

                    invoice_establishment = InvoiceEstablishment(
                        invoice=invoice,
                        establishment=establishment,
                        establishment_number=establishment.number,
                        establishment_name=establishment.name,
                        establishment_siret=establishment.siret,
                        establishment_finess=establishment.finess,
                        establishment_ape_code=establishment.ape_code,
                        establishment_capacity=capacity,
                        establishment_unit_price=unit_price,
                        establishment_tva_number='',
                        establishment_infos=establishment_infos,
                        establishment_address=establishment.address,
                        establishment_city=establishment.city,
                        establishment_country=establishment.country,
                        establishment_zip_code=establishment.zip_code,
                        establishment_mobile=establishment.mobile,
                        establishment_fix=establishment.fix,
                        establishment_email=establishment.email,
                        establishment_iban=establishment.iban,
                        establishment_bic=establishment.bic,
                        establishment_bank_name=establishment.bank_name,
                        creator=creator
                    )

                    # Save the invoice_establishment to update changes
                    invoice_establishment.save()

                    for manager in establishment.managers.all():
                        if manager.employee:
                            managers.append(manager.employee)

                    present_beneficiaries = establishment.get_present_beneficiaries(year, month, financiers=[financier])
                    present_beneficiaries = sorted(present_beneficiaries, key=lambda item: (item['beneficiary_entry'].beneficiary.id, item['beneficiary_entry'].beneficiary.first_name, item['beneficiary_entry'].beneficiary.last_name))
                    # Créer les éléments de facture à partir des bénéficiaires présents
                    invoice_items = []
                    for item in present_beneficiaries:
                        release_date = item['beneficiary_entry'].release_date
                        if release_date and release_date.year == int(year) and release_date.month == int(month):
                            release_date = release_date
                        else:
                            release_date = None
                        try:
                            invoice_item = InvoiceItem.objects.get(invoice=invoice, invoice_establishment__establishment=item['establishment'], entry_date=item['beneficiary_entry'].entry_date)
                        except InvoiceItem.DoesNotExist:
                            amount_ht, amount_ttc = calculate_amounts(unit_price=unit_price, quantity=item['days_in_month'], tva=0, discount=0)
                            invoice_item = InvoiceItem(
                                    invoice=invoice,
                                    invoice_establishment=invoice_establishment,
                                    label=f"Bénéficiaire : {item['beneficiary_entry'].beneficiary.preferred_name}",
                                    preferred_name=item['beneficiary_entry'].beneficiary.preferred_name,
                                    first_name=item['beneficiary_entry'].beneficiary.first_name,
                                    last_name=item['beneficiary_entry'].beneficiary.last_name,
                                    birth_date=item['beneficiary_entry'].beneficiary.birth_date,
                                    entry_date=item['beneficiary_entry'].entry_date,
                                    release_date=release_date,
                                    description=f"{item['days_in_month']} jour(s) dans le mois {month}/{year}",
                                    measurement_unit=establishment.measurement_activity_unit,
                                    unit_price=unit_price,
                                    quantity=item['days_in_month'],  # Utiliser le nombre de jours comme quantité
                                    amount_ht=amount_ht,  # Calcul automatique si nécessaire
                                    amount_ttc=amount_ttc,  # Calcul automatique si nécessaire
                                    beneficiary=item['beneficiary_entry'].beneficiary,
                                    creator=creator
                                )
                            invoice_items.append(invoice_item)
                        except Exception as e:
                            return GenerateInvoice(invoice=None, success=False, message=f"Erreur lors de la création des éléments de facture : {str(e)}")

                    # Bulk creation des éléments de facture
                    try:
                        InvoiceItem.objects.bulk_create(invoice_items)
                    except Exception as e:
                        return GenerateInvoice(invoice=None, success=False, message=f"Erreur lors de la création des éléments de facture : {str(e)}")

                    invoice_establishment.update_totals()

            # Update invoice totals after adding all items
            if managers:
                invoice.managers.set(managers)
                invoice.set_signatures(employees=managers, creator=creator)
            invoice.update_totals()
            return GenerateInvoice(invoice=invoice, success=True, message=f"Facture {action_message} avec succée.")

        except Exception as e:
            return GenerateInvoice(invoice=None, success=False, message=f"Une erreur s'est produite : {str(e)}")


class DeleteInvoice(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    invoice = graphene.Field(InvoiceType)
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
            invoice = Invoice.objects.get(pk=id, company=current_user.the_current_company)
        except Invoice.DoesNotExist as e:
            raise e
        if (current_user.is_superuser or current_user.can_manage_finance() or invoice.creator==current_user) and invoice.status=="DRAFT":
            if invoice.status == 'DRAFT':
                invoice.delete()
                deleted = True
                success = True
            else:
                message = "La facture ne peut pas être supprimée."
        else:
            message = "Vous n'avez pas les droits nécessaires pour effectuer cette action."
        return DeleteInvoice(
            deleted=deleted, success=success, message=message, id=id
        )

#******************************************************************************************************************
#************************************************************************
class SalesMutation(graphene.ObjectType):
    create_client = CreateClient.Field()
    update_client = UpdateClient.Field()
    update_client_state = UpdateClientState.Field()
    delete_client = DeleteClient.Field()

    generate_invoice = GenerateInvoice.Field()

    create_invoice = CreateInvoice.Field()
    update_invoice = UpdateInvoice.Field()
    update_invoice_fields = UpdateInvoiceFields.Field()
    delete_invoice = DeleteInvoice.Field()