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
st.title("GridForge Utility Parser — Batch Mode Enabled")

st.write("Upload one or multiple utility bill PDFs. Each will be parsed and combined into a single CSV export.")

uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)

all_rows = []  # store parsed rows for batch CSV

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"Processing: {uploaded_file.name}")

        # Extract text
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        full_text = "\n".join(pages_text)

        # Detect provider
        provider_key = detect_provider(full_text)
        st.write(f"Detected Provider: **{provider_key}**")

        # Parse
        parser = PARSER_MAP.get(provider_key, parse_unknown)
        parsed = parser(full_text)

        # Display parsed fields
        with st.expander(f"Parsed Fields for {uploaded_file.name}", expanded=False):
            cols = st.columns(3)
            edited = {}

            for i, col_name in enumerate(COLUMNS):
                col = cols[i % 3]
                value = parsed.get(col_name, "")
                if isinstance(value, float):
                    value = round(value, 2)
                edited[col_name] = col.text_input(f"{col_name} ({uploaded_file.name})", str(value))

        # Add to batch list
        all_rows.append(edited)

    # ---- EXPORT ALL AS ONE CSV ----
    st.subheader("Batch Export")

    df = pd.DataFrame(all_rows)
    csv_bytes = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download ALL Parsed Bills as ONE CSV",
        data=csv_bytes,
        file_name="utility_bills_batch_export.csv",
        mime="text/csv"
    )
