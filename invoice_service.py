from azure_client import create_document_intelligence_client
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest


def analyze_invoice_from_file(file_path: str) -> AnalyzeResult:
    client = create_document_intelligence_client()

    with open(file_path, "rb") as file:
        poller = client.begin_analyze_document(model_id="prebuilt-invoice", body=file)

    result = poller.result()
    return result


def analyze_invoice_from_url(file_url: str) -> AnalyzeResult:
    client = create_document_intelligence_client()

    poller = client.begin_analyze_document(model_id="prebuilt-invoice", body=AnalyzeDocumentRequest(url_source=file_url))
    
    result = poller.result()
    return result