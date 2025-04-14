import streamlit as st
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="Calculadora de Carry Trade", layout="wide")

st.title("Calculadora de Escenarios de Carry Trade")
st.markdown("Esta aplicación permite calcular diferentes escenarios de carry trade basados en el precio inicial, final y bandas superior e inferior.")

# Sidebar para inputs
st.sidebar.header("Datos de Entrada")

# Crear dos pestañas para diferentes instrumentos
instrument_tab1, instrument_tab2 = st.tabs(["Instrumento 1", "Instrumento 2"])

# Función para calcular la tabla de resultados
def calculate_carry_trade_table(ticker, inicio_price, finish_price, cotizacion_date, expiry_date, 
                              banda_superior_inicio, banda_superior_finish, 
                              banda_inferior_inicio, banda_inferior_finish):
    
    # Calcular rendimiento del bono
    rendimiento_bono = (finish_price / inicio_price - 1) * 100
    
    # Crear tabla de venta USD inicio vs compra USD finish
    venta_usd_inicio_values = [banda_inferior_inicio, 
                             round(banda_inferior_inicio + (banda_superior_inicio - banda_inferior_inicio) * 0.2, 2),
                             round(banda_inferior_inicio + (banda_superior_inicio - banda_inferior_inicio) * 0.4, 2),
                             round(banda_inferior_inicio + (banda_superior_inicio - banda_inferior_inicio) * 0.6, 2),
                             round(banda_inferior_inicio + (banda_superior_inicio - banda_inferior_inicio) * 0.8, 2),
                             banda_superior_inicio]
    
    compra_usd_finish_values = [banda_inferior_finish, 
                              round(banda_inferior_finish + (banda_superior_finish - banda_inferior_finish) * 0.2, 2),
                              round(banda_inferior_finish + (banda_superior_finish - banda_inferior_finish) * 0.4, 2),
                              round(banda_inferior_finish + (banda_superior_finish - banda_inferior_finish) * 0.6, 2),
                              round(banda_inferior_finish + (banda_superior_finish - banda_inferior_finish) * 0.8, 2),
                              banda_superior_finish]
    
    # Crear matriz de resultados como DataFrame
    results = []
    for venta in venta_usd_inicio_values:
        row = []
        for compra in compra_usd_finish_values:
            # Paso 1: Calcular rendimiento cambiario (vender USD al precio inicial y recomprar al precio final)
            # Si vendo USD a un precio más alto y recompro a un precio más bajo, tengo ganancia
            return_cambiario = ((venta / compra) - 1) * 100
            
            # Paso 2: Sumar el rendimiento del bono
            # El rendimiento total es la suma de ambos componentes
            return_total = round(return_cambiario + rendimiento_bono, 2)
            
            row.append(return_total)
        results.append(row)
    
    # Crear DataFrame con los resultados
    df = pd.DataFrame(results, 
                     index=[f"${venta:.2f}" for venta in venta_usd_inicio_values],
                     columns=[f"${compra:.2f}" for compra in compra_usd_finish_values])
    
    # Renombrar índice
    df.index.name = "VENTA USD INICIO"
    
    return df, venta_usd_inicio_values, compra_usd_finish_values, rendimiento_bono

# Función para aplicar formato de color a la tabla
def color_table(val):
    if val > 20:
        color = 'background-color: #2d882d'
    elif val > 10:
        color = 'background-color: #55aa55'
    elif val > 5:
        color = 'background-color: #88cc88'
    elif val > 0:
        color = 'background-color: #aaddaa'
    elif val > -5:
        color = 'background-color: #ffcccc'
    elif val > -10:
        color = 'background-color: #ff9999'
    else:
        color = 'background-color: #ff7777'
    return color

# Contenido para la pestaña 1
with instrument_tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        ticker1 = st.text_input("Ticker", "S30S5", key="ticker1")
        
        inicio_price1 = st.number_input("Precio Inicio", value=135.45, key="inicio_price1")
        finish_price1 = st.number_input("Precio Finish", value=158.98, key="finish_price1")
        
        cotizacion_date1 = st.date_input("Fecha de Cotización", 
                                      datetime.date.today(), key="cotizacion_date1")
        expiry_date1 = st.date_input("Fecha de Vencimiento", 
                                  datetime.date.today() + datetime.timedelta(days=60), key="expiry_date1")
        
        # Cálculo de días entre fechas
        dias_plazo1 = (expiry_date1 - cotizacion_date1).days
        st.write(f"Plazo: {dias_plazo1} días")
    
    with col2:
        st.subheader("Bandas")
        banda_superior_inicio1 = st.number_input("Banda Superior Inicio", value=1400.00, key="bs_inicio1")
        banda_superior_finish1 = st.number_input("Banda Superior Finish", value=1477.47, key="bs_finish1")
        
        banda_inferior_inicio1 = st.number_input("Banda Inferior Inicio", value=1000.00, key="bi_inicio1")
        banda_inferior_finish1 = st.number_input("Banda Inferior Finish", value=944.67, key="bi_finish1")
    
    # Calcular tabla de resultados
    results_df1, venta_values1, compra_values1, rendimiento_bono1 = calculate_carry_trade_table(
        ticker1, inicio_price1, finish_price1, cotizacion_date1, expiry_date1,
        banda_superior_inicio1, banda_superior_finish1, 
        banda_inferior_inicio1, banda_inferior_finish1
    )
    
    # Mostrar tabla con formato
    st.subheader(f"Escenarios de Carry Trade para {ticker1}")
    st.write(f"Rendimiento del bono: {rendimiento_bono1:.2f}% (De {inicio_price1} a {finish_price1})")
    st.write("Los valores en la tabla representan el rendimiento total: ganancia cambiaria + rendimiento del bono")
    st.dataframe(results_df1.style.applymap(color_table), height=300)
    
    # Mostrar datos adicionales
    data_table1 = pd.DataFrame({
        "": ["INICIO", "FINISH"],
        "Valor": [inicio_price1, finish_price1]
    })
    
    banda_table1 = pd.DataFrame({
        "": ["BANDA SUPERIOR", "BANDA INFERIOR"],
        "INICIO": [banda_superior_inicio1, banda_inferior_inicio1],
        "FINISH": [banda_superior_finish1, banda_inferior_finish1]
    })
    
    col3, col4 = st.columns(2)
    with col3:
        st.write("Datos de Cotización:")
        st.write(f"Fecha: {cotizacion_date1.strftime('%d/%m/%Y')}")
        st.dataframe(data_table1, hide_index=True)
    
    with col4:
        st.write("Bandas:")
        st.dataframe(banda_table1, hide_index=True)

