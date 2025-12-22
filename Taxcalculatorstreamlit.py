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
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type="csv")
st.sidebar.markdown("---")
st.sidebar.info("💡 Finance-ready • Supports large CSV")

# ---------------- GREEN THEME (SAFE) ----------------
st.markdown("""
<style>
/* ===== BASE ===== */
.stApp {
    background-color: #F5FBF7;
    color: #1F2937;
}

/* ===== LAYOUT ===== */
.block-container {
    padding: 2.5rem 3rem;
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    color: #14532D;
    font-weight: 700;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #ECFDF5;
    border-right: 2px solid #A7F3D0;
}
section[data-testid="stSidebar"] * {
    color: #065F46;
    font-weight: 500;
}

/* ===== INFO / SUCCESS ===== */
.stAlert {
    background-color: #ECFDF5 !important;
    border: 1px solid #A7F3D0 !important;
    color: #065F46 !important;
    border-radius: 10px;
}

/* ===== TABLE ===== */
.stDataFrame thead tr th {
    background-color: #D1FAE5 !important;
    color: #065F46 !important;
}
.stDataFrame tbody tr td {
    background-color: #F5FBF7 !important;
    color: #1F2937 !important;
    border-color: #A7F3D0 !important;
}

/* ===== INPUTS ===== */
input {
    background-color: #FFFFFF !important;
    border: 1px solid #10B981 !important;
    border-radius: 6px !important;
}

/* ===== BUTTONS ===== */
button {
    background-color: #10B981 !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.1rem !important;
}
button:hover {
    background-color: #059669 !important;
}

/* ===== DOWNLOAD BUTTON ===== */
div[data-testid="stDownloadButton"] > button {
    background-color: #16A34A !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background-color: #15803D !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div style="
    background:#ECFDF5;
    padding:25px;
    border-radius:14px;
    border-left:8px solid #10B981;
">
<h1>💰 Indian Income Tax Calculator</h1>
<p style="font-size:16px;color:#065F46;">
Compare Old vs New Regime • CSV • Excel • PDF
</p>
</div>
""", unsafe_allow_html=True)

st.write("")

st.info(
    "📄 Upload CSV with columns:\n"
    "**Name, Department, Age, grossincome, Deductions**"
)

# ---------------- TAX LOGIC ----------------
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

# ---------------- MAIN ----------------
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
           [result["Old Tax"].sum(), result["New Tax"].sum()],
           color=["#10B981", "#059669"])
    ax.yaxis.set_major_formatter(FuncFormatter(indian))
    ax.set_title("Total Tax Comparison")
    st.pyplot(fig)

    st.download_button("⬇️ Download CSV", result.to_csv(index=False), "Tax_Output.csv")
    st.download_button("⬇️ Download Excel", create_excel(result), "Tax_Output.xlsx")
    st.download_button("⬇️ Download PDF", generate_pdf(result), "Tax_Report.pdf")

else:
    st.warning("⚠ Upload a CSV file to begin")
