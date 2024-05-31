import graphene
from graphene_django import DjangoObjectType
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.db.models import Q

from vehicles.models import Vehicle, VehicleEstablishment, VehicleEmployee, VehicleOwnership
from medias.models import Folder, File

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

class VehicleType(DjangoObjectType):
    class Meta:
        model = Vehicle
        fields = "__all__"
    image = graphene.String()
    def resolve_image( instance, info, **kwargs ):
        return instance.image and info.context.build_absolute_uri(instance.image.image.url)

class VehicleNodeType(graphene.ObjectType):
    nodes = graphene.List(VehicleType)
    total_count = graphene.Int()

class VehicleFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

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
    expected_mileage = graphene.Int(required=False)

class VehicleInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=True)
    name = graphene.String(required=True)
    registration_number = graphene.String(required=True)
    vehicle_brand_id = graphene.Int(name="vehicleBrand", required=False)
    vehicle_model_id = graphene.Int(name="vehicleModel", required=False)
    state = graphene.String(required=True)
    crit_air_vignette = graphene.String(required=True)
    description = graphene.String(required=True)
    observation = graphene.String(required=True)
    is_active = graphene.Boolean(required=True)
    vehicle_establishments = graphene.List(VehicleEstablishmentInput, required=False)
    vehicle_employees = graphene.List(VehicleEmployeeInput, required=False)
    vehicle_ownerships = graphene.List(VehicleOwnershipInput, required=False)

class VehiclesQuery(graphene.ObjectType):
    vehicles = graphene.Field(VehicleNodeType, vehicle_filter= VehicleFilterInput(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    vehicle = graphene.Field(VehicleType, id = graphene.ID())
    def resolve_vehicles(root, info, vehicle_filter=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        company = user.current_company if user.current_company is not None else user.company
        total_count = 0
        vehicles = Vehicle.objects.filter(company=company)
        if vehicle_filter:
            keyword = vehicle_filter.get('keyword', '')
            starting_date_time = vehicle_filter.get('starting_date_time')
            ending_date_time = vehicle_filter.get('ending_date_time')
            if keyword:
                vehicles = vehicles.filter(Q(name__icontains=keyword) | Q(registration_number__icontains=keyword) | Q(driver_name__icontains=keyword))
            if starting_date_time:
                vehicles = vehicles.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                vehicles = vehicles.filter(created_at__lte=ending_date_time)
        vehicles = vehicles.order_by('-created_at')
        total_count = vehicles.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            vehicles = vehicles[offset:offset + limit]
        return VehicleNodeType(nodes=vehicles, total_count=total_count)

    def resolve_vehicle(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            vehicle = None
        return vehicle

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
        vehicle_establishments = vehicle_data.pop("vehicle_establishments") if "vehicle_establishments" in vehicle_data else []
        vehicle_employees = vehicle_data.pop("vehicle_employees") if "vehicle_employees" in vehicle_data else []
        vehicle_ownerships = vehicle_data.pop("vehicle_ownerships") if "vehicle_ownerships" in vehicle_data else []
        Vehicle.objects.filter(pk=id).update(**vehicle_data)
        vehicle = Vehicle.objects.get(pk=id)
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
        done = True
        success = True
        vehicle = None
        message = ''
        try:
            vehicle = Vehicle.objects.get(pk=id)
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
        message = ''
        current_user = info.context.user
        if current_user.is_superuser:
            vehicle = Vehicle.objects.get(pk=id)
            vehicle.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteVehicle(deleted=deleted, success=success, message=message, id=id)

#*************************************************************************#
class VehiclesMutation(graphene.ObjectType):
    create_vehicle = CreateVehicle.Field()
    update_vehicle = UpdateVehicle.Field()
    update_vehicle_state = UpdateVehicleState.Field()
    delete_vehicle = DeleteVehicle.Field()