import json
import folium
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

from PIL                      import Image
from plotly                   import express as px
from folium.plugins           import MarkerCluster
from streamlit_folium         import folium_static
from matplotlib.pyplot        import figimage
from distutils.fancy_getopt   import OptionDummy



st.set_page_config(page_title='App - Venta de casas',
                    layout="wide", 
                    page_icon=':house',  
                    initial_sidebar_state="expanded")

st.sidebar.markdown("# Parámetros")

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.title('Dinámica Inmobiliaria en King County')
st.header('Propuesto por [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)')


@st.cache
def get_data():
     url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
     return pd.read_csv(url)

data = get_data()
data_ref = data.copy()
# data = data.head(100)


data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d').dt.date
data['yr_built']= pd.to_datetime(data['yr_built'], format = '%Y').dt.year
# data['yr_renovated'] = data['yr_renovated'].apply(lambda x: pd.to_datetime(x, format ='%Y') if x >0 else x )
# data['id'] = data['id'].astype(str)

#llenar la columna anterior con new_house para fechas anteriores a 2015-01-01
data['house_age'] = 'NA'
#llenar la columna anterior con new_house para fechas anteriores a 2015-01-01
data.loc[data['yr_built']>1990,'house_age'] = 'new_house' 
#llenar la columna anterior con old_house para fechas anteriores a 2015-01-01
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'

data['zipcode'] = data['zipcode'].astype(str)


data.loc[data['yr_built']>=1990,'house_age'] = 'new_house' 
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'

data.loc[data['bedrooms']<=1, 'dormitory_type'] = 'studio'
data.loc[data['bedrooms']==2, 'dormitory_type'] = 'apartment'
data.loc[data['bedrooms']>2, 'dormitory_type'] = 'house'

data.loc[data['condition']<=2, 'condition_type'] = 'bad'
data.loc[data['condition'].isin([3,4]), 'condition_type'] = 'regular'
data.loc[data['condition']== 5, 'condition_type'] = 'good'

data['price_tier'] = data['price'].apply(lambda x: 'Primer cuartil' if x <= 321950 else
                                                   'Segundo cuartil' if (x > 321950) & (x <= 450000) else
                                                   'Tercer cuartil' if (x > 450000) & (x <= 645000) else
                                                   'Cuarto cuartil')

data['price/sqft'] = data['price']/data['sqft_living']

# st.dataframe(data)
st.write('Este dashboard tiene por objevito presentar rápida y fácilmente la información derivada del estudio de la dinámica inmobiliaria en King Count, WA (USA). Los datos están disponibles [aquí](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) ')



## Filtros
st.subheader('Filtros Requeridos')
# construccion = st.slider('Construcción después de:', int(data['yr_built'].min()),int(data['yr_built'].max()),1991)


st.markdown("""
Las casas han sido divididas en cuatro grupos de igual tañamo, basadas en su precio. 
-  El Primer Cuartil contendrá información de las propiedades que cuestan menos de \$321.950 
-  El Segundo Cuartil contendrá información de las propiedades que cuestan entre \$321.950 y \$450.000
-  El Tercer Cuartil contendrá información de las propiedades que cuestan entre \$450.000 y \$645.000
-  El Cuarto Cuartil contendrá información de las propiedades que cuestan más de \$645.000
    """)
tier = st.multiselect(
     'Cuartil de precios',
    list(data['price_tier'].unique()),
     list(data['price_tier'].unique()))


st.markdown("""
El código postal puede utilizarse como proxy para lo localización de un inmueble en King County. Por favor, consulte [aquí](https://www.zipdatamaps.com/king-wa-county-zipcodes) para más información. 
    """)

zipcod = st.multiselect(
     'Códigos postales',
      list(sorted(set(data['zipcode']))),
      list(sorted(set(data['zipcode']))))
data = data[(data['price_tier'].isin(tier))&(data['zipcode'].isin(zipcod))]
st.subheader('Filtros adicionales (Opcionales)')


OptFiltro = st.multiselect(
     'Variables a incluir en los filtros:',
     ['Habitaciones', 'Baños', 'Área construida (pies cuadrados)','Pisos','Vista al agua','Evaluación de la propiedad','Condición'],
     ['Habitaciones', 'Baños'])


if 'Habitaciones' in OptFiltro: 
     if data['bedrooms'].min() < data['bedrooms'].max():
          min_habs, max_habs = st.sidebar.select_slider(
          'Número de Habitaciones',
          options=list(sorted(set(data['bedrooms']))),
          value=(data['bedrooms'].min(),data['bedrooms'].max()))
          data = data[(data['bedrooms']>= min_habs)&(data['bedrooms']<= max_habs)]
     else:
          st.markdown("""
               El filtro **Habitaciones** no es aplicable para la selección actual de valores
               """)
