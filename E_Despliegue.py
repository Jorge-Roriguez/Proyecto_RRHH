# En este archivo se muestra el despliegue del modelo con las predicciones para 2017

# -------------------------- Librerias necesarias ------------------------------------------

import pandas as pd
import sqlite3 as sql
import joblib
import numpy as np
import openpyxl
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import importlib
import A_Funciones as funciones  # Archivo de funciones propias 
importlib.reload(funciones)

# -------------------------- Conectarse a db para traer tablas -----------------------------

# Crear conexíon 
#conn = sql.connect('C:\\Users\\jorge\\Desktop\\Proyecto RRHH\\data\\db')
conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()

# Leer datos para 2016 
df_2016 = pd.read_sql("SELECT * FROM tabla_2016", conn)

# -------------------- Aplicar transformaciones a los datos (Imputar, Dummies, Escalar) ----

df_t = funciones.preparar_datos(df_2016)
df_t


# -------------------------- Cargar modelo y realizar predicciones -------------------------

m_xg = joblib.load('Salidas\\xg_final.pkl')
predicciones = m_xg.predict(df_t)
df_pred = pd.DataFrame(predicciones, columns = ['pred_retiros_2017'])


# -------------------------- Dataframe completo con predicciones ---------------------------------

# Datos no escalados para interpretar 
df_retiros_var = df_2016[['EmployeeID', 'Department', 'Age', 'MonthlyIncome', 'EnvironmentSatisfaction',
                           'TrainingTimesLastYear', 'JobSatisfaction', 'NumCompaniesWorked',
                           'WorkLifeBalance', 'DistanceFromHome', 'PercentSalaryHike',
                           'StockOptionLevel', 'YearsAtCompany', 'JobInvolvement', 
                           'BusinessTravel', 'Gender']]

df_retiros_var = pd.concat([df_retiros_var, df_pred], axis = 1)
 

# -------------------------- Exportaciones de datos para despliegue  -------------------------------------------------------------

# Retiros de los empleados por departamento (Diseño de la solución) datos al archivo DB
df_retiros_var.loc[:, ['EmployeeID', 'Department', 'pred_retiros_2017']].to_sql('retiros_pred', conn, if_exists = 'replace', index = False)

# Retiros de los empleados por departamento (Diseño de la solución) datos al archivo excel
retiros = df_retiros_var[df_retiros_var['pred_retiros_2017'] == 1]
df_predicciones_2017 = retiros[['EmployeeID', 'Department', 'pred_retiros_2017']]
df_predicciones_2017.set_index('EmployeeID', inplace = True) 
df_predicciones_2017.to_excel('Salidas\\df_predicciones_2017.xlsx')

no_retiros = df_retiros_var[df_retiros_var['pred_retiros_2017'] == 0] # Datos de las personas que no se retiran

# -------------------------- Análsis exploratorio de los resultados --------------------------

# Base de datos lista a trabajar 'retiros'

# Diagrama de tortas para los empleados retirados por cada departamento
retiros_dep = retiros.groupby(['Department'])[['pred_retiros_2017']].count().reset_index()

fig = px.pie(retiros_dep, names = 'Department', values = 'pred_retiros_2017', title ='<b>Renuncias de empleados por departamento<b>')

fig.update_layout(
    xaxis_title = 'retiros en cada departamento',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)

valores = retiros_dep['pred_retiros_2017'].tolist()
fig.update_traces(textinfo = 'percent+value', textposition = 'inside', textfont = dict(size = 12))

fig.show();

# Importancias de las variables para el modelo 
importancia = m_xg.feature_importances_
col_names = df_t.columns

importancia_df = pd.DataFrame({'Variable': col_names, 'Importancia': importancia}).sort_values(by = 'Importancia', ascending = False)


# -------------------------- Anlaisis departamento de Research & Development --------------------------

# DataSet para empleados que renuncian del departamento 'Research & Development'
df_Research_1 = retiros[retiros['Department'] == 'Research & Development']
df_Research_0 = no_retiros[no_retiros['Department'] == 'Research & Development']


#                                ********* Businnes Travel *********

