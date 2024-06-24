from robert_ia.secrets import OPENAI_API_KEY
import graphene
import openai
from accounts.models import User

class ChatResponseType(graphene.ObjectType):
    answer = graphene.String()
    number_current_openai_tokens = graphene.Int()

class UserQuestion(graphene.Mutation):
    class Arguments:
        question = graphene.String(required=True)

    Output = ChatResponseType

    @staticmethod
    def mutate(root, info, question):
        current_user = info.context.user
        number_current_openai_tokens = current_user.number_current_openai_tokens
        if number_current_openai_tokens <= 0:
            return ChatResponseType(answer="Vous avez consommé vos tokens d'aujourd'hui", number_current_openai_tokens=0)
        try:
            if not question:
                raise Exception('No question provided')

            # Assurez-vous d'avoir configuré votre clé API OpenAI dans secrets.py
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Utiliser le modèle Chat
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            )

            answer = response.choices[0].message['content'].strip()
            new_number_current_openai_tokens = number_current_openai_tokens - 1
            User.objects.filter(pk=current_user.id).update(number_current_openai_tokens=new_number_current_openai_tokens)
            return ChatResponseType(answer=answer, number_current_openai_tokens=new_number_current_openai_tokens)

        except Exception as e:
            return ChatResponseType(answer=str(e))

class RobertIaMutation(graphene.ObjectType):
    user_question = UserQuestion.Field()