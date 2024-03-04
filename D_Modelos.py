
# Importar librerías clásicas de ciencia de datos
import pandas as pd
import numpy as np
import sqlite3 as sql
import importlib
import A_Funciones as funciones  # Archivo de funciones propias 
importlib.reload(funciones) 

# Importar librerías de modelos candidatos 
from sklearn.linear_model import LogisticRegression # Regresión logística
from sklearn.svm import SVC # Support Vector Classifier
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

y = df_2015.renuncia2016 # Separamos variable objetivo
X0 = df_2015.loc[:,~ df_2015.columns.isin(['renuncia2016'])] # Separamos variables explicativas de objetivo

scaler = StandardScaler()
scaler.fit(X0)

X1 = scaler.transform(X0)
X = pd.DataFrame(X1 , columns = X0.columns)
X


# ---------------------------------- Métodos Wrapper ---------------------------------------------------- # 

# Definimos los modelos a evaluar para selección de características 
m_lr = LogisticRegression()
m_svc = SVC()
m_SGD = SGDClassifier()
m_xgb = XGBClassifier()

modelos = list([m_lr,m_svc,m_SGD,m_xgb])


# Eliminación hacia atrás (RFE)
# Se entrena un modelo que contenga todos los K regresores 


def recursive_feature_selection(X,y,model,k): # model = modelo que me va a servir de estimador
  rfe = RFE(model, n_features_to_select=k, step=1) # step=1 cada cuanto el toma la decision de tomar una caracteristica
  fit = rfe.fit(X, y)
  X_new = fit.support_

  print("Num Features: %s" % (fit.n_features_))
  print("Selected Features: %s" % (fit.support_))
  print("Feature Ranking: %s" % (fit.ranking_))

  return X_new


X_new = recursive_feature_selection(X,y,m_lr,20)

df_new = X.iloc[:,X_new]
df_new.head()
