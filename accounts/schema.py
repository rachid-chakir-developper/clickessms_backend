import graphene
import channels_graphql_ws
from graphene_django import DjangoObjectType
from django.contrib.auth import logout
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from graphql_jwt.decorators import login_required
from graphene_file_upload.scalars import Upload

from django.contrib.auth.models import Group, Permission

from django.db.models import Q

from accounts.models import User, UserCompany, Device
from medias.models import File

from human_ressources.schema import EmployeeType

from accounts.broadcaster import broadcastUserUpdated, broadcastUserCurrentLocalisationAsked

class UserCompanyType(DjangoObjectType):
    class Meta:
        model = UserCompany
        fields = "__all__"

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"
    pk = graphene.Int()
    photo = graphene.String()
    photo = graphene.String()
    cover_image = graphene.String()
    archived = graphene.Boolean()
    verified = graphene.Boolean()
    secondary_email = graphene.String()
    employee = graphene.Field(EmployeeType)
    companies = graphene.List(UserCompanyType)
    def resolve_pk(instance, info):
        return instance.pk
    def resolve_photo( instance, info, **kwargs ):
        return instance.photo and info.context.build_absolute_uri(instance.photo.image.url)
    def resolve_cover_image( instance, info, **kwargs ):
        return instance.cover_image and info.context.build_absolute_uri(instance.cover_image.image.url)
    def resolve_archived(instance, info):
        return instance.status.archived
    def resolve_verified(instance, info):
        return instance.status.verified
    def resolve_secondary_email(instance, info):
        return instance.status.secondary_email
    def resolve_employee(instance, info):
        user = info.context.user
        return instance.getEmployeeInCompany(company=user.current_company or user.company) if user.is_authenticated else instance.employee
    def resolve_companies(instance, info):
        return instance.managed_companies.all()

class UserNodeType(graphene.ObjectType):
    nodes = graphene.List(UserType)
    total_count = graphene.Int()

class UserFilterInput(graphene.InputObjectType):
    keyword = graphene.String(required=False)
    starting_date_time = graphene.DateTime(required=False)
    ending_date_time = graphene.DateTime(required=False)

class DeviceType(DjangoObjectType):
    class Meta:
        model = Device
        fields = "__all__"

class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = "__all__"

class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission
        fields = "__all__"

class UserInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    number = graphene.String(required=False)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password1 = graphene.String(required=False)
    password2 = graphene.String(required=False)
    description = graphene.String(required=False)
    observation = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    is_cgu_accepted = graphene.Boolean(required=False)
    employee_id = graphene.Int(name="employee", required=False)
    company_id = graphene.Int(name="company", required=False)

class DeviceInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    token = graphene.String(required=True)
    platform = graphene.String(required=True)

class CurrentLocalisationInput(graphene.InputObjectType):
    current_latitude = graphene.String(required=False)
    current_longitude = graphene.String(required=False)

