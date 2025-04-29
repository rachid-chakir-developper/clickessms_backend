
from printer.excel_generators.generate_excel_activity_month import generate_excel_activity_month

def generate_excel(info=None, dashboard_activity_filter=None, document_type=None, id=None, data=None):
    try:
        datas={"data": data}
        if document_type=='activity_month' or True:
        	return generate_excel_activity_month(info=info, dashboard_activity_filter=dashboard_activity_filter, data=None)
        return None
    
    except Exception as e:
        print(f"Erreur lors de la génération du excel : {e}")
        raise e  # Renvoyer l'exception pour que l'appelant puisse la gérer