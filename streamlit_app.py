import streamlit as st
import pandas as pd
import requests
import altair as alt

st.set_page_config(page_title="Monitoring Pojazdów GZM", page_icon="🚍")

st.title("🚍 Monitoring Pojazdów GZM")
st.write("Aplikacja wizualizuje dane o lokalizacji pojazdów transportu publicznego GZM w czasie rzeczywistym.")

# --- Pobieranie i cachowanie danych ---
@st.cache_data(ttl=60)
def fetch_data():
    """Pobiera dane z API SDIP GZM i zwraca je jako obiekt JSON."""
    url = "https://sdip.transportgzm.pl/main?action=v"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd podczas pobierania danych: {e}")
        return None

vehicle_data = fetch_data()

if vehicle_data:
    df = pd.DataFrame(vehicle_data)
    df['lineLabel'] = df['lineLabel'].astype(str)

    st.header("Liczba pojazdów na linii")

    line_counts = df['lineLabel'].value_counts().reset_index()
    line_counts.columns = ['lineLabel', 'count']

    chart = alt.Chart(line_counts).mark_bar().encode(
        x=alt.X('lineLabel:N', title='Numer Linii', sort='-y'),
        y=alt.Y('count:Q', title='Liczba Pojazdów'),
        tooltip=[alt.Tooltip('lineLabel', title='Linia'), alt.Tooltip('count', title='Liczba pojazdów')]
    ).properties(
        title='Aktualna liczba pojazdów na poszczególnych liniach'
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
    
    st.divider() 

    st.header("Pojazdy na linii")

    filter_input = st.text_input("Filtruj po liniach (wpisz numery po przecinku, np. 41, 669, M1)")

    if filter_input:
        selected_lines = [line.strip() for line in filter_input.split(',')]
        filtered_df = df[df['lineLabel'].isin(selected_lines)]
    else:
        filtered_df = df

    table_display_df = filtered_df[['trip', 'id']].copy()
    table_display_df['id'] = table_display_df['id'].str.replace('_', '/')
    table_display_df = table_display_df.rename(columns={'id': 'numer taborowy'})

    table_display_df['brygada'] = table_display_df['trip'].str[:-2]
    table_display_df['nr kursu'] = table_display_df['trip'].str.split('/').str[1]
    
    table_display_df = table_display_df.sort_values(by='trip')
    final_df_to_display = table_display_df[['brygada', 'nr kursu', 'numer taborowy']]
    
    st.write(f"Znaleziono **{len(final_df_to_display)}** pojazdów.")
    
    st.dataframe(final_df_to_display, use_container_width=True, hide_index=True)

else:
    st.warning("Nie udało się załadować danych o pojazdach. Spróbuj odświeżyć stronę za chwilę.")