class UserQuery(graphene.ObjectType):
    users = graphene.Field(UserNodeType, user_filter= UserFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    contacts = graphene.Field(UserNodeType, user_filter= UserFilterInput(required=False), id_company = graphene.ID(required=False), offset = graphene.Int(required=False), limit = graphene.Int(required=False), page = graphene.Int(required=False))
    user = graphene.Field(UserType, id = graphene.ID())
    current_user = graphene.Field(UserType)
    basic_infos = graphene.Field(UserType, id = graphene.ID(required=False))
    groups = graphene.List(GroupType)
    user_companies = graphene.List(UserCompanyType)
    group = graphene.Field(GroupType, id = graphene.ID())
    permissions = graphene.List(PermissionType)
    permission = graphene.Field(PermissionType, id = graphene.ID())
    devices = graphene.List(DeviceType)
    def resolve_users(root, info, user_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        total_count = 0
        users = User.objects.filter(company__id=id_company) if id_company else User.objects.all()
        if user_filter:
            keyword = user_filter.get('keyword', '')
            starting_date_time = user_filter.get('starting_date_time')
            ending_date_time = user_filter.get('ending_date_time')
            if keyword:
                users = users.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword) |
                        Q(employee__first_name__icontains=keyword) | Q(employee__last_name__icontains=keyword) | Q(employee__email__icontains=keyword)
                    )
            if starting_date_time:
                users = users.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                users = users.filter(created_at__lte=ending_date_time)
        users = users.order_by('-created_at')
        total_count = users.count()
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            users = users[offset:offset + limit]
        return UserNodeType(nodes=users, total_count=total_count)

    def resolve_contacts(root, info, user_filter=None, id_company=None, offset=None, limit=None, page=None):
        # We can easily optimize query count in the resolve method
        user = info.context.user
        total_count = 0
        users = User.objects.filter(~Q(id=user.id), company__id=id_company) if id_company else User.objects.filter(~Q(id=user.id))
        if user_filter:
            keyword = user_filter.get('keyword', '')
            starting_date_time = user_filter.get('starting_date_time')
            ending_date_time = user_filter.get('ending_date_time')
            if keyword:
                users = users.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(email__icontains=keyword) |
                        Q(employee__first_name__icontains=keyword) | Q(employee__last_name__icontains=keyword) | Q(employee__email__icontains=keyword)
                    )
            if starting_date_time:
                users = users.filter(created_at__gte=starting_date_time)
            if ending_date_time:
                users = users.filter(created_at__lte=ending_date_time)
        if page:
            offset = limit * (page - 1)
        if offset is not None and limit is not None:
            users = users[offset:offset + limit]
        total_count = users.count()
        return UserNodeType(nodes=users, total_count=total_count)

    def resolve_user(root, info, id):
        # We can easily optimize query count in the resolve method
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            user = None
        return user


    def resolve_user_companies(root, info):
        # We can easily optimize query count in the resolve method
        return UserCompany.objects.all()
    def resolve_current_user(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None

    def resolve_groups(root, info):
        # We can easily optimize query count in the resolve method
        groups = Group.objects.all()
        return groups

    def resolve_group(root, info, id):
        # We can easily optimize query count in the resolve method
        group = Group.objects.get(pk=id)
        return group

    def resolve_permissions(root, info):
        # We can easily optimize query count in the resolve method
        permissions = Permission.objects.all()
        return permissions

    def resolve_permission(root, info, id):
        # We can easily optimize query count in the resolve method
        permission = Permission.objects.get(pk=id)
        return permission

    def resolve_basic_infos(root, info, id=None):
        user = info.context.user
        # We can easily optimize query count in the resolve method
        #user = User.objects.get(pk=id)
        return user

    def resolve_devices(root, info):
        # We can easily optimize query count in the resolve method
        devices = Device.objects.all()
        return devices

class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)
        user_groups = graphene.List(graphene.Int, required=False)
        user_permissions = graphene.List(graphene.Int, required=False)

    user = graphene.Field(UserType)

    def mutate(root, info, photo=None, cover_image=None, user_groups=None, user_permissions=None,  user_data=None):
        creator = info.context.user
        employee_id = user_data.pop("employee_id")
        # company_id = user_data.pop("company_id")

        password1 = user_data.username if 'username' in user_data else 'password1'
        password2 = user_data.username if 'username' in user_data else 'password2'
        if password1 in user_data:
            password1 = user_data.pop("password1")
        if password2 in user_data:
            password2 = user_data.pop("password2")
        if password1 and password1 and password1 != password2:
            raise ValueError("Les mots de passe ne correspondent pas")
        user = User(**user_data)
        user.creator = creator
        user.company = creator.company
        user.save()
        user.setEmployeeForCompany(employee_id=employee_id)
        if user_groups is not None:
            groups = Group.objects.filter(id__in=user_groups)
            user.groups.set(groups)
        if user_permissions is not None:
            user_permissions = Permission.objects.filter(id__in=user_permissions)
            user.user_permissions.set(user_permissions)
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = user.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                user.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = user.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                user.cover_image = cover_image_file
        if password1:
            user.set_password(password1)
        user.status.verified = True
        user.status.save(update_fields=["verified"])
        user.save()
        return CreateUser(user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_data = UserInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)
        user_groups = graphene.List(graphene.Int, required=False)
        user_permissions = graphene.List(graphene.Int, required=False)

    user = graphene.Field(UserType)

    def mutate(root, info, id, photo=None, cover_image=None, user_groups=None, user_permissions=None,  user_data=None):
        creator = info.context.user
        employee_id = user_data.pop("employee_id")
        # company_id = user_data.pop("company_id")
        password1 = None
        password2 = None
        if password1 in user_data:
            password1 = user_data.pop("password1")
        if password2 in user_data:
            password2 = user_data.pop("password2")
        if password1 and password1 and password1 != password2:
            raise ValueError("Les mots de passe ne correspondent pas")
        User.objects.filter(pk=id).update(**user_data)
        user = User.objects.get(pk=id)
        user.setEmployeeForCompany(employee_id=employee_id)
        if user.status.verified is False:
            user.status.verified = True
            user.status.save(update_fields=["verified"])
        if not user.company:
            User.objects.filter(pk=id).update(company=creator.company)
        if user_groups is not None:
            groups = Group.objects.filter(id__in=user_groups)
            user.groups.set(groups)
        if user_permissions is not None:
            user_permissions = Permission.objects.filter(id__in=user_permissions)
            user.user_permissions.set(user_permissions)
        if not photo and user.photo:
            photo_file = user.photo
            photo_file.delete()
        if not cover_image and user.cover_image:
            cover_image_file = user.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = user.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                user.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = user.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                user.cover_image = cover_image_file
            user.save()
        if password1:
            user.set_password(password1)
            user.save()
        user = User.objects.get(pk=id)
        return UpdateUser(user=user)

