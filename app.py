import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

st.set_page_config(layout='wide')

st.title("Mapa de regalías")

reg = pd.read_csv('regalias_prov_pop.csv')
mapa = gpd.read_parquet("muns.parquet")
mapa.columns = ['CodEntidad', 'geometry']
reg['CodEntidad'] = [f"0{i}" if len(str(i)) == 4 else str(i) for i in reg['CodEntidad'] ]


tab1, tab2 = st.tabs(['Mapa', 'Datos'])

with tab1:

    valor = st.selectbox("Seleccione un valor a calcular", ['Valor total', 'Valor total (precios 24)', 'Valor per cápita (precios 2024)'])
    dic_valor = {"Valor total": 'Valor',
                 "Valor total (precios 24)": "Valor_24",
                 "Valor per cápita (precios 2024)":"Valor_pc_24"}
    valor = dic_valor[valor]
    df = gpd.GeoDataFrame(reg
        .groupby(["NombreDepto",'CodEntidad','Periodo','C1', 'C2'])[valor]
        .sum()
        .reset_index()
        .merge(mapa)
        .assign(NombreDepto=lambda x: x['NombreDepto'].str.strip()))

    periods = df['Periodo'].unique().tolist()
    period = st.select_slider("Seleccione un periodo: ",  periods)
    filtro = df[(df['Periodo'] == period)]
    deptos = filtro['NombreDepto'].unique().tolist()
    depto = st.selectbox("Seleccione un departamento: ", ['Todos'] + deptos)
    if depto != 'Todos':
        filtro = filtro[(filtro['NombreDepto'] == depto)]
    cats = filtro['C1'].unique().tolist()
    cat = st.selectbox("Seleccione una categoría: ", ['Total'] + cats)
    if cat != 'Total':
        filtro = filtro[filtro['C1'] == cat]
    subcats = filtro['C2'].unique().tolist()
    subcat = st.selectbox("Seleccione una subcategoría: ", ['Total'] + subcats)
    if subcat != 'Total':
        filtro = filtro[filtro['C2'] == subcat]
    else:
        filtro = filtro.groupby(['geometry'])[valor].sum().reset_index()
    

    filtro = gpd.GeoDataFrame(filtro)
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_axis_off()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title(f"{depto} - {cat}")
    filtro.plot(column=valor, ax=ax, legend=True)

    st.pyplot(fig)

with tab2:
    st.dataframe(reg)