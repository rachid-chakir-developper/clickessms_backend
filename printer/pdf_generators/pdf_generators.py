from django.template.loader import render_to_string
from io import BytesIO
from weasyprint import HTML

from sales.models import Invoice

def generate_pdf_from_rml(document_type, id, data):
    """ Génère un PDF à partir d'un template HTML/RML et des données fournies et retourne un BytesIO. """
    try:
        # Charger le template HTML (qui pourrait inclure du RML) correspondant au type de document
        template=None
        datas={"data": data}
        if document_type=='invoice':
            invoice = Invoice.objects.get(pk=id)
            template = f"sales/{document_type}.html"
            datas["invoice"] = invoice
        
        html_content = render_to_string(template, datas)

        # Convertir le contenu HTML en PDF avec WeasyPrint
        pdf = HTML(string=html_content).write_pdf()

        # Retourner le PDF sous forme de BytesIO
        pdf_file = BytesIO(pdf)

        # Si nécessaire, réinitialiser le curseur du fichier BytesIO pour d'autres opérations
        pdf_file.seek(0)

        return pdf_file
        # return None
    
    except Exception as e:
        print(f"Erreur lors de la génération du PDF : {e}")
        raise e  # Renvoyer l'exception pour que l'appelant puisse la gérer
