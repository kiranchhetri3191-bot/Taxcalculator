import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Indian Income Tax Calculator",
    page_icon="💰",
    layout="wide"
)

# ---------------- SIMPLE GREEN THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #F0FDF4;
    color: #1F2937;
}
h1, h2, h3 {
    color: #065F46;
}
section[data-testid="stSidebar"] {
    background-color: #ECFDF5;
    border-right: 2px solid #10B981;
}
section[data-testid="stSidebar"] * {
    color: #065F46;
}
button {
    background-color: #10B981 !important;
    color: white !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Controls")
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type="csv")

# ---------------- HEADER ----------------
st.title("💰 Indian Income Tax Calculator")
st.caption("Clean • Green • Stable")

st.info(
    "CSV columns required:\n"
    "**Name, Department, Age, grossincome, Deductions**"
)

# ---------------- TAX FUNCTIONS ----------------
def salary_after_standard_deduction(salary):
    return max(salary - 50000, 0)

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

    return round(tax * 1.04, 2)

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

    return round(tax * 1.04, 2)

# ---------------- MAIN LOGIC ----------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Uploaded Data")
    st.dataframe(df, use_container_width=True)

    records = []
    for _, row in df.iterrows():
        income = salary_after_standard_deduction(row["grossincome"])
        old_tax = old_regime_tax(income, row["Deductions"], row["Age"])
        new_tax = new_regime_tax(income)

        records.append({
            "Name": row["Name"],
            "Department": row["Department"],
            "Age": row["Age"],
            "Income": income,
            "Old Tax": old_tax,
            "New Tax": new_tax,
            "Recommended": "Old" if old_tax < new_tax else "New"
        })

    result = pd.DataFrame(records)

    st.success("✅ Calculation completed")
    st.dataframe(result, use_container_width=True)

    # ---------------- CHART ----------------
    fig, ax = plt.subplots()
    ax.bar(
        ["Old Regime", "New Regime"],
        [result["Old Tax"].sum(), result["New Tax"].sum()]
    )
    ax.set_title("Total Tax Comparison")
    st.pyplot(fig)

else:
    st.warning("⚠ Upload a CSV file to begin")
