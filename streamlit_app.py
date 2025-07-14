import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora de Carry Trade",
    page_icon="💹",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS (OPCIONAL) ---
# Se inyecta CSS para mejorar la apariencia de las tarjetas de métricas y otros elementos.
st.markdown("""
<style>
    /* Estilo para contenedores de métricas */
    [data-testid="stMetric"] {
        background-color: #262730;
        border: 1px solid #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Estilo para el valor de la métrica */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }
    /* Estilo para la etiqueta de la métrica */
    [data-testid="stMetricLabel"] {
        font-size: 16px;
        color: #A0A0A0;
    }
    /* Estilo para las pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1E1E1E;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNCIONES PRINCIPALES ---

def calculate_carry_trade_table(banda_superior_inicio, banda_superior_finish,
                                banda_inferior_inicio, banda_inferior_finish):
    """
    Calcula la matriz de escenarios de carry trade.
    Genera 6 puntos de precio para el inicio y el final, espaciados uniformemente entre las bandas.
    """
    # Crear un rango de 6 valores de venta y compra entre las bandas inferior y superior.
    venta_usd_inicio_values = np.linspace(banda_inferior_inicio, banda_superior_inicio, 6)
    compra_usd_finish_values = np.linspace(banda_inferior_finish, banda_superior_finish, 6)

    # Crear la matriz de resultados calculando el retorno para cada par de venta/compra.
    results_matrix = np.zeros((6, 6))
    for i, venta in enumerate(venta_usd_inicio_values):
        for j, compra in enumerate(compra_usd_finish_values):
            if compra != 0:
                # Fórmula de retorno: ((Precio Venta / Precio Compra) - 1) * 100
                return_pct = ((venta / compra) - 1) * 100
                results_matrix[i, j] = return_pct
            else:
                results_matrix[i, j] = np.nan # Evitar división por cero

    # Crear un DataFrame de Pandas con los resultados para una mejor visualización.
    df = pd.DataFrame(
        results_matrix,
        index=[f"${v:.2f}" for v in venta_usd_inicio_values],
        columns=[f"${c:.2f}" for c in compra_usd_finish_values]
    )
    df.index.name = "VENTA USD INICIO"
    df.columns.name = "COMPRA USD FINISH"
    return df

def color_gradient_style(val):
    """
    Aplica un degradado de color a las celdas de la tabla basado en el valor del retorno.
    Verdes para ganancias, Rojos para pérdidas.
    """
    if pd.isna(val):
        return 'background-color: #333333' # Color para valores nulos
    
    # Paleta de colores mejorada (de rojo intenso a verde intenso)
    if val > 15: color = '#1a9850'  # Verde oscuro
    elif val > 10: color = '#66bd63'
    elif val > 5: color = '#a6d96a'
    elif val > 0: color = '#d9ef8b'   # Verde claro
    elif val == 0: color = '#ffffbf' # Amarillo neutral
    elif val > -5: color = '#fee08b'  # Naranja claro
    elif val > -10: color = '#fdae61'
    elif val > -15: color = '#f46d43'
    else: color = '#d73027'  # Rojo intenso
    
    return f'background-color: {color}; color: {"black" if val > -5 and val < 5 else "white"};'

def display_instrument_inputs(suffix, defaults):
    """
    Crea los campos de entrada para un instrumento en el panel lateral.
    """
    st.subheader(f"Instrumento: {defaults['ticker']}")
    
    # Usar columnas para organizar mejor los inputs
    col1, col2 = st.columns(2)
    with col1:
        ticker = st.text_input("Ticker", defaults['ticker'], key=f"ticker{suffix}")
        inicio_price = st.number_input("Precio Inicio", value=defaults['inicio_price'], format="%.2f", key=f"inicio_price{suffix}")
        banda_superior_inicio = st.number_input("Banda Superior Inicio", value=defaults['bs_inicio'], format="%.2f", key=f"bs_inicio{suffix}")
        banda_inferior_inicio = st.number_input("Banda Inferior Inicio", value=defaults['bi_inicio'], format="%.2f", key=f"bi_inicio{suffix}")

    with col2:
        cotizacion_date = st.date_input("Fecha de Cotización", datetime.date.today(), key=f"cotizacion_date{suffix}")
        finish_price = st.number_input("Precio Finish", value=defaults['finish_price'], format="%.2f", key=f"finish_price{suffix}")
        banda_superior_finish = st.number_input("Banda Superior Finish", value=defaults['bs_finish'], format="%.2f", key=f"bs_finish{suffix}")
        banda_inferior_finish = st.number_input("Banda Inferior Finish", value=defaults['bi_finish'], format="%.2f", key=f"bi_finish{suffix}")
    
    expiry_date = st.date_input("Fecha de Vencimiento", datetime.date.today() + datetime.timedelta(days=defaults['days_to_expiry']), key=f"expiry_date{suffix}")
    
    # Retornar todos los valores en un diccionario para fácil acceso
    return {
        "ticker": ticker,
        "inicio_price": inicio_price,
        "finish_price": finish_price,
        "cotizacion_date": cotizacion_date,
        "expiry_date": expiry_date,
        "banda_superior_inicio": banda_superior_inicio,
        "banda_superior_finish": banda_superior_finish,
        "banda_inferior_inicio": banda_inferior_inicio,
        "banda_inferior_finish": banda_inferior_finish
    }

# --- INTERFAZ DE USUARIO (UI) ---

st.title("💹 Calculadora de Escenarios de Carry Trade")
st.markdown("Una herramienta visual para analizar los posibles rendimientos de operaciones de carry trade, comparando diferentes escenarios de precios de entrada y salida.")

# --- PANEL LATERAL CON INPUTS ---
with st.sidebar:
    st.header("⚙️ Parámetros de Entrada")
    
    # Valores por defecto para cada instrumento
    defaults1 = {
        'ticker': 'S30S5', 'inicio_price': 135.45, 'finish_price': 158.98,
        'bs_inicio': 1400.00, 'bi_inicio': 1000.00, 'bs_finish': 1477.47,
        'bi_finish': 944.67, 'days_to_expiry': 60
    }
    defaults2 = {
        'ticker': 'TTD26', 'inicio_price': 94.00, 'finish_price': 161.14,
        'bs_inicio': 1400.00, 'bi_inicio': 1000.00, 'bs_finish': 1694.47,
        'bi_finish': 789.67, 'days_to_expiry': 180
    }

    # Crear expanders para cada instrumento para una UI más limpia
    with st.expander("Primer Instrumento", expanded=True):
        params1 = display_instrument_inputs(1, defaults1)

    with st.expander("Segundo Instrumento"):
        params2 = display_instrument_inputs(2, defaults2)

# --- ÁREA PRINCIPAL CON RESULTADOS ---

# Crear pestañas para mostrar los resultados de cada instrumento
tab1, tab2 = st.tabs([f"📊 {params1['ticker']}", f"📊 {params2['ticker']}"])

# Procesar y mostrar resultados para el Instrumento 1
with tab1:
    st.header(f"Análisis para {params1['ticker']}")
    
    # Calcular días al vencimiento
    days_to_expiry1 = (params1['expiry_date'] - params1['cotizacion_date']).days
    
    # Mostrar métricas clave en columnas
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Precio Inicio", f"${params1['inicio_price']:.2f}")
    m_col2.metric("Precio Finish", f"${params1['finish_price']:.2f}")
    m_col3.metric("Días al Venc.", f"{days_to_expiry1} días")
    tna_estimada = (((params1['finish_price'] / params1['inicio_price']) - 1) * (365 / days_to_expiry1) * 100) if days_to_expiry1 > 0 else 0
    m_col4.metric("TNA Estimada", f"{tna_estimada:.2%}")

    # Mostrar tabla de resultados
    st.subheader("Matriz de Retornos (%)")
    results_df1 = calculate_carry_trade_table(
        params1['banda_superior_inicio'], params1['banda_superior_finish'],
        params1['banda_inferior_inicio'], params1['banda_inferior_finish']
    )
    st.dataframe(results_df1.style.applymap(color_gradient_style).format("{:.2f}%"), use_container_width=True)
    st.caption("La tabla muestra el retorno porcentual. Eje vertical (filas): Precio de venta inicial. Eje horizontal (columnas): Precio de compra final.")

# Procesar y mostrar resultados para el Instrumento 2
with tab2:
    st.header(f"Análisis para {params2['ticker']}")
    
    days_to_expiry2 = (params2['expiry_date'] - params2['cotizacion_date']).days
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Precio Inicio", f"${params2['inicio_price']:.2f}")
    m_col2.metric("Precio Finish", f"${params2['finish_price']:.2f}")
    m_col3.metric("Días al Venc.", f"{days_to_expiry2} días")
    tna_estimada2 = (((params2['finish_price'] / params2['inicio_price']) - 1) * (365 / days_to_expiry2) * 100) if days_to_expiry2 > 0 else 0
    m_col4.metric("TNA Estimada", f"{tna_estimada2:.2%}")

    st.subheader("Matriz de Retornos (%)")
    results_df2 = calculate_carry_trade_table(
        params2['banda_superior_inicio'], params2['banda_superior_finish'],
        params2['banda_inferior_inicio'], params2['banda_inferior_finish']
    )
    st.dataframe(results_df2.style.applymap(color_gradient_style).format("{:.2f}%"), use_container_width=True)
    st.caption("La tabla muestra el retorno porcentual. Eje vertical (filas): Precio de venta inicial. Eje horizontal (columnas): Precio de compra final.")

# --- SECCIÓN DE AYUDA ---
with st.expander("ℹ️ Cómo utilizar esta calculadora"):
    st.markdown("""
    1.  **Configure los Parámetros:** En el panel lateral, ajuste los valores para cada instrumento financiero que desee analizar. Puede expandir o contraer la sección de cada uno.
    2.  **Analice las Métricas:** Las tarjetas en la parte superior de cada pestaña resumen los datos más importantes, incluyendo una TNA estimada.
    3.  **Explore la Matriz de Retornos:**
        * La tabla principal muestra los retornos porcentuales para una gama de escenarios.
        * Los colores indican la rentabilidad: **verde** para ganancias y **rojo** para pérdidas, con intensidades variables.
        * **Eje Vertical:** Corresponde a los posibles precios a los que usted *vende* dólares al inicio de la operación.
        * **Eje Horizontal:** Corresponde a los posibles precios a los que usted *compra* dólares al final de la operación.
    4.  **Compare Instrumentos:** Navegue entre las pestañas para comparar fácilmente los resultados de los dos instrumentos configurados.
    """)