class UpdateUserState(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    user = graphene.Field(UserType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id, user_fields=None):
        creator = info.context.user
        done = True
        success = True
        user = None
        message = ''
        try:
            user = User.objects.get(pk=id)
            User.objects.filter(pk=id).update(is_active=not user.is_active)
            user.refresh_from_db()
        except Exception as e:
            done = False
            success = False
            user=None
            message = "Une erreur s'est produite."
        return UpdateUserState(done=done, success=success, message=message,user=user)

class addBasicInfos(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        basic_infos_data = UserInput(required=True)
        photo = Upload(required=False)
        cover_image = Upload(required=False)

    basic_infos = graphene.Field(UserType)

    def mutate(root, info, id=None, photo=None, cover_image=None, basic_infos_data=None):
        creator = info.context.user
        User.objects.filter(pk=creator.id).update(**basic_infos_data)
        user = User.objects.get(pk=creator.id)
        if not photo and user.photo:
            photo_file = user.photo
            photo_file.delete()
        if not cover_image and user.cover_image:
            cover_image_file = user.cover_image
            cover_image_file.delete()
        if info.context.FILES:
            # file1 = info.context.FILES['1']
            if photo and isinstance(photo, UploadedFile):
                photo_file = user.photo
                if not photo_file:
                    photo_file = File()
                    photo_file.creator = creator
                photo_file.image = photo
                photo_file.save()
                user.photo = photo_file
            # file2 = info.context.FILES['2']
            if cover_image and isinstance(cover_image, UploadedFile):
                cover_image_file = user.cover_image
                if not cover_image_file:
                    cover_image_file = File()
                    cover_image_file.creator = creator
                cover_image_file.image = cover_image
                cover_image_file.save()
                user.cover_image = cover_image_file
            user.save()
        return addBasicInfos(basic_infos=user)


class UpdateUserCurrentLocalisation(graphene.Mutation):
    class Arguments:
        current_localisation_data = CurrentLocalisationInput(required=True)

    user = graphene.Field(UserType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, current_localisation_data=None):
        done = True
        success = True
        message = ''
        try:
            current_user = info.context.user
            User.objects.filter(pk=current_user.id).update(**current_localisation_data)
            current_user = User.objects.get(pk=current_user.id)
            broadcastUserUpdated(current_user)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return UpdateUserCurrentLocalisation(done=done, success=success, message=message)

class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    user = graphene.Field(UserType)
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
            user = User.objects.get(pk=id)
            if not user.is_superuser:
                user.delete()
                deleted = True
                success = True
            else:
                message = "Je suis un superuser. vous ne pouvez pas me supprimer."
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteUser(deleted=deleted, success=success, message=message, id=id)



class LogoutUser(graphene.Mutation):
    user = graphene.Field(UserType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info):
        done = False
        success = False
        message = ''
        user = info.context.user
        if not user.is_authenticated:
            message = "Vous n'étes pas connecté."
            user = None
        else:
            try:
                logout(info.context)
                done = True
                success = True
            except Exception as e:
                message = "Une erreur s'est produite."
        return LogoutUser(done=done, success=success, message=message, user=user)

#**************************************************************************************

class RegisterDevice(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=False)
        device_data = DeviceInput(required=False)

    device = graphene.Field(DeviceType)
    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, id=None, device_data=None):
        creator = info.context.user
        done = True
        success = True
        device = None
        message = ''
        try:
            try:
                device = Device.objects.get(token=device_data.token)
                device.is_user_online_here=True
                if device.user.id != creator.id:
                    device.creator = creator
                    device.user = creator
            except Device.DoesNotExist:
                device = Device(**device_data)
                device.creator = creator
                device.user = creator
            device.save()
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return RegisterDevice(done=done, success=success, message=message, device=device)

class AskToUsersCurrentLocalisations(graphene.Mutation):
    class Arguments:
        is_asked = graphene.Boolean(required=False)

    done = graphene.Boolean()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, is_asked=None):
        creator = info.context.user
        done = True
        success = True
        message = ''
        try:
            broadcastUserCurrentLocalisationAsked(is_asked=True)
        except Exception as e:
            done = False
            success = False
            message = "Une erreur s'est produite."
        return AskToUsersCurrentLocalisations(done=done, success=success, message=message)

