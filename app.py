import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date

st.set_page_config(page_title="Dozajsan İş Takip", page_icon="📊", layout="wide")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def init_connection():
    # Streamlit Secrets üzerinden güvenli bağlantı (credentials.json dosyası yerine)
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Dozajsan_Is_Takip").sheet1
    return sheet

try:
    sheet = init_connection()
except Exception as e:
    st.error(f"Google Drive bağlantı hatası: {e}")
    st.stop()
