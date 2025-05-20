import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q, Count

from vehicles.models import Vehicle, VehicleEstablishment, VehicleEmployee, VehicleOwnership, VehicleInspection, VehicleTechnicalInspection, VehicleInspectionFailure, VehicleRepair, VehicleTheCarriedOutRepair, VehicleRepairVigilantPoint
from medias.models import Folder, File
from medias.schema import MediaInput

class VehicleEstablishmentType(DjangoObjectType):
    class Meta:
        model = VehicleEstablishment
        fields = "__all__"

class VehicleEmployeeType(DjangoObjectType):
    class Meta:
        model = VehicleEmployee
        fields = "__all__"

class VehicleOwnershipType(DjangoObjectType):
    class Meta:
        model = VehicleOwnership
        fields = "__all__"

class VehicleInspectionType(DjangoObjectType):
    class Meta:
        model = VehicleInspection
        fields = "__all__"
    

class VehicleInspectionNodeType(graphene.ObjectType):
    nodes = graphene.List(VehicleInspectionType)
    total_count = graphene.Int()

class VehicleInspectionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    vehicles = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)


class VehicleInspectionFailureType(DjangoObjectType):
    class Meta:
        model = VehicleInspectionFailure
        fields = "__all__"


class VehicleTechnicalInspectionType(DjangoObjectType):
    class Meta:
        model = VehicleTechnicalInspection
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )
    

class VehicleTechnicalInspectionNodeType(graphene.ObjectType):
    nodes = graphene.List(VehicleTechnicalInspectionType)
    total_count = graphene.Int()

class VehicleTechnicalInspectionFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    vehicles = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class VehicleTheCarriedOutRepairType(DjangoObjectType):
    class Meta:
        model = VehicleTheCarriedOutRepair
        fields = "__all__"

class VehicleRepairVigilantPointType(DjangoObjectType):
    class Meta:
        model = VehicleRepairVigilantPoint
        fields = "__all__"


class VehicleRepairType(DjangoObjectType):
    class Meta:
        model = VehicleRepair
        fields = "__all__"

    document = graphene.String()

    def resolve_document(instance, info, **kwargs):
        return instance.document and info.context.build_absolute_uri(
            instance.document.file.url
        )
    

class VehicleRepairNodeType(graphene.ObjectType):
    nodes = graphene.List(VehicleRepairType)
    total_count = graphene.Int()

class VehicleRepairFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    vehicles = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class VehicleType(DjangoObjectType):
    class Meta:
        model = Vehicle
        fields = "__all__"
    image = graphene.String()
    mileage = graphene.Float(required=False)
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)
    def resolve_mileage( instance, info, **kwargs ):
        return instance.current_vehicle_inspection.mileage if instance.current_vehicle_inspection else None

class VehicleNodeType(graphene.ObjectType):
    nodes = graphene.List(VehicleType)
    total_count = graphene.Int()

class VehicleFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)
    establishments = graphene.List(graphene.Int, required=False)
    employees = graphene.List(graphene.Int, required=False)
    order_by = graphene.String(required=False)

class VehicleEstablishmentInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=False)
    establishments = graphene.List(graphene.Int, required=False)

class VehicleEmployeeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    starting_date = graphene.DateTime(required=False)
    ending_date = graphene.DateTime(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=False)
    employees = graphene.List(graphene.Int, required=False)

class VehicleOwnershipInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    ownership_type = graphene.String(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=False)
    purchase_date = graphene.DateTime(required=False)
    purchase_price = graphene.Decimal(required=False)
    sale_date = graphene.DateTime(required=False)
    sale_price = graphene.Decimal(required=False)
    rental_starting_date = graphene.DateTime(required=False)
    rental_ending_date = graphene.DateTime(required=False)
    rental_price = graphene.Decimal(required=False)
    rent_purchase_price = graphene.Decimal(required=False)
    expected_mileage = graphene.Float(required=False)
    loan_details = graphene.String(required=False)

class VehicleInspectionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=True)
    inspection_date_time = graphene.DateTime(required=False)
    next_inspection_date = graphene.DateTime(required=False)
    next_technical_inspection_date = graphene.DateTime(required=False)
    controller_employees = graphene.List(graphene.Int, required=False)
    controller_partner_id = graphene.Int(name="controllerPartner", required=False)
    mileage = graphene.Float(required=False)
    is_registration_card_here = graphene.Boolean(required=False)
    is_insurance_certificate_here = graphene.Boolean(required=False)
    is_insurance_attestation_here = graphene.Boolean(required=False)
    is_technical_control_here = graphene.Boolean(required=False)
    is_oil_level_checked = graphene.Boolean(required=False)
    is_windshield_washer_level_checked = graphene.Boolean(required=False)
    is_brake_fluid_level_checked = graphene.Boolean(required=False)
    is_coolant_level_checked = graphene.Boolean(required=False)
    is_tire_pressure_checked = graphene.Boolean(required=False)
    is_lights_condition_checked = graphene.Boolean(required=False)
    is_body_condition_checked = graphene.Boolean(required=False)
    remarks = graphene.String(required=False)


class VehicleInspectionFailureInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    vehicle_technical_inspection_id = graphene.Int(name="vehicleTechnicalInspection", required=False)
    failure_type = graphene.String(required=False)
    description = graphene.String(required=False)

class VehicleTechnicalInspectionInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=True)
    inspection_date_time = graphene.DateTime(required=False)
    next_inspection_date = graphene.DateTime(required=False)
    observation = graphene.String(required=False)
    state = graphene.String(required=False)
    failures = graphene.List(VehicleInspectionFailureInput, required=False)

class VehicleTheCarriedOutRepairInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    vehicle_repair_id = graphene.Int(name="VehicleRepair", required=False)
    description = graphene.String(required=False)

class VehicleRepairVigilantPointInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    vehicle_repair_id = graphene.Int(name="VehicleRepair", required=False)
    description = graphene.String(required=False)

class VehicleRepairInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    label = graphene.String(required=False)
    vehicle_id = graphene.Int(name="vehicle", required=True)
    garage_partner_id = graphene.Int(name="garagePartner", required=False)
    repair_date_time = graphene.DateTime(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    state = graphene.String(required=False)
    report = graphene.String(required=False)
    total_amount = graphene.Decimal(required=False)
    repairs = graphene.List(VehicleTheCarriedOutRepairInput, required=False)
    vigilant_points = graphene.List(VehicleRepairVigilantPointInput, required=False)

class VehicleInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    name = graphene.String(required=False)
    registration_number = graphene.String(required=True)
    vehicle_brand_id = graphene.Int(name="vehicleBrand", required=False)
    vehicle_model_id = graphene.Int(name="vehicleModel", required=False)
    state = graphene.String(required=False)
    crit_air_vignette = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    vehicle_establishments = graphene.List(VehicleEstablishmentInput, required=False)
    vehicle_employees = graphene.List(VehicleEmployeeInput, required=False)
    vehicle_ownerships = graphene.List(VehicleOwnershipInput, required=False)

class VehiclesQuery(graphene.ObjectType):
    vehicles = graphene.Field(VehicleNodeType, vehicle_filter= VehicleFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    vehicle = graphene.Field(VehicleType, id = graphene.ID())
    vehicle_inspections = graphene.Field(VehicleInspectionNodeType, vehicle_inspection_filter= VehicleInspectionFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    vehicle_inspection = graphene.Field(VehicleInspectionType, id = graphene.ID())
    vehicle_technical_inspections = graphene.Field(VehicleTechnicalInspectionNodeType, vehicle_technical_inspection_filter= VehicleTechnicalInspectionFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    vehicle_technical_inspection = graphene.Field(VehicleTechnicalInspectionType, id = graphene.ID())
    vehicle_repairs = graphene.Field(VehicleRepairNodeType, vehicle_repair_filter= VehicleRepairFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    vehicle_repair = graphene.Field(VehicleRepairType, id = graphene.ID())
    def resolve_vehicles(root, info, vehicle_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        employee = user.get_employee_in_company()
        total_count = 0
        vehicles = Vehicle.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_parking():
            if user.is_manager():
                vehicles = vehicles.filter(Q(vehicle_establishments__establishments__managers__employee=employee) | Q(vehicle_employees__employees=employee) | Q(creator=user))
            else:
                if employee:
                    employee_current_estabs = []
                    if employee.current_contract:
                        employee_current_estabs = employee.current_contract.establishments.values_list('establishment', flat=True)
                    vehicles = vehicles.filter(
                        Q(vehicle_establishments__establishments__in=employee.establishments.all()) |
                        Q(vehicle_establishments__establishments__in=employee_current_estabs) |
                        Q(vehicle_employees__employees=employee) |
                        Q(creator=user)
                        )
        the_order_by = '-created_at'
        if vehicle_filter:
            keyword = vehicle_filter.get('keyword', '')
            starting_date_time = vehicle_filter.get('starting_date_time')
            ending_date_time = vehicle_filter.get('ending_date_time')
            establishments = vehicle_filter.get('establishments')
            employees = vehicle_filter.get('employees')
            order_by = vehicle_filter.get('order_by')
            if keyword:
                vehicles = vehicles.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(vehicle_brand__name__icontains=keyword) | Q(vehicle_model__name__icontains=keyword))
            if establishments:
                vehicles = vehicles.filter(vehicle_establishments__establishments__id__in=establishments)
            if employees:
                vehicles = vehicles.filter(vehicle_employees__employees__id__in=employees)
            if starting_date_time:
                vehicles = vehicles.filter(starting_date_time__date__gte=starting_date_time.date())
            if ending_date_time:
                vehicles = vehicles.filter(starting_date_time__date__lte=ending_date_time.date())
            if order_by:
                the_order_by = order_by
        vehicles = vehicles.order_by(the_order_by).distinct()
        total_count = vehicles.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            vehicles = vehicles[offset:offset + limit]
        return VehicleNodeType(nodes=vehicles, total_count=total_count)

    def resolve_vehicle(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            vehicle = Vehicle.objects.get(pk=id, company=company)
        except Vehicle.DoesNotExist:
            vehicle = None
        return vehicle
    def resolve_vehicle_inspections(root, info, vehicle_inspection_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        vehicle_inspections = VehicleInspection.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_parking():
            if user.is_manager():
                vehicle_inspections = vehicle_inspections.filter(Q(vehicle__vehicle_establishments__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                vehicle_inspections = vehicle_inspections.filter(creator=user)
        the_order_by = '-created_at'
        if vehicle_inspection_filter:
            keyword = vehicle_inspection_filter.get('keyword', '')
            starting_date_time = vehicle_inspection_filter.get('starting_date_time')
            ending_date_time = vehicle_inspection_filter.get('ending_date_time')
            vehicles = vehicle_inspection_filter.get('vehicles')
            order_by = vehicle_inspection_filter.get('order_by')
            if vehicles:
                vehicle_inspections = vehicle_inspections.filter(vehicle__id__in=vehicles)
            if keyword:
                vehicle_inspections = vehicle_inspections.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                vehicle_inspections = vehicle_inspections.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                vehicle_inspections = vehicle_inspections.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        vehicle_inspections = vehicle_inspections.order_by(the_order_by).distinct()
        total_count = vehicle_inspections.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            vehicle_inspections = vehicle_inspections[offset:offset + limit]
        return VehicleInspectionNodeType(nodes=vehicle_inspections, total_count=total_count)

    def resolve_vehicle_inspection(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            vehicle_inspection = VehicleInspection.objects.get(pk=id, company=company)
        except VehicleInspection.DoesNotExist:
            vehicle_inspection = None
        return vehicle_inspection


    def resolve_vehicle_technical_inspections(root, info, vehicle_technical_inspection_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        vehicle_technical_inspections = VehicleTechnicalInspection.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_parking():
            if user.is_manager():
                vehicle_technical_inspections = vehicle_technical_inspections.filter(Q(vehicle__vehicle_establishments__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                vehicle_technical_inspections = vehicle_technical_inspections.filter(creator=user)
        the_order_by = '-created_at'
        if vehicle_technical_inspection_filter:
            keyword = vehicle_technical_inspection_filter.get('keyword', '')
            starting_date_time = vehicle_technical_inspection_filter.get('starting_date_time')
            ending_date_time = vehicle_technical_inspection_filter.get('ending_date_time')
            vehicles = vehicle_technical_inspection_filter.get('vehicles')
            order_by = vehicle_technical_inspection_filter.get('order_by')
            if vehicles:
                vehicle_technical_inspections = vehicle_technical_inspections.filter(vehicle__id__in=vehicles)
            if keyword:
                vehicle_technical_inspections = vehicle_technical_inspections.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                vehicle_technical_inspections = vehicle_technical_inspections.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                vehicle_technical_inspections = vehicle_technical_inspections.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        vehicle_technical_inspections = vehicle_technical_inspections.order_by(the_order_by).distinct()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            vehicle_technical_inspections = vehicle_technical_inspections[offset:offset + limit]
        return VehicleTechnicalInspectionNodeType(nodes=vehicle_technical_inspections, total_count=total_count)

    def resolve_vehicle_technical_inspection(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            vehicle_technical_inspection = VehicleTechnicalInspection.objects.get(pk=id, company=company)
        except VehicleTechnicalInspection.DoesNotExist:
            vehicle_technical_inspection = None
        return vehicle_technical_inspection


    def resolve_vehicle_repairs(root, info, vehicle_repair_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        total_count = 0
        vehicle_repairs = VehicleRepair.objects.filter(company=company, is_deleted=False)
        if not user.can_manage_parking():
            if user.is_manager():
                vehicle_repairs = vehicle_repairs.filter(Q(vehicle__vehicle_establishments__establishments__managers__employee=user.get_employee_in_company()) | Q(creator=user))
            else:
                vehicle_repairs = vehicle_repairs.filter(creator=user)
        the_order_by = '-created_at'
        if vehicle_repair_filter:
            keyword = vehicle_repair_filter.get('keyword', '')
            starting_date_time = vehicle_repair_filter.get('starting_date_time')
            ending_date_time = vehicle_repair_filter.get('ending_date_time')
            vehicles = vehicle_repair_filter.get('vehicles')
            order_by = vehicle_repair_filter.get('order_by')
            if vehicles:
                vehicle_repairs = vehicle_repairs.filter(vehicle__id__in=vehicles)
            if keyword:
                vehicle_repairs = vehicle_repairs.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                vehicle_repairs = vehicle_repairs.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                vehicle_repairs = vehicle_repairs.filter(created_at__lte=ending_date_time)
            if order_by:
                the_order_by = order_by
        vehicle_repairs = vehicle_repairs.order_by(the_order_by).distinct()
        total_count = vehicle_repairs.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            vehicle_repairs = vehicle_repairs[offset:offset + limit]
        return VehicleRepairNodeType(nodes=vehicle_repairs, total_count=total_count)

    def resolve_vehicle_repair(root, info, id):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.the_current_company
        try:
            vehicle_repair = VehicleRepair.objects.get(pk=id, company=company)
        except VehicleRepair.DoesNotExist:
            vehicle_repair = None
        return vehicle_repair

#************************************************************************

class CreateVehicle(graphene.Mutation):
    class Arguments:
        vehicle_data = VehicleInput(required=True)
        image = Upload(required=False)

    vehicle = graphene.Field(VehicleType)

    def mutate(root, info, image=None, vehicle_data=None):
        creator = info.context.user
        vehicle_establishments = vehicle_data.pop("vehicle_establishments") if "vehicle_establishments" in vehicle_data else []
        vehicle_employees = vehicle_data.pop("vehicle_employees") if "vehicle_employees" in vehicle_data else []
        vehicle_ownerships = vehicle_data.pop("vehicle_ownerships") if "vehicle_ownerships" in vehicle_data else []
        vehicle = Vehicle(**vehicle_data)
        vehicle.creator = creator
        vehicle.company = creator.current_company if creator.current_company is not None else creator.company
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = vehicle.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                vehicle.image = image_file
        vehicle.save()
        folder = Folder.objects.create(name=str(vehicle.id)+'_'+vehicle.name,creator=creator)
        vehicle.folder = folder
        vehicle.save()
        for item in vehicle_establishments:
            establishment_ids = item.pop("establishments")
            vehicle_establishment = VehicleEstablishment(**item)
            vehicle_establishment.vehicle = vehicle
            vehicle_establishment.save()
            vehicle_establishment.establishments.set(establishment_ids)
        for item in vehicle_employees:
            employees_ids = item.pop("employees")
            vehicle_employee = VehicleEmployee(**item)
            vehicle_employee.vehicle = vehicle
            vehicle_employee.save()
            vehicle_employee.employees.set(employees_ids)
        for item in vehicle_ownerships:
            vehicle_ownership = VehicleOwnership(**item)
            vehicle_ownership.vehicle = vehicle
            vehicle_ownership.save()
        return CreateVehicle(vehicle=vehicle)

class UpdateVehicle(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        vehicle_data = VehicleInput(required=True)
        image = Upload(required=False)

    vehicle = graphene.Field(VehicleType)

    def mutate(root, info, id, image=None, vehicle_data=None):
        creator = info.context.user
        try:
            vehicle = Vehicle.objects.get(pk=id, company=creator.the_current_company)
        except Vehicle.DoesNotExist:
            raise e
        vehicle_establishments = vehicle_data.pop("vehicle_establishments") if "vehicle_establishments" in vehicle_data else []
        vehicle_employees = vehicle_data.pop("vehicle_employees") if "vehicle_employees" in vehicle_data else []
        vehicle_ownerships = vehicle_data.pop("vehicle_ownerships") if "vehicle_ownerships" in vehicle_data else []
        Vehicle.objects.filter(pk=id).update(**vehicle_data)
        vehicle.refresh_from_db()
        if not vehicle.folder or vehicle.folder is None:
            folder = Folder.objects.create(name=str(vehicle.id)+'_'+vehicle.name,creator=creator)
            Vehicle.objects.filter(pk=id).update(folder=folder)
        if not image and vehicle.image:
            image_file = vehicle.image
            image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if image and isinstance(image, UploadedFile):
                image_file = vehicle.image
                if not image_file:
                    image_file = File()
                    image_file.creator = creator
                image_file.image = image
                image_file.save()
                vehicle.image = image_file
            vehicle.save()
        vehicle_establishment_ids = [item.id for item in vehicle_establishments if item.id is not None]
        VehicleEstablishment.objects.filter(vehicle=vehicle).exclude(id__in=vehicle_establishment_ids).delete()
        for item in vehicle_establishments:
            establishment_ids = item.pop("establishments")
            if id in item or 'id' in item:
                VehicleEstablishment.objects.filter(pk=item.id).update(**item)
                vehicle_establishment = VehicleEstablishment.objects.get(pk=item.id)
            else:
                vehicle_establishment = VehicleEstablishment(**item)
                vehicle_establishment.vehicle = vehicle
                vehicle_establishment.save()
            vehicle_establishment.establishments.set(establishment_ids)
        vehicle_employee_ids = [item.id for item in vehicle_employees if item.id is not None]
        VehicleEmployee.objects.filter(vehicle=vehicle).exclude(id__in=vehicle_employee_ids).delete()
        for item in vehicle_employees:
            employee_ids = item.pop("employees")
            if id in item or 'id' in item:
                VehicleEmployee.objects.filter(pk=item.id).update(**item)
                vehicle_employee = VehicleEmployee.objects.get(pk=item.id)
            else:
                vehicle_employee = VehicleEmployee(**item)
                vehicle_employee.vehicle = vehicle
                vehicle_employee.save()
            vehicle_employee.employees.set(employee_ids)
        vehicle_ownership_ids = [item.id for item in vehicle_ownerships if item.id is not None]
        VehicleOwnership.objects.filter(vehicle=vehicle).exclude(id__in=vehicle_ownership_ids).delete()
        for item in vehicle_ownerships:
            if id in item or 'id' in item:
                VehicleOwnership.objects.filter(pk=item.id).update(**item)
            else:
                vehicle_ownership = VehicleOwnership(**item)
                vehicle_ownership.vehicle = vehicle
                vehicle_ownership.save()
        return UpdateVehicle(vehicle=vehicle)

class UpdateVehicleState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    vehicle = graphene.Field(VehicleType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, vehicle_fields=None):
        creator = info.context.user
        try:
            vehicle = Vehicle.objects.get(pk=id, company=creator.the_current_company)
        except Vehicle.DoesNotExist:
            raise e
        done = True
        success = True
        message = ''
        try:
            Vehicle.objects.filter(pk=id).update(is_active=not vehicle.is_active)
            vehicle.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            vehicle=None
            message = "Une erreur s'est produite."
        return UpdateVehicleState(done=done, success=success, message=message,vehicle=vehicle)


class DeleteVehicle(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    vehicle = graphene.Field(VehicleType)
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
            vehicle = Vehicle.objects.get(pk=id, company=current_user.the_current_company)
        except Vehicle.DoesNotExist:
            raise e
        if current_user.can_manage_facility() or current_user.is_manager() or vehicle.creator==current_user:
            # vehicle = Vehicle.objects.get(pk=id)
            # vehicle.delete()
            Vehicle.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteVehicle(deleted=deleted, success=success, message=message, id=id)

#***************************************************************************************************
#***********************************************************************************************************

class CreateVehicleInspection(graphene.Mutation):
    class Arguments:
        vehicle_id = graphene.ID(required=False)
        vehicle_inspection_data = VehicleInspectionInput(required=False)
        images = graphene.List(MediaInput, required=False)
        videos = graphene.List(MediaInput, required=False)

    vehicle_inspection = graphene.Field(VehicleInspectionType)

    def mutate(root, info, vehicle_id=None, images=None, videos=None, vehicle_inspection_data=None):
        creator = info.context.user
        controller_employees_ids = vehicle_inspection_data.pop("controller_employees") if 'controller_employees' in vehicle_inspection_data else []
        vehicle_inspection = VehicleInspection(**vehicle_inspection_data)
        vehicle_inspection.creator = creator
        vehicle_inspection.company = creator.current_company if creator.current_company is not None else creator.company
        vehicle_inspection.save()
        folder = Folder.objects.create(name=str(vehicle_inspection.id)+'_'+vehicle_inspection.number,creator=creator)
        vehicle_inspection.folder = folder
        if controller_employees_ids and controller_employees_ids is not None:
            vehicle_inspection.controller_employees.set(controller_employees_ids)
        if creator.get_partner_in_company():
            vehicle_inspection.controller_partner = creator.get_partner_in_company()
        if not images:
            images = []
        for image_media in images:
            image = image_media.image
            caption = image_media.caption
            if id in image_media or 'id' in image_media:
                image_file = File.objects.get(pk=image_media.id)
            else:
                image_file = File()
                image_file.creator = creator
            if info.context.FILES and image and isinstance(image, UploadedFile):
                image_file.image = image
            image_file.caption = caption
            image_file.save()
            vehicle_inspection.images.add(image_file)
        if not videos:
            videos = []
        for video_media in videos:
            video = video_media.video
            caption = video_media.caption
            if id in video_media  or 'id' in video_media:
                video_file = File.objects.get(pk=video_media.id)
            else:
                video_file = File()
                video_file.creator = creator
            if info.context.FILES and video and isinstance(video, UploadedFile):
                video_file.video = video
            video_file.caption = caption
            video_file.save()
            vehicle_inspection.videos.add(video_file)
        vehicle_inspection.save()
        return CreateVehicleInspection(vehicle_inspection=vehicle_inspection)

class UpdateVehicleInspection(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        vehicle_inspection_data = VehicleInspectionInput(required=False)
        images = graphene.List(MediaInput, required=False)
        videos = graphene.List(MediaInput, required=False)

    vehicle_inspection = graphene.Field(VehicleInspectionType)

    def mutate(root, info, id, images=None, videos=None, vehicle_inspection_data=None):
        creator = info.context.user
        try:
            vehicle_inspection = VehicleInspection.objects.get(pk=id, company=creator.the_current_company)
        except VehicleInspection.DoesNotExist:
            raise e
        controller_employees_ids = vehicle_inspection_data.pop("controller_employees") if 'controller_employees' in vehicle_inspection_data else []
        VehicleInspection.objects.filter(pk=id).update(**vehicle_inspection_data)
        vehicle_inspection.refresh_from_db()
        if controller_employees_ids is not None:
            vehicle_inspection.controller_employees.set(controller_employees_ids)
        if not images:
            images = []
        else:
            image_ids = [item.id for item in images if item.id is not None]
            File.objects.filter(image_vehicle_inspections=vehicle_inspection).exclude(id__in=image_ids).delete()
        if creator.get_partner_in_company():
            vehicle_inspection.controller_partner = creator.get_partner_in_company()
        for image_media in images:
            image = image_media.image
            caption = image_media.caption
            if id in image_media or 'id' in image_media:
                image_file = File.objects.get(pk=image_media.id)
            else:
                image_file = File()
                image_file.creator = creator
            if info.context.FILES and image and isinstance(image, UploadedFile):
                image_file.image = image
            image_file.caption = caption
            image_file.save()
            vehicle_inspection.images.add(image_file)
        if not videos:
            videos = []
        else:
            video_ids = [item.id for item in videos if item.id is not None]
            File.objects.filter(video_vehicle_inspections=vehicle_inspection).exclude(id__in=video_ids).delete()
        for video_media in videos:
            video = video_media.video
            caption = video_media.caption
            if id in video_media  or 'id' in video_media:
                video_file = File.objects.get(pk=video_media.id)
            else:
                video_file = File()
                video_file.creator = creator
            if info.context.FILES and video and isinstance(video, UploadedFile):
                video_file.video = video
            video_file.caption = caption
            video_file.save()
            vehicle_inspection.videos.add(video_file)
        vehicle_inspection.save()
        return UpdateVehicleInspection(vehicle_inspection=vehicle_inspection)

class DeleteVehicleInspection(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    vehicle_inspection = graphene.Field(VehicleInspectionType)
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
            vehicle_inspection = VehicleInspection.objects.get(pk=id, company=current_user.the_current_company)
        except VehicleInspection.DoesNotExist:
            raise e
        if current_user.can_manage_facility() or current_user.is_manager() or vehicle_inspection.creator==current_user:
            # vehicle_inspection = VehicleInspection.objects.get(pk=id)
            # vehicle_inspection.delete()
            VehicleInspection.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteVehicleInspection(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
# ************************************************************************


class CreateVehicleTechnicalInspection(graphene.Mutation):
    class Arguments:
        vehicle_technical_inspection_data = VehicleTechnicalInspectionInput(required=True)
        document = Upload(required=False)

    vehicle_technical_inspection = graphene.Field(VehicleTechnicalInspectionType)

    def mutate(root, info, document=None, vehicle_technical_inspection_data=None):
        creator = info.context.user
        failures = vehicle_technical_inspection_data.pop("failures") if "failures" in vehicle_technical_inspection_data else []
        vehicle_technical_inspection = VehicleTechnicalInspection(**vehicle_technical_inspection_data)
        vehicle_technical_inspection.creator = creator
        vehicle_technical_inspection.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = vehicle_technical_inspection.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                vehicle_technical_inspection.document = document_file
        vehicle_technical_inspection.save()
        folder = Folder.objects.create(
            name=str(vehicle_technical_inspection.id) + "_" + vehicle_technical_inspection.number, creator=creator
        )
        vehicle_technical_inspection.folder = folder
        vehicle_technical_inspection.save()
        for item in failures:
            failure = VehicleInspectionFailure(**item)
            failure.vehicle_technical_inspection = vehicle_technical_inspection
            failure.save()
        return CreateVehicleTechnicalInspection(vehicle_technical_inspection=vehicle_technical_inspection)


class UpdateVehicleTechnicalInspection(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        vehicle_technical_inspection_data = VehicleTechnicalInspectionInput(required=True)
        document = Upload(required=False)

    vehicle_technical_inspection = graphene.Field(VehicleTechnicalInspectionType)

    def mutate(root, info, id, document=None, vehicle_technical_inspection_data=None):
        creator = info.context.user
        try:
            vehicle_technical_inspection = VehicleTechnicalInspection.objects.get(pk=id, company=creator.the_current_company)
        except VehicleTechnicalInspection.DoesNotExist:
            raise e
        failures = vehicle_technical_inspection_data.pop("failures") if "failures" in vehicle_technical_inspection_data else []
        VehicleTechnicalInspection.objects.filter(pk=id).update(**vehicle_technical_inspection_data)
        vehicle_technical_inspection.refresh_from_db()
        if not vehicle_technical_inspection.folder or vehicle_technical_inspection.folder is None:
            folder = Folder.objects.create(
                name=str(vehicle_technical_inspection.id) + "_" + vehicle_technical_inspection.number, creator=creator
            )
            VehicleTechnicalInspection.objects.filter(pk=id).update(folder=folder)
        if not document and vehicle_technical_inspection.document:
            document_file = vehicle_technical_inspection.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = vehicle_technical_inspection.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                vehicle_technical_inspection.document = document_file
            vehicle_technical_inspection.save()
        failure_ids = [item.id for item in failures if item.id is not None]
        VehicleInspectionFailure.objects.filter(vehicle_technical_inspection=vehicle_technical_inspection).exclude(id__in=failure_ids).delete()
        for item in failures:
            if id in item or 'id' in item:
                VehicleInspectionFailure.objects.filter(pk=item.id).update(**item)
            else:
                failure = VehicleInspectionFailure(**item)
                failure.vehicle_technical_inspection = vehicle_technical_inspection
                failure.save()
        return UpdateVehicleTechnicalInspection(vehicle_technical_inspection=vehicle_technical_inspection)


class DeleteVehicleTechnicalInspection(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    vehicle_technical_inspection = graphene.Field(VehicleTechnicalInspectionType)
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
            vehicle_technical_inspection = VehicleTechnicalInspection.objects.get(pk=id, company=current_user.the_current_company)
        except VehicleTechnicalInspection.DoesNotExist:
            raise e
        if current_user.can_manage_facility() or current_user.is_manager() or vehicle_technical_inspection.creator==current_user:
            # vehicle_technical_inspection = VehicleTechnicalInspection.objects.get(pk=id)
            # vehicle_technical_inspection.delete()
            VehicleTechnicalInspection.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteVehicleTechnicalInspection(deleted=deleted, success=success, message=message, id=id)


# ***************************************************************************************************************#
# ***************************************************************************************************************#

#*************************************************************************#
# ************************************************************************


class CreateVehicleRepair(graphene.Mutation):
    class Arguments:
        vehicle_repair_data = VehicleRepairInput(required=True)
        document = Upload(required=False)

    vehicle_repair = graphene.Field(VehicleRepairType)

    def mutate(root, info, document=None, vehicle_repair_data=None):
        creator = info.context.user
        repairs = vehicle_repair_data.pop("repairs") if "repairs" in vehicle_repair_data else []
        vigilant_points = vehicle_repair_data.pop("vigilant_points") if "vigilant_points" in vehicle_repair_data else []
        vehicle_repair = VehicleRepair(**vehicle_repair_data)
        vehicle_repair.creator = creator
        vehicle_repair.company = (
            creator.current_company
            if creator.current_company is not None
            else creator.company
        )
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = vehicle_repair.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                vehicle_repair.document = document_file
        vehicle_repair.save()
        folder = Folder.objects.create(
            name=str(vehicle_repair.id) + "_" + vehicle_repair.number, creator=creator
        )
        vehicle_repair.folder = folder
        if creator.get_partner_in_company():
            vehicle_repair.garage_partner = creator.get_partner_in_company()
        vehicle_repair.save()
        for item in repairs:
            repair = VehicleTheCarriedOutRepair(**item)
            repair.vehicle_repair = vehicle_repair
            repair.save()
        for item in vigilant_points:
            vigilant_point = VehicleRepairVigilantPoint(**item)
            vigilant_point.vehicle_repair = vehicle_repair
            vigilant_point.save()
        return CreateVehicleRepair(vehicle_repair=vehicle_repair)


class UpdateVehicleRepair(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        vehicle_repair_data = VehicleRepairInput(required=True)
        document = Upload(required=False)

    vehicle_repair = graphene.Field(VehicleRepairType)

    def mutate(root, info, id, document=None, vehicle_repair_data=None):
        creator = info.context.user
        try:
            vehicle_repair = VehicleRepair.objects.get(pk=id, company=creator.the_current_company)
        except VehicleRepair.DoesNotExist:
            raise e
        repairs = vehicle_repair_data.pop("repairs") if "repairs" in vehicle_repair_data else []
        vigilant_points = vehicle_repair_data.pop("vigilant_points") if "vigilant_points" in vehicle_repair_data else []
        VehicleRepair.objects.filter(pk=id).update(**vehicle_repair_data)
        vehicle_repair = VehicleRepair.objects.get(pk=id)
        if not vehicle_repair.folder or vehicle_repair.folder is None:
            folder = Folder.objects.create(
                name=str(vehicle_repair.id) + "_" + vehicle_repair.number, creator=creator
            )
            VehicleRepair.objects.filter(pk=id).update(folder=folder)
        if not document and vehicle_repair.document:
            document_file = vehicle_repair.document
            document_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if document and isinstance(document, UploadedFile):
                document_file = vehicle_repair.document
                if not document_file:
                    document_file = File()
                    document_file.creator = creator
                document_file.file = document
                document_file.save()
                vehicle_repair.document = document_file
            vehicle_repair.save()
        if creator.get_partner_in_company():
            vehicle_repair.garage_partner = creator.get_partner_in_company()
            vehicle_repair.save()

        repair_ids = [item.id for item in repairs if item.id is not None]
        VehicleTheCarriedOutRepair.objects.filter(vehicle_repair=vehicle_repair).exclude(id__in=repair_ids).delete()
        for item in repairs:
            if id in item or 'id' in item:
                VehicleTheCarriedOutRepair.objects.filter(pk=item.id).update(**item)
            else:
                repair = VehicleTheCarriedOutRepair(**item)
                repair.vehicle_repair = vehicle_repair
                repair.save()
        vigilant_point_ids = [item.id for item in vigilant_points if item.id is not None]
        VehicleRepairVigilantPoint.objects.filter(vehicle_repair=vehicle_repair).exclude(id__in=vigilant_point_ids).delete()
        for item in vigilant_points:
            if id in item or 'id' in item:
                VehicleRepairVigilantPoint.objects.filter(pk=item.id).update(**item)
            else:
                vigilant_point = VehicleRepairVigilantPoint(**item)
                vigilant_point.vehicle_repair = vehicle_repair
                vigilant_point.save()
        return UpdateVehicleRepair(vehicle_repair=vehicle_repair)

class DeleteVehicleRepair(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    vehicle_repair = graphene.Field(VehicleRepairType)
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
            vehicle_repair = VehicleRepair.objects.get(pk=id, company=current_user.the_current_company)
        except VehicleRepair.DoesNotExist:
            raise e
        if current_user.can_manage_facility() or current_user.is_manager() or vehicle_repair.creator==current_user:
            # vehicle_repair = VehicleRepair.objects.get(pk=id)
            # vehicle_repair.delete()
            VehicleRepair.objects.filter(pk=id).update(is_deleted=True)
            deleted = True
            success = True
        else:
            message = "Oups ! Vous n'avez pas les droits pour supprimer cet élément."
        return DeleteVehicleRepair(deleted=deleted, success=success, message=message, id=id)


# ***************************************************************************************************************#
# ***************************************************************************************************************#
class VehiclesMutation(graphene.ObjectType):
    create_vehicle = CreateVehicle.Field()
    update_vehicle = UpdateVehicle.Field()
    update_vehicle_state = UpdateVehicleState.Field()
    delete_vehicle = DeleteVehicle.Field()

    create_vehicle_inspection = CreateVehicleInspection.Field()
    update_vehicle_inspection = UpdateVehicleInspection.Field()
    delete_vehicle_inspection = DeleteVehicleInspection.Field()

    create_vehicle_technical_inspection = CreateVehicleTechnicalInspection.Field()
    update_vehicle_technical_inspection = UpdateVehicleTechnicalInspection.Field()
    delete_vehicle_technical_inspection = DeleteVehicleTechnicalInspection.Field()

    create_vehicle_repair = CreateVehicleRepair.Field()
    update_vehicle_repair = UpdateVehicleRepair.Field()
    delete_vehicle_repair = DeleteVehicleRepair.Field()