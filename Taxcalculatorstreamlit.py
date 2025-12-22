import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from matplotlib.ticker import FuncFormatter

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Indian Income Tax Calculator",
    page_icon="💰",
    layout="wide"
)

# ================= SIDEBAR =================
st.sidebar.title("⚙ Controls")
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type="csv")
st.sidebar.info("Supports large CSV (50k–100k rows)")

# ================= SAFE THEME =================
if dark_mode:
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #EAEAEA;
    }
    h1, h2, h3, h4 {
        color: #FFFFFF;
    }
    .block-container
