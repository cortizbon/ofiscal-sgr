import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd

st.set_page_config(layout='wide')

st.title("Mapa de regalías")

reg = pd.read_csv('regalias_prov_pop.csv')
mapa = gpd.read_parquet("muns.parquet")
mapa.columns = ['CodEntidad', 'geometry']
reg['CodEntidad'] = [f"0{i}" if len(str(i)) == 4 else str(i) for i in reg['CodEntidad'] ]
df = gpd.GeoDataFrame(reg
        .groupby(["NombreDepto",'CodEntidad','Periodo','C1'])['Valor_pc_24']
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
cat = st.selectbox("Seleccione una categoría: ", cats)
filtro = filtro[filtro['C1'] == cat]

fig, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.set_axis_off()
ax.set_title(f"{depto} - {cat}")
filtro.plot(column='Valor_pc_24', ax=ax, legend=True)

st.pyplot(fig)

if depto != 'Todos':
    filtro2 = df[df['NombreDepto'] == depto]
    piv = filtro2.pivot_table(index='Periodo',
                              columns='C1',
                              values='Valor_pc_24',
                              aggfunc='sum')
    
    fig, ax = plt.subplots(1, 1, )
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    piv.plot(ax=ax)
    st.pyplot(fig)
