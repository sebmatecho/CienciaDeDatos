import streamlit as st 
import pandas as pd
import seaborn as sns
import numpy as np
import datetime as datetime
from dateutil.relativedelta import relativedelta # to add days or years

from matplotlib import pyplot as plt
import plotly.express as px


st.write("""
# House price prediction project
## Sébastien Lozano Forero

""")

df = pd.read_csv( 'data/kc_house_data.csv' )

df['is_waterfront'] = df['waterfront'].apply( lambda x: 'yes' if x == 1 else 'no' )

df['level'] = df['price'].apply( lambda x: '<320K' if x< 320000 else 
                                           '320K-450K' if ( x > 320000) & ( x < 450000) else
                                           '450K-650K' if ( x > 450000) & ( x < 645000) else '>650K' )
df['level'] = df['level'].astype( str )

df['year'] = pd.to_datetime(df['date']).dt.strftime('%Y')
df['date2'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
df['Year_week'] = pd.to_datetime(df['date']).dt.strftime('%Y-%U')



style = {'description_width': 'initial'}


price_limit = st.slider('Maximun Price', 75000, 540000,10000000)


waterfront_bar = st.selectbox(
     'Water View',
     df['is_waterfront'].unique().tolist())


 ## Range selector
cols1,_ = st.columns((1,2)) # To make it narrower
format = 'YYYY-MM-DD'  # format output
start_date = datetime.date(year=2014,month=5,day=2)
end_date = datetime.date(year=2015,month=5,day=27)
max_days = end_date-start_date
        
date_available = cols1.slider('Available since', min_value=start_date, value=end_date ,max_value=end_date, format=format)


houses = df[(df['date']>=str(date_available)) & 
            (df['price'] <= price_limit) & 
            (df['is_waterfront'] == waterfront_bar)][['id', 'lat', 'long', 'price', 'level']]
    
fig = px.scatter_mapbox( houses, 
                             lat='lat', 
                             lon='long',
                             color='level', 
                             size='price', 
                             color_continuous_scale=px.colors.cyclical.IceFire,
                             size_max=15,
                             zoom=10 ) 

fig.update_layout( mapbox_style='open-street-map' )
fig.update_layout( height=600, margin={'r':0, 't':0, 'l':0, 'b':0} )
st.plotly_chart(fig, use_container_width=True)

