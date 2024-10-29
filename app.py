import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium

# Cargar los datos
@st.cache_data
def cargar_dbOperational():
    dataOperational = pd.read_excel('db_operational.xlsx')
    return dataOperational

data_base_operational = cargar_dbOperational()

# Título de la página principal
st.title("Producción de Hidrógeno Verde")

# Calcular los KPIs
produccion_total_mundial = data_base_operational['Capacity_Nm³ H₂/y'].sum()

# Definir los países de interés para LATAM
countries_of_interest = ["Colombia", "Chile", "Argentina", "Peru", "Brazil"]
produccion_total_latam = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]['Capacity_Nm³ H₂/y'].sum()
produccion_total_colombia = data_base_operational[data_base_operational['Country'] == "Colombia"]['Capacity_Nm³ H₂/y'].sum()

# Definir el factor de emisión de CO2
factor_emision_gas_natural = 10.5  # kg CO2/kg H2
data_base_operational['Producción H₂ (toneladas)'] = data_base_operational['Capacity_Nm³ H₂/y'] / 1000  # Convertir Nm³ a toneladas
data_base_operational['Reducción CO₂ (toneladas)'] = data_base_operational['Producción H₂ (toneladas)'] * factor_emision_gas_natural  # Toneladas de CO₂ evitadas

co2_reducido_latam = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]['Reducción CO₂ (toneladas)'].sum()

# Mostrar KPIs
kpi1 = st.selectbox("Selecciona la unidad para Producción Total Mundial:", ["Nm³ H₂/y", "MW"], index=0)
kpi2 = st.selectbox("Selecciona la unidad para Producción Total en LATAM:", ["Nm³ H₂/y", "MW"], index=0)
produccion_mundial = produccion_total_mundial if kpi1 == "Nm³ H₂/y" else produccion_total_mundial * 0.000277778  # Convertir a MW
produccion_latam = produccion_total_latam if kpi2 == "Nm³ H₂/y" else produccion_total_latam * 0.000277778  # Convertir a MW
produccion_colombia_mw = produccion_total_colombia * 0.000277778  # Producción total de Colombia en MW

st.metric("Producción Total Mundial", f"{produccion_mundial:,.0f} {kpi1}")
st.metric("Producción Total en LATAM", f"{produccion_latam:,.0f} {kpi2}")
st.metric("Producción Total en Colombia (MW)", f"{produccion_colombia_mw:,.0f} MW")
st.metric("Cantidad de CO2 Reducido en LATAM (toneladas)", f"{co2_reducido_latam:,.0f}")

# Crear las pestañas (9 pestañas en total)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Tipos de Tecnologías Usadas",
    "Dispersión por Tecnología",
    "Evolución por Año",
    "Contribución de los Líderes",
    "Total Proyectos en LATAM",
    "Total Producción en LATAM",
    "Mapa LATAM",
    "Reducción CO2 America",
    "Proyectos de Colombia"
])

# Pestaña 1: Tipos de tecnologías usadas a nivel mundial
with tab1:
    # Filtrar los datos para excluir 'unknown'
    filtered_data = data_base_operational[data_base_operational['Technology_electricity_details'] != 'Unknown']

    # Agrupar por 'Technology_electricity_details' y contar
    count_details = filtered_data.groupby('Technology_electricity_details').size().reset_index(name='Count')

    # Graficar los resultados en un gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))  # Ajustar el tamaño de la figura
    ax.bar(count_details['Technology_electricity_details'], count_details['Count'], color='skyblue', edgecolor='black')

    # Títulos y etiquetas
    ax.set_title('Tipos de Tecnologías Usadas a Nivel Mundial', fontsize=16)
    ax.set_xlabel('Tecnología', fontsize=14)
    ax.set_ylabel('Conteo', fontsize=14)
    ax.set_xticks(count_details['Technology_electricity_details'])  # Asegurar que los ticks estén alineados
    ax.set_xticklabels(count_details['Technology_electricity_details'], rotation=45)  # Rotar etiquetas del eje X
    ax.grid(axis='y')  # Añadir cuadrícula en el eje Y

    # Mostrar la gráfica en Streamlit
    st.pyplot(fig)


# Pestaña 2: de Dispersión: Gráfico de distribución por tecnología
with tab2:
    st.subheader("Distribución de Proyectos por Tecnología")
    tech_counts = data_base_operational['Technology'].value_counts()
    fig, ax = plt.subplots()
    tech_counts.plot(kind='bar', ax=ax, color='orange')
    ax.set_title("Distribución de Proyectos por Tecnología")
    ax.set_xlabel("Tecnología")
    ax.set_ylabel("Conteo de Proyectos")
    st.pyplot(fig)

