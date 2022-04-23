import pandas as pd
import seaborn as sns
from plotly import express as px
from matplotlib import pyplot as plt
from matplotlib import gridspec 
import streamlit as st 

st.title('Esta es nuestra primera aplicación :)')


st.write('Escribir texto dentro del cuerpo de nuestra apliación')

data = pd.read_csv('data/kc_house_data.csv')

st.write('El data frame con el que vamos a trabajar se ve de esta manera')
st.dataframe(data)

df = data.loc[data['yr_renovated']>1930, ['price', 'yr_renovated']].groupby('yr_renovated').mean().reset_index()
st.line_chart(df['price'])





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