# Contenido para la pestaña 2
with instrument_tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        ticker2 = st.text_input("Ticker", "TTD26", key="ticker2")
        
        inicio_price2 = st.number_input("Precio Inicio", value=94.00, key="inicio_price2")
        finish_price2 = st.number_input("Precio Finish", value=161.14, key="finish_price2")
        
        cotizacion_date2 = st.date_input("Fecha de Cotización", 
                                      datetime.date.today(), key="cotizacion_date2")
        expiry_date2 = st.date_input("Fecha de Vencimiento", 
                                  datetime.date.today() + datetime.timedelta(days=180), key="expiry_date2")
        
        # Cálculo de días entre fechas
        dias_plazo2 = (expiry_date2 - cotizacion_date2).days
        st.write(f"Plazo: {dias_plazo2} días")
    
    with col2:
        st.subheader("Bandas")
        banda_superior_inicio2 = st.number_input("Banda Superior Inicio", value=1400.00, key="bs_inicio2")
        banda_superior_finish2 = st.number_input("Banda Superior Finish", value=1694.47, key="bs_finish2")
        
        banda_inferior_inicio2 = st.number_input("Banda Inferior Inicio", value=1000.00, key="bi_inicio2")
        banda_inferior_finish2 = st.number_input("Banda Inferior Finish", value=789.67, key="bi_finish2")
    
    # Calcular tabla de resultados
    results_df2, venta_values2, compra_values2, rendimiento_bono2 = calculate_carry_trade_table(
        ticker2, inicio_price2, finish_price2, cotizacion_date2, expiry_date2,
        banda_superior_inicio2, banda_superior_finish2, 
        banda_inferior_inicio2, banda_inferior_finish2
    )
    
    # Mostrar tabla con formato
    st.subheader(f"Escenarios de Carry Trade para {ticker2}")
    st.write(f"Rendimiento del bono: {rendimiento_bono2:.2f}% (De {inicio_price2} a {finish_price2})")
    st.write("Los valores en la tabla representan el rendimiento total: ganancia cambiaria + rendimiento del bono")
    st.dataframe(results_df2.style.applymap(color_table), height=300)
    
    # Mostrar datos adicionales
    data_table2 = pd.DataFrame({
        "": ["INICIO", "FINISH"],
        "Valor": [inicio_price2, finish_price2]
    })
    
    banda_table2 = pd.DataFrame({
        "": ["BANDA SUPERIOR", "BANDA INFERIOR"],
        "INICIO": [banda_superior_inicio2, banda_inferior_inicio2],
        "FINISH": [banda_superior_finish2, banda_inferior_finish2]
    })
    
    col3, col4 = st.columns(2)
    with col3:
        st.write("Datos de Cotización:")
        st.write(f"Fecha: {cotizacion_date2.strftime('%d/%m/%Y')}")
        st.dataframe(data_table2, hide_index=True)
    
    with col4:
        st.write("Bandas:")
        st.dataframe(banda_table2, hide_index=True)

# Añadir información adicional
st.markdown("---")
st.markdown("""
### Cómo utilizar esta calculadora:
1. Ingrese los datos del instrumento financiero en los campos correspondientes
2. La tabla muestra los retornos porcentuales para diferentes escenarios de compra y venta
3. Los colores indican la rentabilidad: verde = positiva, rojo = negativa
4. Puede comparar dos instrumentos diferentes utilizando las pestañas

### Cálculo del Carry Trade:
La estrategia de carry trade implementada tiene dos componentes:

1. **Rendimiento del bono**: (precio_finish / precio_inicio - 1) * 100
   - Este es el rendimiento por mantener el bono desde su precio inicial hasta el precio final

2. **Rendimiento cambiario**: ((venta_usd_inicio / compra_usd_finish) - 1) * 100
   - Este es el rendimiento por vender USD al inicio (a un precio mayor) y recomprarlos al final (a un precio menor)

3. **Retorno total**: Rendimiento del bono + Rendimiento cambiario
   - La tabla muestra este valor total para cada combinación de precios

### Ejemplo práctico:
- Vendo USD a $1400 (tipo de cambio inicial)
- Compro un bono a $135 que al vencimiento vale $158 (rendimiento del 17%)
- Recompro USD a $950 (tipo de cambio final)
- Ganancia cambiaria: ((1400/950) - 1) * 100 = 47.37%
- Ganancia total: 47.37% + 17% = 64.37%

### Notas:
- La tabla muestra una matriz de escenarios posibles basados en los precios de entrada
- Los valores de VENTA USD INICIO están en el eje vertical (filas)
- Los valores de COMPRA USD FINISH están en el eje horizontal (columnas)
- Los porcentajes indican el rendimiento total del carry trade para cada combinación
""")
