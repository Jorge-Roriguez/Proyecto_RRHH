# Este apartado será para realizar el análsis exploratorio de los datos tratados en preprocesamiento

# Librerias necesarias 
import pandas as pd                             # Para manejo de datos
import sqlite3 as sql                           # Para bases de datos sql
import matplotlib as mpl                        # Gráficos
import matplotlib.pyplot as plt                 # Gráficos
from pandas.plotting import scatter_matrix      # Para matriz de correlaciones
from sklearn import tree                        # Para ajustar arboles de decisión
from sklearn.tree import export_text            # Para exportar reglas del árbol
from IPython.display import display, Markdown
pd.set_option('display.max_columns', None)
import sys
import A_Funciones as funciones                 # Archivo de funciones propias

# Para visualizaciones
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.pyplot import figure
import seaborn as sns


# ----------------------------- Importación de los datos tratados ----------------------------- 

conn = sql.connect('C:\\Users\\jorge\\Desktop\\Proyecto RRHH\\data\\db')
#conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()

df_2015 = pd.read_sql("select * from tabla_2015", conn)
df_2016 = pd.read_sql("select * from tabla_2016", conn)

# ----------------------------- Análisis univariado variable respuesta -----------------------------

# Histograma renuncias de empleados en 2016
fig = make_subplots(rows = 1, cols = 1)

fig.add_trace(
    go.Histogram(x = df_2015['renuncia2016'], name = 'Histograma de renuncias', marker_color = 'thistle'),
    row = 1, col = 1
)

fig.update_layout(
    title_text = "Distribución renuncias de empleados en 2016",
    template = 'simple_white')

fig.show();

fig_renuncias = fig # Guardamos el histograma

print("La cantidad de renuncias de empleados en 2016 es: ", df_2015['renuncia2016'].sum(), 
      "\nLo que equivale a: ", round(df_2015['renuncia2016'].sum()/len(df_2015) * 100, 2), 
      "% de los empleados de la compañia")

# ----------------------------- Análisis univariado variable departament -----------------------------

# Diagrama de tortas para los empleados por departamentos en 2015
base = df_2015.groupby(['Department'])[['renuncia2016']].count().reset_index().sort_values('renuncia2016', ascending = False).rename(columns ={'renuncia2016':'count'})

fig = px.pie(base, names = 'Department', values = 'count', title ='<b>Empleados por departamento<b>')

fig.update_layout(
    xaxis_title = 'Empleados en cada departamento',
    yaxis_title = 'Cantidad',
    template = 'simple_white',
    title_x = 0.5)

fig.show();
fig_departamentos = fig # Guardamos el diagrama de torta

print("Empleados por departamento: \n", 
      "\nResearch & Development: ", base['count'][1], 
      "\nSales: ", base['count'][2], 
      "\nHuman Resources: ", base['count'][0])

# ----------------------------- Matriz de coorrelación  -----------------------------

figure(figsize = (17, 10), dpi = 70);
sns.heatmap(df_2015._get_numeric_data().corr(), annot = True);


# Convertimos los datos de tipo float a int (POR la naturaleza de cada variable)
df_2015 = df_2015.astype({'Age':'int64', 'DistanceFromHome':'int64', 'Education':'int64', 
                          'JobLevel':'int64', 'NumCompaniesWorked':'int64', 
                          'PercentSalaryHike':'int64', 'StandardHours':'int64',
                          'StockOptionLevel':'int64', 'TotalWorkingYears':'int64',
                          'TrainingTimesLastYear':'int64', 'YearsAtCompany':'int64',
                          'YearsSinceLastPromotion':'int64', 'YearsWithCurrManager': 'int64',
                          'EnvironmentSatisfaction':'int64', 'JobSatisfaction':'int64',
                          'WorkLifeBalance':'int64', 'MonthlyIncome':'int64'})

# ----------------------------- Análsis univariado variable edad de empleados --------

# Histograma y boxplot de la edad de los empleados en 2015
fig = make_subplots(rows=1, cols=2)

fig.add_trace(
    go.Histogram(x=df_2015['Age'], name='Histograma años de empleados', marker_color='cadetblue'),
    row=1, col=1
)

fig.add_trace(
    go.Box(y=df_2015['Age'], name='Boxplot años de empleados', marker_color='firebrick'),
    row=1, col=2
)

fig.update_layout(
    title_text="Distribución de edad de los empleados",
    template='simple_white')
fig.show()

fig_edad = fig    # Guardamos los gráficos
