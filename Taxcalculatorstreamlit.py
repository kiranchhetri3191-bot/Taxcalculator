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
    border-radius: 6px !importa
