from matplotlib.pyplot import figimage
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
from plotly import express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static


st.title('Dinámica Inmobiliaria en King County')

# data = pd.read_csv('data/kc_house_data.csv')

url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
data = pd.read_csv(url,index_col=0,parse_dates=[0])



data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d').dt.date
data['yr_built']= pd.to_datetime(data['yr_built'], format = '%Y').dt.year
# data['yr_renovated'] = data['yr_renovated'].apply(lambda x: pd.to_datetime(x, format ='%Y') if x >0 else x )
# data['id'] = data['id'].astype(str)
data['zipcode'] = data['zipcode'].astype(str)


data.loc[data['yr_built']>=1990,'house_age'] = 'new_house' 
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'

data.loc[data['bedrooms']<=1, 'dormitory_type'] = 'studio'
data.loc[data['bedrooms']==2, 'dormitory_type'] = 'apartment'
data.loc[data['bedrooms']>2, 'dormitory_type'] = 'house'

data.loc[data['condition']<=2, 'condition_type'] = 'bad'
data.loc[data['condition'].isin([3,4]), 'condition_type'] = 'regular'
data.loc[data['condition']== 5, 'condition_type'] = 'good'

data['price_tier'] = data['price'].apply(lambda x: 'tier 1' if x <= 321950 else
                                                      'tier 2' if (x > 321950) & (x <= 450000) else
                                                      'tier 3' if (x > 450000) & (x <= 645000) else
                                                      'tier 4')

data['price/sqft'] = data['price']/data['sqft_living']

st.dataframe(data)

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

construccion = st.slider('Construcción después de:', int(data['yr_built'].min()),int(data['yr_built'].max()),1991)

tier = st.multiselect(
     'Banda de precios',
    list(data['price_tier'].unique()),
     list(data['price_tier'].unique()))

zipcod = st.multiselect(
     'Códigos postales',
      list(data['zipcode'].unique()),
      list(data['zipcode'].unique()))



data = data[(data['price_tier'].isin(tier))&(data['zipcode'].isin(zipcod))&
            (data['yr_built']>construccion)]
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
st.dataframe(df_EDA)  
# houses = data[['lat','long','price','sqft_living']]
# houses['price_tier'] = houses['price'].apply(lambda x: 'tier 1' if x <= 321950 else
#                                                       'tier 2' if (x > 321950) & (x <= 450000) else
#                                                       'tier 3' if (x > 450000) & (x <= 645000) else
#                                                       'tier 4')
              
# fig = px.scatter_mapbox(data_frame=houses,
#                   lat = 'lat',
#                   lon = 'long',
#                   size = 'sqft_living',
#                     color = 'price_tier') 
# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
# st.plotly_chart(fig)
# df_test = data.head(1000)
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