if 'Baños' in OptFiltro: 
     if data['bathrooms'].min() < data['bathrooms'].max():
          min_banhos, max_banhos = st.sidebar.select_slider(
          'Número de baños ',
          options=list(sorted(set(data['bathrooms']))),
          value=(data['bathrooms'].min(), data['bathrooms'].max()))
          data = data[(data['bathrooms']>= min_banhos)&(data['bathrooms']<= max_banhos)]
     else:
          st.markdown("""
               El filtro **Baños** no es aplicable para la selección actual de valores
               """)
if 'Área construida (pies cuadrados)' in OptFiltro: 
     if data['sqft_living'].min() < data['sqft_living'].max():
          area = st.sidebar.slider('Área construida menor a', int(data['sqft_living'].min()),int(data['sqft_living'].max()),2000)
          data = data[data['sqft_living']<area]
     else:  
          st.markdown("""
               El filtro **Área construida (pies cuadrados)** no es aplicable para la selección actual de valores
               """)

if 'Pisos' in OptFiltro: 
     if data['floors'].min() < data['floors'].max():
          min_pisos, max_pisos = st.sidebar.select_slider(
          'Número de Pisos',
          options=list(sorted(set(data['floors']))),
          value=(data['floors'].min(),data['floors'].max()))
          data = data[(data['floors']>= min_pisos)&(data['floors']<= max_pisos)]
     else:
          st.markdown("""
               El filtro **Pisos** no es aplicable para la selección actual de valores
               """)

if 'Vista al agua' in OptFiltro: 
     if data['view'].min() < data['view'].max():
          min_vista, max_vista = st.sidebar.select_slider(
          'Puntaje de vista al agua',
          options=list(sorted(set(data['view']))),
          value=(data['view'].min(),data['view'].max()))
          data = data[(data['view']>= min_vista)&(data['view']<= max_vista)]
     else:
          st.markdown("""
               El filtro **Vista al agua** no es aplicable para la selección actual de valores
               """)
if 'Evaluación de la propiedad' in OptFiltro:
     if data['grade'].min() < data['grade'].max():
          min_cond, max_cond = st.sidebar.select_slider(
          'Índice de evaluación de la propiedad',
          options=list(sorted(set(data['grade']))),
          value=(data['grade'].min(),data['grade'].max()))
          data = data[(data['grade']>= min_cond)&(data['grade']<= max_cond)]
     else:
          st.markdown("""
               El filtro **Evaluación de la propiedad** no es aplicable para la selección actual de valores
               """)

if 'Condición' in OptFiltro:
     if data['condition'].min() < data['condition'].max():
          min_condi, max_condi = st.sidebar.select_slider(
          'Condición de la propiedad',
          options=list(sorted(set(data['condition']))),
          value=(data['condition'].min(),data['condition'].max()))
          data = data[(data['condition']>= min_condi)&(data['condition']<= max_condi)]
     else:
          st.markdown("""
               El filtro **Condición** no es aplicable para la selección actual de valores
               """)

# Mapas 

