from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Google Drive Destekli İş Takip Sistemi",
    page_icon="📊",
    layout="wide",
)

# --- GOOGLE SHEETS BAĞLANTISI ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


@st.cache_resource
def init_connection():
  creds = ServiceAccountCredentials.from_json_keyfile_name(
      "credentials.json", scope
  )
  client = gspread.authorize(creds)
  sheet = client.open("Dozajsan_Is_Takip").sheet1
  return sheet


try:
  sheet = init_connection()
except Exception as e:
  st.error(
      f"Google Drive bağlantı hatası! Lütfen 'credentials.json' dosyanızı ve"
      f" tablo adını ('Dozajsan_Is_Takip') kontrol edin. Hata: {e}"
  )
  st.stop()


def load_data_from_sheet():
  data = sheet.get_all_records()
  return data


def save_data_to_sheet(tasks):
  sheet.clear()
  if tasks:
    df = pd.DataFrame(tasks)
    sheet.update(
        [df.columns.values.tolist()] + df.values.tolist()
    )


tasks = load_data_from_sheet()

st.title("🏭 Dozajsan | Google Drive Destekli Üretim & Satınalma Takip Paneli")
st.markdown("Veriler doğrudan Google Drive hesabınızdaki E-Tabloda saklanır.")

# ----------------- YENİ İŞ / SÜREÇ EKLE (SOL MENÜ) -----------------
st.sidebar.header("➕ Yeni Süreç / İş Ekle")
with st.sidebar.form("add_task_form"):
  process_type = st.selectbox(
      "Süreç Türü", ["Üretim Planlama", "Satınalma", "Montaj & Test", "Genel İş"]
  )
  project_name = st.text_input("Proje / Müşteri Adı (Örn: Nurol Teknoloji)")
  task_title = st.text_input("İş / Parça / Malzeme Tanımı")
  assigned_to = st.selectbox(
      "İşi Başlatan / Sorumlu",
      [
          "Mehmet Fahrettin Çemenyemez",
          "Satınalma Ekibi",
          "Üretim Ekibi",
          "Montaj Ekibi",
          "AR-GE",
      ],
  )
  status = st.selectbox(
      "Mevcut Durum",
      [
          "1. Planlandı / Beklemede",
          "2. Satınalma Aşamasında",
          "3. Üretimde",
          "4. Montajda",
          "5. Kalite / Test Aşamasında",
          "6. Tamamlandı",
      ],
  )
  completed_by = st.text_input("Tamamlayan Kişi / Birim")
  next_step = st.text_area("Sonraki Adım / Sıradaki İşlem")
  due_date = st.date_input("Termin / Hedef Tarih", date.today())
  notes = st.text_area("Detaylı Teknik Notlar")

  submitted = st.form_submit_button("Drive'a Kaydet")
  if submitted:
    if project_name and task_title:
      new_task = {
          "id": len(tasks) + 1,
          "process_type": process_type,
          "project": project_name,
          "title": task_title,
          "assigned": assigned_to,
          "status": status,
          "completed_by": completed_by if completed_by else "-",
          "next_step": next_step if next_step else "-",
          "due_date": str(due_date),
          "notes": notes,
      }
      tasks.append(new_task)
      save_data_to_sheet(tasks)
      st.sidebar.success("Başarıyla Google Drive'a kaydedildi!")
      st.rerun()
    else:
      st.sidebar.error("Lütfen Proje Adı ve İş Tanımı alanlarını doldurun.")

# ----------------- ANA EKRAN & TABLO -----------------
if tasks:
  df = pd.DataFrame(tasks)
  st.subheader("📊 Google Drive Senkronize Süreç Tablosu")
  st.dataframe(df, use_container_width=True)

  st.markdown("---")
  st.subheader("✏️ Süreç Güncelle / İlerlet")
  task_ids = [t["id"] for t in tasks]
  selected_task_id = st.selectbox(
      "İş ID Seçin",
      task_ids,
      format_func=lambda x: next(
          (
              f"ID: {t['id']} | {t['project']} - {t['title']}"
              for t in tasks
              if t["id"] == x
          ),
          "",
      ),
  )

  if selected_task_id:
    selected_task = next((t for t in tasks if t["id"] == selected_task_id), None)
    if selected_task:
      with st.form("update_form"):
        col1, col2 = st.columns(2)
        with col1:
          new_status = st.selectbox(
              "Durumu Güncelle",
              [
                  "1. Planlandı / Beklemede",
                  "2. Satınalma Aşamasında",
                  "3. Üretimde",
                  "4. Montajda",
                  "5. Kalite / Test Aşamasında",
                  "6. Tamamlandı",
              ],
          )
          new_completed = st.text_input(
              "Tamamlayan Kişi", value=selected_task["completed_by"]
          )
        with col2:
          new_next = st.text_area(
              "Sonraki Adım", value=selected_task["next_step"]
          )
          new_notes = st.text_input("Notlar", value=selected_task["notes"])

        if st.form_submit_button("Güncellemeyi Drive'a Kaydet"):
          for t in tasks:
            if t["id"] == selected_task_id:
              t["status"] = new_status
              t["completed_by"] = new_completed
              t["next_step"] = new_next
              t["notes"] = new_notes
          save_data_to_sheet(tasks)
          st.success("Google Drive tablosu güncellendi!")
          st.rerun()
else:
  st.info("Tablonuzda henüz veri yok. Sol menüden ilk süreci ekleyebilirsiniz.")