import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q, Subquery, OuterRef

from human_ressources.models import CareerEntry, Employee, EmployeeGroup, EmployeeGroupItem, EmployeeContract,EmployeeContractMission, EmployeeContractEstablishment, EmployeeContractReplacedEmployee, Beneficiary, BeneficiaryAdmissionDocument, BeneficiaryStatusEntry, BeneficiaryEndowmentEntry, BeneficiaryEntry, BeneficiaryAdmission, BeneficiaryGroup, BeneficiaryGroupItem, Advance
from medias.models import Folder, File, DocumentRecord
from data_management.models import EmployeeMission, AddressBookEntry
from companies.models import Establishment
from accounts.models import User
from medias.schema import MediaInput, DocumentRecordInput

from data_management.schema import CustomFieldValueInput
from data_management.utils import CustomFieldEntityBase

from notifications.notificator import notify_beneficiary_admission
from django.utils import timezone

class AdvanceType(DjangoObjectType):
    class Meta:
        model = Advance
        fields = "__all__"

class PageInfoType(graphene.ObjectType):
    hasNextPage = graphene.Boolean()
    hasPreviousPage = graphene.Boolean()

class AdvanceNodeType(graphene.ObjectType):
    nodes = graphene.List(AdvanceType)
    total_count = graphene.Int()
    page_info = graphene.Field(PageInfoType)

class AdvanceFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    status = graphene.String(required=False)
    employee_id = graphene.ID(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class AdvanceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    amount = graphene.Decimal(required=True)
    month = graphene.Date(required=True)
    reason = graphene.String(required=False)
    status = graphene.String(required=False)
    comments = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=True)
    validated_by_id = graphene.Int(name="validatedBy", required=False)

class CreateAdvance(graphene.Mutation):
    class Arguments:
        amount = graphene.Decimal(required=True)
        month = graphene.Date(required=True)
        reason = graphene.String(required=False)
        employee_id = graphene.ID(required=True)
        
    advance = graphene.Field(AdvanceType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, amount, month, employee_id, reason=None):
        user = info.context.user
        success = False
        message = ""
        advance = None
        
        if not user.is_authenticated:
            message = "Vous devez être connecté pour créer un acompte."
            return CreateAdvance(advance=advance, success=success, message=message)
            
        try:
            employee = Employee.objects.get(pk=employee_id)
            
            # Si l'utilisateur n'est pas admin ou RH, vérifier qu'il est l'employé concerné
            if not user.is_staff and not user.is_superuser:
                try:
                    user_employee = Employee.objects.get(user=user)
                    if user_employee.id != employee.id:
                        message = "Vous ne pouvez créer un acompte que pour vous-même."
                        return CreateAdvance(advance=advance, success=success, message=message)
                except Employee.DoesNotExist:
                    message = "Votre profil employé n'existe pas."
                    return CreateAdvance(advance=advance, success=success, message=message)
            
            # Créer l'acompte
            advance = Advance.objects.create(
                amount=amount,
                month=month,
                reason=reason,
                employee=employee,
                creator=user,
                company=employee.company
            )
            
            success = True
            message = "Acompte créé avec succès."
            return CreateAdvance(advance=advance, success=success, message=message)
            
        except Employee.DoesNotExist:
            message = "L'employé spécifié n'existe pas."
            return CreateAdvance(advance=advance, success=success, message=message)
        except Exception as e:
            message = f"Une erreur est survenue lors de la création de l'acompte: {str(e)}"
            return CreateAdvance(advance=advance, success=success, message=message)

class UpdateAdvance(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        advance_data = AdvanceInput(required=True)

    advance = graphene.Field(AdvanceType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, advance_data=None):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateAdvance(advance=None, success=False, message="Vous devez être connecté pour effectuer cette action.")
            
        try:
            # Récupérer l'acompte
            advance = Advance.objects.get(pk=id, is_deleted=False)
            
            # Vérifier les permissions
            is_admin_or_hr = user.is_staff or user.is_superuser
            
            if not is_admin_or_hr:
                try:
                    employee = Employee.objects.get(user=user)
                    if advance.employee != employee:
                        return UpdateAdvance(advance=None, success=False, message="Vous ne pouvez pas modifier une demande d'acompte qui ne vous appartient pas.")
                    
                    
                    # Les employés ne peuvent modifier que les demandes en attente
                    if advance.status != "PENDING":
                        return UpdateAdvance(advance=None, success=False, message="Vous ne pouvez pas modifier une demande d'acompte qui a déjà été traitée.")
                        
                    # Les employés ne peuvent pas changer le statut
                    if advance_data.status and advance_data.status != advance.status:
                        return UpdateAdvance(advance=None, success=False, message="Vous n'avez pas la permission de changer le statut de la demande.")
                except Employee.DoesNotExist:
                    return UpdateAdvance(advance=None, success=False, message="Vous n'êtes pas un employé enregistré dans le système.")
            
            # Mise à jour des champs
            if advance_data.amount:
                advance.amount = advance_data.amount
            if advance_data.month:
                advance.month = advance_data.month
            if advance_data.reason is not None:
                advance.reason = advance_data.reason
                
            # Seuls les admin/RH peuvent faire ces modifications
            if is_admin_or_hr:
                if advance_data.status:
                    advance.status = advance_data.status
                if advance_data.comments is not None:
                    advance.comments = advance_data.comments
                if advance_data.validated_by:
                    advance.validated_by_id = advance_data.validated_by
                    advance.validation_date = timezone.now()
            
            advance.save()
            
            return UpdateAdvance(advance=advance, success=True, message="Demande d'acompte mise à jour avec succès.")
        except Advance.DoesNotExist:
            return UpdateAdvance(advance=None, success=False, message="Demande d'acompte introuvable.")
        except Exception as e:
            return UpdateAdvance(advance=None, success=False, message=f"Une erreur est survenue: {str(e)}")

class ValidateAdvance(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        status = graphene.String(required=True)
        comments = graphene.String(required=False)

    advance = graphene.Field(AdvanceType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, status, comments=None):
        user = info.context.user
        if not user.is_authenticated:
            return ValidateAdvance(advance=None, success=False, message="Vous devez être connecté pour effectuer cette action.")
            
        # Vérifier que l'utilisateur est un administrateur ou RH
        if not user.is_staff and not user.is_superuser:
            return ValidateAdvance(advance=None, success=False, message="Vous n'avez pas la permission de valider des demandes d'acompte.")
            
        try:
            # Récupérer l'acompte
            advance = Advance.objects.get(pk=id, is_deleted=False)
            
            # Vérifier que le statut est valide
            if status not in ["PENDING", "APPROVED", "REJECTED", "MODIFIED"]:
                return ValidateAdvance(advance=None, success=False, message="Statut non valide.")
                
            # Mise à jour des champs
            advance.status = status
            if comments is not None:
                advance.comments = comments
                
            # Enregistrer la validation
            try:
                validator = Employee.objects.get(user=user)
                advance.validated_by = validator
            except Employee.DoesNotExist:
                pass
                
            advance.validation_date = timezone.now()
            advance.save()
            
            return ValidateAdvance(advance=advance, success=True, message="Demande d'acompte validée avec succès.")
        except Advance.DoesNotExist:
            return ValidateAdvance(advance=None, success=False, message="Demande d'acompte introuvable.")
        except Exception as e:
            return ValidateAdvance(advance=None, success=False, message=f"Une erreur est survenue: {str(e)}")

class DeleteAdvance(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    advance = graphene.Field(AdvanceType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message="Vous devez être connecté pour effectuer cette action.")
            
        try:
            # Récupérer l'acompte
            advance = Advance.objects.get(pk=id, is_deleted=False)
            
            # Vérifier les permissions
            is_admin_or_hr = user.is_staff or user.is_superuser
            
            if not is_admin_or_hr:
                try:
                    employee = Employee.objects.get(user=user)
                    if advance.employee != employee:
                        return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message="Vous ne pouvez pas supprimer une demande d'acompte qui ne vous appartient pas.")
                    
                    # Les employés ne peuvent supprimer que les demandes en attente
                    if advance.status != "PENDING":
                        return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message="Vous ne pouvez pas supprimer une demande d'acompte qui a déjà été traitée.")
                except Employee.DoesNotExist:
                    return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message="Vous n'êtes pas un employé enregistré dans le système.")
            
            # Marquer comme supprimé
            advance.is_deleted = True
            advance.save()
            
            return DeleteAdvance(advance=advance, id=id, deleted=True, success=True, message="Demande d'acompte supprimée avec succès.")
        except Advance.DoesNotExist:
            return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message="Demande d'acompte introuvable.")
        except Exception as e:
            return DeleteAdvance(advance=None, id=id, deleted=False, success=False, message=f"Une erreur est survenue: {str(e)}")

# Définition des types de base pour la pagination
class PageInfoType(graphene.ObjectType):
    hasNextPage = graphene.Boolean()
    hasPreviousPage = graphene.Boolean()

# Définition des types pour Advance

class AddressBookEntryType(DjangoObjectType):
    class Meta:
        model = AddressBookEntry
        fields = "__all__"

