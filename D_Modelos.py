# En este archivo se modela los algoritmos para el modelo de predicción 

# -------------------------- Librerias necesarias -------------------------------------

# Importar librerías clásicas de ciencia de datos
import pandas as pd
import numpy as np
import sqlite3 as sql

import importlib
import A_Funciones as funciones  # Archivo de funciones propias 
importlib.reload(funciones)


# Importar librerías de modelos candidatos 
from sklearn.linear_model import LogisticRegression # Regresión logística
from sklearn.ensemble import RandomForestClassifier  # Clasificador bosques aleatorios
from sklearn.linear_model import SGDClassifier # Descenso de gradiente estocástico
from xgboost import XGBClassifier # XGBoost 


# Importar librerías para selección de variables 
from sklearn.feature_selection import RFE # Método Wrapper - Eliminación hacia atrás 

# Librerias para gráficas
import matplotlib.pyplot as plt
import seaborn as sns

# Importar librerías para validación cruzada 
from sklearn.model_selection import cross_val_predict, cross_val_score, cross_validate

# Librería para construir matriz de confusión 
from sklearn.metrics import confusion_matrix

# Importar otras librerías importantes
from sklearn.preprocessing import StandardScaler # Para normalizar de datos
from sklearn.model_selection import RandomizedSearchCV # Seleccionar mejor modelo
import joblib # Para guardar modelos 
import openpyxl # Para crear archivos .xlsx 

# -------------------------- Conectarse a db para traer tablas -----------------------------

conn = sql.connect('C:\\Users\\jorge\\Desktop\\Proyecto RRHH\\data\\db')
#conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()

# Leemos tablas 2015  
df_2015 = pd.read_sql("SELECT * FROM tabla_2015", conn)

# ----------------------- Terminar preprocesado con Pandas ----------------------------------

# 1) Ya no necesitamos el EmployeeID 
df_2015.drop('EmployeeID', axis= 1, inplace = True)

# 2) Utilizamos funciones para recategorizar EducationField y JobRole a solo tres categorías 
funciones.clasificador_education(df_2015, 'EducationField')
funciones.clasificador_jobrole(df_2015, 'JobRole')

# 3) Eliminamos columnas EducationField y JobRole porque están recategorizadas 
df_2015.drop(['EducationField','JobRole'], axis = 1, inplace = True)

# 4) Convertimos categóricas a dummies
df_2015 = pd.get_dummies(df_2015, dtype = int)

# ----------------------------------- Selección de variables ---------------------------------

# Escalamos variables y separamos variables explicativas - variable objetivo
y = df_2015.renuncia2016 
X0 = df_2015.loc[:,~ df_2015.columns.isin(['renuncia2016'])]

scaler = StandardScaler()
scaler.fit(X0)

X1 = scaler.transform(X0)
X = pd.DataFrame(X1 , columns = X0.columns)
X

# ---------------------------------- Métodos Wrapper -----------------------------------------------------------

# Definimos los modelos a evaluar para selección de características 
m_lr = LogisticRegression()  
m_rf = RandomForestClassifier()
m_SGD = SGDClassifier()
m_xgb = XGBClassifier()

modelos = list([m_lr,m_rf,m_SGD,m_xgb])


# Eliminación hacia atrás (RFE)

#Se entrena un modelo que contenga todos los K regresores 
#Con la siguiente función ejecutamos un RFE para la lista de modelos 
#funciones.funcion_rfe(modelos,X,y,20,1)
#Convertimos el resultado en un dataframe para poder entender mejor los resultados 

df_resultados = pd.DataFrame(funciones.funcion_rfe(modelos, X, y, 25, 1))
df_resultados.fillna('No incluída',inplace = True)
df_resultados

# Creamos lista con variables seleccionadas tras analizar df_resultados y utilizar criterio de expertos
# (Revista Portafolio)

var_names = ['Department_Human Resources','Department_Research & Development',
             'Department_Sales','Age','MonthlyIncome','EnvironmentSatisfaction',
             'TrainingTimesLastYear','JobSatisfaction','NumCompaniesWorked',
             'WorkLifeBalance','DistanceFromHome', 'PercentSalaryHike', 'StockOptionLevel',
             'YearsAtCompany', 'JobInvolvement', 'BusinessTravel_Travel_Frequently',
             'Gender_Female']

list_cat = ['BusinessTravel', 'Department', 'Gender', 'MaritalStatus', 'education_sector','job_rol']
list_dummies = ['BusinessTravel', 'Department', 'Gender', 'MaritalStatus', 'education_sector','job_rol']