# info geojson
url2 = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/KingCount.geojson'
col1, col2 = st.columns(2)
with col1:
     st.header("Densidad de casas disponibles por código postal")
     data_aux = data[['id','zipcode']].groupby('zipcode').count().reset_index()
     custom_scale = (data_aux['id'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()

     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=8)
     folium.Choropleth(geo_data=url2, 
                    data=data_aux,
                    key_on='feature.properties.ZIPCODE',
                    columns=['zipcode', 'id'],
                    threshold_scale=custom_scale,
                    fill_color='YlOrRd',
                    highlight=True).add_to(mapa)
     folium_static(mapa)

with col2: 
     st.header("Precios de casas disponibles por código postal")
     data_aux = data[['price','zipcode']].groupby('zipcode').mean().reset_index()
     custom_scale = (data_aux['price'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()

     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=8)
     folium.Choropleth(geo_data=url2, 
                    data=data_aux,
                    key_on='feature.properties.ZIPCODE',
                    columns=['zipcode', 'price'],
                    threshold_scale=custom_scale,
                    fill_color='YlOrRd',
                    highlight=True).add_to(mapa)
     folium_static(mapa)


col1, col2 = st.columns(2)
with col1:
     st.header("Costo de pie cuadrado por código postal")
     data_aux = data[['price/sqft','zipcode']].groupby('zipcode').mean().reset_index()
     custom_scale = (data_aux['price/sqft'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()

     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=8)
     folium.Choropleth(geo_data=url2, 
                    data=data_aux,
                    key_on='feature.properties.ZIPCODE',
                    columns=['zipcode', 'price/sqft'],
                    threshold_scale=custom_scale,
                    fill_color='YlOrRd',
                    highlight=True).add_to(mapa)
     folium_static(mapa)

with col2: 
     st.header("Ubicación y detalles de casas disponibles")
     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=9)
     markercluster = MarkerCluster().add_to(mapa)
     for nombre, fila in data.iterrows():
          folium.Marker([fila['lat'],fila['long']],
                         popup = 'Precio: ${}, \n Fecha: {} \n {} habitaciones \n {} baños \n constuida en {} \n área de {} pies cuadrados \n Precio por pie cuadrado: {}'.format(
                         fila['price'],
                         fila['date'],
                         fila['bedrooms'],
                         fila['bathrooms'],
                         fila['yr_built'], 
                         fila['sqft_living'], 
                         fila['price/sqft'])
          ).add_to(markercluster)
     folium_static(mapa)


# Estadística Descriptiva 
att_num = data.select_dtypes(include = ['int64','float64'])
media = pd.DataFrame(att_num.apply(np.mean))
mediana = pd.DataFrame(att_num.apply(np.median))
std = pd.DataFrame(att_num.apply(np.std))
maximo = pd.DataFrame(att_num.apply(np.max))
minimo = pd.DataFrame(att_num.apply(np.min))
df_EDA = pd.concat([minimo,media,mediana,maximo,std], axis = 1)
df_EDA.columns = ['Mínimo','Media','Mediana','Máximo','std']
st.header('Datos descriptivos')
df_EDA = df_EDA.drop(index =['id', 'lat', 'long','yr_built','yr_renovated'], axis = 0 )

df_EDA.index =['Precio','No. Cuartos', 'No. Baños', 'Área construida (pies cuadrados)', 
                    'Área del terreno (pies cuadrados)', 'No. pisos', 'Vista agua (dummy)',
                    'Puntaje de la vista', 'Condición','Evaluación propiedad (1-13)',
                    'Área sobre tierra', 'Área sótano', 'Área construída 15 casas más próximas', 
                    'Área del terreno 15 casas más próximas', 'Precio por pie cuadrado']
col1, col2 = st.columns(2)
col1.metric("No. Casas", data.shape[0],str(100*round(data.shape[0]/data_ref.shape[0],4))+'% de las casas disponibles',delta_color="off")
col2.metric("No. Casas Nuevas (Construida después de 1990)",data[data['house_age'] == 'new_house'].shape[0],str(100*round(data[data['house_age'] == 'new_house'].shape[0]/data_ref.shape[0],4))+'% de las casas disponibles',delta_color="off")
st.dataframe(df_EDA)  

st.header('Algunas tendencias')


col1, col2 = st.columns(2)
with col1: 
     st.write('Evolución del precio por tipo de propiedad y año de construcción')
     data['dormitory_type']=data['bedrooms'].apply(lambda x: 'Estudio' if x <=1 else 'Apartamento' if x==2 else 'Casa' )
     df = data[['yr_built', 'price','dormitory_type']].groupby(['yr_built','dormitory_type']).mean().reset_index()
     with sns.axes_style("darkgrid"):
          plt.style.use('dark_background')
          fig = plt.figure(figsize=(7,7)) # try different values
          fig = sns.lineplot(x ='yr_built', y= 'price', data = df, hue="dormitory_type", style="dormitory_type")
          fig.set_xlabel("Año de Construcción", fontsize = 17)
          fig.set_ylabel("Precio (Millones de Dólares)", fontsize = 17)
          fig.legend(title='Tipo de propiedad', loc='upper right', labels=['Apartamento', 'Casa','Estudio'])
          fig = fig.figure
          st.pyplot(fig)


with col2: 
     st.write('Evolución del precio por pie cuadrado por tipo de propiedad y año de construcción')
     df = data[['yr_built', 'price/sqft','dormitory_type']].groupby(['yr_built','dormitory_type']).mean().reset_index()
     with sns.axes_style("darkgrid"):
          plt.style.use('dark_background')
          fig = plt.figure(figsize=(7,7)) # try different values
          fig = sns.lineplot(x ='yr_built', y= 'price/sqft', data = df, hue="dormitory_type", style="dormitory_type")
          fig.set_xlabel("Año de Construcción", fontsize = 17)
          fig.set_ylabel("Precio por pie cuadrado (Dólares)", fontsize = 17)
          fig.legend(title='Tipo de propiedad', loc='upper right', labels=['Apartamento', 'Casa','Estudio'])
          fig = fig.figure
          st.pyplot(fig)