# Análisis de los viajes con fines laborales de los empleados retirados y no retirados

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Research_1['BusinessTravel'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Research_0['BusinessTravel'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de los viajes respecto a negocios",
    template = 'simple_white')
fig.show();


#                                ********* Years At Company *********

# Análisis de los años en la compañía que tienen los empleados retirados y no retirados
years_1 = df_Research_1.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_1, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Renuncias por años en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()

years_0 = df_Research_0.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_0, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Permanencia en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()

 
 #           ********* JobSatisfaction,EnvironmentSatisfaction y WorkLifeBalance  *********


resumen = {'EnviromentSatistaction': [df_Research_1['EnvironmentSatisfaction'].mode()[0],df_Research_0['EnvironmentSatisfaction'].mode()[0]],
           'JobSatisfaction': [df_Research_1['JobSatisfaction'].mode()[0],df_Research_0['JobSatisfaction'].mode()[0]],
           'WorkLifeBalance': [ df_Research_1['WorkLifeBalance'].mode()[0],df_Research_0['WorkLifeBalance'].mode()[0]]}

resumen1 = pd.DataFrame(resumen, index = ['Renuncian', 'No renuncian'])
resumen1

 #                               ********* MonthlyIncome  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Research_1['MonthlyIncome'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Research_0['MonthlyIncome'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de los salarios mensuales",
    template = 'simple_white')
fig.show();

 #                               ********* Age  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Research_1['Age'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Research_0['Age'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de edades",
    template = 'simple_white')
fig.show();


# -------------------------- Anlaisis Sales ------------------------------------------------------

# DataSet para empleados que renuncian del departamento 'Sales'
df_Sales_1 = retiros[retiros['Department'] == 'Sales']
df_Sales_0 = no_retiros[no_retiros['Department'] == 'Sales']

#           ********* JobSatisfaction,EnvironmentSatisfaction y WorkLifeBalance  *********


resumen = {'EnviromentSatistaction': [df_Sales_1['EnvironmentSatisfaction'].mode()[0],df_Sales_0['EnvironmentSatisfaction'].mode()[0]],
           'JobSatisfaction': [df_Sales_1['JobSatisfaction'].mode()[0],df_Sales_0['JobSatisfaction'].mode()[0]],
           'WorkLifeBalance': [ df_Sales_1['WorkLifeBalance'].mode()[0],df_Sales_0['WorkLifeBalance'].mode()[0]]}

resumen2 = pd.DataFrame(resumen, index = ['Renuncian', 'No renuncian'])
resumen2

#                                ********* Years At Company *********

# Análisis de los años en la compañía que tienen los empleados retirados y no retirados
years_1 = df_Sales_1.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_1, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Renuncias por años en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()

years_0 = df_Sales_0.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_0, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Permanencia en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()

 #                               ********* MonthlyIncome  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Sales_1['MonthlyIncome'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Sales_0['MonthlyIncome'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de los salarios mensuales",
    template = 'simple_white')
fig.show();


 #                               ********* Age  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Sales_1['Age'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Sales_0['Age'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de edades",
    template = 'simple_white')
fig.show();



# -------------------------- Anlaisis Human Resources --------------------------------------------

# DataSet para empleados que renuncian del departamento 'Human Resources'
df_Human_1 = retiros[retiros['Department'] == 'Human Resources']
df_Human_0 = no_retiros[no_retiros['Department'] == 'Human Resources']

#           ********* JobSatisfaction,EnvironmentSatisfaction y WorkLifeBalance  *********


resumen = {'EnviromentSatistaction': [df_Human_1['EnvironmentSatisfaction'].mode()[0],df_Human_0['EnvironmentSatisfaction'].mode()[0]],
           'JobSatisfaction': [df_Human_1['JobSatisfaction'].mode()[0],df_Human_0['JobSatisfaction'].mode()[0]],
           'WorkLifeBalance': [ df_Human_1['WorkLifeBalance'].mode()[0],df_Human_0['WorkLifeBalance'].mode()[0]]}

resumen2 = pd.DataFrame(resumen, index = ['Renuncian', 'No renuncian'])
resumen2

 #                               ********* MonthlyIncome  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Human_1['MonthlyIncome'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Human_0['MonthlyIncome'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de los salarios mensuales",
    template = 'simple_white')
fig.show();


 #                               ********* Age  *********

fig = make_subplots(rows = 1, cols = 2)
fig.add_trace(
    go.Histogram(x = df_Human_1['Age'], name = 'Empleados que renuncian', marker_color = 'red'),
    row = 1, col = 1
)

fig.add_trace(
    go.Histogram(x = df_Human_0['Age'], name = 'Empleados que no renuncian', marker_color = 'green'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Histograma de edades",
    template = 'simple_white')
fig.show();

# Análisis de los años en la compañía que tienen los empleados retirados y no retirados
years_1 = df_Human_1.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_1, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Renuncias por años en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()

years_0 = df_Human_1.groupby(['YearsAtCompany'])[['EmployeeID']].count().reset_index()

fig = px.line(years_0, x = 'YearsAtCompany', y = 'EmployeeID')
fig.update_layout(
    title ='<b>Permanencia en la compañía<b>',
    xaxis_title = 'Años',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)
fig.show()
