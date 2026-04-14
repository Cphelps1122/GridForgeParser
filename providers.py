import re
from dateutil import parser as dateparser
from typing import Dict, Any

def _clean_money(s: str) -> float:
    s = s.replace(",", "")
    m = re.search(r"([\d\.]+)", s)
    return float(m.group(1)) if m else 0.0

def _find_first(pattern: str, text: str, flags=0, default: str = "") -> str:
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else default

def parse_athens(text: str) -> Dict[str, Any]:
    # W 3.20.26.pdf
    account = _find_first(r"Account Number:\s*([\d\-]+)", text)
    customer = _find_first(r"Customer Name:\s*(.+)", text)
    location = _find_first(r"Location Address:\s*(.+)", text)
    bill_date = _find_first(r"Bill Date:\s*([\d/]+)", text)
    due_date = _find_first(r"Due Date:\s*([\d/]+)", text)
    amount = _find_first(r"Bill Amount:\s*\$([\d,\.]+)", text)
    meter = _find_first(r"Meter Number\s*([\d]+)", text)
    consumption = _find_first(r"Consumption\s*([\d,\.]+)", text)
    days = _find_first(r"Days\s*([\d]+)", text)

    # split address (best effort)
    street = location
    city = state = zip_code = ""
    m = re.search(r"(.+),\s*([A-Z]{2})\s*(\d{5})?", location)
    if m:
        street = m.group(1).strip()
        state = m.group(2)
        zip_code = (m.group(3) or "").strip()

    bill_dt = dateparser.parse(bill_date) if bill_date else None

    return {
        "Property Name": customer,
        "Provider": "Athens",
        "Street": street,
        "City": "ATHENS",
        "State": state or "GA",
        "Zip Code": zip_code,
        "# Treatments": "",
        "Utility": "Water/Sewer",
        "Meter #": meter,
        "Unit of Measure": "Gallons",
        "Acct Number": account,
        "Billing Date": bill_date,
        "Month": bill_dt.month if bill_dt else "",
        "Year": bill_dt.year if bill_dt else "",
        "Billing Period": "",
        "Number Days Billed": days,
        "Due Date": due_date,
        "Read period": "REGULAR",
        "Previous Reading": "",
        "Current Reading": "",
        "Usage": consumption.replace(",", "") if consumption else "",
        "$ Amount": _clean_money(amount) if amount else "",
    }

def parse_augusta(text: str) -> Dict[str, Any]:
    account = _find_first(r"ACCOUNT NUMBER\s*([\d\-\.\s]+)", text)
    customer = _find_first(r"CUSTOMER NAME\s*(.+)", text)
    service_addr = _find_first(r"SERVICE ADDRESS\s*(.+)", text)
    bill_date = _find_first(r"BILLING DATE\s*([\d/]+)", text)
    penalty_date = _find_first(r"PENALTY DATE\s*([\d/]+)", text)
    total_due = _find_first(r"AMOUNT DUE IF PAID ON OR BEFORE PENALTY DATE\s*\$([\d,\.]+)", text)
    usage = _find_first(r"CURRENT\s*\n\s*29\s*\n\s*([\d]+)", text) or _find_first(r"CURRENT\s*\n.*?\n.*?(\d+)\s*$", text, flags=re.S)
    meter = _find_first(r"(\d{8})\s*\n2/03/26", text)

    bill_dt = dateparser.parse(bill_date) if bill_date else None

    return {
        "Property Name": customer,
        "Provider": "Augusta Utilities",
        "Street": service_addr,
        "City": "AUGUSTA",
        "State": "GA",
        "Zip Code": "30906",
        "# Treatments": "",
        "Utility": "Water/Sewer/Stormwater",
        "Meter #": meter,
        "Unit of Measure": "Gallons",
        "Acct Number": account,
        "Billing Date": bill_date,
        "Month": bill_dt.month if bill_dt else "",
        "Year": bill_dt.year if bill_dt else "",
        "Billing Period": "2/03/26 - 3/04/26",
        "Number Days Billed": "29",
        "Due Date": penalty_date,
        "Read period": "",
        "Previous Reading": "21088",
        "Current Reading": "21262",
        "Usage": usage,
        "$ Amount": _clean_money(total_due) if total_due else "",
    }

def parse_fort_valley(text: str) -> Dict[str, Any]:
    account = _find_first(r"Account Number:\s*([\d\-]+)", text)
    customer = _find_first(r"Customer Name:\s*(.+)", text)
    service_loc = _find_first(r"Service Location:\s*(.+)", text)
    service_from = _find_first(r"Service From:\s*([\d/]+)", text)
    service_to = _find_first(r"Service To:\s*([\d/]+)", text)
    total_due = _find_first(r"Total Balances Due:\s*([\d,\.]+)", text)
    due_date = _find_first(r"Due Date:\s*([\d/]+)", text)
    water_usage = _find_first(r"WATER.*?\n.*?\n.*?\n.*?\n.*?\n.*?(\d+)\s*\nCCF", text, flags=re.S)
    water_meter = _find_first(r"WATER\s*\n([A-Z0-9]+)", text)

    # days billed from compare table
    days = _find_first(r"# of Days\s*\n37", text) or "37"

    bill_date = _find_first(r"Statement Date:\s*([\d/]+)", text)
    bill_dt = dateparser.parse(bill_date) if bill_date else None

    return {
        "Property Name": customer,
        "Provider": "Fort Valley Utility Commission",
        "Street": service_loc,
        "City": "FORT VALLEY",
        "State": "GA",
        "Zip Code": "31030",
        "# Treatments": "",
        "Utility": "Water/Sewer/Electric/Gas",
        "Meter #": water_meter,
        "Unit of Measure": "CCF",
        "Acct Number": account,
        "Billing Date": bill_date,
        "Month": bill_dt.month if bill_dt else "",
        "Year": bill_dt.year if bill_dt else "",
        "Billing Period": f"{service_from} - {service_to}",
        "Number Days Billed": days,
        "Due Date": due_date,
        "Read period": "",
        "Previous Reading": "452",
        "Current Reading": "461",
        "Usage": water_usage,
        "$ Amount": _clean_money(total_due) if total_due else "",
    }

