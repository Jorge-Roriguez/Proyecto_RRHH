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

# -------------------------- Aplicar transformaciones a los datos (Imputar, Dummies, Escalar) ----

df_t = funciones.preparar_datos(df_2016)
df_t







