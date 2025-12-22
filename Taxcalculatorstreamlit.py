import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from matplotlib.ticker import FuncFormatter

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Indian Tax Calculator",
    page_icon="💰",
    layout="wide"
)

# ---------------- THEME TOGGLE ----------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

# ---------------- GLOBAL CSS ----------------
if dark_mode:
    st.markdown("""
    <style>
    /* ===== BASE ===== */
    .stApp {
        background-color: #0E1117;
        color: #EAEAEA;
    }

    html, body, [class*="css"] {
        color: #EAEAEA !important;
    }

    /* ===== LAYOUT ===== */
    .block-container {
        padding: 3rem 3rem 3rem 3rem !important;
    }

    /* ===== HEADINGS ===== */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #0B1320 !important;
        border-right: 1px solid #1F2937;
        padding: 1rem;
    }

    section[data-testid="stSidebar"] * {
        color: #EAEAEA !important;
    }

    /* ===== CARDS ===== */
    .card {
        background-color: #111827;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #1F2937;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    /* ===== ALERTS ===== */
    .stAlert {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 12px;
    }

    /* ===== DATAFRAME ===== */
    .stDataFrame {
        background-color: #0E1117 !important;
    }

    .stDataFrame thead tr th {
        background-color: #111827 !important;
        color: #FFFFFF !important;
    }

    .stDataFrame tbody tr td {
        background-color: #0E1117 !important;
        color: #EAEAEA !important;
        border-color: #1F2937 !important;
    }

    /* ===== INPUTS ===== */
    input, textarea {
        background-color: #0B1320 !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }

    label {
        color: #EAEAEA !important;
    }

    /* ===== BUTTONS ===== */
    button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* Download button */
    div[data-testid="stDownloadButton"] > button {
        background-color: #22C55E !important;
        color: white !important;
        opacity: 1 !important;
        filter: none !important;
        padding: 0.6rem 1.4rem !important;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #16A34A !important;
    }

    /* ===== FILE UPLOADER ===== */
    section[data-testid="stFileUploader"] {
        background-color: #111827 !important;
        border: 1px dashed #374151 !important;
        border-radius: 12px;
        padding: 15px;
    }

    </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="card">
    <h1>💰 Indian Income Tax Calculator</h1>
    <p style="font-size:16px; color:#9CA3AF;">
    Compare Old vs New Regime • Bulk CSV • PDF • Excel
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------- INFO ----------------
st.info(
    "📄 Upload a CSV with columns:\n\n"
    "**Name, Department, Age, grossincome, Deductions**"
)

# ---------------- SIDEBAR ----------------
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type="csv")

# ---------------- TAX FUNCTIONS ----------------
def apply_surcharge_and_cess(tax, income):
    surcharge = 0
    if income > 5_000_000:
        surcharge = tax * 0.10
    total = tax + surcharge
    return round(total * 1.04, 2)

def old_regime_tax(income, deductions, age):
    taxable = max(income - deductions, 0)
    exemption = 250000 if age < 60 else 300000 if age < 80 else 500000
    if taxable <= exemption:
        return 0

    tax = 0
    if taxable <= 500000:
        tax = (taxable - exemption) * 0.05
    elif taxable <= 1000000:
        tax = (500000 - exemption) * 0.05 + (taxable - 500000) * 0.20
    else:
        tax = (500000 - exemption) * 0.05 + 500000 * 0.20 + (taxable - 1000000) * 0.30

    if taxable <= 500000:
        return 0

    return apply_surcharge_and_cess(tax, taxable)

def new_regime_tax(income):
    slabs = [
        (300000, 0),
        (600000, 0.05),
        (900000, 0.10),
        (1200000, 0.15),
        (1500000, 0.20),
    ]

    tax = 0
    prev = 0
    for limit, rate in slabs:
        if income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (income - prev) * rate
            break

    if income > 1500000:
        tax += (income - 1500000) * 0.30

    if income <= 700000:
        return 0

    return apply_surcharge_and_cess(tax, income)

def salary_after_standard_deduction(salary):
    return max(salary - 50000, 0)

@st.cache_data
def create_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def generate_pdf(df):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, h - 40, "Indian Income Tax Report")
    pdf.setFont("Helvetica", 10)

    y = h - 80
    for _, r in df.iterrows():
        pdf.drawString(40, y, f"{r['Employee']} | Old ₹{int(r['Old Tax'])} | New ₹{int(r['New Tax'])}")
        y -= 16
        if y < 50:
            pdf.showPage()
            y = h - 50

    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.markdown("### 📋 Uploaded Data")
    st.dataframe(df, use_container_width=True)

    n = st.number_input("Records to process", 1, len(df), min(20, len(df)))
    df = df.head(n)

    records = []
    for _, row in df.iterrows():
        income = salary_after_standard_deduction(row["grossincome"])
        old_tax = old_regime_tax(income, row["Deductions"], row["Age"])
        new_tax = new_regime_tax(income)

        records.append({
            "Employee": row["Name"],
            "Department": row["Department"],
            "Age": row["Age"],
            "Income": income,
            "Old Tax": old_tax,
            "New Tax": new_tax,
            "Recommended": "Old" if old_tax < new_tax else "New"
        })

    out = pd.DataFrame(records)

    st.success("✅ Tax calculation completed")
    st.dataframe(out, use_container_width=True)

    # ---------------- CHART ----------------
    def indian(x, _):
        return f"₹{x/1e5:.1f}L" if x < 1e7 else f"₹{x/1e7:.1f}Cr"

    fig, ax = plt.subplots()
    ax.bar(["Old Regime", "New Regime"], [out["Old Tax"].sum(), out["New Tax"].sum()])
    ax.yaxis.set_major_formatter(FuncFormatter(indian))
    ax.set_title("Total Tax Comparison")
    st.pyplot(fig)

    # ---------------- DOWNLOADS ----------------
    st.download_button("📄 Download PDF", generate_pdf(out), "Tax_Report.pdf")
    st.download_button("⬇️ Download CSV", out.to_csv(index=False), "Tax_Output.csv")
    st.download_button("⬇️ Download Excel", create_excel(out), "Tax_Output.xlsx")

else:
    st.warning("⚠ Upload a CSV file to begin")
