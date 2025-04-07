import graphene
from clickessms_backend.graphql_ws_consumer import SGIGraphqlWsConsumer
from graphql_auth.schema import MeQuery
from graphql_auth import mutations

from accounts.schema import UserQuery, UserMutation, UserSubscription, UserType
from medias.schema import MediasQuery, MediasMutation
from the_mailer.schema import TheMailerQuery, TheMailerMutation
from data_management.schema import DataQuery, DataMutation
from searching.schema import SearchQuery
from dashboard.schema import DashboardQuery, DashboardMutation
from companies.schema import CompanyQuery, CompanyMutation
from human_ressources.schema import HumanRessourcesQuery, HumanRessourcesMutation
from recruitment.schema import RecruitmentQuery, RecruitmentMutation
from stocks.schema import StocksQuery, StocksMutation
from computers.schema import ComputersQuery, ComputersMutation
from vehicles.schema import VehiclesQuery, VehiclesMutation
from partnerships.schema import PartnershipsQuery, PartnershipsMutation
from sales.schema import SalesQuery, SalesMutation
from purchases.schema import PurchasesQuery, PurchasesMutation
from works.schema import WorksQuery, WorksMutation, WorksSubscription
from feedbacks.schema import CommentsQuery, CommentsMutation, CommentsSubscription
from notifications.schema import NotificationsQuery, NotificationsMutation, NotificationsSubscription
from chat.schema import ChatQuery, ChatMutation, ChatSubscription
from loan_management.schema import LoansQuery, LoansMutation
from activities.schema import ActivitiesQuery, ActivitiesMutation
from qualities.schema import QualitiesQuery, QualitiesMutation, QualitiesSubscription
from administratives.schema import AdministrativesQuery, AdministrativesMutation
from finance.schema import FinanceQuery, FinanceMutation
from governance.schema import GovernanceQuery, GovernanceMutation
from sce.schema import SceQuery, SceMutation
from blog.schema import BlogQuery, BlogMutation
from planning.schema import PlanningQuery, PlanningMutation
from building_estate.schema import BuildingEstateQuery, BuildingEstateMutation
from printer.schema import PrinterMutation
from robert_ia.schema import RobertIaMutation

class ObtainJSONWebToken(mutations.ObtainJSONWebToken):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
    	user = info.context.user
    	return cls(user=user)

class Register(mutations.Register):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        user = info.context.user
        return cls(user=user)

class CustomPasswordChange(mutations.PasswordChange):
    user = graphene.Field(UserType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        user = info.context.user

        # Vérifier si l'utilisateur a déjà changé son mot de passe
        if not user.is_must_change_password:
            raise Exception("Vous avez déjà changé votre mot de passe.")

        # Exécuter la mutation d'origine
        response = super().mutate(root, info, **kwargs)

        # Si le changement est réussi, mettre à jour is_must_change_password
        if response.success:
            user.is_must_change_password = False
            user.save()

        return response

class AuthMutation(graphene.ObjectType):
    # register = mutations.Register.Field()
    register = Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    # token_auth = mutations.ObtainJSONWebToken.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()
    update_account = mutations.UpdateAccount.Field()
    # Mot de passe standard (permet à tout utilisateur de changer son mot de passe)
    password_change = mutations.PasswordChange.Field()
    # Changement de mot de passe obligatoire (désactive is_must_change_password après exécution)
    first_password_change = CustomPasswordChange.Field()

class Query(MeQuery, UserQuery, MediasQuery, TheMailerQuery, DataQuery, SearchQuery, DashboardQuery,
    CompanyQuery, HumanRessourcesQuery, RecruitmentQuery, StocksQuery, ComputersQuery,
    VehiclesQuery, PartnershipsQuery, PurchasesQuery, SalesQuery, WorksQuery,
    CommentsQuery, NotificationsQuery, ChatQuery, LoansQuery, ActivitiesQuery,
    QualitiesQuery, AdministrativesQuery, FinanceQuery, GovernanceQuery, SceQuery,
    BlogQuery, PlanningQuery, BuildingEstateQuery,
    graphene.ObjectType):
    pass

class Mutation(AuthMutation, UserMutation, MediasMutation, TheMailerMutation, DataMutation, DashboardMutation,
    CompanyMutation, HumanRessourcesMutation, RecruitmentMutation, StocksMutation, ComputersMutation,
    VehiclesMutation, PartnershipsMutation, PurchasesMutation, SalesMutation, WorksMutation,
    CommentsMutation, NotificationsMutation, ChatMutation, LoansMutation, ActivitiesMutation,
    QualitiesMutation, AdministrativesMutation, FinanceMutation, GovernanceMutation, SceMutation,
    BlogMutation, PlanningMutation,  BuildingEstateMutation, PrinterMutation, RobertIaMutation,
    graphene.ObjectType):
   pass

class Subscription(UserSubscription, QualitiesSubscription, WorksSubscription, CommentsSubscription,
    NotificationsSubscription, ChatSubscription,
    graphene.ObjectType):
   pass

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
# schema = graphene.Schema(query=Query, mutation=Mutation)

class AppGraphqlWsConsumer(SGIGraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    schema = schema