class CareerEntryType(DjangoObjectType):
    class Meta:
        model = CareerEntry
        fields = "__all__"

class EmployeeContractEstablishmentType(DjangoObjectType):
    class Meta:
        model = EmployeeContractEstablishment
        fields = "__all__"

class EmployeeContractMissionType(DjangoObjectType):
    class Meta:
        model = EmployeeContractMission
        fields = "__all__"

class EmployeeContractReplacedEmployeeType(DjangoObjectType):
    class Meta:
        model = EmployeeContractReplacedEmployee
        fields = "__all__"

class EmployeeLeaveDayInfosType(graphene.ObjectType):
    rest_paid_leave_days = graphene.Float()
    acquired_paid_leave_days_by_month = graphene.Decimal()
    acquired_paid_leave_days = graphene.Decimal()
    being_acquired_paid_leave_days = graphene.Decimal()
    reported_paid_leave_days_per_year = graphene.JSONString()
    total_reported_paid_leave_days = graphene.Decimal()
    rest_rwt_leave_days = graphene.Float()
    rest_temporary_leave_days = graphene.Float()

class EmployeeContractType(DjangoObjectType):
    class Meta:
        model = EmployeeContract
        fields = "__all__"
    document = graphene.String()
    leave_day_infos = graphene.Field(EmployeeLeaveDayInfosType)
    def resolve_document( instance, info, **kwargs ):
        return instance.document and info.context.build_absolute_uri(instance.document.file.url)
    def resolve_leave_day_infos( instance, info, **kwargs ):
        return EmployeeLeaveDayInfosType(
            rest_paid_leave_days=instance.rest_paid_leave_days,
            acquired_paid_leave_days_by_month=instance.acquired_paid_leave_days_by_month,
            acquired_paid_leave_days=instance.acquired_paid_leave_days,
            being_acquired_paid_leave_days=instance.being_acquired_paid_leave_days,
            reported_paid_leave_days_per_year=instance.get_reported_paid_leave_days_per_year(),
            total_reported_paid_leave_days=instance.total_reported_paid_leave_days,
            rest_rwt_leave_days=instance.rest_rwt_leave_days,
            rest_temporary_leave_days=instance.rest_temporary_leave_days,
            )

class EmployeeContractNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeContractType)
    total_count = graphene.Int()

class EmployeeContractFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    employees = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class EmployeeType(DjangoObjectType):
    class Meta:
        model = Employee
        fields = "__all__"
    first_name = graphene.String()
    last_name = graphene.String()
    photo = graphene.String()
    cover_image = graphene.String()
    signature = graphene.String()
    current_contract = graphene.Field(EmployeeContractType)
    sce_roles = graphene.List(graphene.String)
    def resolve_first_name( instance, info, **kwargs ):
        return instance.first_name and instance.first_name.capitalize()
    def resolve_last_name( instance, info, **kwargs ):
        return instance.last_name and instance.last_name.upper()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)
    def resolve_signature( instance, info, **kwargs ):
        return instance.signature and info.context.build_absolute_uri(instance.signature.image.url)
    def resolve_current_contract( instance, info, **kwargs ):
        return instance.current_contract
    def resolve_sce_roles( instance, info, **kwargs ):
        return instance.sce_roles

class EmployeeNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeType)
    total_count = graphene.Int()

class EmployeeFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class EmployeeGroupItemType(DjangoObjectType):
    class Meta:
        model = EmployeeGroupItem
        fields = "__all__"

class EmployeeGroupType(DjangoObjectType):
    class Meta:
        model = EmployeeGroup
        fields = "__all__"
    image = graphene.String()
    employees = graphene.List(EmployeeGroupItemType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_employees( instance, info, **kwargs ):
        return instance.employee_group_items.all()

class EmployeeGroupNodeType(graphene.ObjectType):
    nodes = graphene.List(EmployeeGroupType)
    total_count = graphene.Int()

class EmployeeGroupFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class BeneficiaryAdmissionDocumentType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAdmissionDocument
        fields = "__all__"
    document = graphene.String()
    def resolve_document( instance, info, **kwargs ):
        return instance.document and info.context.build_absolute_uri(instance.document.file.url)

class BeneficiaryStatusEntryType(DjangoObjectType):
    class Meta:
        model = BeneficiaryStatusEntry
        fields = "__all__"
    document = graphene.String()
    def resolve_document( instance, info, **kwargs ):
        return instance.document and info.context.build_absolute_uri(instance.document.file.url)

class BeneficiaryEndowmentEntryType(DjangoObjectType):
    class Meta:
        model = BeneficiaryEndowmentEntry
        fields = "__all__"

class BeneficiaryEntryType(DjangoObjectType):
    class Meta:
        model = BeneficiaryEntry
        fields = "__all__"

class BeneficiaryType(DjangoObjectType):
    class Meta:
        model = Beneficiary
        fields = "__all__"
    first_name = graphene.String()
    preferred_name = graphene.String()
    last_name = graphene.String()
    photo = graphene.String()
    cover_image = graphene.String()
    age = graphene.Float()
    balance_details = graphene.JSONString()
    balance = graphene.Float()
    total_expenses = graphene.Float()
    total_payments = graphene.Float()
    def resolve_first_name( instance, info, **kwargs ):
        return instance.first_name and instance.first_name.capitalize()
    def resolve_preferred_name( instance, info, **kwargs ):
        return instance.preferred_name and instance.preferred_name.upper()
    def resolve_last_name( instance, info, **kwargs ):
        return instance.last_name and instance.last_name.upper()
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)
    def resolve_age( instance, info, **kwargs ):
        return instance.age
    def resolve_balance_details( instance, info, **kwargs ):
        return instance.balance_details
    def resolve_balance( instance, info, **kwargs ):
        return instance.balance
    def resolve_total_expenses( instance, info, **kwargs ):
        return instance.total_expenses
    def resolve_total_payments( instance, info, **kwargs ):
        return instance.total_payments

class BeneficiaryNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryType)
    total_count = graphene.Int()

class BeneficiaryFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class BeneficiaryGroupItemType(DjangoObjectType):
    class Meta:
        model = BeneficiaryGroupItem
        fields = "__all__"

class BeneficiaryGroupType(DjangoObjectType):
    class Meta:
        model = BeneficiaryGroup
        fields = "__all__"
    image = graphene.String()
    beneficiaries = graphene.List(BeneficiaryGroupItemType)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_beneficiaries( instance, info, **kwargs ):
        return instance.beneficiary_group_items.all()

class BeneficiaryGroupNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryGroupType)
    total_count = graphene.Int()

class BeneficiaryGroupFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class CareerEntryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    career_type = graphene.String(required=False)
    institution = graphene.String(required=False)
    title = graphene.String(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    email = graphene.String(required=False)
    full_address = graphene.String(required=False)
    description = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    professional_status_id = graphene.Int(name="professionalStatus", required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)


class AddressBookEntryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    title = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    full_address = graphene.String(required=False)
    description = graphene.String(required=False)
    mobile = graphene.String(required=False)
    fix = graphene.String(required=False)
    fax = graphene.String(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)

class EmployeeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    registration_number = graphene.String(required=False)
    first_name = graphene.String(required=False)
    preferred_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    social_security_number = graphene.String(required=False)
    birth_date = graphene.DateTime(required=False)
    birth_place = graphene.String(required=False)
    nationality = graphene.String(required=False)
    hiring_date = graphene.DateTime(required=False)
    probation_end_date = graphene.DateTime(required=False)
    work_end_date = graphene.DateTime(required=False)
    starting_salary = graphene.Float(required=False)
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
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    gender = graphene.String(required=False)

class EmployeeGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    employees = graphene.List(graphene.Int, required=False)

class EmployeeContractReplacedEmployeeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    position = graphene.String(required=False)
    reason = graphene.String(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)

class EmployeeContractInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    title = graphene.String(required=True)
    position = graphene.String(required=False)
    monthly_gross_salary = graphene.Decimal(required=False)
    salary = graphene.Decimal(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    started_at = graphene.DateTime(required=False)
    ended_at = graphene.DateTime(required=False)
    initial_paid_leave_days = graphene.Decimal(required=False)
    initial_rwt_days = graphene.Decimal(required=False)
    initial_temporary_days = graphene.Decimal(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    missions = graphene.List(graphene.Int, required=False)
    establishments = graphene.List(graphene.Int, required=False)
    contract_type = graphene.String(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    replaced_employees = graphene.List(EmployeeContractReplacedEmployeeInput, required=False)

class BeneficiaryAdmissionDocumentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    document = Upload(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    admission_document_type_id = graphene.Int(name="admissionDocumentType", required=False)
    financier_id = graphene.Int(name="financier", required=False)

class BeneficiaryStatusEntryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    document = Upload(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    beneficiary_status_id = graphene.Int(name="beneficiaryStatus", required=False)

class BeneficiaryEndowmentEntryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    initial_balance = graphene.Decimal(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    endowment_type_id = graphene.Int(name="endowmentType", required=False)

class BeneficiaryEntryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    entry_date = graphene.DateTime(required=False)
    due_date = graphene.DateTime(required=False)
    release_date = graphene.DateTime(required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    establishments = graphene.List(graphene.Int, required=False)
    internal_referents = graphene.List(graphene.Int, required=False)

class BeneficiaryInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=True)
    preferred_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    birth_date = graphene.DateTime(required=False)
    birth_address = graphene.String(required=False)
    birth_city = graphene.String(required=False)
    birth_country = graphene.String(required=False)
    nationality = graphene.String(required=False)
    admission_date = graphene.DateTime(required=False)
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
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    iban = graphene.String(required=False)
    bic = graphene.String(required=False)
    bank_name = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    gender = graphene.String(required=False)
    professional_status_id = graphene.Int(name="professionalStatus", required=False)
    beneficiary_admission_documents = graphene.List(BeneficiaryAdmissionDocumentInput, required=False)
    beneficiary_status_entries = graphene.List(BeneficiaryStatusEntryInput, required=False)
    beneficiary_endowment_entries = graphene.List(BeneficiaryEndowmentEntryInput, required=False)
    beneficiary_entries = graphene.List(BeneficiaryEntryInput, required=False)
    address_book_entries = graphene.List(AddressBookEntryInput, required=False)
    career_entries = graphene.List(CareerEntryInput, required=False)
    document_records = graphene.List(DocumentRecordInput, required=False)

class BeneficiaryAdmissionType(DjangoObjectType):
    class Meta:
        model = BeneficiaryAdmission
        fields = "__all__"
    age = graphene.Float()
    def resolve_age( instance, info, **kwargs ):
        return instance.age

class BeneficiaryAdmissionNodeType(graphene.ObjectType):
    nodes = graphene.List(BeneficiaryAdmissionType)
    total_count = graphene.Int()

class BeneficiaryAdmissionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    statuses = graphene.List(graphene.String, required=False)
    list_type = graphene.String(required=False)
    order_by = graphene.String(required=False)

class BeneficiaryAdmissionFieldInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    status = graphene.String(required=False)
    response_date = graphene.DateTime(required=False)
    status_reason = graphene.String(required=False)

class BeneficiaryAdmissionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    pre_admission_date = graphene.DateTime(required=False)
    reception_date = graphene.DateTime(required=False)
    first_name = graphene.String(required=True)
    preferred_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    email = graphene.String(required=False)
    birth_date = graphene.DateTime(required=False)
    birth_address = graphene.String(required=False)
    birth_city = graphene.String(required=False)
    birth_country = graphene.String(required=False)
    nationality = graphene.String(required=False)
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
    web_site = graphene.String(required=False)
    other_contacts = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    gender = graphene.String(required=False)
    status = graphene.String(required=False)
    response_date = graphene.DateTime(required=False)
    status_reason = graphene.String(required=False)
    professional_status_id = graphene.Int(name="professionalStatus", required=False)
    beneficiary_id = graphene.Int(name="beneficiary", required=False)
    financier_id = graphene.Int(name="financier", required=False)
    employee_id = graphene.Int(name="employee", required=False)
    establishments = graphene.List(graphene.Int, required=False)

class BeneficiaryGroupInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=True)
    is_active = graphene.Boolean(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    beneficiaries = graphene.List(graphene.Int, required=False)

class HumanRessourcesQuery(graphene.ObjectType):
    employees = graphene.Field(EmployeeNodeType, employee_filter= EmployeeFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee = graphene.Field(EmployeeType, id = graphene.ID())
    employee_contracts = graphene.Field(EmployeeContractNodeType, employee_contract_filter= EmployeeContractFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee_contract = graphene.Field(EmployeeContractType, id = graphene.ID())
    employee_groups = graphene.Field(EmployeeGroupNodeType, employee_group_filter= EmployeeGroupFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    employee_group = graphene.Field(EmployeeGroupType, id = graphene.ID())
    beneficiaries = graphene.Field(BeneficiaryNodeType, beneficiary_filter= BeneficiaryFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary = graphene.Field(BeneficiaryType, id = graphene.ID())
    beneficiary_admissions = graphene.Field(
        BeneficiaryAdmissionNodeType,
        beneficiary_admission_filter=BeneficiaryAdmissionFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType, id=graphene.ID())
    beneficiary_groups = graphene.Field(BeneficiaryGroupNodeType, beneficiary_group_filter= BeneficiaryGroupFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    beneficiary_group = graphene.Field(BeneficiaryGroupType, id = graphene.ID())
    
    # Ces champs fonctionnent maintenant car AdvanceNodeType est défini au début du fichier
    advances = graphene.Field(
        AdvanceNodeType,
        advance_filter=AdvanceFilterInput(required=False),
        offset=graphene.Int(required=False),
        limit=graphene.Int(required=False),
        page=graphene.Int(required=False),
    )
    advance = graphene.Field(AdvanceType, id=graphene.ID())

    def resolve_employees(root, info, employee_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        employees = Employee.objects.filter(company__id=id_company, is_deleted=False) if id_company else Employee.objects.filter(company=company, is_deleted=False)
        # if not user.can_manage_administration():
        #     if user.is_manager():
        #         employees = employees.filter(Q(employee_contracts__establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
        #     else:
        #         employees = employees.filter(creator=user)
        the_order_by = '-created_at'
        if employee_filter:
            keyword = employee_filter.get('keyword', '')
            starting_date_time = employee_filter.get('starting_date_time')
            ending_date_time = employee_filter.get('ending_date_time')
            establishments = employee_filter.get('establishments')
            order_by = employee_filter.get('order_by')
            if keyword:
                employees = employees.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(preferred_name__icontains=keyword) | Q(email__icontains=keyword) | Q(registration_number__icontains=keyword))
            if establishments:
                employees = employees.filter(employee_contracts__establishments__establishment__id__in=establishments)
            if starting_date_time:
                employees = employees.filter(created_at__date__gte=starting_date_time.date())
            if ending_date_time:
                employees = employees.filter(created_at__date__lte=ending_date_time.date())
            if order_by:
                the_order_by = order_by
        employees = employees.order_by(the_order_by).distinct()
        total_count = employees.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employees = employees[offset:offset + limit]
        return EmployeeNodeType(nodes=employees, total_count=total_count)

    def resolve_employee(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee = Employee.objects.get(pk=id)
        except Employee.DoesNotExist:
            employee = None
        return employee

    def resolve_employee_contracts(root, info, employee_contract_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        employee_contracts = EmployeeContract.objects.filter(employee__company=company, is_deleted=False)
        if not user.can_manage_administration():
            if user.is_manager():
                employee_contracts = employee_contracts.filter(Q(establishments__establishment__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                employee_contracts = employee_contracts.filter(creator=user)
        the_order_by = '-created_at'
        if employee_contract_filter:
            keyword = employee_contract_filter.get('keyword', '')
            starting_date_time = employee_contract_filter.get('starting_date_time')
            ending_date_time = employee_contract_filter.get('ending_date_time')
            employees = employee_contract_filter.get('employees')
            order_by = employee_contract_filter.get('order_by')
            if employees:
                employee_contracts = employee_contracts.filter(employee__id__in=employees)
            if keyword:
                employee_contracts = employee_contracts.filter(Q(title__icontains=keyword))
            if starting_date_time:
                employee_contracts = employee_contracts.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                employee_contracts = employee_contracts.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        employee_contracts = employee_contracts.order_by(the_order_by).distinct()
        total_count = employee_contracts.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employee_contracts = employee_contracts[offset:offset + limit]
        return EmployeeContractNodeType(nodes=employee_contracts, total_count=total_count)

    def resolve_employee_contract(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee_contract = EmployeeContract.objects.get(pk=id)
        except EmployeeContract.DoesNotExist:
            employee_contract = None
        return employee_contract

    def resolve_employee_groups(root, info, employee_group_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        employee_groups = EmployeeGroup.objects.filter(company=company, is_deleted=False)
        if employee_group_filter:
            keyword = employee_group_filter.get('keyword', '')
            starting_date_time = employee_group_filter.get('starting_date_time')
            ending_date_time = employee_group_filter.get('ending_date_time')
            if keyword:
                employee_groups = employee_groups.filter(Q(title__icontains=keyword))
            if starting_date_time:
                employee_groups = employee_groups.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                employee_groups = employee_groups.filter(created_at__lte=ending_date_time)
        employee_groups = employee_groups.order_by('-created_at').distinct()
        total_count = employee_groups.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            employee_groups = employee_groups[offset:offset + limit]
        return EmployeeGroupNodeType(nodes=employee_groups, total_count=total_count)

    def resolve_employee_group(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            employee_group = EmployeeGroup.objects.get(pk=id)
        except EmployeeGroup.DoesNotExist:
            employee_group = None
        return employee_group

    def resolve_beneficiaries(root, info, beneficiary_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        beneficiaries = Beneficiary.objects.filter(company__id=id_company, is_deleted=False) if id_company else Beneficiary.objects.filter(company=company, is_deleted=False)
        # if not user.can_manage_administration():
        #     if user.is_manager():
        #         beneficiaries = beneficiaries.filter(Q(beneficiary_entries__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
        #     else:
        #         beneficiaries = beneficiaries.filter(creator=user)
        the_order_by = '-created_at'
        if beneficiary_filter:
            keyword = beneficiary_filter.get('keyword', '')
            starting_date_time = beneficiary_filter.get('starting_date_time')
            ending_date_time = beneficiary_filter.get('ending_date_time')
            establishments = beneficiary_filter.get('establishments')
            list_type = beneficiary_filter.get('list_type') # OUT / ALL
            order_by = beneficiary_filter.get('order_by')
            if list_type:
                if list_type == 'OUT':
                    today = timezone.now().date()
                    beneficiaries = beneficiaries.filter(beneficiary_entries__release_date__lt=today)
            if keyword:
                beneficiaries = beneficiaries.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(preferred_name__icontains=keyword) | Q(email__icontains=keyword))
            if starting_date_time:
                beneficiaries = beneficiaries.filter(beneficiary_entries__entry_date__gte=starting_date_time)
            if ending_date_time:
                beneficiaries = beneficiaries.filter(beneficiary_entries__entry_date__lte=ending_date_time)
            if establishments:
                last_entry_subquery = BeneficiaryEntry.objects.filter(
                    beneficiary=OuterRef('pk')
                ).order_by('-entry_date').values('id')[:1]
                beneficiaries = beneficiaries.filter(
                    beneficiary_entries__id=Subquery(last_entry_subquery),
                    beneficiary_entries__establishments__id__in=establishments
                )
            if order_by:
                the_order_by = order_by
        beneficiaries = beneficiaries.order_by(the_order_by).distinct()
        total_count = beneficiaries.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiaries = beneficiaries[offset:offset + limit]
        return BeneficiaryNodeType(nodes=beneficiaries, total_count=total_count)

    def resolve_beneficiary(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            beneficiary = Beneficiary.objects.get(pk=id)
        except Beneficiary.DoesNotExist:
            beneficiary = None
        return beneficiary
    def resolve_beneficiary_admissions(
        root, info, beneficiary_admission_filter=None, offset=None, limit=None, page=None
    ):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        beneficiary_admissions = BeneficiaryAdmission.objects.filter(company=company)
        if not user.can_manage_activity():
            if user.is_manager():
                beneficiary_admissions = beneficiary_admissions.filter(Q(establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                beneficiary_admissions = beneficiary_admissions.filter(creator=user)
        the_order_by = '-created_at'
        if beneficiary_admission_filter:
            keyword = beneficiary_admission_filter.get("keyword", "")
            starting_date_time = beneficiary_admission_filter.get("starting_date_time")
            ending_date_time = beneficiary_admission_filter.get("ending_date_time")
            establishments = beneficiary_admission_filter.get('establishments')
            statuses = beneficiary_admission_filter.get('statuses')
            list_type = beneficiary_admission_filter.get('list_type') # ALL_BENEFICIARY_ADMISSION_REQUESTS / MY_BENEFICIARY_ADMISSIONS / MY_BENEFICIARY_ADMISSION_REQUESTS / ALL
            order_by = beneficiary_admission_filter.get('order_by')
            if establishments:
                beneficiary_admissions = beneficiary_admissions.filter(establishment__id__in=establishments)
            if list_type:
                if list_type == 'MY_BENEFICIARY_ADMISSIONS':
                    beneficiary_admissions = beneficiary_admissions.filter(creator=user)
                elif list_type == 'MY_BENEFICIARY_ADMISSION_REQUESTS':
                    beneficiary_admissions = beneficiary_admissions.filter(creator=user)
                elif list_type == 'ALL':
                    pass
            if keyword:
                beneficiary_admissions = beneficiary_admissions.filter(
                    Q(name__icontains=keyword)
                )
            if starting_date_time:
                beneficiary_admissions = beneficiary_admissions.filter(starting_date__gte=starting_date_time)
            if ending_date_time:
                beneficiary_admissions = beneficiary_admissions.filter(starting_date__lte=ending_date_time)
            if statuses:
                beneficiary_admissions = beneficiary_admissions.filter(status__in=statuses)
            if order_by:
                the_order_by = order_by
        beneficiary_admissions = beneficiary_admissions.order_by(the_order_by).distinct()
        total_count = beneficiary_admissions.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiary_admissions = beneficiary_admissions[offset : offset + limit]
        return BeneficiaryAdmissionNodeType(nodes=beneficiary_admissions, total_count=total_count)

    def resolve_beneficiary_admission(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            beneficiary_admission = BeneficiaryAdmission.objects.get(pk=id)
        except BeneficiaryAdmission.DoesNotExist:
            beneficiary_admission = None
        return beneficiary_admission

    def resolve_beneficiary_groups(root, info, beneficiary_group_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        beneficiary_groups = BeneficiaryGroup.objects.filter(company=company, is_deleted=False)
        if beneficiary_group_filter:
            keyword = beneficiary_group_filter.get('keyword', '')
            starting_date_time = beneficiary_group_filter.get('starting_date_time')
            ending_date_time = beneficiary_group_filter.get('ending_date_time')
            if keyword:
                beneficiary_groups = beneficiary_groups.filter(Q(title__icontains=keyword))
            if starting_date_time:
                beneficiary_groups = beneficiary_groups.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                beneficiary_groups = beneficiary_groups.filter(created_at__lte=ending_date_time)
        beneficiary_groups = beneficiary_groups.order_by('-created_at').distinct()
        total_count = beneficiary_groups.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            beneficiary_groups = beneficiary_groups[offset:offset + limit]
        return BeneficiaryGroupNodeType(nodes=beneficiary_groups, total_count=total_count)

    def resolve_beneficiary_group(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        if not user.is_authenticated:
            return None
        try:
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
            return beneficiary_group
        except BeneficiaryGroup.DoesNotExist:
            return None

    def resolve_advances(root, info, advance_filter=None, offset=None, limit=None, page=None):
        # Filtrage et pagination des acomptes
        user = info.context.user
        if not user.is_authenticated:
            return AdvanceNodeType(nodes=[], total_count=0, page_info=PageInfoType(hasNextPage=False, hasPreviousPage=False))

        # Base query - exclure les soft-deleted
        qs = Advance.objects.filter(is_deleted=False)
        
        # Filtres
        if advance_filter:
            # Filtrer par mot-clé (recherche dans numéro, raison, commentaires)
            if advance_filter.keyword:
                keyword = advance_filter.keyword
                qs = qs.filter(
                    Q(number__icontains=keyword) | 
                    Q(reason__icontains=keyword) | 
                    Q(comments__icontains=keyword)
                )
                
            # Filtrer par statut
            if advance_filter.status:
                qs = qs.filter(status=advance_filter.status)
                
            # Filtrer par employé
            if advance_filter.employee_id:
                qs = qs.filter(employee_id=advance_filter.employee_id)
        
        # Si pas admin ou RH, montrer uniquement les acomptes de l'employé connecté
        if not user.is_staff and not user.is_superuser:
            try:
                employee = Employee.objects.get(user=user)
                qs = qs.filter(employee=employee)
            except Employee.DoesNotExist:
                return AdvanceNodeType(nodes=[], total_count=0, page_info=PageInfoType(hasNextPage=False, hasPreviousPage=False))
        
        # Pagination
        total_count = qs.count()
        
        if page and limit:
            start = (page - 1) * limit
            end = page * limit
            has_next_page = total_count > end
            has_previous_page = page > 1
            qs = qs[start:end]
        else:
            has_next_page = False
            has_previous_page = False
            
        # Retour
        return AdvanceNodeType(
            nodes=qs,
            total_count=total_count,
            page_info=PageInfoType(
                hasNextPage=has_next_page,
                hasPreviousPage=has_previous_page
            )
        )
        
    def resolve_advance(root, info, id):
        # Vérifier l'authentification
        user = info.context.user
        if not user.is_authenticated:
            return None
            
        try:
            advance = Advance.objects.get(pk=id, is_deleted=False)
            
            # Si l'utilisateur n'est pas admin ou RH, vérifier qu'il est propriétaire de la demande
            if not user.is_staff and not user.is_superuser:
                try:
                    employee = Employee.objects.get(user=user)
                    if advance.employee != employee:
                        return None
                except Employee.DoesNotExist:
                    return None
                    
            return advance
        except Advance.DoesNotExist:
            return None

class CreateEmployee(graphene.Mutation):
    class Arguments:
        employee_data = EmployeeInput(required=True)

    employee = graphene.Field(EmployeeType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, employee_data=None):
        creator = info.context.user
        employee = Employee(**employee_data)
        employee.creator = creator
        employee.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = employee.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                employee.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = employee.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                employee.cover_image = cover_image_file
            if signature and isinstance(signature, UploadedFile):
                signature_file = employee.signature
                if not signature_file:
                    signature_file = File()
                    signature_file.creator = creator
                signature_file.image = signature
                signature_file.save()
                employee.signature = signature_file
        employee.save()
        folder = Folder.objects.create(name=str(employee.id)+'_'+employee.first_name+'-'+employee.last_name,creator=creator)
        employee.folder = folder
        employee.save()
        return CreateEmployee(employee=employee)

class UpdateEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_data = EmployeeInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)
        signature = Upload(required=False)

    employee = graphene.Field(EmployeeType)

    def mutate(root, info, id, photo=None, cover_image=None, signature=None,  employee_data=None):
        creator = info.context.user
        Employee.objects.filter(pk=id).update(**employee_data)
        employee = Employee.objects.get(pk=id)
        if not employee.folder or employee.folder is None:
            folder = Folder.objects.create(name=str(employee.id)+'_'+employee.first_name+'-'+employee.last_name,creator=creator)
            Employee.objects.filter(pk=id).update(folder=folder)
        if not photo and employee.photo:
            photo_file = employee.photo
            photo_file.delete()
        if not cover_image and employee.cover_image:
            cover_image_file = employee.cover_image
            cover_image_file.delete()
        if not signature and employee.signature:
            signature_file = employee.signature
            signature_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = employee.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                employee.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = employee.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                employee.cover_image = cover_image_file
            if signature and isinstance(signature, UploadedFile):
                signature_file = employee.signature
                if not signature_file:
                    signature_file = File()
                    signature_file.creator = creator
                signature_file.image = signature
                signature_file.save()
                employee.signature = signature_file
            employee.save()
        employee = Employee.objects.get(pk=id)
        return UpdateEmployee(employee=employee)

class UpdateEmployeeState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee = graphene.Field(EmployeeType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, employee_fields=None):
        creator = info.context.user
        done = True
        success = True
        employee = None
        message = ''
        try:
            employee = Employee.objects.get(pk=id)
            Employee.objects.filter(pk=id).update(is_active=not employee.is_active)
            employee.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            employee=None
            message = "Une erreur s'est produite."
        return UpdateEmployeeState(done=done, success=success, message=message,employee=employee)

class DeleteEmployee(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee = graphene.Field(EmployeeType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        employee = Employee.objects.get(pk=id)
        if current_user.can_manage_administration() or current_user.is_manager() or (employee.creator == current_user):
            # employee = Employee.objects.get(pk=id)
            # employee.delete()
            Employee.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteEmployee(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

#**************************************************************************************************************

class CreateEmployeeContract(graphene.Mutation):
    class Arguments:
        employee_contract_data = EmployeeContractInput(required=True)
        document = Upload(required=False)

    employee_contract = graphene.Field(EmployeeContractType)

    def mutate(root, info, document=None, employee_contract_data=None):
        creator = info.context.user
        mission_ids = employee_contract_data.pop("missions")
        establishment_ids = employee_contract_data.pop("establishments")
        replaced_employees = employee_contract_data.pop("replaced_employees")
        employee_contract = EmployeeContract(**employee_contract_data)
        employee_contract.creator = creator
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = employee_contract.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                employee_contract.document = document_file
        employee_contract.save()
        folder = Folder.objects.create(name=str(employee_contract.id)+'_'+employee_contract.title,creator=creator)
        employee_contract.folder = folder
        
        missions = EmployeeMission.objects.filter(id__in=mission_ids)
        for mission in missions:
            try:
                employee_contract_mission = EmployeeContractMission.objects.get(mission__id=mission.id, employee_contract__id=employee_contract.id)
            except EmployeeContractMission.DoesNotExist:
                EmployeeContractMission.objects.create(
                        employee_contract=employee_contract,
                        mission=mission,
                        creator=creator
                    )
        
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                employee_contract_establishment = EmployeeContractEstablishment.objects.get(establishment__id=establishment.id, employee_contract__id=employee_contract.id)
            except EmployeeContractEstablishment.DoesNotExist:
                EmployeeContractEstablishment.objects.create(
                        employee_contract=employee_contract,
                        establishment=establishment,
                        creator=creator
                    )

        for item in replaced_employees:
            replaced_employee = EmployeeContractReplacedEmployee(**item)
            replaced_employee.employee_contract = employee_contract
            replaced_employee.save()


        employee_contract.save()
        return CreateEmployeeContract(employee_contract=employee_contract)

class UpdateEmployeeContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_contract_data = EmployeeContractInput(required=True)
        document = Upload(required=False)

    employee_contract = graphene.Field(EmployeeContractType)

    def mutate(root, info, id, document=None, employee_contract_data=None):
        creator = info.context.user
        mission_ids = employee_contract_data.pop("missions")
        establishment_ids = employee_contract_data.pop("establishments")
        replaced_employees = employee_contract_data.pop("replaced_employees")
        EmployeeContract.objects.filter(pk=id).update(**employee_contract_data)
        employee_contract = EmployeeContract.objects.get(pk=id)
        if not employee_contract.folder or employee_contract.folder is None:
            folder = Folder.objects.create(name=str(employee_contract.id)+'_'+employee_contract.title,creator=creator)
            EmployeeContract.objects.filter(pk=id).update(folder=folder)
        if not document and employee_contract.document:
            document_file = employee_contract.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = employee_contract.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                employee_contract.document = document_file
            employee_contract.save()

        EmployeeContractMission.objects.filter(employee_contract=employee_contract).exclude(mission__id__in=mission_ids).delete()
        missions = EmployeeMission.objects.filter(id__in=mission_ids)
        for mission in missions:
            try:
                employee_contract_mission = EmployeeContractMission.objects.get(mission__id=mission.id, employee_contract__id=employee_contract.id)
            except EmployeeContractMission.DoesNotExist:
                EmployeeContractMission.objects.create(
                        employee_contract=employee_contract,
                        mission=mission,
                        creator=creator
                    )

        EmployeeContractEstablishment.objects.filter(employee_contract=employee_contract).exclude(establishment__id__in=establishment_ids).delete()
        establishments = Establishment.objects.filter(id__in=establishment_ids)
        for establishment in establishments:
            try:
                employee_contract_establishment = EmployeeContractEstablishment.objects.get(establishment__id=establishment.id, employee_contract__id=employee_contract.id)
            except EmployeeContractEstablishment.DoesNotExist:
                EmployeeContractEstablishment.objects.create(
                        employee_contract=employee_contract,
                        establishment=establishment,
                        creator=creator
                    )
        replaced_employee_ids = [item.id for item in replaced_employees if item.id is not None]
        EmployeeContractReplacedEmployee.objects.filter(employee_contract=employee_contract).exclude(id__in=replaced_employee_ids).delete()
        for item in replaced_employees:
            if id in item or 'id' in item:
                EmployeeContractReplacedEmployee.objects.filter(pk=item.id).update(**item)
            else:
                replaced_employee = EmployeeContractReplacedEmployee(**item)
                replaced_employee.employee_contract = employee_contract
                replaced_employee.save()
        return UpdateEmployeeContract(employee_contract=employee_contract)

class DeleteEmployeeContract(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_contract = graphene.Field(EmployeeContractType)
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
            employee_contract = EmployeeContract.objects.get(pk=id)
            employee_contract.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEmployeeContract(deleted=deleted, success=success, message=message, id=id)

#***********************************************************************************************

class CreateEmployeeGroup(graphene.Mutation):
    class Arguments:
        employee_group_data = EmployeeGroupInput(required=True)
        image = Upload(required=False)

    employee_group = graphene.Field(EmployeeGroupType)

    def mutate(root, info, image=None, employee_group_data=None):
        creator = info.context.user
        employee_ids = employee_group_data.pop("employees")
        employee_group = EmployeeGroup(**employee_group_data)
        employee_group.creator = creator
        employee_group.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = employee_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                employee_group.image = image_file
        employee_group.save()
        folder = Folder.objects.create(name=str(employee_group.id)+'_'+employee_group.name,creator=creator)
        employee_group.folder = folder
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_group_item = EmployeeGroupItem.objects.get(employee__id=employee.id, employee_group__id=employee_group.id)
            except EmployeeGroupItem.DoesNotExist:
                EmployeeGroupItem.objects.create(
                        employee_group=employee_group,
                        employee=employee,
                        creator=creator
                    )
        employee_group.save()
        return CreateEmployeeGroup(employee_group=employee_group)

class UpdateEmployeeGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        employee_group_data = EmployeeGroupInput(required=True)
        image = Upload(required=False)

    employee_group = graphene.Field(EmployeeGroupType)

    def mutate(root, info, id, image=None, employee_group_data=None):
        creator = info.context.user
        employee_ids = employee_group_data.pop("employees")
        EmployeeGroup.objects.filter(pk=id).update(**employee_group_data)
        employee_group = EmployeeGroup.objects.get(pk=id)
        if not employee_group.folder or employee_group.folder is None:
            folder = Folder.objects.create(name=str(employee_group.id)+'_'+employee_group.name,creator=creator)
            EmployeeGroup.objects.filter(pk=id).update(folder=folder)
        if not image and employee_group.image:
            image_file = employee_group.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = employee_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                employee_group.image = image_file
            employee_group.save()
        EmployeeGroupItem.objects.filter(employee_group=employee_group).exclude(employee__id__in=employee_ids).delete()
        employees = Employee.objects.filter(id__in=employee_ids)
        for employee in employees:
            try:
                employee_group_item = EmployeeGroupItem.objects.get(employee__id=employee.id, employee_group__id=employee_group.id)
            except EmployeeGroupItem.DoesNotExist:
                EmployeeGroupItem.objects.create(
                        employee_group=employee_group,
                        employee=employee,
                        creator=creator
                    )
        return UpdateEmployeeGroup(employee_group=employee_group)

class UpdateEmployeeGroupState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_group = graphene.Field(EmployeeGroupType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, employee_group_fields=None):
        creator = info.context.user
        done = True
        success = True
        employee_group = None
        message = ''
        try:
            employee_group = EmployeeGroup.objects.get(pk=id)
            EmployeeGroup.objects.filter(pk=id).update(is_active=not employee_group.is_active)
            employee_group.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            employee_group=None
            message = "Une erreur s'est produite."
        return UpdateEmployeeGroupState(done=done, success=success, message=message,employee_group=employee_group)


class DeleteEmployeeGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    employee_group = graphene.Field(EmployeeGroupType)
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
            employee_group = EmployeeGroup.objects.get(pk=id)
            employee_group.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteEmployeeGroup(deleted=deleted, success=success, message=message, id=id)

#************************************************************************
#********************************************************************************************************

class CreateBeneficiary(graphene.Mutation):
    class Arguments:
        beneficiary_data = BeneficiaryInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    beneficiary = graphene.Field(BeneficiaryType)

    def mutate(root, info, photo=None, cover_image=None,  beneficiary_data=None):
        creator = info.context.user
        beneficiary_admission_documents = beneficiary_data.pop("beneficiary_admission_documents", None)
        beneficiary_status_entries = beneficiary_data.pop("beneficiary_status_entries", None)
        beneficiary_entries = beneficiary_data.pop("beneficiary_entries", None)
        beneficiary_endowment_entries = beneficiary_data.pop("beneficiary_endowment_entries", None)
        address_book_entries = beneficiary_data.pop("address_book_entries", None)
        career_entries = beneficiary_data.pop("career_entries", None)
        document_records = beneficiary_data.pop("document_records", None)
        
        beneficiary = Beneficiary(**beneficiary_data)
        beneficiary.creator = creator
        beneficiary.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = beneficiary.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                beneficiary.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = beneficiary.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                beneficiary.cover_image = cover_image_file
        beneficiary.save()
        folder = Folder.objects.create(name=str(beneficiary.id)+'_'+beneficiary.first_name+'-'+beneficiary.last_name,creator=creator)
        beneficiary.folder = folder
        beneficiary.save()
        for item in beneficiary_admission_documents:
            document = item.pop("document") if "document" in item else None
            beneficiary_admission_document = BeneficiaryAdmissionDocument(**item)
            beneficiary_admission_document.beneficiary = beneficiary
            if document and isinstance(document, UploadedFile):
                document_file = beneficiary_admission_document.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                beneficiary_admission_document.document = document_file
            beneficiary_admission_document.save()
        for item in beneficiary_status_entries:
            document = item.pop("document") if "document" in item else None
            beneficiary_status_entry = BeneficiaryStatusEntry(**item)
            beneficiary_status_entry.beneficiary = beneficiary
            if document and isinstance(document, UploadedFile):
                document_file = beneficiary_status_entry.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                beneficiary_status_entry.document = document_file
            beneficiary_status_entry.save()
        for item in beneficiary_entries:
            establishment_ids = item.pop("establishments")
            internal_referent_ids = item.pop("internal_referents")
            beneficiary_entry = BeneficiaryEntry(**item)
            beneficiary_entry.beneficiary = beneficiary
            beneficiary_entry.save()
            beneficiary_entry.establishments.set(establishment_ids)
            beneficiary_entry.internal_referents.set(internal_referent_ids)
        for item in beneficiary_endowment_entries:
            beneficiary_endowment_entry = BeneficiaryEndowmentEntry(**item)
            beneficiary_endowment_entry.beneficiary = beneficiary
            beneficiary_endowment_entry.save()
        for item in address_book_entries:
            address_book_entry = AddressBookEntry(**item)
            address_book_entry.creator = creator
            address_book_entry.company = creator.the_current_company
            address_book_entry.beneficiary = beneficiary
            address_book_entry.save()
        for item in career_entries:
            career_entry = CareerEntry(**item)
            career_entry.creator = creator
            career_entry.company = creator.the_current_company
            career_entry.beneficiary = beneficiary
            career_entry.save()
        for item in document_records:
            document = item.pop("document", None)
            document_record = DocumentRecord(**item)
            document_record.creator = creator
            document_record.company = creator.the_current_company
            document_record.beneficiary = beneficiary
            if document and isinstance(document, UploadedFile):
                document_file = document_record.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                document_record.document = document_file
            document_record.save()
        return CreateBeneficiary(beneficiary=beneficiary)

class UpdateBeneficiary(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_data = BeneficiaryInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    beneficiary = graphene.Field(BeneficiaryType)

    def mutate(root, info, id, photo=None, cover_image=None,  beneficiary_data=None):
        creator = info.context.user
        beneficiary_admission_documents = beneficiary_data.pop("beneficiary_admission_documents", None)
        beneficiary_status_entries = beneficiary_data.pop("beneficiary_status_entries", None)
        beneficiary_entries = beneficiary_data.pop("beneficiary_entries", None)
        beneficiary_endowment_entries = beneficiary_data.pop("beneficiary_endowment_entries", None)
        address_book_entries = beneficiary_data.pop("address_book_entries", None)
        career_entries = beneficiary_data.pop("career_entries", None)
        document_records = beneficiary_data.pop("document_records", None)
        
        Beneficiary.objects.filter(pk=id).update(**beneficiary_data)
        beneficiary = Beneficiary.objects.get(pk=id)
        if not beneficiary.folder or beneficiary.folder is None:
            folder = Folder.objects.create(name=str(beneficiary.id)+'_'+beneficiary.first_name+'-'+beneficiary.last_name,creator=creator)
            Beneficiary.objects.filter(pk=id).update(folder=folder)
        if not photo and beneficiary.photo:
            photo_file = beneficiary.photo
            photo_file.delete()
        if not cover_image and beneficiary.cover_image:
            cover_image_file = beneficiary.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = beneficiary.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                beneficiary.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = beneficiary.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                beneficiary.cover_image = cover_image_file
            beneficiary.save()
        beneficiary = Beneficiary.objects.get(pk=id)
        beneficiary_admission_document_ids = [item.id for item in beneficiary_admission_documents if item.id is not None]
        BeneficiaryAdmissionDocument.objects.filter(beneficiary=beneficiary).exclude(id__in=beneficiary_admission_document_ids).delete()
        for item in beneficiary_admission_documents:
            document = item.pop("document") if "document" in item else None
            if id in item or 'id' in item:
                BeneficiaryAdmissionDocument.objects.filter(pk=item.id).update(**item)
                beneficiary_admission_document = BeneficiaryAdmissionDocument.objects.get(pk=item.id)
            else:
                beneficiary_admission_document = BeneficiaryAdmissionDocument(**item)
                beneficiary_admission_document.beneficiary = beneficiary
                beneficiary_admission_document.save()
            if not document and beneficiary_admission_document.document:
                document_file = beneficiary_admission_document.document
                document_file.delete()
            if document and isinstance(document, UploadedFile):
                document_file = beneficiary_admission_document.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                beneficiary_admission_document.document = document_file
                beneficiary_admission_document.save()
        beneficiary_status_entry_ids = [item.id for item in beneficiary_status_entries if item.id is not None]
        BeneficiaryStatusEntry.objects.filter(beneficiary=beneficiary).exclude(id__in=beneficiary_status_entry_ids).delete()
        for item in beneficiary_status_entries:
            document = item.pop("document") if "document" in item else None
            if id in item or 'id' in item:
                BeneficiaryStatusEntry.objects.filter(pk=item.id).update(**item)
                beneficiary_status_entry = BeneficiaryStatusEntry.objects.get(pk=item.id)
            else:
                beneficiary_status_entry = BeneficiaryStatusEntry(**item)
                beneficiary_status_entry.beneficiary = beneficiary
                beneficiary_status_entry.save()
            if not document and beneficiary_status_entry.document:
                document_file = beneficiary_status_entry.document
                document_file.delete()
            if document and isinstance(document, UploadedFile):
                document_file = beneficiary_status_entry.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                beneficiary_status_entry.document = document_file
                beneficiary_status_entry.save()
        beneficiary_entry_ids = [item.id for item in beneficiary_entries if item.id is not None]
        BeneficiaryEntry.objects.filter(beneficiary=beneficiary).exclude(id__in=beneficiary_entry_ids).delete()
        for item in beneficiary_entries:
            establishment_ids = item.pop("establishments")
            internal_referent_ids = item.pop("internal_referents")
            if id in item or 'id' in item:
                BeneficiaryEntry.objects.filter(pk=item.id).update(**item)
                beneficiary_entry = BeneficiaryEntry.objects.get(pk=item.id)
            else:
                beneficiary_entry = BeneficiaryEntry(**item)
                beneficiary_entry.beneficiary = beneficiary
                beneficiary_entry.save()
            beneficiary_entry.establishments.set(establishment_ids)
            beneficiary_entry.internal_referents.set(internal_referent_ids)
            
        beneficiary_endowment_entry_ids = [item.id for item in beneficiary_endowment_entries if item.id is not None]
        BeneficiaryEndowmentEntry.objects.filter(beneficiary=beneficiary).exclude(id__in=beneficiary_endowment_entry_ids).delete()
        for item in beneficiary_endowment_entries:
            if id in item or 'id' in item:
                BeneficiaryEndowmentEntry.objects.filter(pk=item.id).update(**item)
                beneficiary_endowment_entry = BeneficiaryEndowmentEntry.objects.get(pk=item.id)
            else:
                beneficiary_endowment_entry = BeneficiaryEndowmentEntry(**item)
                beneficiary_endowment_entry.beneficiary = beneficiary
                beneficiary_endowment_entry.save()
            
        address_book_entry_ids = [item.id for item in address_book_entries if item.id is not None]
        AddressBookEntry.objects.filter(beneficiary=beneficiary).exclude(id__in=address_book_entry_ids).delete()
        for item in address_book_entries:
            if id in item or 'id' in item:
                AddressBookEntry.objects.filter(pk=item.id).update(**item)
                address_book_entry = AddressBookEntry.objects.get(pk=item.id)
            else:
                address_book_entry = AddressBookEntry(**item)
                address_book_entry.creator = creator
                address_book_entry.company = creator.the_current_company
                address_book_entry.beneficiary = beneficiary
                address_book_entry.save()
            
        career_entry_ids = [item.id for item in career_entries if item.id is not None]
        CareerEntry.objects.filter(beneficiary=beneficiary).exclude(id__in=career_entry_ids).delete()
        for item in career_entries:
            if id in item or 'id' in item:
                CareerEntry.objects.filter(pk=item.id).update(**item)
                career_entry = CareerEntry.objects.get(pk=item.id)
            else:
                career_entry = CareerEntry(**item)
                career_entry.creator = creator
                career_entry.company = creator.the_current_company
                career_entry.beneficiary = beneficiary
                career_entry.save()

        document_record_ids = [item.id for item in document_records if item.id is not None]
        DocumentRecord.objects.filter(beneficiary=beneficiary).exclude(id__in=document_record_ids).delete()
        for item in document_records:
            document = item.pop("document", None)
            if id in item or 'id' in item:
                DocumentRecord.objects.filter(pk=item.id).update(**item)
                document_record = DocumentRecord.objects.get(pk=item.id)
            else:
                document_record = DocumentRecord(**item)
                document_record.creator = creator
                document_record.company = creator.the_current_company
                document_record.beneficiary = beneficiary
                document_record.save()
            if not document and document_record.document:
                document_file = document_record.document
                document_file.delete()
            if document and isinstance(document, UploadedFile):
                document_file = document_record.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                document_record.document = document_file
                document_record.save()

        return UpdateBeneficiary(beneficiary=beneficiary)

class UpdateBeneficiaryState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary = graphene.Field(BeneficiaryType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_fields=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary = None
        message = ''
        try:
            beneficiary = Beneficiary.objects.get(pk=id)
            Beneficiary.objects.filter(pk=id).update(is_active=not beneficiary.is_active)
            beneficiary.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            beneficiary=None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryState(done=done, success=success, message=message,beneficiary=beneficiary)

class DeleteBeneficiary(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary = graphene.Field(BeneficiaryType)
    id = graphene.ID()
    deleted = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id):
        deleted = False
        success = False
        message = ''
        current_user = info.context.user
        beneficiary = Beneficiary.objects.get(pk=id)
        if current_user.can_manage_administration() or current_user.is_manager() or (beneficiary.creator == current_user):
            # beneficiary = Beneficiary.objects.get(pk=id)
            # beneficiary.delete()
            Beneficiary.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Impossible de supprimer : vous n'avez pas les droits nécessaires."
        return DeleteBeneficiary(deleted=deleted, success=success, message=message, id=id)

#************************************************************************

# *************************************************************************************************#
# *************************************************************************************************#

class CreateBeneficiaryAdmission(graphene.Mutation):
    class Arguments:
        beneficiary_admission_data = BeneficiaryAdmissionInput(required=True)
        files = graphene.List(MediaInput, required=False)

    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType)

    def mutate(root, info, files=None, beneficiary_admission_data=None):
        creator = info.context.user
        establishment_ids = beneficiary_admission_data.pop("establishments", None)
        beneficiary_admission = BeneficiaryAdmission(**beneficiary_admission_data)
        beneficiary_admission.creator = creator
        beneficiary_admission.company = creator.the_current_company
        beneficiary_admission.save()
        if establishment_ids and establishment_ids is not None:
            beneficiary_admission.establishments.set(establishment_ids)
        folder = Folder.objects.create(name=str(beneficiary_admission.id)+'_'+beneficiary_admission.first_name+'-'+beneficiary_admission.last_name,creator=creator)
        beneficiary_admission.folder = folder
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
                file_file.folder = beneficiary_admission.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            beneficiary_admission.files.add(file_file)
        beneficiary_admission.save()
        if not beneficiary_admission.employee:
            beneficiary_admission.employee = creator.get_employee_in_company()
            beneficiary_admission.save()
        if beneficiary_admission.status == 'PENDING':
            activity_managers = User.get_activity_managers_in_user_company(user=creator)
            for activity_manager in activity_managers:
                notify_beneficiary_admission(sender=creator, recipient=activity_manager, beneficiary_admission=beneficiary_admission, action='ADDED')
        return CreateBeneficiaryAdmission(beneficiary_admission=beneficiary_admission)


class UpdateBeneficiaryAdmission(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_admission_data = BeneficiaryAdmissionInput(required=True)
        files = graphene.List(MediaInput, required=False)

    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType)

    def mutate(root, info, id, files=None, beneficiary_admission_data=None):
        creator = info.context.user
        establishment_ids = beneficiary_admission_data.pop("establishments", None)
        BeneficiaryAdmission.objects.filter(pk=id).update(**beneficiary_admission_data)
        beneficiary_admission = BeneficiaryAdmission.objects.get(pk=id)
        if establishment_ids and establishment_ids is not None:
            beneficiary_admission.establishments.set(establishment_ids)
        if not beneficiary_admission.folder or beneficiary_admission.folder is None:
            folder = Folder.objects.create(name=str(beneficiary_admission.id)+'_'+beneficiary_admission.first_name+'-'+beneficiary_admission.last_name,creator=creator)
            BeneficiaryAdmission.objects.filter(pk=id).update(folder=folder)
            beneficiary_admission.refresh_from_db()
        if not beneficiary_admission.employee:
            beneficiary_admission.employee = creator.get_employee_in_company()
            beneficiary_admission.save()
        if not files:
            files = []
        else:
            file_ids = [item.id for item in files if item.id is not None]
            File.objects.filter(file_beneficiary_admissions=beneficiary_admission).exclude(id__in=file_ids).delete()
        for file_media in files:
            file = file_media.file
            caption = file_media.caption
            if id in file_media  or 'id' in file_media:
                file_file = File.objects.get(pk=file_media.id)
            else:
                file_file = File()
                file_file.creator = creator
                file_file.folder = beneficiary_admission.folder
            if info.context.FILES and file and isinstance(file, UploadedFile):
                file_file.file = file
            file_file.caption = caption
            file_file.save()
            beneficiary_admission.files.add(file_file)
        beneficiary_admission.save()
        is_draft = True if beneficiary_admission.status == 'DRAFT' else False
        if is_draft:
            BeneficiaryAdmission.objects.filter(pk=id).update(status='PENDING')
            beneficiary_admission.refresh_from_db()
        notify_beneficiary_admission(sender=creator, recipient=beneficiary_admission.creator, beneficiary_admission=beneficiary_admission, action='UPDATED')
        return UpdateBeneficiaryAdmission(beneficiary_admission=beneficiary_admission)


class UpdateBeneficiaryAdmissionState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_admission_fields=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary_admission = None
        message = ""
        try:
            beneficiary_admission = BeneficiaryAdmission.objects.get(pk=id)
            BeneficiaryAdmission.objects.filter(pk=id).update(
                is_active=not beneficiary_admission.is_active
            )
            beneficiary_admission.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            beneficiary_admission = None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryAdmissionState(
            done=done, success=success, message=message, beneficiary_admission=beneficiary_admission
        )

class UpdateBeneficiaryAdmissionFields(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_admission_data = BeneficiaryAdmissionFieldInput(required=True)

    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_admission_data=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary_admission = None
        message = ''
        try:
            beneficiary_admission = BeneficiaryAdmission.objects.get(pk=id)
            BeneficiaryAdmission.objects.filter(pk=id).update(**beneficiary_admission_data)
            beneficiary_admission.refresh_from_db()
            if 'status' in beneficiary_admission_data:
                if creator.can_manage_activity() or creator.is_manager():
                    employee_user = beneficiary_admission.employee.user if beneficiary_admission.employee else beneficiary_admission.creator
                    if employee_user:
                        notify_beneficiary_admission(sender=creator, recipient=employee_user, beneficiary_admission=beneficiary_admission)
                else:
                    activity_managers = User.get_activity_managers_in_user_company(user=creator)
                    for activity_manager in activity_managers:
                        notify_beneficiary_admission(sender=creator, recipient=activity_manager, beneficiary_admission=beneficiary_admission)
                beneficiary_admission.refresh_from_db()
        except Exception as e:
            print(e)
            done = False
            success = False
            beneficiary_admission=None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryAdmissionFields(done=done, success=success, message=message, beneficiary_admission=beneficiary_admission)


class DeleteBeneficiaryAdmission(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_admission = graphene.Field(BeneficiaryAdmissionType)
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
            beneficiary_admission = BeneficiaryAdmission.objects.get(pk=id)
            beneficiary_admission.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBeneficiaryAdmission(
            deleted=deleted, success=success, message=message, id=id
        )
# *************************************************************************#
class GenerateBeneficiary(graphene.Mutation):
    class Arguments:
        id_beneficiary_admission = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    beneficiary = graphene.Field(BeneficiaryType)

    def mutate(self, info, id_beneficiary_admission):
        creator = info.context.user
        # Vérifier si l'admission du bénéficiaire existe
        try:
            beneficiary_admission = BeneficiaryAdmission.objects.get(id=id_beneficiary_admission)
        except BeneficiaryAdmission.DoesNotExist:
            return GenerateBeneficiary(success=False, message="Admission du bénéficiaire introuvable.")

        # Vérifier si un bénéficiaire existe déjà avec le même ID (optionnel selon votre logique)
        if beneficiary_admission.beneficiary:
            return GenerateBeneficiary(success=True, beneficiary=beneficiary_admission.beneficiary, message="Un bénéficiaire avec ce numéro existe déjà.")

        # Créer un nouvel objet Beneficiary
        beneficiary = Beneficiary(
            gender=beneficiary_admission.gender,
            preferred_name=beneficiary_admission.preferred_name,
            first_name=beneficiary_admission.first_name,
            last_name=beneficiary_admission.last_name,
            email=beneficiary_admission.email,
            birth_date=beneficiary_admission.birth_date,
            birth_address=beneficiary_admission.birth_address,
            birth_city=beneficiary_admission.birth_city,
            birth_country=beneficiary_admission.birth_country,
            nationality=beneficiary_admission.nationality,
            professional_status=beneficiary_admission.professional_status,
            latitude=beneficiary_admission.latitude,
            longitude=beneficiary_admission.longitude,
            city=beneficiary_admission.city,
            country=beneficiary_admission.country,
            zip_code=beneficiary_admission.zip_code,
            address=beneficiary_admission.address,
            additional_address=beneficiary_admission.additional_address,
            mobile=beneficiary_admission.mobile,
            fix=beneficiary_admission.fix,
            fax=beneficiary_admission.fax,
            web_site=beneficiary_admission.web_site,
            other_contacts=beneficiary_admission.other_contacts,
            description=beneficiary_admission.description,
            observation=beneficiary_admission.observation,
            company=beneficiary_admission.company,
            creator=creator,
        )

        beneficiary.save()
        folder = Folder.objects.create(name=str(beneficiary.id)+'_'+beneficiary.first_name+'-'+beneficiary.last_name, creator=creator)
        beneficiary.folder = folder
        beneficiary.save()
        beneficiary_admission.folder.folder = folder
        beneficiary_admission.folder.save()
        beneficiary_admission.beneficiary = beneficiary
        beneficiary_admission.save()

        return GenerateBeneficiary(
            success=True,
            message="Bénéficiaire créé avec succès.",
            beneficiary=beneficiary,
        )

# *************************************************************************#
class CreateBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        beneficiary_group_data = BeneficiaryGroupInput(required=True)
        image = Upload(required=False)

    beneficiary_group = graphene.Field(BeneficiaryGroupType)

    def mutate(root, info, image=None, beneficiary_group_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_group_data.pop("beneficiaries")
        beneficiary_group = BeneficiaryGroup(**beneficiary_group_data)
        beneficiary_group.creator = creator
        beneficiary_group.company = creator.the_current_company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = beneficiary_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                beneficiary_group.image = image_file
        beneficiary_group.save()
        folder = Folder.objects.create(name=str(beneficiary_group.id)+'_'+beneficiary_group.name,creator=creator)
        beneficiary_group.folder = folder
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_group_item = BeneficiaryGroupItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_group__id=beneficiary_group.id)
            except BeneficiaryGroupItem.DoesNotExist:
                BeneficiaryGroupItem.objects.create(
                        beneficiary_group=beneficiary_group,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        beneficiary_group.save()
        return CreateBeneficiaryGroup(beneficiary_group=beneficiary_group)

class UpdateBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        beneficiary_group_data = BeneficiaryGroupInput(required=True)
        image = Upload(required=False)

    beneficiary_group = graphene.Field(BeneficiaryGroupType)

    def mutate(root, info, id, image=None, beneficiary_group_data=None):
        creator = info.context.user
        beneficiary_ids = beneficiary_group_data.pop("beneficiaries")
        BeneficiaryGroup.objects.filter(pk=id).update(**beneficiary_group_data)
        beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
        if not beneficiary_group.folder or beneficiary_group.folder is None:
            folder = Folder.objects.create(name=str(beneficiary_group.id)+'_'+beneficiary_group.name,creator=creator)
            BeneficiaryGroup.objects.filter(pk=id).update(folder=folder)
        if not image and beneficiary_group.image:
            image_file = beneficiary_group.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = beneficiary_group.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                beneficiary_group.image = image_file
            beneficiary_group.save()
        BeneficiaryGroupItem.objects.filter(beneficiary_group=beneficiary_group).exclude(beneficiary__id__in=beneficiary_ids).delete()
        beneficiaries = Beneficiary.objects.filter(id__in=beneficiary_ids)
        for beneficiary in beneficiaries:
            try:
                beneficiary_group_item = BeneficiaryGroupItem.objects.get(beneficiary__id=beneficiary.id, beneficiary_group__id=beneficiary_group.id)
            except BeneficiaryGroupItem.DoesNotExist:
                BeneficiaryGroupItem.objects.create(
                        beneficiary_group=beneficiary_group,
                        beneficiary=beneficiary,
                        creator=creator
                    )
        return UpdateBeneficiaryGroup(beneficiary_group=beneficiary_group)

class UpdateBeneficiaryGroupState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_group = graphene.Field(BeneficiaryGroupType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, beneficiary_group_fields=None):
        creator = info.context.user
        done = True
        success = True
        beneficiary_group = None
        message = ''
        try:
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
            BeneficiaryGroup.objects.filter(pk=id).update(is_active=not beneficiary_group.is_active)
            beneficiary_group.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            beneficiary_group=None
            message = "Une erreur s'est produite."
        return UpdateBeneficiaryGroupState(done=done, success=success, message=message,beneficiary_group=beneficiary_group)


class DeleteBeneficiaryGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    beneficiary_group = graphene.Field(BeneficiaryGroupType)
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
            beneficiary_group = BeneficiaryGroup.objects.get(pk=id)
            beneficiary_group.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteBeneficiaryGroup(deleted=deleted, success=success, message=message, id=id)

#************************************************************************
#*******************************************************************************************************************************
class HumanRessourcesMutation(graphene.ObjectType):
    create_employee = CreateEmployee.Field()
    update_employee = UpdateEmployee.Field()
    update_employee_state = UpdateEmployeeState.Field()
    delete_employee = DeleteEmployee.Field()
    
    create_employee_contract = CreateEmployeeContract.Field()
    update_employee_contract = UpdateEmployeeContract.Field()
    delete_employee_contract = DeleteEmployeeContract.Field()

    create_employee_group = CreateEmployeeGroup.Field()
    update_employee_group = UpdateEmployeeGroup.Field()
    update_employee_group_state = UpdateEmployeeGroupState.Field()
    delete_employee_group = DeleteEmployeeGroup.Field()

    create_beneficiary = CreateBeneficiary.Field()
    update_beneficiary = UpdateBeneficiary.Field()
    update_beneficiary_state = UpdateBeneficiaryState.Field()
    delete_beneficiary = DeleteBeneficiary.Field()

    create_beneficiary_admission = CreateBeneficiaryAdmission.Field()
    update_beneficiary_admission = UpdateBeneficiaryAdmission.Field()
    update_beneficiary_admission_state = UpdateBeneficiaryAdmissionState.Field()
    update_beneficiary_admission_fields = UpdateBeneficiaryAdmissionFields.Field()
    delete_beneficiary_admission = DeleteBeneficiaryAdmission.Field()

    generate_beneficiary = GenerateBeneficiary.Field()

    create_beneficiary_group = CreateBeneficiaryGroup.Field()
    update_beneficiary_group = UpdateBeneficiaryGroup.Field()
    update_beneficiary_group_state = UpdateBeneficiaryGroupState.Field()
    delete_beneficiary_group = DeleteBeneficiaryGroup.Field()
    
    # Maintenant que toutes les classes sont définies dans le bon ordre, nous pouvons activer ces mutations
    create_advance = CreateAdvance.Field()
    update_advance = UpdateAdvance.Field()
    validate_advance = ValidateAdvance.Field()
    delete_advance = DeleteAdvance.Field()