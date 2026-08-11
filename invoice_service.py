from azure_client import create_document_intelligence_client
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from io import BytesIO


def analyze_invoice_from_file(file_path: str) -> AnalyzeResult:
    """Analyze invoice from a local file path."""
    client = create_document_intelligence_client()

    with open(file_path, "rb") as file:
        poller = client.begin_analyze_document(model_id="prebuilt-invoice", body=file)

    return poller.result()


def analyze_invoice_from_url(file_url: str) -> AnalyzeResult:
    """Analyze invoice from a URL source."""
    client = create_document_intelligence_client()

    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=AnalyzeDocumentRequest(url_source=file_url)
    )

    return poller.result()


def analyze_invoice_from_bytes(file_bytes: bytes) -> AnalyzeResult:
    """Analyze invoice from bytes (e.g., Streamlit file upload)."""
    client = create_document_intelligence_client()

    file_stream = BytesIO(file_bytes)

    poller = client.begin_analyze_document(
        model_id="prebuilt-invoice",
        body=file_stream
    )

    return poller.result()


# ==================== Helper functions for field extraction ====================


def get_string_value(fields: dict, field_name: str):
    """Extract string value from a field."""
    field = (fields or {}).get(field_name)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_date_value(fields: dict, field_name: str):
    """Extract date value from a field and return as string."""
    field = (fields or {}).get(field_name)
    value = getattr(field, "value_date", None) if field else None
    return str(value) if value else None


def get_currency_value(fields: dict, field_name: str):
    """Extract currency value from a field."""
    field = (fields or {}).get(field_name)
    currency = getattr(field, "value_currency", None) if field else None

    if not currency:
        return None

    return {
        "amount": getattr(currency, "amount", None),
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }


def get_address_value(fields: dict, field_name: str):
    """Extract address value from a field."""
    field = (fields or {}).get(field_name)
    address = getattr(field, "value_address", None) if field else None

    if not address:
        return None

    return {
        "street_address": getattr(address, "street_address", None),
        "city": getattr(address, "city", None),
        "state": getattr(address, "state", None),
        "postal_code": getattr(address, "postal_code", None),
        "country_region": getattr(address, "country_region", None),
    }


def get_address_recipient(fields: dict, field_name: str):
    """Extract address recipient (string) from a field."""
    field = (fields or {}).get(field_name)
    if not field:
        return None
    return getattr(field, "value_string", None)


# ==================== Nested field helpers (for line items) ====================


def get_nested_string(obj: dict, key: str):
    """Extract nested string value from an object."""
    field = (obj or {}).get(key)
    if not field:
        return None
    return getattr(field, "value_string", None)


def get_nested_number(obj: dict, key: str):
    """Extract nested number value from an object."""
    field = (obj or {}).get(key)
    if not field:
        return None
    return getattr(field, "value_number", None)


def get_nested_date(obj: dict, key: str):
    """Extract nested date value from an object and return as string."""
    field = (obj or {}).get(key)
    value = getattr(field, "value_date", None) if field else None
    return str(value) if value else None


def get_nested_currency(obj: dict, key: str):
    """Extract nested currency value from an object."""
    field = (obj or {}).get(key)
    currency = getattr(field, "value_currency", None) if field else None

    if not currency:
        return None

    return {
        "amount": getattr(currency, "amount", None),
        "currency_symbol": getattr(currency, "symbol", None),
        "currency_code": getattr(currency, "currency_code", None),
    }


# ==================== Line items extraction ====================


def get_items(fields: dict):
    """Extract line items from invoice fields."""
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
            "unit": get_nested_number(item_object, "Unit"),
            "unit_price": get_nested_currency(item_object, "UnitPrice"),
            "amount": get_nested_currency(item_object, "Amount"),
            "product_code": get_nested_string(item_object, "ProductCode"),
            "date": get_nested_date(item_object, "Date"),
            "tax": get_nested_string(item_object, "Tax"),
        })

    return items


# ==================== Main extraction function ====================


def extract_invoice_data(result: AnalyzeResult) -> dict:
    """
    Extract all available fields from Document Intelligence invoice result.
    Returns a dictionary with complete invoice data including all addresses,
    dates, financial fields, and line items.
    """
    invoices_data = []

    documents = getattr(result, "documents", None) or []

    for document in documents:
        fields = getattr(document, "fields", None) or {}

        invoice_data = {
            # Document metadata
            "document_type": getattr(document, "doc_type", None),
            "confidence": getattr(document, "confidence", None),

            # Vendor information
            "vendor_name": get_string_value(fields, "VendorName"),
            "vendor_address": get_address_value(fields, "VendorAddress"),
            "vendor_address_recipient": get_address_recipient(fields, "VendorAddressRecipient"),
            "vendor_tax_id": get_string_value(fields, "VendorTaxId"),

            # Customer information
            "customer_name": get_string_value(fields, "CustomerName"),
            "customer_id": get_string_value(fields, "CustomerId"),
            "customer_address": get_address_value(fields, "CustomerAddress"),
            "customer_address_recipient": get_address_recipient(fields, "CustomerAddressRecipient"),
            "customer_tax_id": get_string_value(fields, "CustomerTaxId"),

            # Invoice identifiers and dates
            "invoice_id": get_string_value(fields, "InvoiceId"),
            "invoice_date": get_date_value(fields, "InvoiceDate"),
            "due_date": get_date_value(fields, "DueDate"),
            "purchase_order": get_string_value(fields, "PurchaseOrder"),
            "payment_term": get_string_value(fields, "PaymentTerm"),

            # Billing address
            "billing_address": get_address_value(fields, "BillingAddress"),
            "billing_address_recipient": get_address_recipient(fields, "BillingAddressRecipient"),

            # Shipping address
            "shipping_address": get_address_value(fields, "ShippingAddress"),
            "shipping_address_recipient": get_address_recipient(fields, "ShippingAddressRecipient"),

            # Remittance address
            "remittance_address": get_address_value(fields, "RemittanceAddress"),
            "remittance_address_recipient": get_address_recipient(fields, "RemittanceAddressRecipient"),

            # Service address and dates
            "service_address": get_address_value(fields, "ServiceAddress"),
            "service_address_recipient": get_address_recipient(fields, "ServiceAddressRecipient"),
            "service_start_date": get_date_value(fields, "ServiceStartDate"),
            "service_end_date": get_date_value(fields, "ServiceEndDate"),

            # Financial fields
            "invoice_total": get_currency_value(fields, "InvoiceTotal"),
            "subtotal": get_currency_value(fields, "SubTotal"),
            "total_tax": get_currency_value(fields, "TotalTax"),
            "total_discount": get_currency_value(fields, "TotalDiscount"),
            "previous_unpaid_balance": get_currency_value(fields, "PreviousUnpaidBalance"),
            "amount_due": get_currency_value(fields, "AmountDue"),

            # Payment details
            "paid_in_four_installments": get_string_value(fields, "PaidInFourInstallments"),

            # Line items
            "items": get_items(fields),
        }

        invoices_data.append(invoice_data)

    return {"invoices": invoices_data}