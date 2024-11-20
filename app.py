import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import io
from matplotlib.colors import LinearSegmentedColormap

DIC_COLORES = {'verde':["#009966"],
               'ro_am_na':["#FFE9C5", "#F7B261","#D8841C", "#dd722a","#C24C31", "#BC3B26"],
               'az_verd': ["#CBECEF", "#81D3CD", "#0FB7B3", "#009999"],
               'ax_viol': ["#D9D9ED", "#2F399B", "#1A1F63", "#262947"],
               'ofiscal': ["#F9F9F9", "#2635bf"]}

def generate_custom_cmap(colors, name="custom_cmap", n_bins=256):
    """
    Generate a custom colormap using specified colors.

    Parameters:
        colors (list): List of colors in hex, RGB, or named format. 
                       Example: ['#ff0000', 'blue', (0.5, 1, 0.5)]
        name (str): Name of the colormap.
        n_bins (int): Number of discrete bins for the colormap (default: 256).

    Returns:
        LinearSegmentedColormap: A Matplotlib colormap object.
    """
    if len(colors) < 2:
        raise ValueError("At least two colors are required to create a colormap.")
    
    return LinearSegmentedColormap.from_list(name, colors, N=n_bins)

cmap_at = generate_custom_cmap(["#262947", "#0FB7B3", "#81D3CD"])


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
    filtro.plot(column=valor, ax=ax, legend=True, cmap=cmap_at, edgecolor='lightgray', linewidth=0.15)

    buffer = io.BytesIO()
    fig.savefig(buffer, format='svg')
    buffer.seek(0)  # Move to the beginning of the buffer
    svg_data = buffer.getvalue()  # Get the SVG data
    st.pyplot(fig)
    # Create a download button for the SVG file
    st.download_button(
        label="Download SVG Image",
        data=svg_data,
        file_name="plot.svg",
        mime="image/svg+xml"
)

    

with tab2:
    st.dataframe(reg)