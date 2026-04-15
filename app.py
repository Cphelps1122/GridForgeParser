import io
import streamlit as st
import pdfplumber
import pandas as pd

from detect_provider import detect_provider
from providers import (
    parse_athens,
    parse_augusta,
    parse_fort_valley,
    parse_macon,
    parse_milledgeville,
    parse_unknown,
)

# ---- CONFIG ----
COLUMNS = [
    "Property Name",
    "Provider",
    "Street",
    "City",
    "State",
    "Zip Code",
    "# Treatments",
    "Utility",
    "Meter #",
    "Unit of Measure",
    "Acct Number",
    "Billing Date",
    "Month",
    "Year",
    "Billing Period",
    "Number Days Billed",
    "Due Date",
    "Read period",
    "Previous Reading",
    "Current Reading",
    "Usage",
    "$ Amount",
]

PARSER_MAP = {
    "athens": parse_athens,
    "augusta": parse_augusta,
    "fort_valley": parse_fort_valley,
    "macon": parse_macon,
    "milledgeville": parse_milledgeville,
    "unknown": parse_unknown,
}

# ---- UI ----
st.set_page_config(page_title="GridForge Utility Parser", layout="wide")
st.title("GridForge Utility Parser")

st.write("Upload a utility bill PDF, auto-detect provider, view raw text, review parsed fields, and export to CSV.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract text
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
    full_text = "\n".join(pages_text)

    st.subheader("Raw Extracted Text")
    st.text_area("PDF Text", full_text, height=300)

    # Detect provider
    provider_key = detect_provider(full_text)
    st.subheader("Detected Provider")
    st.write(provider_key if provider_key != "unknown" else "Unknown provider (using generic parser)")

    # Parse
    parser = PARSER_MAP.get(provider_key, parse_unknown)
    parsed = parser(full_text)

    st.subheader("Parsed Fields (Editable)")
    cols = st.columns(3)
    edited = {}

    for i, col_name in enumerate(COLUMNS):
        col = cols[i % 3]
        value = parsed.get(col_name, "")
        if isinstance(value, float):
            value = round(value, 2)
        edited[col_name] = col.text_input(col_name, str(value))

    # ---- CSV EXPORT ----
    st.subheader("Export")

    df = pd.DataFrame([edited])
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Parsed Bill as CSV",
        data=csv_bytes,
        file_name="utility_bill_export.csv",
        mime="text/csv"
    )
