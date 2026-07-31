from config import DOCUMENTINTELLIGENCE_ENDPOINT, DOCUMENTINTELLIGENCE_API_KEY
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient


def create_document_intelligence_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=DOCUMENTINTELLIGENCE_ENDPOINT,
        credential=AzureKeyCredential(DOCUMENTINTELLIGENCE_API_KEY)
    )