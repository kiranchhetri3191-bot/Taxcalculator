import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from matplotlib.ticker import FuncFormatter

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Indian Income Tax Calculator",
    page_icon="💰",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Controls")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type="csv")
st.sidebar.markdown("---")
st.sidebar.caption("Supports large CSV (100k+)")

# ---------------- CLEAN DARK THEME ----------------
if dark_mode:
    st.markdown("""
    <style>
    /* ===== BACKGROUND ===== */
    .stApp {
        background-color: #0f172a;
        color: #e5e7eb;
    }

    /* ===== CONTENT PADDING ===== */
    .block-container {
        padding: 2.5rem 3rem;
    }

    /* ===== HEADINGS ===== */
    h1, h2, h3 {
        color: #f9fafb;
        font-weight: 700;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    /* ===== INFO / SUCCESS ===== */
    .stAlert {
        background-color: #020617;
        border: 1px solid #1e293b;
        color: #e5e7eb;
        border-radius: 10px;
    }

    /* ===== TABLE ===== */
    .stDataFrame {
        background-color: #0f172a;
    }

    .stDataFrame thead tr th {
        background-color: #020617;
        color: #f9fafb;
    }

    .stDataFrame tbody tr td {
        background-color: #0f172a;
        color: #e5e7eb;
        border-color: #1e293b;
    }

    /* ===== INPUTS ===== */
    input {
        background-color: #020617;
        color: #f9fafb;
        border: 1px solid #1e293b;
        border-radius: 6px;
    }

    /* ===== DOWNLOAD BUTTONS ===== */
    div[data-testid="stDownloadButton"] > button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        opacity: 1;
    }

    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #1d4ed8;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("💰 Indian Income Tax Calculator")
st.caption("Old vs New Regime • Bulk CSV • Excel & PDF")

st.info(
    "📄 Upload CSV with columns:\n"
    "**Name, Department, Age, grossincome, Deductions**"
)

# ---------------- TAX FUNCTIONS ----------------
def salary_after_standard_deduction(salary):
    return max(salary - 50000, 0)

def apply_cess(tax):
    return round(tax * 1.04, 2)

def old_regime_tax(income, deductions, age):
    taxable = max(income - deductions, 0)
    exemption = 250000 if age < 60 else 300000 if age < 80 else 500000
    if taxable <= exemption:
        return 0

    if taxable <= 500000:
        tax = (taxable - exemption) * 0.05
    elif taxable <= 1000000:
        tax = (500000 - exemption) * 0.05 + (taxable - 500000) * 0.20
    else:
        tax = (500000 - exemption) * 0.05 + 500000 * 0.20 + (taxable - 1000000) * 0.30

    if taxable <= 500000:
        return 0

    return apply_cess(tax)

def new_regime_tax(income):
    slabs = [
        (300000, 0),
        (600000, 0.05),
        (900000, 0.10),
        (1200000, 0.15),
        (1500000, 0.20)
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

    return apply_cess(tax)

# ---------------- FILE HELPERS ----------------
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
        pdf.drawString(
            40, y,
            f"{r['Name']} | Old ₹{int(r['Old Tax'])} | New ₹{int(r['New Tax'])}"
        )
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

    st.subheader("📋 Uploaded Data")
    st.dataframe(df, use_container_width=True)

    n = st.number_input("Records to process", 1, len(df), min(20, len(df)))
    df = df.head(n)

    rows = []
    for _, r in df.iterrows():
        income = salary_after_standard_deduction(r["grossincome"])
        old_tax = old_regime_tax(income, r["Deductions"], r["Age"])
        new_tax = new_regime_tax(income)

        rows.append({
            "Name": r["Name"],
            "Department": r["Department"],
            "Age": r["Age"],
            "Income": income,
            "Old Tax": old_tax,
            "New Tax": new_tax,
            "Recommended": "Old" if old_tax < new_tax else "New"
        })

    result = pd.DataFrame(rows)

    st.success("✅ Tax calculation completed")
    st.dataframe(result, use_container_width=True)

    def indian(x, _):
        return f"₹{x/1e5:.1f}L" if x < 1e7 else f"₹{x/1e7:.1f}Cr"

    fig, ax = plt.subplots()
    ax.bar(["Old Regime", "New Regime"],
           [result["Old Tax"].sum(), result["New Tax"].sum()])
    ax.yaxis.set_major_formatter(FuncFormatter(indian))
    ax.set_title("Total Tax Comparison")
    st.pyplot(fig)

    st.download_button("⬇️ Download CSV", result.to_csv(index=False), "Tax_Output.csv")
    st.download_button("⬇️ Download Excel", create_excel(result), "Tax_Output.xlsx")
    st.download_button("⬇️ Download PDF", generate_pdf(result), "Tax_Report.pdf")

else:
    st.warning("⚠ Upload a CSV file to begin")
