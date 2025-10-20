import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import random
import json
import os

# ------------------------------
# KONFIGURACJA
# ------------------------------

# Pobieranie secretu z Streamlit
google_creds_json = st.secrets["GOOGLE_CREDS"]["value"]
credentials_dict = json.loads(google_creds_json)

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Uwierzytelnienie z użyciem słownika
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

# ------------------------------
# OTWARCIE ARKUSZA
# ------------------------------

SHEET_ID = "1vxN9KLkqU7QEsFsxucbNjUuRM-ZNwCjBM8EGYMKQBWU"  # Twój ID arkusza
sheet = client.open_by_key(SHEET_ID).sheet1

# ------------------------------
# POBRANIE DANYCH Z ARKUSZA
# ------------------------------

data = sheet.get_all_records(expected_headers=[
    'Słówko', 'Przykładowe zdanie / zdania', 'Nie znam', 'Znam trochę', 'Bardzo dobrze znam'
])

df = pd.DataFrame(data)

# ------------------------------
# MAPOWANIE KOLUMN
# ------------------------------

col_map = {
    "Nie znam": df.columns.get_loc("Nie znam") + 1,
    "Znam trochę": df.columns.get_loc("Znam trochę") + 1,
    "Bardzo dobrze znam": df.columns.get_loc("Bardzo dobrze znam") + 1
}

# ------------------------------
# STREAMLIT QUIZ
# ------------------------------

st.title("Quiz słówek")

if 'current_word_index' not in st.session_state:
    st.session_state.current_word_index = None

# Wybór słówka, które jeszcze nie było ocenione
df_not_done = df[
    (df['Nie znam'] != 1) &
    (df['Znam trochę'] != 1) &
    (df['Bardzo dobrze znam'] != 1)
]

if df_not_done.empty:
    st.write("Wszystkie słówka zostały ocenione!")
else:
    if st.session_state.current_word_index is None:
        random_word = df_not_done.sample(1).iloc[0]
        st.session_state.current_word_index = random_word.name

    current_word = df.loc[st.session_state.current_word_index]
    slowo = current_word['Słówko']
    przyklad = current_word['Przykładowe zdanie / zdania']
    st.subheader(f"Słówko: {slowo}")
    st.write(f"Przykład: {przyklad}")

    def zapisz_wynik(kolumna_nazwa):
        row_number = st.session_state.current_word_index + 2
        col_number = col_map[kolumna_nazwa]
        sheet.update_cell(row_number, col_number, 1)
        st.session_state.current_word_index = None  # następne słówko

    st.button("Nie znam", on_click=zapisz_wynik, args=("Nie znam",))
    st.button("Znam trochę", on_click=zapisz_wynik, args=("Znam trochę",))
    st.button("Bardzo dobrze znam", on_click=zapisz_wynik, args=("Bardzo dobrze znam",))
