import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import date, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Carry Trade USD/ARS Interactivo", layout="wide")

# --- DATOS ESTÁTICOS Y CONFIGURACIÓN ---
# Se definen fuera de las funciones para que no se redeclaren innecesariamente
TICKERS_DATA = {
    "S16A5": {"venc": date(2025, 4, 16), "payoff": 131.211}, "S28A5": {"venc": date(2025, 4, 28), "payoff": 130.813},
    "S16Y5": {"venc": date(2025, 5, 16), "payoff": 136.861}, "S30Y5": {"venc": date(2025, 5, 30), "payoff": 136.331},
    "S18J5": {"venc": date(2025, 6, 18), "payoff": 147.695}, "S30J5": {"venc": date(2025, 6, 30), "payoff": 146.607},
    "S31L5": {"venc": date(2025, 7, 31), "payoff": 147.740}, "S15G5": {"venc": date(2025, 8, 15), "payoff": 146.794},
    "S29G5": {"venc": date(2025, 8, 29), "payoff": 157.700}, "S12S5": {"venc": date(2025, 9, 12), "payoff": 158.977},
    "S30S5": {"venc": date(2025, 9, 30), "payoff": 159.734}, "T17O5": {"venc": date(2025, 10, 15), "payoff": 158.872},
    "S31O5": {"venc": date(2025, 10, 31), "payoff": 132.821}, "S10N5": {"venc": date(2025, 11, 10), "payoff": 122.254},
    "S28N5": {"venc": date(2025, 11, 28), "payoff": 123.561}, "T15D5": {"venc": date(2025, 12, 15), "payoff": 170.838},
    "T30E6": {"venc": date(2026, 1, 30), "payoff": 142.222}, "T13F6": {"venc": date(2026, 2, 13), "payoff": 144.966},
    "T30J6": {"venc": date(2026, 6, 30), "payoff": 144.896}, "T15E7": {"venc": date(2027, 1, 15), "payoff": 160.777},
    "TTM26": {"venc": date(2026, 3, 16), "payoff": 135.238}, "TTJ26": {"venc": date(2026, 6, 30), "payoff": 144.629},
    "TTS26": {"venc": date(2026, 9, 15), "payoff": 152.096}, "TTD26": {"venc": date(2026, 12, 15), "payoff": 161.144}
}
FECHA_ELECCIONES = date(2025, 10, 26)

# --- CACHING Y CARGA DE DATOS ---
@st.cache_data(ttl=300) # Cache por 5 minutos para no sobrecargar la API
def load_data():
    """Carga los precios de bonos y notas desde la API."""
    try:
        notes = requests.get('https://data912.com/live/arg_notes', timeout=10).json()
        bonds = requests.get('https://data912.com/live/arg_bonds', timeout=10).json()
        return pd.DataFrame(notes + bonds)
    except requests.RequestException as e:
        st.error(f"Error al cargar datos de mercado: {e}")
        return None

# --- FUNCIONES DE LA APLICACIÓN ---
def get_mep_price(use_manual, manual_mep):
    """Obtiene el precio del MEP, ya sea automático o manual."""
    if not use_manual:
        try:
            mep_data = requests.get('https://data912.com/live/mep', timeout=5).json()
            return pd.DataFrame(mep_data)['close'].median()
        except (requests.RequestException, KeyError):
            st.warning("No se pudo obtener el MEP automático. Usando valor manual.", icon="⚠️")
            return manual_mep
    return manual_mep

def create_interactive_chart(df_carry, upper_band, lower_band, band_dates):
    """Crea un gráfico interactivo con Plotly."""
    fig = go.Figure()

    # 1. Banda Superior
    fig.add_trace(go.Scatter(
        x=band_dates, y=upper_band,
        mode='lines',
        line=dict(color='rgba(255, 75, 75, 0.8)', width=2, dash='dash'),
        name='Banda Superior (Peg +1%/mes)'
    ))

    # 2. Banda Inferior con relleno
    fig.add_trace(go.Scatter(
        x=band_dates, y=lower_band,
        fill='tonexty', # Rellena el área hasta la traza anterior
        mode='lines',
        line=dict(color='rgba(50, 205, 50, 0.8)', width=2, dash='dash'),
        fillcolor='rgba(128,128,128,0.2)',
        name='Banda Inferior (Peg -1%/mes)'
    ))

    # 3. Breakevens de Carry Trade
    fig.add_trace(go.Scatter(
        x=df_carry['expiration'],
        y=df_carry['BE'],
        mode='lines+markers+text',
        name='Breakevens Carry Trade',
        line=dict(color='cyan', width=3),
        marker=dict(size=8, symbol='circle'),
        text=df_carry.index,
        textposition="top center",
        textfont=dict(color='white', size=10),
        hoverinfo='text',
        hovertext=[
            f"<b>Activo:</b> {row.Index}<br>"
            f"<b>Vencimiento:</b> {row.expiration:%d-%b-%Y}<br>"
            f"<b>Breakeven:</b> ${row.BE:,.2f}"
            for row in df_carry.itertuples()
        ]
    ))
    
    # 4. Línea vertical para las elecciones (CORREGIDO)
    fig.add_vline(
        x=FECHA_ELECCIONES,
        line_width=2,
        line_dash="dot",
        line_color="yellow"
    )
    # Se añade la anotación por separado para evitar el error
    fig.add_annotation(
        x=FECHA_ELECCIONES,
        y=df_carry['BE'].max() * 0.95, # Posición Y relativa al máximo del gráfico
        yref="y",
        text="Elecciones 26/10",
        showarrow=True,
        arrowhead=1,
        ax=20,  # Desplazamiento en X del texto desde la flecha
        ay=-40, # Desplazamiento en Y del texto desde la flecha
        font=dict(color="yellow", size=12)
    )

    # 5. Estilo y Layout del Gráfico
    fig.update_layout(
        template='plotly_dark',
        title='Simulación Interactiva de Carry Trade: Breakevens vs. Crawling Peg',
        yaxis_title='Tipo de Cambio (ARS/USD)',
        xaxis_title='Fecha de Vencimiento',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        hovermode='x unified'
    )
    return fig