X2 = X[var_names]

# Matriz con variables seleccionadas 
X2

# Medimos el desempeño de los modelos para todo el conjunto de datos y para las variables seleccionadas
# Vamos a utilizar F1 - Score como métrica de desempeño, la variable objetivo está desbalanceada 

f1_df = funciones.medir_modelos(modelos,'f1', X, y, 5)
f1_df

f1_var_sel = funciones.medir_modelos(modelos, 'f1', X2, y, 5)
f1_var_sel

f1_df.plot(kind='box')
f1_var_sel.plot(kind='box')

f1_df['xgboost_classifier'].mean()
f1_var_sel['xgboost_classifier'].mean()

# Observamos que el mejor desempeño lo tiene un XGBoost Classifier con el conjunto de variables 
# seleccionadas. Se hará optimización de hiperparámetros para dicho algoritmo con dicho conjunto de datos. 


# -------------------------------- Afinamiento de hiperparámetros XGBoost ----------------------------------- 

param_grid = [{'max_depth': [3,4,5,6], 'scale_pos_weight': [6.44], 
               'eta':[0.01, 0.09, 0.1, 0.2],'subsample': [0.5,0.7,0.8,1]}]

# Parámetros: 
# max_depth -> Para evitar sobreajuste
# scale_pos_weight -> Control the balance of positive and negative weights, useful for unbalanced classes.
# A typical value to consider = sum(negative instances) / sum(positive instances)
# En nuestro caso, no renuncian: 3769 y renuncian: 585
# scale_pos_weight = 3769/585 = 6.44


tun_rf = RandomizedSearchCV(m_xgb, param_distributions = param_grid, n_iter = 5, scoring = "f1")
tun_rf.fit(X2, y)

pd.set_option('display.max_colwidth', 100)
resultados = tun_rf.cv_results_
tun_rf.best_params_
pd_resultados = pd.DataFrame(resultados)
pd_resultados[["params","mean_test_score"]].sort_values(by = "mean_test_score", ascending = False)

xg_final = tun_rf.best_estimator_


# Evaluación para mirar sobreajuste
eval = cross_validate(xg_final, X2, y, cv = 5, scoring = "f1", return_train_score = True)

train = pd.DataFrame(eval['train_score'])
test = pd.DataFrame(eval['test_score'])
train_test = pd.concat([train, test], axis = 1)
train_test.columns = ['train_score','test_score']

train_test 


# Realizamos las predicciones 
predictions = cross_val_predict(xg_final, X2, y, cv = 5)
pred_df = pd.DataFrame(predictions, columns = ['pred']) 


# Añadimos la columna de predicciones a df_2015 pata evaluar rendimiento del modelo
df_2015_con_pred = pd.concat([df_2015, pred_df], axis = 1)

# Construimos matriz de confusión 
conf_matrix = confusion_matrix(df_2015['renuncia2016'], df_2015_con_pred['pred'])
plt.figure(figsize = (8, 6))
sns.heatmap(conf_matrix, annot = True, fmt = "d", cmap = "Blues")
plt.xlabel('Valores predichos')
plt.ylabel('Valores reales observados')
plt.title('Matriz de confusión')
plt.show()


# ------------------- Análisis de variables con mayor importancia ----------------------
importancia = xg_final.feature_importances_
importancia 

col_names = X2.columns

# Crear un DataFrame con la importancia de las características
importancia_df = pd.DataFrame({'Variable': col_names, 'Importancia': importancia})

# Ordenar el DataFrame por importancia de las características
importancia_df  = importancia_df.sort_values(by = 'Importancia', ascending = False)

# Visualizar la importancia de las características
plt.figure(figsize=(10, 6))
plt.barh(importancia_df['Variable'], importancia_df['Importancia'])
plt.xlabel('Importancia')
plt.ylabel('Variable')
plt.title('Peso de cada variable sobre la predicción')
plt.show()

# ------------------- Exportación de datos ------------------- 

joblib.dump(xg_final, 'Salidas\\xg_final.pkl' )            # Modelo con afinamiento
joblib.dump(list_cat, 'Salidas\\list_cat.pkl')             # Variables categóricas
joblib.dump(list_dummies, 'Salidas\\list_dummies.pkl')     # Variables dummies
joblib.dump(var_names, 'Salidas\\var_names.pkl')           # Variables seleccionadas 
joblib.dump(scaler, 'Salidas\\scaler.pkl')                 # Escalador de datos entrenados