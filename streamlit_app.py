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
    df['lineId'] = df['lineId'].astype(str)

    st.header("Liczba pojazdów na linii")

    line_counts = df['lineId'].value_counts().reset_index()
    line_counts.columns = ['lineId', 'count']

    chart = alt.Chart(line_counts).mark_bar().encode(
        x=alt.X('lineId:N', title='Numer Linii', sort='-y'),
        y=alt.Y('count:Q', title='Liczba Pojazdów'),
        tooltip=[alt.Tooltip('lineId', title='Linia'), alt.Tooltip('count', title='Liczba pojazdów')]
    ).properties(
        title='Aktualna liczba pojazdów na poszczególnych liniach'
    )
    st.altair_chart(chart, use_container_width=True)
    
    st.divider() 

    st.header("Szczegółowa tabela pojazdów")

    filter_input = st.text_input("Filtruj po liniach (wpisz numery po przecinku, np. 6, 19, M1)")

    if filter_input:
        selected_lines = [line.strip() for line in filter_input.split(',')]
        filtered_df = df[df['lineLabel'].isin(selected_lines)]
    else:
        filtered_df = df

    table_display_df = filtered_df[['trip', 'id']]
    table_display_df = table_display_df.sort_values(by='trip')
    
    st.write(f"Znaleziono **{len(table_display_df)}** pojazdów.")
    
    st.dataframe(table_display_df, use_container_width=True, hide_index=True)

else:
    st.warning("Nie udało się załadować danych o pojazdach. Spróbuj odświeżyć stronę za chwilę.")