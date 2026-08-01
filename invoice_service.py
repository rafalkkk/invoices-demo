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



def get_string_value(fields: dict, field_name: str):
    field = fields.get(field_name)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_date_value(fields: dict, field_name: str):
    field = fields.get(field_name)
    if not field or not getattr(field, "value_date", None):
        return None
    return str(field.value_date)


def get_currency_value(fields: dict, field_name: str):
    field = fields.get(field_name)
    if not field or not getattr(field, "value_currency", None):
        return None

    currency = field.value_currency
    return {
        "amount": currency.amount,
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }


def get_items(fields: dict):
    items_field = fields.get("Items")
    if not items_field or not items_field.value_array:
        return []

    items = []

    for item in items_field.value_array:
        item_object = item.value_object

        items.append({
            "description": get_nested_string(item_object, "Description"),
            "quantity": get_nested_number(item_object, "Quantity"),
            "unit_price": get_nested_currency(item_object, "UnitPrice"),
            "amount": get_nested_currency(item_object, "Amount"),
            "product_code": get_nested_string(item_object, "ProductCode"),
            "date": get_nested_date(item_object, "Date"),
        })

    return items


def get_nested_string(obj: dict, key: str):
    field = obj.get(key)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_nested_number(obj: dict, key: str):
    field = obj.get(key)
    if not field:
        return None
    return getattr(field, "value_number", None)


def get_nested_date(obj: dict, key: str):
    field = obj.get(key)
    if not field or not getattr(field, "value_date", None):
        return None
    return str(field.value_date)


def get_nested_currency(obj: dict, key: str):
    field = obj.get(key)
    if not field or not getattr(field, "value_currency", None):
        return None

    currency = field.value_currency
    return {
        "amount": currency.amount,
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }



def extract_invoice_data(result: AnalyzeResult) -> dict:
    invoices_data = []

    for document in result.documents:
        fields = document.fields or {}

        invoice_data = {
            "document_type": document.doc_type,
            "confidence": document.confidence,
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