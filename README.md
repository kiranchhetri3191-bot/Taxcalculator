# Indian Income Tax Calculator (Old vs New Regime)

A Python-based web application to calculate and compare income tax liability
under the **Old and New Indian Income Tax Regimes** using real tax slabs,
surcharge, cess, and standard deduction rules.

This project is designed for **practical payroll, HR, and tax-planning use cases**.

---

## 🚀 Features

- 📂 Upload employee data using CSV files
- 🧮 Accurate tax calculation for Old & New Regimes
- 📊 Visual comparison graph (Old vs New Regime)
- 📄 Download tax reports in **PDF**
- 📄 Summary report export **PDF**
- 📁 Export results to **Excel** and **CSV**
- 💡 Helps identify the most beneficial tax regime

---

## 🛠 Tech Stack

- Python
- Pandas
- Streamlit
- Matplotlib
- ReportLab
- OpenPyXL

---

## 📂 Input CSV Format

The uploaded CSV file must contain the following columns:

- Name
- Department
- Age
- GrossIncome
- Deductions

Example:

Name,Department,Age,GrossIncome,Deductions  
Rahul,Finance,32,900000,150000  
Anita,HR,45,1200000,200000

## ⚠️ Practical Reliability & Limitations

- Calculations are based on user-provided data
- The tool does not consider all possible exemptions and special cases
- Actual tax liability may vary depending on individual circumstances
- Tax laws may change over time

## ⚖️ Disclaimer

This application is developed for educational and estimation purposes only.
It is not intended to provide legal or professional tax advice.
Users are advised to consult a qualified tax professional before filing income tax returns.

## 📅 Tax Year

Tax rules applied as per:
- Financial Year (FY): 2024–25
- Assessment Year (AY): 2025–26

## ▶️ How to Run the Project

1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Run the app:
   streamlit run app.py

## © Copyright & Usage

This project is an independently developed academic project.
It uses open-source libraries and publicly available tax rules.
No proprietary or confidential code has been used.

You are free to use this project for learning and non-commercial purposes.

👤 Author

Kiran Chhetri
Bachelor of Commerce (B.Com)
Accounting & Taxation



