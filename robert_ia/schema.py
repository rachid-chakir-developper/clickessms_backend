import graphene
import openai
from accounts.models import User

class ChatResponseType(graphene.ObjectType):
    answer = graphene.String()
    tokens = graphene.Int()

class UserQuestion(graphene.Mutation):
    class Arguments:
        question = graphene.String(required=True)

    Output = ChatResponseType

    @staticmethod
    def mutate(root, info, question):
        current_user = info.context.user
        current_tokens = current_user.tokens
        if current_tokens <= 0:
            return ChatResponseType(answer="Vous avez consommé vos tokens d'aujourd'hui", tokens=0)
        try:
            if not question:
                raise Exception('No question provided')

            # Assurez-vous d'avoir configuré votre clé API OpenAI dans settings.py
            openai.api_key = 'sk-proj-5zqaRwnD6lveLifNElDaT3BlbkFJZtGJzFK8mL8JA0GmLiKq'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Utiliser le modèle Chat
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            )

            answer = response.choices[0].message['content'].strip()
            new_tokens = current_user.tokens - 1
            User.objects.filter(pk=current_user.id).update(tokens=new_tokens)
            return ChatResponseType(answer=answer, tokens=new_tokens)

        except Exception as e:
            return ChatResponseType(answer=str(e))

class RobertIaMutation(graphene.ObjectType):
    user_question = UserQuestion.Field()