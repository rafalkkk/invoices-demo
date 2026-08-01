import json
import streamlit as st
from invoice_service import analyze_invoice_from_bytes, extract_invoice_data


st.set_page_config(page_title="Invoice Reader Demo", page_icon="📄", layout="centered")

st.title("Invoice Reader Demo")
st.write("Upload one invoice file and get extracted data as JSON.")

if "invoice_data" not in st.session_state:
    st.session_state.invoice_data = None

uploaded_file = st.file_uploader("Choose an invoice file", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.info(f"Selected file: {uploaded_file.name}")

    if st.button("Analyze invoice"):
        try:
            file_bytes = uploaded_file.getvalue()

            with st.spinner("Analyzing invoice..."):
                result = analyze_invoice_from_bytes(file_bytes)
                st.session_state.invoice_data = extract_invoice_data(result)
                
        except Exception as error:
            st.error(f"Something went wrong: {error}")

    if st.session_state.invoice_data is not None:
        st.success("Analysis completed.")
        st.subheader("Extracted JSON")
        st.json(st.session_state.invoice_data)

        json_payload = json.dumps(st.session_state.invoice_data, ensure_ascii=False, indent=2)
        st.download_button(label="Download JSON", data=json_payload, file_name="invoice_data.json", mime="application/json")
else:
    st.session_state.invoice_data = None