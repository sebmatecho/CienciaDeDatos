from matplotlib.pyplot import figimage
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
from plotly import express as px

st.title('Dinámica Inmobiliaria en King County')

# data = pd.read_csv('data/kc_house_data.csv')

url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
data = pd.read_csv(url,index_col=0,parse_dates=[0])

data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d')
data['yr_built'] = pd.to_datetime(data['yr_built'], format ='%Y').dt.year


#llenar la columna anterior con new_house para fechas anteriores a 2015-01-01
data['house_age'] = 'NA'
#llenar la columna anterior con new_house para fechas anteriores a 2015-01-01
data.loc[data['yr_built']>1990,'house_age'] = 'new_house' 
#llenar la columna anterior con old_house para fechas anteriores a 2015-01-01
data.loc[data['yr_built']<1990,'house_age'] = 'old_house'




# for i in range(data.shape[0]): 
#     if data.loc[i,'bedrooms']<=1: 
#         data.loc[i,'dormitory_type'] = 'studio'
#     elif data.loc[i,'bedrooms']==2: 
#         data.loc[i,'dormitory_type'] = 'apartment'
#     elif data.loc[i,'bedrooms']>2: 
#         data.loc[i,'dormitory_type'] = 'house'


# data['condition_type']=data['condition'].apply(lambda x:'bad' if x <= 2 else 'regular' if (x==3)|(x==4) else 'good')

st.dataframe(data)

col1, col2 = st.columns(2)
with col1: 
  st.text( 'Dinámica del tamaño de las casas por área de construcción' )  
  chart_data = data[['sqft_living','yr_built']].groupby('yr_built').mean().reset_index()
  st.line_chart(chart_data['sqft_living'])

with col2: 
  st.text( 'Dinámica del precio de las casas por área de construcción' )  
  chart_data = data[['price','yr_built']].groupby('yr_built').mean().reset_index()
  st.line_chart(chart_data['price'])


houses = data[['id','lat','long','price','sqft_living']]

houses['price_tier'] = houses['price'].apply(lambda x: 'tier 1' if x <= 321950 else
                                                      'tier 2' if (x > 321950) & (x <= 450000) else
                                                      'tier 3' if (x > 450000) & (x <= 645000) else
                                                      'tier 4')
              
fig = px.scatter_mapbox(data_frame=houses,
                  lat = 'lat',
                  lon = 'long',
                  size = 'sqft_living',
                    color = 'price_tier') 
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

st.plotly_chart(fig)