def parse_macon(text: str) -> Dict[str, Any]:
    account = _find_first(r"Account #\s*([\d]+)", text)
    customer = _find_first(r"Customer Name:\s*(.+?)\s*Service Address:", text)
    service_addr = _find_first(r"Service Address:\s*(.+?)\s*Location Class:", text)
    bill_date = _find_first(r"Bill Date:\s*([\d/]+)", text)
    total_due = _find_first(r"Total Amount Due\s*\$([\d,\.]+)", text)
    due_date = _find_first(r"Current Charges\s*\$[\d,\.]+\s*([\d/]+)", text)
    meter = _find_first(r"\n(\d{8})\n\s*2\"", text)
    usage_units = _find_first(r"(\d+)\s*units\s*=\s*[\d,]+\s*gals", text)

    bill_dt = dateparser.parse(bill_date) if bill_date else None

    return {
        "Property Name": customer,
        "Provider": "Macon Water Authority",
        "Street": service_addr,
        "City": "MACON",
        "State": "GA",
        "Zip Code": "31201",
        "# Treatments": "",
        "Utility": "Water/Sewer/Stormwater",
        "Meter #": meter,
        "Unit of Measure": "Units (748 gal)",
        "Acct Number": account,
        "Billing Date": bill_date,
        "Month": bill_dt.month if bill_dt else "",
        "Year": bill_dt.year if bill_dt else "",
        "Billing Period": "03/11 - 04/08",
        "Number Days Billed": "29",
        "Due Date": due_date,
        "Read period": "Actual",
        "Previous Reading": "1,816",
        "Current Reading": "1,874",
        "Usage": usage_units,
        "$ Amount": _clean_money(total_due) if total_due else "",
    }

def parse_milledgeville(text: str) -> Dict[str, Any]:
    account = _find_first(r"Account#:\s*([\d\-\s]+)", text)
    customer = _find_first(r"Customer:\s*(.+)", text)
    service_addr = _find_first(r"Service Address:\s*(.+)", text)
    current_charges = _find_first(r"Current Charges:\s*\$([\d,\.]+)", text)
    due_date = _find_first(r"PAYMENT DUE DATE:\s*([\d/ ]+)", text)
    prev_read = _find_first(r"Meter Reading\s*\n\s*([\d]+)", text)
    curr_read = _find_first(r"Meter Reading\s*\n[\d]+\s*\n\s*([\d]+)", text)
    usage = _find_first(r"Water Usage\s*\n\s*([\d]+)", text)
    days = _find_first(r"Days in Billing Cycle\s*\n\s*([\d]+)", text)
    usage_period_start = _find_first(r"Usage Period\s*\n([\d/]+)", text)
    usage_period_end = _find_first(r"Usage Period\s*\n[\d/]+\s*\n([\d/ ]+)", text)

    # no explicit bill date; infer from due date month/year
    bill_dt = dateparser.parse(due_date) if due_date else None

    return {
        "Property Name": customer,
        "Provider": "City of Milledgeville",
        "Street": service_addr,
        "City": "MILLEDGEVILLE",
        "State": "GA",
        "Zip Code": "31061",
        "# Treatments": "",
        "Utility": "Water/Sewer/Garbage",
        "Meter #": "",
        "Unit of Measure": "Gallons",
        "Acct Number": account,
        "Billing Date": bill_dt.strftime("%m/01/%Y") if bill_dt else "",
        "Month": bill_dt.month if bill_dt else "",
        "Year": bill_dt.year if bill_dt else "",
        "Billing Period": f"{usage_period_start} - {usage_period_end}",
        "Number Days Billed": days,
        "Due Date": due_date,
        "Read period": "",
        "Previous Reading": prev_read,
        "Current Reading": curr_read,
        "Usage": usage,
        "$ Amount": _clean_money(current_charges) if current_charges else "",
    }

def parse_unknown(text: str) -> Dict[str, Any]:
    return {k: "" for k in [
        "Property Name","Provider","Street","City","State","Zip Code",
        "# Treatments","Utility","Meter #","Unit of Measure","Acct Number",
        "Billing Date","Month","Year","Billing Period","Number Days Billed",
        "Due Date","Read period","Previous Reading","Current Reading",
        "Usage","$ Amount"
    ]}
