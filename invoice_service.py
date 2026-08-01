from azure_client import create_document_intelligence_client
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest


def analyze_invoice_from_file(file_path: str) -> AnalyzeResult:
    client = create_document_intelligence_client()

    with open(file_path, "rb") as file:
        poller = client.begin_analyze_document(model_id="prebuilt-invoice", body=file)

    return poller.result()


def analyze_invoice_from_url(file_url: str) -> AnalyzeResult:
    client = create_document_intelligence_client()

    poller = client.begin_analyze_document(model_id="prebuilt-invoice", body=AnalyzeDocumentRequest(url_source=file_url))

    return poller.result()


def get_string_value(fields: dict, field_name: str):
    field = (fields or {}).get(field_name)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_date_value(fields: dict, field_name: str):
    field = (fields or {}).get(field_name)
    value = getattr(field, "value_date", None) if field else None
    return str(value) if value else None


def get_currency_value(fields: dict, field_name: str):
    field = (fields or {}).get(field_name)
    currency = getattr(field, "value_currency", None) if field else None

    if not currency:
        return None

    return {
        "amount": getattr(currency, "amount", None),
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }


def get_nested_string(obj: dict, key: str):
    field = (obj or {}).get(key)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_nested_number(obj: dict, key: str):
    field = (obj or {}).get(key)
    if not field:
        return None
    return getattr(field, "value_number", None)


def get_nested_date(obj: dict, key: str):
    field = (obj or {}).get(key)
    value = getattr(field, "value_date", None) if field else None
    return str(value) if value else None


def get_nested_currency(obj: dict, key: str):
    field = (obj or {}).get(key)
    currency = getattr(field, "value_currency", None) if field else None

    if not currency:
        return None

    return {
        "amount": getattr(currency, "amount", None),
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }


def get_items(fields: dict):
    items_field = (fields or {}).get("Items")
    items_array = getattr(items_field, "value_array", None) if items_field else None

    if not items_array:
        return []

    items = []

    for item in items_array:
        item_object = getattr(item, "value_object", None) or {}

        items.append({
            "description": get_nested_string(item_object, "Description"),
            "quantity": get_nested_number(item_object, "Quantity"),
            "unit_price": get_nested_currency(item_object, "UnitPrice"),
            "amount": get_nested_currency(item_object, "Amount"),
            "product_code": get_nested_string(item_object, "ProductCode"),
            "date": get_nested_date(item_object, "Date"),
        })

    return items


def extract_invoice_data(result: AnalyzeResult) -> dict:
    invoices_data = []

    documents = getattr(result, "documents", None) or []

    for document in documents:
        fields = getattr(document, "fields", None) or {}

        invoice_data = {
            "document_type": getattr(document, "doc_type", None),
            "confidence": getattr(document, "confidence", None),
            "vendor_name": get_string_value(fields, "VendorName"),
            "customer_name": get_string_value(fields, "CustomerName"),
            "invoice_id": get_string_value(fields, "InvoiceId"),
            "invoice_date": get_date_value(fields, "InvoiceDate"),
            "due_date": get_date_value(fields, "DueDate"),
            "purchase_order": get_string_value(fields, "PurchaseOrder"),
            "invoice_total": get_currency_value(fields, "InvoiceTotal"),
            "amount_due": get_currency_value(fields, "AmountDue"),
            "subtotal": get_currency_value(fields, "SubTotal"),
            "total_tax": get_currency_value(fields, "TotalTax"),
            "items": get_items(fields),
        }

        invoices_data.append(invoice_data)

    return {"invoices": invoices_data}