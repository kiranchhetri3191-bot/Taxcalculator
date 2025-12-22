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
    page_icon="logo.png",
    layout="wide"
)

# ---------------- SIDEBAR TOGGLE ----------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=True)

# ---------------- CSS ----------------
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
        padding: 3rem !
