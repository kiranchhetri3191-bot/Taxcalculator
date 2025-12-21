import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

#Front-End

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Tax Calculator",
    page_icon="logo.png",
    layout="wide"
)
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=70)

with col2:
    st.markdown(
        "<h1 style='margin-top:15px;'>Indian Income Tax Calculator</h1>",
        unsafe_allow_html=True
    )
#Dark-Mode

dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
    <style>
    /* App background */
    .stApp {
        background-color: #0E1117;
        color: #EAEAEA;
    }
    summary {
        color:#FFFFFF !important;
        front-weight: bold;
    }
    .stMarkdown p, .stMarkdown li {
        color: #EAEAEA !important;
    }
    
    /* All text */
    html, body, [class*="css"] {
        color: #EAEAEA !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5 {
        color: #FFFFFF !important;
    }

    /* File uploader */
    section[data-testid="stFileUploader"] {
        background-color: #1C1F26;
        border: 1px solid #2E3440;
        border-radius: 10px;
    }

    /* Buttons */
    button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px;
    }

    /* Dataframe */
    .stDataFrame {
        background-color: #1C1F26;
    }

    /* Info / success boxes */
    .stAlert {
        background-color: #1C1F26 !important;
        color: #EAEAEA !important;
        border: 1px solid #2E3440;
    }
         /* Sidebar – force green in dark mode */
    section[data-testid="stSidebar"] {
        background-color: #E8F5E9 !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background-color: #F7F9FC;
        color: #1F2937;
    }

    h1, h2, h3 {
        color: #0F4C81;
    }

    section[data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    """
    <h1 style='text-align:center; color:#4CAF50;'>
    💰 Indian Income Tax Calculator
    </h1>
    <p style='text-align:center; font-size:18px;'>
    Compare <b>Old</b> vs <b>New</b> Tax Regime easily
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------- INFO BOX ----------------
st.markdown(
    """
    <div style="
        background-color:#FFFFFF;
        color:#1B5E20;
        padding:15px;
        border-radius:12px;
        border-left:6px solid #4CAF50;
        font-size:16px;
        box-shadow:0 2px 6px rgba(0,0,0,0.15)
    ">
    📄 <b>How to use:</b><br>
    Upload a CSV file with columns:<br>
    <b>Name, Department, Age, grossincome, Deductions</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")  # spacing

# ---------------- SIDEBAR ----------------
st.sidebar.markdown(
    """
    <h2 style='color:#1B5E20;'>⚙ Controls</h2>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload CSV File",
    type="csv"
)

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Use clean data for accurate results")


# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
  
    st.markdown("## 📋 Uploaded Data")
    st.dataframe(df, use_container_width=True)

    st.markdown("## 🧮 Tax Results")
   
    # Example summary cards (you already calculate real tax below)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background-color:#E3F2FD; padding:15px; border-radius:12px;">
            👤 <b>Total Employees</b><br>
            <h2>{}</h2>
            </div>
            """.format(len(df)),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div style="background-color:#E8F5E9; padding:15px; border-radius:12px;">
            💸 <b>Old Regime</b><br>
            <h3>Calculated</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div style="background-color:#FCE4EC; padding:15px; border-radius:12px;">
            🆕 <b>New Regime</b><br>
            <h3>Calculated</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.success("✅ Tax calculation completed successfully!")

else:
    st.warning("⚠ Please upload a CSV file to start")


# --- Helper function: surcharge + cess + marginal relief ---
def apply_surcharge_and_cess(tax, taxable, regime="New"):
    surcharge = 0
    threshold = 0

    if taxable > 50000000:
        surcharge = tax * (0.25 if regime == "New" else 0.37)
        threshold = 50000000
    elif taxable > 20000000:
        surcharge = tax * 0.25
        threshold = 20000000
    elif taxable > 10000000:
        surcharge = tax * 0.15
        threshold = 10000000
    elif taxable > 5000000:
        surcharge = tax * 0.10
        threshold = 5000000

    if surcharge > 0:
        max_surcharge = taxable - threshold
        if surcharge > max_surcharge:
            surcharge = max_surcharge

    total_tax_before_cess = tax + surcharge
    cess = total_tax_before_cess * 0.04
    total_tax = total_tax_before_cess + cess
    return round(total_tax, 2)

# --- Old Regime Tax Calculation ---
def old_regime_tax(grossincome, deductions, age):
    taxable = max(grossincome - deductions, 0)

    if age < 60:
        basic_exemption = 250000
    elif age < 80:
        basic_exemption = 300000
    else:
        basic_exemption = 500000

    tax = 0
    if taxable <= basic_exemption:
        return 0
    elif taxable <= 500000:
        tax = (taxable - basic_exemption) * 0.05
    elif taxable <= 1000000:
        tax = (500000 - basic_exemption) * 0.05 + (taxable - 500000) * 0.20
    else:
        tax = (500000 - basic_exemption) * 0.05 + 500000 * 0.20 + (taxable - 1000000) * 0.30

    if taxable <= 500000:
        return 0

    return apply_surcharge_and_cess(tax, taxable, "Old")

# --- New Regime Tax Calculation ---
def new_regime_tax(income):
    taxable = income
    tax = 0
    prev_limit = 0
    slabs = [300000, 600000, 900000, 1200000, 1500000]
    rates = [0, 0.05, 0.10, 0.15, 0.20, 0.30]

    for i in range(len(slabs)):
        if taxable > slabs[i]:
            tax += (slabs[i] - prev_limit) * rates[i]
            prev_limit = slabs[i]
        else:
            tax += (taxable - prev_limit) * rates[i]
            break
    if taxable > 1500000:
        tax += (taxable - 1500000) * 0.30

    if taxable <= 700000:
        return 0

    return apply_surcharge_and_cess(tax, taxable, "New")

# --- Income Collector ---
def income_collected(grossincome):
    grossincome = max(grossincome - 50000, 0)  # Standard deduction on salary only
    return grossincome
def generate_pdf(df):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 50, "Indian Income Tax Report")

    pdf.setFont("Helvetica", 10)
    y = height - 90

    for _, row in df.iterrows():
        line = (
            f"{row['EmployeeID']} | "
            f"Old Tax: Rs{row['Old Regime Tax']} | "
            f"New Tax: Rs{row['New Regime Tax']} | "
            f"Recommended: {row['Recommended']}"
        )
        pdf.drawString(50, y, line)
        y -= 18

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y = height - 50

    pdf.save()
    buffer.seek(0)
    return buffer            

# --- Streamlit App ---
st.title("Indian Income Tax Regime Calculator")
st.write("Upload a CSV file with columns: Name, Department, Age, grossincome, Deductions")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df_input = pd.read_csv(uploaded_file)
    n = st.number_input("Number of records to process", min_value=1, max_value=len(df_input), value=min(10, len(df_input)))
    df_input = df_input.head(n).sort_values(by='Age', ascending=False, ignore_index=True)

    records = []

    for index, row in df_input.iterrows():
        grossincome = income_collected(row["grossincome"])
        old_tax = old_regime_tax(grossincome, row["Deductions"], row["Age"])
        new_tax = new_regime_tax(grossincome)
        recommended = "Old Regime" if old_tax < new_tax else "New Regime"

        records.append({
            "EmployeeID": row["Name"],
            "Department": row["Department"],
            "Age": row["Age"],
            "Income": grossincome,
            "Deductions": row["Deductions"],
            "Old Regime Tax": old_tax,
            "New Regime Tax": new_tax,
            "Recommended": recommended
        })

    df_output = pd.DataFrame(records)
    st.success("✅ Tax calculation completed!")
    st.dataframe(df_output.head(11))

    #Tax Comparison Chat

    st.markdown("### 📊 Tax Comparison (Old vs New Regime)")

    total_old_tax = df_output["Old Regime Tax"].sum()
    total_new_tax = df_output["New Regime Tax"].sum()

    # Defining the formatter
    from matplotlib.ticker import FuncFormatter
    
    # Disables scientific notion

    def indian_format(x, pos):
        if x >= 10000000: return f'₹{x/10000000:.1f} Cr'
        elif x >= 100000: return f'₹{x/100000:.1f} L'
        else: return f'₹{x/1000:.0f} K' if x >= 1000 else f'₹{x:.0f}'

    # Creating Chat
    
    fig, ax = plt.subplots()

    ax.bar(
        ["Old Regime", "New Regime"],
        [total_old_tax, total_new_tax]
        )

    ax.set_ylabel("Total Tax Amount (Rs)")
    ax.set_title("Total Tax Liability Comparison")
    ax.yaxis.set_major_formatter(FuncFormatter(indian_format))
    st.pyplot(fig)
    
    #PDF Download Button

    pdf_buffer = generate_pdf(df_output)

    st.download_button(
        label="📄 Download Tax Report (PDF)",
        data=pdf_buffer,
        file_name="Income_Tax_Report.pdf",
        mime="application/pdf"
    )

    csv = df_output.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️Download Results as CSV", csv, "Tax_Calculation_Output.csv", "text/csv")
    #For Excell download

    excel_buffer = BytesIO()
    df_output.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="⬇️ Download Results as Excel",
        data=excel_buffer,
        file_name="Tax_Calculation_Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Please upload a CSV file to begin..")






    
























