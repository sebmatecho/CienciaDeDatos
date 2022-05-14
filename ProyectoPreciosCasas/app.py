from distutils.fancy_getopt import OptionDummy
from matplotlib.pyplot import figimage
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
from plotly import express as px
import folium
import json
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

st.set_page_config(layout="wide")

st.title('Dinámica Inmobiliaria en King County')
st.header('Propuesto por [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)')
# data = pd.read_csv('data/kc_house_data.csv')



url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
data = pd.read_csv(url)#,index_col=0,parse_dates=[0])
data_aux = data.copy()


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

# col1, col2 = st.columns(2)
# with col1: 
#   st.text( 'Dinámica del tamaño de las casas por área de construcción' )  
#   chart_data = data[['sqft_living','yr_built']].groupby('yr_built').mean().reset_index()
#   st.line_chart(chart_data['sqft_living'])

# with col2: 
#   st.text( 'Dinámica del precio de las casas por área de construcción' )  
#   chart_data = data[['price','yr_built']].groupby('yr_built').mean().reset_index()
#   st.line_chart(chart_data['price'])

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
     min_habs, max_habs = st.select_slider(
     'Número de Habitaciones',
     options=list(sorted(set(data['bedrooms']))),
     value=(data['bedrooms'].min(),data['bedrooms'].max()))
     data = data[(data['bedrooms']>= min_habs)&(data['bedrooms']<= max_habs)]

if 'Baños' in OptFiltro: 
     min_banhos, max_banhos = st.select_slider(
     'Número de baños ',
     options=list(sorted(set(data['bathrooms']))),
     value=(data['bathrooms'].min(), data['bathrooms'].max()))
     data = data[(data['bathrooms']>= min_banhos)&(data['bathrooms']<= max_banhos)]

if 'Área construida (pies cuadrados)' in OptFiltro: 
    area = st.slider('Área construida menor a', int(data['sqft_living'].min()),int(data['sqft_living'].max()),2000)
    data = data[data['sqft_living']<area]

if 'Pisos' in OptFiltro: 
     min_pisos, max_pisos = st.select_slider(
     'Número de Pisos',
     options=list(sorted(set(data['floors']))),
     value=(data['floors'].min(),data['floors'].max()))
     data = data[(data['floors']>= min_pisos)&(data['floors']<= max_pisos)]

if 'Vista al agua' in OptFiltro: 
     min_vista, max_vista = st.select_slider(
     'Puntaje de vista al agua',
     options=list(sorted(set(data['view']))),
     value=(data['view'].min(),data['view'].max()))
     data = data[(data['view']>= min_vista)&(data['view']<= max_vista)]

if 'Evaluación de la propiedad' in OptFiltro:
     min_cond, max_cond = st.select_slider(
     'Índice de evaluación de la propiedad',
     options=list(sorted(set(data['grade']))),
     value=(data['grade'].min(),data['grade'].max()))
     data = data[(data['grade']>= min_cond)&(data['grade']<= max_cond)]

if 'Condición' in OptFiltro:
     min_condi, max_condi = st.select_slider(
     'Índice de evaluación de la propiedad',
     options=list(sorted(set(data['condition']))),
     value=(data['condition'].min(),data['condition'].max()))
     data = data[(data['condition']>= min_condi)&(data['condition']<= max_condi)]

# Mapas 
col1, col2 = st.columns(2)
with col1:
     st.header("Densidad de casas disponibles por código postal")
     data_aux = data[['id','zipcode']].groupby('zipcode').count().reset_index()
     custom_scale = (data_aux['id'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()

     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=8)
     folium.Choropleth(geo_data='https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/KingCount.geojson', 
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
     folium.Choropleth(geo_data='https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/KingCount.geojson', 
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
     data_aux = data[['price/sqft','zipcode']].groupby('zipcode').count().reset_index()
     custom_scale = (data_aux['price/sqft'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()

     mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=8)
     folium.Choropleth(geo_data='https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/KingCount.geojson', 
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
df_EDA = df_EDA.drop(index =['lat', 'long','yr_built','yr_renovated'], axis = 0 )

df_EDA.index =['Índice','Precio','No. Cuartos', 'No. Baños', 'Área construida (pies cuadrados)', 
                    'Área del terreno (pies cuadrados)', 'No. pisos', 'Vista agua (dummy)',
                    'Puntaje de la vista', 'Condición','Evaluación propiedad (1-13)',
                    'Área sobre tierra', 'Área sótano', 'Área construída 15 casas más próximas', 
                    'Área del terreno 15 casas más próximas', 'Precio por pie cuadrado']
col1, col2 = st.columns(2)
col1.metric("No. Casas", data.shape[0],str(100*round(data.shape[0]/data_aux.shape[0],4))+'% de las casas disponibles',delta_color="off")
col2.metric("No. Casas Nuevas (Construida después de 1990)",data[data['house_age'] == 'new_house'].shape[0],str(100*round(data[data['house_age'] == 'new_house'].shape[0]/data_aux.shape[0],4))+'% de las casas disponibles',delta_color="off")
st.dataframe(df_EDA)  