# --- INTERFAZ DE USUARIO (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Parámetros de Simulación")

    # Parámetros MEP
    use_manual_mep = st.toggle("Usar valor MEP manual", value=False)
    manual_mep_input = st.number_input(
        "Valor MEP Manual (ARS/USD)",
        min_value=0.0,
        value=1250.0,
        step=1.0,
        disabled=not use_manual_mep
    )
    st.markdown("---")
    st.info("Las bandas de crawling peg son fijas para esta visualización (Sup: +1% mensual, Inf: -1% mensual).")


# --- CUERPO PRINCIPAL DE LA APLICACIÓN ---
st.title("Simulador de Carry Trade USD/ARS 🇦🇷")
st.markdown(
    """
    Esta herramienta interactiva calcula y visualiza los **precios de breakeven (equilibrio)** para operaciones de *carry trade* con bonos y letras argentinas.
    Compara estos puntos contra un **corredor de tipo de cambio (crawling peg)** fijo.
    """
)

# --- LÓGICA PRINCIPAL ---
with st.spinner('Cargando datos de mercado y calculando...'):
    df_mercado = load_data()

    if df_mercado is not None and not df_mercado.empty:
        # 1. Obtener MEP
        mep = get_mep_price(use_manual_mep, manual_mep_input)
        st.sidebar.metric("MEP Utilizado para Cálculo", f"${mep:,.2f}")

        # 2. Calcular Breakevens
        tickers_list = list(TICKERS_DATA.keys())
        df_carry = (
            df_mercado[df_mercado.symbol.isin(tickers_list) & df_mercado.c.notna() & (df_mercado.c > 0)]
              .set_index('symbol')
              .assign(
                  payoff=lambda d: d.index.map({k: v['payoff'] for k, v in TICKERS_DATA.items()}),
                  expiration=lambda d: pd.to_datetime(d.index.map({k: v['venc'] for k, v in TICKERS_DATA.items()})),
                  BE=lambda d: mep * (d.payoff / d.c)
              )
              .sort_values('expiration')
        )

        if not df_carry.empty:
            # 3. Calcular Bandas de Crawling Peg (Valores fijos)
            start_band = date.today()
            all_dates = sorted(df_carry['expiration'].dt.date.tolist() + [FECHA_ELECCIONES])
            band_dates = [start_band] + all_dates
            
            months_off = [(d - start_band).days / 30.44 for d in band_dates]
            # Valores fijos para las bandas
            upper_band_values = [1400 * (1.01)**m for m in months_off]
            lower_band_values = [1000 * (0.99)**m for m in months_off]

            # 4. Mostrar Gráfico
            st.header("📊 Gráfico Interactivo de Breakevens")
            interactive_chart = create_interactive_chart(df_carry, upper_band_values, lower_band_values, band_dates)
            st.plotly_chart(interactive_chart, use_container_width=True)

            # 5. Mostrar Tabla de Datos
            st.header("📄 Tabla de Datos Resumen")
            table = df_carry.reset_index()[['symbol', 'expiration', 'BE']].copy()
            table.columns = ['Activo', 'Vencimiento', 'Breakeven (ARS/USD)']
            table['Días restantes'] = table['Vencimiento'].apply(lambda d: (d.date() - date.today()).days)
            
            st.dataframe(
                table.style.format({
                    'Vencimiento': "{:%d-%m-%Y}",
                    'Breakeven (ARS/USD)': "{:,.2f}"
                }),
                use_container_width=True
            )

            st.info(
                """
                - **Breakeven (ARS/USD)**: Es el tipo de cambio Dólar MEP futuro al cual la ganancia en pesos de la inversión es cero. Si el MEP a esa fecha es mayor, se obtiene una ganancia en dólares.
                - **Bandas de Crawling Peg**: Representan un corredor hipotético del tipo de cambio con valores fijos.
                """,
                icon="💡"
            )
        else:
            st.warning("No se encontraron datos para los activos especificados después de filtrar. No se puede generar el gráfico.")
    else:
        st.error("No se pudieron cargar los datos del mercado. Intenta de nuevo más tarde.")
