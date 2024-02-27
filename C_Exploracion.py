import pandas as pd ### para manejo de datos
import sqlite3 as sql #### para bases de datos sql
import matplotlib as mpl ## gráficos
import matplotlib.pyplot as plt ### gráficos
from pandas.plotting import scatter_matrix  ## para matriz de correlaciones
from sklearn import tree ###para ajustar arboles de decisión
from sklearn.tree import export_text ## para exportar reglas del árbol
from IPython.display import display, Markdown
pd.set_option('display.max_columns', None)
import sys


sys.path.append('C:\\Users\\jorge\\Desktop\\Proyecto RRHH')  # Agregamos ruta de colaborador 1 
sys.path.append('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH') # Agregamos ruta de colaborador 2
sys.path

import A_Funciones as funciones ### archivo de funciones propias



conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()

curr.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
curr.fetchall()

df_2015 =pd.read_sql("select * from tablal",conn)
df_2015

df_2016 = pd.read_sql("select * from tabla2", conn)
df_2016


tabla_completa = pd.concat([df_2015, df_2016], axis=0)
tabla_completa


def check_df(dataframe, head=10):
    display(Markdown('*Dimensiones base general*'))
    display(dataframe.shape)

    display(Markdown('*Número de duplicados*'))
    display(dataframe.duplicated().sum())
    display(dataframe[dataframe.duplicated(keep='last')])
    display(dataframe[dataframe.duplicated(keep='first')])

    display(print(" \n "))

    display(Markdown('*Tipos*'))
    display(dataframe.dtypes)

    display(Markdown('*Primeros Registros*'))
    display(dataframe.head(head))

    display(Markdown('*Nulos*'))
    display(dataframe.isnull().sum())

    display(Markdown('*Percentiles*'))
    display(dataframe.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df_2015)
check_df(df_2016)


