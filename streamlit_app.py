import streamlit as st

# Verificar matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    st.error("El módulo matplotlib no está instalado. Por favor, agrega `matplotlib` a tu entorno (pip install matplotlib) y vuelve a intentar.")
    st.stop()

import pandas as pd
import requests
from datetime import date, timedelta

st.set_page_config(page_title="Carry Trade USD/ARS", layout="wide")
st.title("Simulación USD/ARS: Breakevens y Bandas de Crawling Peg")
st.markdown(
    "Visualiza los breakevens de carry trades contra un corredor dinámico de crawling peg, "
    "y marca las elecciones argentinas (26/10/2025)."
)

# Parámetros de usuario
mep_input = st.number_input("MEP actual (ARS/USD)", min_value=0.0, value=1250.0, step=1.0)
use_manual = st.checkbox("Usar valor MEP manual", value=False)

if st.button("Calcular"):
    # 1. Definición de tickers y payoff
    tickers = {
        "S16A5": date(2025, 4, 16), "S28A5": date(2025, 4, 28),
        "S16Y5": date(2025, 5, 16), "S30Y5": date(2025, 5, 30),
        "S18J5": date(2025, 6, 18), "S30J5": date(2025, 6, 30),
        "S31L5": date(2025, 7, 31), "S15G5": date(2025, 8, 15),
        "S29G5": date(2025, 8, 29), "S12S5": date(2025, 9, 12),
        "S30S5": date(2025, 9, 30), "T17O5": date(2025, 10, 15),
        "S31O5": date(2025, 10, 31), "S10N5": date(2025, 11, 10),
        "S28N5": date(2025, 11, 28), "T15D5": date(2025, 12, 15),
        "T30E6": date(2026, 1, 30), "T13F6": date(2026, 2, 13),
        "T30J6": date(2026, 6, 30), "T15E7": date(2027, 1, 15),
        "TTM26": date(2026, 3, 16), "TTJ26": date(2026, 6, 30),
        "TTS26": date(2026, 9, 15), "TTD26": date(2026, 12, 15)
    }
    payoff = {
        "S16A5": 131.211, "S28A5": 130.813, "S16Y5": 136.861, "S30Y5": 136.331,
        "S18J5": 147.695, "S30J5": 146.607, "S31L5": 147.74,  "S15G5": 146.794,
        "S29G5": 157.7,   "S12S5": 158.977, "S30S5": 159.734, "T17O5": 158.872,
        "S31O5": 132.821, "S10N5": 122.254, "S28N5": 123.561, "T15D5": 170.838,
        "T30E6": 142.222, "T13F6": 144.966, "T30J6": 144.896, "T15E7": 160.777,
        "TTM26": 135.238, "TTJ26": 144.629, "TTS26": 152.096, "TTD26": 161.144
    }

    # 2. Obtener MEP
    if not use_manual:
        try:
            mep_data = requests.get('https://data912.com/live/mep', timeout=5).json()
            mep = pd.DataFrame(mep_data).close.median()
        except:
            st.warning("Error al obtener MEP automático, usando valor manual.")
            mep = mep_input
    else:
        mep = mep_input

    # 3. Descargar precios
    notes = requests.get('https://data912.com/live/arg_notes').json()
    bonds = requests.get('https://data912.com/live/arg_bonds').json()
    df = pd.DataFrame(notes + bonds)

    # 4. Calcular breakevens
    carry = (
        df[df.symbol.isin(tickers)]
          .set_index('symbol')
          .assign(
              payoff     = lambda d: d.index.map(payoff),
              expiration = lambda d: d.index.map(tickers),
              BE         = lambda d: mep * (d.payoff / d.c)
          )
          .sort_values('expiration')
    )

    # 5. Gráfico
    dates_be = carry['expiration'].tolist()
    prices_be = carry['BE'].tolist()
    start_band = date(2025, 4, 14)
    months_off = [(d - start_band).days / 30 for d in [start_band] + dates_be]
    upper_band = [1400 * (1.01)**m for m in months_off]
    lower_band = [1000 * (0.99)**m for m in months_off]

    fig, ax = plt.subplots(figsize=(14,7), dpi=150, facecolor='black')
    ax.set_facecolor('black')
    ax.grid(color='white', linestyle='--', alpha=0.2)
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('white'); ax.spines['left'].set_color('white')

    ax.plot([start_band] + dates_be, upper_band, color='red', linestyle='--', lw=2, label='Banda sup')
    ax.plot([start_band] + dates_be, lower_band, color='green', linestyle='--', lw=2, label='Banda inf')
    ax.fill_between([start_band] + dates_be, lower_band, upper_band, color='gray', alpha=0.15)
    ax.plot(dates_be, prices_be, color='cyan', lw=3, marker='o', label='Breakevens')

    elec = date(2025, 10, 26)
    ax.axvline(elec, color='yellow', lw=2)
    ax.text(elec, ax.get_ylim()[1]*0.95, 'Elecciones 26/10/2025', color='yellow', rotation=90,
            va='top', ha='right', fontsize=12)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    ax.legend(facecolor='white', framealpha=0.3)
    st.pyplot(fig)

    # 6. Tabla
    table = carry.reset_index()[['symbol','expiration','BE']].copy()
    table.columns = ['Activo','Vencimiento','Break-even (ARS/USD)']
    table['Días restantes'] = table['Vencimiento'].apply(lambda d: (d - date.today()).days)
    st.dataframe(table)

    st.markdown(
        """
        **Explicación**:
        - *Activo*: Ticker del bono o nota.
        - *Vencimiento*: Fecha de pago del payoff.
        - *Break-even*: Tipo de cambio necesario para no ganar ni perder en ARS.
        - *Días restantes*: Días hasta el vencimiento.
        """
    )
