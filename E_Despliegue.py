# En este archivo se muestra el despliegue del modelo con las predicciones para 2017

# -------------------------- Librerias necesarias ------------------------------------------

import pandas as pd
import sqlite3 as sql
import joblib
import numpy as np
import openpyxl

import importlib
import A_Funciones as funciones  # Archivo de funciones propias 
importlib.reload(funciones)

# -------------------------- Conectarse a db para traer tablas -----------------------------

# Crear conexíon 
conn = sql.connect('C:\\Users\\jorge\\Desktop\\Proyecto RRHH\\data\\db')
#conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
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
 

# -------------------------- Llevar datos a BD para despliegue -------------------------------------------------------------

# Retiros de los empleados por departamento (Diseño de la solución)
df_retiros_var.loc[:, ['EmployeeID', 'Department', 'pred_retiros_2017']].to_sql('retiros_pred', conn, if_exists = 'replace', index = False)


# -------------------------- Predicciones por departamento -----------------------------------

retiros = df_retiros_var[df_retiros_var['pred_retiros_2017'] == 1]
retiros_dep = retiros.groupby(['Department'])[['pred_retiros_2017']].count().reset_index()
retiros_dep


# -------------------------- Exportar los resultados de interés --------------------------

# Retiros por departamentos
df_predicciones_2017 = retiros[['EmployeeID', 'Department', 'pred_retiros_2017']]
df_predicciones_2017.set_index('EmployeeID', inplace = True) 
df_predicciones_2017.to_excel('Salidas\\df_predicciones_2017.xlsx')


# -------------------------- Análsis exploratorio de los resultados --------------------------