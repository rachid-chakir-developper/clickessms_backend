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
from vehicles.schema import VehiclesQuery, VehiclesMutation
from partnerships.schema import PartnershipsQuery, PartnershipsMutation
from sales.schema import SalesQuery, SalesMutation
from purchases.schema import PurchasesQuery, PurchasesMutation
from works.schema import WorksQuery, WorksMutation
from feedbacks.schema import CommentsQuery, CommentsMutation, CommentsSubscription
from notifications.schema import NotificationsQuery, NotificationsMutation, NotificationsSubscription
from chat.schema import ChatQuery, ChatMutation, ChatSubscription
from loan_management.schema import LoansQuery, LoansMutation
from activities.schema import ActivitiesQuery, ActivitiesMutation
from qualities.schema import QualitiesQuery, QualitiesMutation
from administratives.schema import AdministrativesQuery, AdministrativesMutation
from finance.schema import FinanceQuery, FinanceMutation

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
    CompanyQuery, HumanRessourcesQuery, StocksQuery,
    VehiclesQuery, PartnershipsQuery, PurchasesQuery, SalesQuery, WorksQuery,
    CommentsQuery, NotificationsQuery, ChatQuery, LoansQuery, ActivitiesQuery,
    QualitiesQuery, AdministrativesQuery, FinanceQuery,
    graphene.ObjectType):
    pass

class Mutation(AuthMutation, UserMutation, MediasMutation, DataMutation,
    CompanyMutation, HumanRessourcesMutation, StocksMutation,
    VehiclesMutation, PartnershipsMutation, PurchasesMutation, SalesMutation, WorksMutation,
    CommentsMutation, NotificationsMutation, ChatMutation, LoansMutation, ActivitiesMutation,
    QualitiesMutation, AdministrativesMutation, FinanceMutation,
    graphene.ObjectType):
   pass

class Subscription(UserSubscription, CommentsSubscription, NotificationsSubscription, ChatSubscription, graphene.ObjectType):
   pass

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
# schema = graphene.Schema(query=Query, mutation=Mutation)

class AppGraphqlWsConsumer(SGIGraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    schema = schema