#**************************************************************************************

class CreateGroup(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        group_permissions = graphene.List(graphene.Int, required=False)

    group = graphene.Field(GroupType)

    def mutate(root, info, group_permissions, name):
        group = Group(name=name)
        group.save()
        permissions = Permission.objects.filter(id__in=group_permissions)
        group.permissions.set(permissions)
        group.save()
        return CreateGroup(group=group)

class UpdateGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        group_permissions = graphene.List(graphene.Int, required=False)

    group = graphene.Field(GroupType)

    def mutate(root, info, group_permissions, id, name):
        Group.objects.filter(pk=id).update(name=name)
        group = Group.objects.get(pk=id)
        permissions = Permission.objects.filter(id__in=group_permissions)
        group.permissions.set(permissions)
        group.save()
        return UpdateGroup(group=group)


class DeleteGroup(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    group = graphene.Field(GroupType)
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
            group = Group.objects.get(pk=id)
            group.delete()
            deleted = True
            success = True
        else:
            message = "Vous n'êtes pas un Superuser."
        return DeleteGroup(deleted=deleted, success=success, message=message, id=id)

#**************************************************************************************

class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    update_user_state = UpdateUserState.Field()
    add_basic_infos = addBasicInfos.Field()
    update_user_current_localisation = UpdateUserCurrentLocalisation.Field()
    delete_user = DeleteUser.Field()
    logout_user = LogoutUser.Field()
    register_device = RegisterDevice.Field()
    create_group = CreateGroup.Field()
    update_group = UpdateGroup.Field()
    delete_group = DeleteGroup.Field()


#*********************************Subscription****************************************#

class OnUserUpdated(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    user = graphene.Field(UserType)

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_USER_UPDATED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if False:
            return OnUserUpdated.SKIP
        return OnUserUpdated(user=payload)

class OnUserCurrentLocalisationAsked(channels_graphql_ws.Subscription):
    """Simple GraphQL subscription."""

    # Leave only latest 64 messages in the server queue.
    notification_queue_limit = 64

    # Subscription payload.
    is_asked = graphene.Boolean()

    class Arguments:
        """That is how subscription arguments are defined."""

    @staticmethod
    def subscribe(root, info):
        """Called when user subscribes."""

        # Return the list of subscription group names.
        return ["ON_USER_LOCALISATION_ASKED"]

    @staticmethod
    def publish(payload, info):
        """Called to notify the client."""

        # Here `payload` contains the `payload` from the `broadcast()`
        # invocation (see below). You can return `MySubscription.SKIP`
        # if you wish to suppress the notification to a particular
        # client. For example, this allows to avoid notifications for
        # the actions made by this particular client.
        if not payload['is_asked']:
            return OnUserCurrentLocalisationAsked.SKIP
        return OnUserCurrentLocalisationAsked(asked=payload['is_asked'])

#***********************************Subscription***************************************************

class UserSubscription(graphene.ObjectType):
    on_user_updated = OnUserUpdated.Field()
    on_user_current_localisation_asked = OnUserCurrentLocalisationAsked.Field()
