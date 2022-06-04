import streamlit as st
import pandas as pd
import joblib
import numpy as np


st.title("Pronosticando precios de casas")
st.sidebar.markdown("Características")



def get_data():
     url = 'https://raw.githubusercontent.com/sebmatecho/CienciaDeDatos/master/ProyectoPreciosCasas/data/kc_house_data.csv'
     return pd.read_csv(url)

data = get_data()
X = pd.DataFrame()
banhos = st.sidebar.select_slider(
          'Número de Baños',
          options=list(sorted(set(data['bathrooms']))))

X.loc[0,'bathrooms'] = banhos
scaler = joblib.load('../parameters/bathrooms.sav')
X[['bathrooms']] = scaler.transform(X[['bathrooms']])


pisos = st.sidebar.select_slider(
          'Número de Pisos',
          options=list(sorted(set(data['floors']))))

X.loc[0,'floors'] = pisos
scaler = joblib.load('../parameters/floors.sav')
X[['floors']] = scaler.transform(X[['floors']])


habitaciones = st.sidebar.number_input('Número de habitaciones', min_value=1, max_value=10, value=3, step=1)

X.loc[0,'bedrooms'] = habitaciones
scaler = joblib.load('../parameters/bedrooms.sav')
X[['bedrooms']] = scaler.transform(X[['bedrooms']])

area = st.sidebar.number_input('Área del inmueble')

X.loc[0,'sqft_living'] = area
scaler = joblib.load('../parameters/sqft_living.sav')
X[['sqft_living']] = scaler.transform(X[['sqft_living']])


waterfront = st.sidebar.selectbox(
     'La propiedad tiene vista al agua?',
     ('Sí', 'No'))

if waterfront == 'Sí': 
    waterfront = 1
else:  
    waterfront = 0

X.loc[0,'waterfront'] = waterfront
scaler = joblib.load('../parameters/waterfront.sav')
X[['waterfront']] = scaler.transform(X[['waterfront']])

vista = st.sidebar.selectbox(
     'Puntaje de la vista',
     (0,1,2,3,4))

X.loc[0,'view'] = vista
scaler = joblib.load('../parameters/view.sav')
X[['view']] = scaler.transform(X[['view']])



condicion = st.sidebar.selectbox(
     'Condición del inmueble',
     (0,1,2,3,4))

X.loc[0,'condition'] = condicion
scaler = joblib.load('../parameters/condition.sav')
X[['condition']] = scaler.transform(X[['condition']])


puntaje =  st.sidebar.selectbox(
     'Puntaje sobre la construcción',
     (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13))


X.loc[0,'grade'] = puntaje
scaler = joblib.load('../parameters/grade.sav')
X[['grade']] = scaler.transform(X[['grade']])


renovacion = st.sidebar.selectbox(
     'La propiedad ha sido renovada?',
     ('Sí', 'No'))

if renovacion == 'Sí': 
    renovacion = 1
else:  
    renovacion = 0

X.loc[0,'yr_renovated_dummy'] = renovacion
scaler = joblib.load('../parameters/yr_renovated_dummy.sav')
X[['yr_renovated_dummy']] = scaler.transform(X[['yr_renovated_dummy']])


edad = st.sidebar.number_input('Edad de la propiedad', min_value=1, max_value=100, value=20, step=1)

X.loc[0,'property_age'] = edad
scaler = joblib.load('../parameters/property_age.sav')
X[['property_age']] = scaler.transform(X[['property_age']])


agree = st.checkbox('Los parámetros han sido cargados. Calcular precio')

if agree:
    modelo_final = joblib.load('../modelos/xbg_final.sav')
    precio = modelo_final.predict(X)[0]
    st.balloons()
    st.success('El precio ha sido calculado')
    st.write('El precio sugerido es:', np.expm1(precio))
    