# Pestaña 3: Evolución de la capacidad de producción de hidrógeno por año
with tab3:
    st.subheader("Evolución de la Capacidad de Producción de Hidrógeno por Año")
    capacidad_por_anio = data_base_operational.groupby('Date online')['Capacity_Nm³ H₂/y'].sum()
    fig, ax = plt.subplots()
    capacidad_por_anio.plot(kind='line', ax=ax, marker='o', color='green')
    ax.set_title("Evolución de la Capacidad de Producción de Hidrógeno por Año")
    ax.set_xlabel("Año")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    st.pyplot(fig)

# Pestaña 4: Contribución de los líderes en la producción de hidrógeno
with tab4:
    st.subheader("Contribución de los Líderes en la Producción de Hidrógeno a Nivel Mundial")
    top_paises = data_base_operational.groupby('Country')['Capacity_Nm³ H₂/y'].sum().nlargest(5)
    fig, ax = plt.subplots()
    top_paises.plot(kind='bar', ax=ax, color='coral')
    ax.set_title("Contribución de los Principales Países en la Producción de Hidrógeno")
    ax.set_xlabel("País")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    st.pyplot(fig)

# Pestaña 5: Total de proyectos en LATAM
with tab5:
    st.subheader("Total de Proyectos en LATAM")
    filtered_df = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]
    grouped_df = filtered_df.groupby('Country').agg(
        total_capacity=('Capacity_Nm³ H₂/y', 'sum'),
        total_projects=('Country', 'count')
    ).reset_index()
    
    # Gráfica de Pie para el total de proyectos
    fig, ax = plt.subplots()
    ax.pie(grouped_df['total_projects'], labels=grouped_df['Country'], autopct='%1.1f%%', startangle=140)
    ax.set_title("Total de Proyectos por País")
    ax.axis('equal')
    st.pyplot(fig)

# Pestaña 6: Total producción en LATAM
with tab6:
    st.subheader("Total Producción en LATAM")
    fig, ax = plt.subplots()
    ax.bar(grouped_df['Country'], grouped_df['total_capacity'], color='skyblue')
    ax.set_title("Capacidad Total por País (Nm³ H₂/y)")
    ax.set_xlabel("País")
    ax.set_ylabel("Capacidad Total (Nm³ H₂/y)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Pestaña 7: Mapa LATAM
with tab7:
    coordinates = {
        'Argentina': (-38.4161, -63.6167),
        'Brazil': (-14.2350, -51.9253),
        'Chile': (-35.6751, -71.5429),
        'Colombia': (4.5709, -74.2973),
        'Peru': (-9.1899, -75.0152)
    }
    # Filtrar los datos para LATAM
    filtered_df = data_base_operational[data_base_operational['Country'].isin(coordinates.keys())]
    grouped_df = filtered_df.groupby('Country').agg(total_capacity=('Capacity_Nm³ H₂/y', 'sum')).reset_index()

    # Añadir columnas de latitud y longitud
    grouped_df['Latitude'] = grouped_df['Country'].map(lambda x: coordinates[x][0])
    grouped_df['Longitude'] = grouped_df['Country'].map(lambda x: coordinates[x][1])

    # Crear el mapa centrado en Sudamérica
    map_center = [-8, -55]  # Coordenadas aproximadas del centro de Sudamérica
    map_south_america = folium.Map(location=map_center, zoom_start=4)

    st.subheader("Mapa de Producción de Hidrógeno en LATAM")
    # Agregar marcadores al mapa para cada país
    for idx, row in grouped_df.iterrows():
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=row['total_capacity'] * 0.00001,  # Ajustar el tamaño del círculo
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=f"{row['Country']}: {row['total_capacity']} Nm³ H₂/y"
        ).add_to(map_south_america)
    # Convertir el mapa a HTML y mostrarlo en Streamlit
    st.components.v1.html(map_south_america._repr_html_(), width=725, height=500)

# Pestaña 8: Reducción de CO₂ por País
with tab8:
    st.title("Reducción de CO₂ por País")
    co2_data = data_base_operational[data_base_operational['Country'].isin(countries_of_interest)]
    co2_reduction = co2_data.groupby('Country')['Reducción CO₂ (toneladas)'].sum()
    
    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    plt.bar(co2_reduction.index, co2_reduction, color='skyblue')
    plt.xlabel("País")
    plt.ylabel("Reducción CO₂ (toneladas)")
    plt.title("Reducción total de CO₂ por País en Latinoamérica")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Pestaña 9: Proyectos de Colombia
with tab9:
    st.subheader("Proyectos de Colombia")
    colombia_projects = data_base_operational[data_base_operational['Country'] == "Colombia"][['Project name', 'Capacity_Nm³ H₂/y', 'Date online']]
    st.dataframe(colombia_projects)


