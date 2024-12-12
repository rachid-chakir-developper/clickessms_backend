import graphene
from clickessms_backend.graphql_ws_consumer import SGIGraphqlWsConsumer
from graphql_auth.schema import MeQuery
from graphql_auth import mutations

from accounts.schema import UserQuery, UserMutation, UserSubscription, UserType
from medias.schema import MediasQuery, MediasMutation
from data_management.schema import DataQuery, DataMutation
from searching.schema import SearchQuery
from dashboard.schema import DashboardQuery
from companies.schema import CompanyQuery, CompanyMutation
from human_ressources.schema import HumanRessourcesQuery, HumanRessourcesMutation
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
   password_change = mutations.PasswordChange.Field()

class Query(MeQuery, UserQuery, MediasQuery, DataQuery, SearchQuery, DashboardQuery,
    CompanyQuery, HumanRessourcesQuery, StocksQuery, ComputersQuery,
    VehiclesQuery, PartnershipsQuery, PurchasesQuery, SalesQuery, WorksQuery,
    CommentsQuery, NotificationsQuery, ChatQuery, LoansQuery, ActivitiesQuery,
    QualitiesQuery, AdministrativesQuery, FinanceQuery, GovernanceQuery, SceQuery,
    BlogQuery, PlanningQuery,
    graphene.ObjectType):
    pass

class Mutation(AuthMutation, UserMutation, MediasMutation, DataMutation,
    CompanyMutation, HumanRessourcesMutation, StocksMutation, ComputersMutation,
    VehiclesMutation, PartnershipsMutation, PurchasesMutation, SalesMutation, WorksMutation,
    CommentsMutation, NotificationsMutation, ChatMutation, LoansMutation, ActivitiesMutation,
    QualitiesMutation, AdministrativesMutation, FinanceMutation, GovernanceMutation, SceMutation,
    BlogMutation, PlanningMutation, RobertIaMutation,
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