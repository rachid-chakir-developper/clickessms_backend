import graphene
from django.http import HttpResponse
from printer.pdf_generators.pdf_generators import generate_pdf_from_rml
import base64
import io

class GeneratePdfMutation(graphene.Mutation):
    class Arguments:
        document_type = graphene.String(required=True)
        id = graphene.ID(required=False)
        data = graphene.JSONString(required=False)

    pdf_file = graphene.String()

    def mutate(self, info, document_type, id=None, data=None):
        try:
            # Générer le PDF à partir du RML
            pdf_buffer = generate_pdf_from_rml(document_type, id, data)
            
            # Convertir le PDF en base64 pour le renvoyer comme chaîne
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
            
            return GeneratePdfMutation(pdf_file=pdf_base64)
        except Exception as e:
            raise e

class PrinterMutation(graphene.ObjectType):
    generate_pdf = GeneratePdfMutation.Field()
