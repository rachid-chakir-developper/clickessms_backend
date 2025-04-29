import graphene
from django.http import HttpResponse
from printer.pdf_generators.pdf_generators import generate_pdf_from_rml
from printer.excel_generators.excel_generators import generate_excel
import base64
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Font, Border, Side
from openpyxl.utils import get_column_letter
from datetime import date
from io import BytesIO
from dashboard.schema import DashboardActivityFilterInput


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

class ExportExcelMutation(graphene.Mutation):
    class Arguments:
        document_type = graphene.String(required=False)
        id = graphene.ID(required=False)
        data = graphene.JSONString(required=False)
        dashboard_activity_filter= DashboardActivityFilterInput(required=False)

    success = graphene.Boolean()
    file_base64 = graphene.String()

    def mutate(self, info, dashboard_activity_filter=None, document_type=None, id=None, data=None):
        try:
            # Générer le PDF à partir du RML
            file_base64 = generate_excel(info=info, dashboard_activity_filter=dashboard_activity_filter, document_type=document_type, id=id, data=data)
            return ExportExcelMutation(success=True, file_base64=file_base64)
        except Exception as e:
            raise e

class PrinterMutation(graphene.ObjectType):
    generate_pdf = GeneratePdfMutation.Field()
    export_excel = ExportExcelMutation.Field()
