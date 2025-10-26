import streamlit as st
import pandas as pd

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

    csv = df_output.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "Tax_Calculation_Output.csv", "text/csv")

    excel = df_output.to_excel(index=False)
    st.download_button("Download Results as Excel", excel, "Tax_Calculation_Output.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Please upload a CSV file to begin..")





    