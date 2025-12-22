
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from matplotlib.ticker import FuncFormatter

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Tax Calculator",
    page_icon="logo.png",
    layout="wide"
)

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo.png", width=70)
with col2:
    st.markdown("<h1 style='margin-top:15px;'>Indian Income Tax Calculator</h1>", unsafe_allow_html=True)

# ---------------- DARK MODE ----------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
    <style>
    /* ---------- BASE ---------- */
    .stApp {
        background-color: #0E1117;
        color: #EAEAEA;
    }

    html, body, [class*="css"] {
        color: #EAEAEA !important;
    }

    /* ---------- HEADINGS ---------- */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {
        background-color: #0B1320 !important;
        border-right: 1px solid #1F2937;
    }

    section[data-testid="stSidebar"] * {
        color: #EAEAEA !important;
    }

    /* ---------- INFO / SUCCESS / WARNING / ERROR ---------- */
    .stAlert {
        background-color: #111827 !important;
        color: #EAEAEA !important;
        border: 1px solid #1F2937 !important;
        border-radius: 10px;
    }

    /* ---------- DATAFRAME ---------- */
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

    /* ---------- FILE UPLOADER ---------- */
    section[data-testid="stFileUploader"] {
        background-color: #111827 !important;
        border: 1px dashed #374151 !important;
        border-radius: 10px;
        padding: 10px;
    }

    /* ---------- FILE UPLOADER HELPER TEXT FIX ---------- */
    section[data-testid="stFileUploader"] div {
        color: #D1D5DB !important; /* light grey, clearly visible */
    }

    section[data-testid="stFileUploader"] small {
        color: #9CA3AF !important; /* secondary helper text */
    }

    section[data-testid="stFileUploader"] span {
        color: #E5E7EB !important;
    }

    /* ---------- INPUTS ---------- */
    input, textarea {
        background-color: #0B1320 !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
    }

    label {
        color: #EAEAEA !important;
    }

    /* ---------- BUTTONS ---------- */
    button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        border: none !important;
    }

    button:hover {
        background-color: #1D4ED8 !important;
    }

    /* ---------- NUMBER INPUT ARROWS ---------- */
    div[data-baseweb="input"] svg {
        fill: #FFFFFF !important;
    }

    /* ---------- PLOTS ---------- */
    .js-plotly-plot, .stPlotlyChart, canvas {
        background-color: #0E1117 !important;
    }

    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    .stApp { background-color:#F7F9FC; color:#1F2937; }
    h1,h2,h3 { color:#0F4C81; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- INFO ----------------
st.info(
    "📄 **How to use:** Upload a CSV with columns:\n\n"
    "**Name, Department, Age, GrossIncome, Deductions**"
)

# ---------------- SIDEBAR UPLOADER ----------------
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type="csv")

# ---------------- TAX FUNCTIONS ----------------
def apply_surcharge_and_cess(tax, taxable, regime):
    surcharge = 0
    if taxable > 50000000:
        surcharge = tax * (0.25 if regime == "New" else 0.37)
    elif taxable > 20000000:
        surcharge = tax * 0.25
    elif taxable > 10000000:
        surcharge = tax * 0.15
    elif taxable > 5000000:
        surcharge = tax * 0.10

    total = tax + surcharge
    cess = total * 0.04
    return round(total + cess, 2)

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

    return apply_surcharge_and_cess(tax, taxable, "Old")

def new_regime_tax(income):
    slabs = [
        (300000, 0.00),
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

    return apply_surcharge_and_cess(tax, income, "New")

def salary_after_standard_deduction(salary):
    return max(salary - 50000, 0)

def generate_pdf(df):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 50, "Indian Income Tax Report")
    pdf.setFont("Helvetica", 10)

    y = height - 90
    for _, row in df.iterrows():
        line = f"{row['EmployeeID']} | Old: ₹{int(row['Old Regime Tax'])} | New: ₹{int(row['New Regime Tax'])}"
        pdf.drawString(50, y, line)
        y -= 18
        if y < 50:
            pdf.showPage()
            y = height - 50

    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------- MAIN LOGIC ----------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.markdown("## 📋 Uploaded Data")
    st.dataframe(df, use_container_width=True)

    n = st.number_input("Records to process", 1, len(df), min(10, len(df)))
    df = df.head(n).sort_values(by="Age", ascending=False)

    records = []
    for _, row in df.iterrows():
        income = salary_after_standard_deduction(row["GrossIncome"])
        old_tax = old_regime_tax(income, row["Deductions"], row["Age"])
        new_tax = new_regime_tax(income)

        records.append({
            "EmployeeID": row["Name"],
            "Department": row["Department"],
            "Age": row["Age"],
            "Income": income,
            "Deductions": row["Deductions"],
            "Old Regime Tax": old_tax,
            "New Regime Tax": new_tax,
            "Recommended": "Old Regime" if old_tax < new_tax else "New Regime"
        })

    df_out = pd.DataFrame(records)
    st.success("✅ Tax calculation completed")
    st.dataframe(df_out)

    # ---------------- CHART ----------------
    def indian_format(x, pos):
        if x >= 1e7: return f'₹{x/1e7:.1f} Cr'
        if x >= 1e5: return f'₹{x/1e5:.1f} L'
        return f'₹{x:.0f}'

    fig, ax = plt.subplots()
    ax.bar(["Old Regime", "New Regime"],
           [df_out["Old Regime Tax"].sum(), df_out["New Regime Tax"].sum()])
    ax.yaxis.set_major_formatter(FuncFormatter(indian_format))
    ax.set_title("Total Tax Comparison")
    st.pyplot(fig)

    # ---------------- DOWNLOADS ----------------
    st.download_button(
        "📄 Download PDF",
        generate_pdf(df_out),
        "Income_Tax_Report.pdf",
        "application/pdf"
    )

    st.download_button(
        "⬇️ Download CSV",
        df_out.to_csv(index=False).encode("utf-8"),
        "Tax_Output.csv",
        "text/csv"
    )

    @st.cache_data
    def create_excel(df):
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)
        return buffer


    excel_buffer = create_excel(df_out)

    st.download_button(
        "⬇️ Download Excel",
        excel_buffer,
        "Tax_Output.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


else:
    st.warning("⚠ Upload a CSV file to begin")




