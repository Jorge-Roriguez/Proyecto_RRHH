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


# ------------Convertimos los datos de tipo float a int (POR la naturaleza de cada variable) ---------

df_2015 = df_2015.astype({'Age':'int64', 'DistanceFromHome':'int64', 'Education':'int64', 
                          'JobLevel':'int64', 'NumCompaniesWorked':'int64', 
                          'PercentSalaryHike':'int64', 'EmployeeID':'object',
                          'StockOptionLevel':'int64', 'TotalWorkingYears':'int64',
                          'TrainingTimesLastYear':'int64', 'YearsAtCompany':'int64',
                          'YearsSinceLastPromotion':'int64', 'YearsWithCurrManager': 'int64',
                          'EnvironmentSatisfaction':'int64', 'JobSatisfaction':'int64',
                          'WorkLifeBalance':'int64', 'MonthlyIncome':'int64'})


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
base = df_2015.groupby(['Department'])[['EmployeeID']].count().reset_index().sort_values('EmployeeID', ascending = False).rename(columns ={'EmployeeID':'count'})

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


# ----------------------------- Análisis univariado variable edad de empleados ------------------------

# Histograma y boxplot de la edad de los empleados en 2015
fig = make_subplots(rows = 1, cols = 2)

fig.add_trace(
    go.Histogram(x = df_2015['Age'], name = 'Histograma años de empleados', marker_color = 'cadetblue'),
    row = 1, col = 1
)

fig.add_trace(
    go.Box(y = df_2015['Age'], name = 'Boxplot años de empleados', marker_color = 'firebrick'),
    row = 1, col = 2
)

fig.update_layout(
    title_text = "Distribución de edad de los empleados",
    template = 'simple_white')
fig.show()

fig_edad = fig    # Guardamos los gráficos


# ----------------------------- Análisis univariado satisfacción entorno de trabajo ------------------

# Diagrama del nivel de satisfacción laboral en 2015
base = df_2015.groupby(['EnvironmentSatisfaction'])[['EmployeeID']].count().reset_index()

cant = df_2015['EnvironmentSatisfaction'].count()

fig = px.pie(base , values = 'EmployeeID', names = 'EnvironmentSatisfaction', title = '<b>Nivel de satisfacción laboral<b>',
             hole = .5)

fig.update_layout(
    template = 'simple_white',
    legend_title = '<b>Ambiente laboral<b>',
    title_x = 0.5,
    annotations = [dict(text = 'Muestras:<br>'+str(cant), x=0.5, y = 0.5, font_size = 20, showarrow = False)])

fig.show()

fig_ambiente_lab = fig  # Guardamos la figura 


# Información complementaria - Porcentaje de renuncias en un ambiente laboral bajo
consulta = df_2015[['EnvironmentSatisfaction','renuncia2016']]
cons = consulta[consulta['EnvironmentSatisfaction'] == 1].sum()

print("Empleados que renuncian en un ambiente laboral bajo: ", cons.iloc[1], 
      "\nLo que equivale a un: ", round(cons.iloc[1]/df_2015['renuncia2016'].sum()*100,2),
      "% del total de renuncias")


# ----------------------------- Análisis bivariado Renuncias por departamentos ------------------------

renuncias = df_2015[df_2015['renuncia2016'] == 1]
base = renuncias.groupby(['Department'])[['renuncia2016']].count().reset_index()

grap_renVSdep = sns.barplot(x = "Department", y = "renuncia2016", data = base, hue = 'Department');
print("Porcentajes de retiros por departamento: ",
      "\nHuman Resources: ",round(base['renuncia2016'].iloc[0]/base['renuncia2016'].sum()*100, 2),"%",
      "\nResearch & Development: ",round(base['renuncia2016'].iloc[1]/base['renuncia2016'].sum()*100, 2),"%",
      "\nSales: ",round(base['renuncia2016'].iloc[2]/base['renuncia2016'].sum()*100, 2),"%")


# ----------------------------- Análisis bivariado Renuncias por edad ---------------------------------

base = renuncias.groupby(['Age'])[['renuncia2016']].count().reset_index()

grap_renVSage = sns.lineplot(x = 'Age', y = 'renuncia2016', data = base)
print('El aumento en la edad de los empleados no implica mayor cantidad de retiros',
      '\nEntre los empleados con 25 a 35 años es dónde se presentan mayores retiros')


# ----------------------------- Análisis bivariado Renuncias por ambiente laboral ---------------------

base = renuncias.groupby(['EnvironmentSatisfaction'])[['renuncia2016']].count().reset_index()

grap_renVSamb = sns.barplot(x = "EnvironmentSatisfaction", y = "renuncia2016", data = base, palette = "Blues_d");
print("Apesar de la proporción desigual de empleados en los distintos niveles de ambiente laboral,",
      "\nLa cantidad de renuncias no se ven discrimindas por el ambiente laboral")


# ----------------------------- Matriz de coorrelación  ----------------------------------------------

figure(figsize = (17, 10), dpi = 70);
fig_correlación = sns.heatmap(df_2015._get_numeric_data().corr(), annot = True);
fig_correlación