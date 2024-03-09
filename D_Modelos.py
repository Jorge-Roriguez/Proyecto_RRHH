
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


# Importar librerías para validación cruzada 
from sklearn.model_selection import cross_val_predict, cross_val_score, cross_validate

# Importar otras librerías importantes
from sklearn.preprocessing import StandardScaler # Para normalizar de datos
from sklearn.model_selection import RandomizedSearchCV # Seleccionar mejor modelo
import joblib # Para guardar modelos 
import openpyxl # Para crear archivos .xlsx 

# -------------------------- Conectarse a db para traer tablas -----------------------------#

# conn = sql.connect('C:\\Users\\jorge\\Desktop\\Proyecto RRHH\\data\\db')
conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()

# Leemos tablas 2015 y 2016 
df_2015 = pd.read_sql("SELECT * FROM tabla_2015", conn)
df_2016 = pd.read_sql("SELECT * FROM tabla_2016", conn)
df_2015

# ----------------------- Terminar preprocesado con Pandas ----------------------------------------#

# 1) Ya no necesitamos el EmployeeID 
df_2015.drop('EmployeeID', axis= 1, inplace = True)
df_2016.drop('EmployeeID', axis = 1, inplace = True)

# 2) Utilizamos funciones para recategorizar EducationField y JobRole a solo tres categorías 
funciones.clasificador_education(df_2015, 'EducationField')
funciones.clasificador_jobrole(df_2015,'JobRole')
funciones.clasificador_education(df_2016, 'EducationField')
funciones.clasificador_jobrole(df_2016,'JobRole')

# 3) Eliminamos columnas EducationField y JobRole porque están recategorizadas 
df_2015.drop(['EducationField','JobRole'], axis = 1, inplace = True)
df_2016.drop(['EducationField','JobRole'], axis = 1, inplace = True)


# 4) Convertimos categóricas a dummies

df_2015 = pd.get_dummies(df_2015, dtype = int)
df_2016 = pd.get_dummies(df_2015, dtype = int)

# ----------------------------------- Selección de variables ----------------------------------------------#

# Escalamos variables y separamos variables regresoras - variable objetivo
y = df_2015.renuncia2016 
X0 = df_2015.loc[:,~ df_2015.columns.isin(['renuncia2016'])]

scaler = StandardScaler()
scaler.fit(X0)

X1 = scaler.transform(X0)
X = pd.DataFrame(X1 , columns = X0.columns)
X

# ---------------------------------- Métodos Wrapper ---------------------------------------------------- # 

# Definimos los modelos a evaluar para selección de características 
m_lr = LogisticRegression()  
m_rf = RandomForestClassifier()
m_SGD = SGDClassifier()
m_xgb = XGBClassifier()

modelos = list([m_lr,m_rf,m_SGD,m_xgb])


# Eliminación hacia atrás (RFE)
# Se entrena un modelo que contenga todos los K regresores 

#Con la siguiente función ejecutamos un RFE para la lista de modelos 
#funciones.funcion_rfe(modelos,X,y,20,1)
#Convertimos el resultado en un dataframe para poder entender mejor los resultados 

df_resultados = pd.DataFrame(funciones.funcion_rfe(modelos,X,y,25,1))
df_resultados.fillna('No incluída',inplace=True)
df_resultados



# Creamos lista con variables seleccionadas tras analizar df_resultados y utilizar criterio de expertos
# (Portafolio)

var_names = ['Department_Human Resources','Department_Research & Development',
             'Department_Sales','Age','MonthlyIncome','EnvironmentSatisfaction',
             'TrainingTimesLastYear','JobSatisfaction','NumCompaniesWorked',
             'WorkLifeBalance','DistanceFromHome', 'PercentSalaryHike', 'StockOptionLevel',
             'YearsAtCompany', 'JobInvolvement', 'BusinessTravel_Travel_Frequently',
             'Gender_Female', 'Gender_Male', 'MaritalStatus_Single', 'MaritalStatus_Married']

X2 = X[var_names]

# Matriz con variables seleccionadas 
X2


# Medimos el desempeño de los modelos para todo el conjunto de datos y para las variables seleccionadas
# Vamos a utilizar F1 - Score como métrica de desempeño, la variable objetivo está desbalanceada 


f1_df = funciones.medir_modelos(modelos,'f1',X,y,5)
f1_df

f1_var_sel = funciones.medir_modelos(modelos, 'f1',X2,y,5)
f1_var_sel

f1_df.plot(kind='box')
f1_var_sel.plot(kind='box')

f1_df['xgboost_classifier'].mean()
f1_var_sel['xgboost_classifier'].mean()

# Observamos que el mejor desempeño lo tiene un XGBoost Classifier con el conjunto de variables 
# seleccionadas. Se hará optimización de hiperparámetros para dicho algoritmo para dicho conjunto de datos. 


# -------------------------------------- Afinamiento de hiperparámetros XGBoost ------------------------------- #

m_xgb = XGBClassifier()

hiper = m_xgb.get_params()
hiper

param_grid = [{'max_depth': [3,4,5,6], 'scale_pos_weight': [6.44], 
               'eta':[0.01, 0.09, 0.1, 0.2],'subsample': [0.5,0.7,0.8,1] }]


# max_depth para evitar sobreajuste
# scale_pos_weight: Control the balance of positive and negative weights, useful for unbalanced classes.
# A typical value to consider: sum(negative instances) / sum(positive instances)

# En nuestro caso, no renuncian: 3769 y renuncian: 585
# scale_pos_weight = 3769/585 = 6.44

## binary:hinge: hinge loss for binary classification. 
# This makes predictions of 0 or 1, rather than producing probabilities.


tun_rf=RandomizedSearchCV(m_xgb,param_distributions=param_grid,n_iter=10,scoring="f1")
tun_rf.fit(X2,y)

pd.set_option('display.max_colwidth', 100)
resultados=tun_rf.cv_results_
tun_rf.best_params_
pd_resultados=pd.DataFrame(resultados)
pd_resultados[["params","mean_test_score"]].sort_values(by="mean_test_score", ascending=False)
