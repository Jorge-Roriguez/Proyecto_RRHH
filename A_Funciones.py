# Este apartado será para disponer de todas las funciones requeridas para el proyecto de recursos humanos


# Librerias necesarias 
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer # Para imputación
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import cross_val_predict, cross_val_score, cross_validate
import joblib
from sklearn.preprocessing import StandardScaler # Escalar variables 
from sklearn.feature_selection import RFE


# Esta función permite ejecutar un archivo  con extensión .sql que contenga varias consultas

def ejecutar_sql (nombre_archivo, cur):
  sql_file=open(nombre_archivo)
  sql_as_string=sql_file.read()
  sql_file.close
  cur.executescript(sql_as_string)
  
  
def imputar_numericas (df, tipo):

    if str(tipo) == 'mean':
        numericas = df.select_dtypes(include=['number']).columns
        imp_mean = SimpleImputer(strategy='mean')
        df[numericas] = imp_mean.fit_transform(df[numericas])
        return df
    
    if str(tipo) == 'most_frequent':
        numericas = df.select_dtypes(include=['number']).columns
        imp_mean = SimpleImputer(strategy='most_frequent')
        df[numericas] = imp_mean.fit_transform(df[numericas])
        return df
    

def sel_variables(modelos,X,y,threshold):
    
    var_names_ac=np.array([])
    for modelo in modelos:
        #modelo=modelos[i]
        modelo.fit(X,y)
        sel = SelectFromModel(modelo, prefit=True,threshold=threshold)
        var_names= modelo.feature_names_in_[sel.get_support()]
        var_names_ac=np.append(var_names_ac, var_names)
        var_names_ac=np.unique(var_names_ac)
    
    return var_names_ac


def medir_modelos(modelos,scoring,X,y,cv):

    metric_modelos=pd.DataFrame()
    for modelo in modelos:
        scores=cross_val_score(modelo,X,y, scoring=scoring, cv=cv )
        pdscores=pd.DataFrame(scores)
        metric_modelos=pd.concat([metric_modelos,pdscores],axis=1)
    
    metric_modelos.columns=["reg_lineal","decision_tree","random_forest","gradient_boosting"]
    return metric_modelos



def preparar_datos (df):
   
    

    ####### Cargar y procesar nuevos datos ######
   
    
    # Cargar modelo y listas 
    
   
    list_cat=joblib.load("list_cat.pkl")
    list_dummies=joblib.load("list_dummies.pkl")
    var_names=joblib.load("var_names.pkl")
    scaler=joblib.load( "scaler.pkl") 

    # Ejecutar funciones de transformaciones
    
    df=imputar_f(df,list_cat)
    df_dummies=pd.get_dummies(df,columns=list_dummies)
    df_dummies= df_dummies.loc[:,~df_dummies.columns.isin(['perf_2023','EmpID2'])]
    X2=scaler.transform(df_dummies)
    X=pd.DataFrame(X2,columns=df_dummies.columns)
    X=X[var_names]
    
    
    return X


def convertir_fecha(dataframe, columna):

    dataframe[columna] = pd.to_datetime(dataframe[columna])

    return dataframe.info()

def convertir_fecha(dataframe, columna):

    dataframe[columna] = pd.to_datetime(dataframe[columna])

    return dataframe.info()


def clasificador_jobrole(df, nombre_columna):
    df[nombre_columna] = df[nombre_columna].astype('category')

    # Definimos las categorías y cómo las vamos a recategorizar 
    diccionario_rol = {
        'Healthcare Representative': 'Research & Development',
        'Research Scientist': 'Research & Development',
        'Sales Executive': 'Sales',
        'Human Resources': 'Human Resources',
        'Research Director': 'Research & Development',
        'Laboratory Technician': 'Research & Development',
        'Manufacturing Director': 'Research & Development',
        'Sales Representative': 'Sales',
        'Manager': 'Manager'
    }

    # Creamos una columna nueva que contenga la recategorización 
    df["job_rol"] = df[nombre_columna].replace(diccionario_rol)

    return df

def clasificador_education(df, nombre_columna):
    df[nombre_columna] = df[nombre_columna].astype('category')

    # Definimos las categorías y cómo las vamos a recategorizar 
    diccionario_educacion = {
        'Life Sciences': 'Research',
        'Other': 'Research',
        'Medical': 'Research',
        'Technical Degree': 'Research',
        'Marketing': 'Marketing',
        'Human Resources': 'Human Resources',
    }

    # Creamos una columna nueva que contenga la recategorización 
    df["education_sector"] = df[nombre_columna].replace(diccionario_educacion)

    return df


def funcion_rfe(modelos,X,y, num_variables, paso):
  resultados = {}
  for modelo in modelos: 
    rfemodelo = RFE(modelo, n_features_to_select = num_variables, step = paso)
    fit = rfemodelo.fit(X,y)
    var_names = fit.get_feature_names_out()
    puntaje = fit.ranking_
    diccionario_importancia = {}
    nombre_modelo = modelo.__class__.__name__

    for i,j in zip(var_names,puntaje):
      diccionario_importancia[i] = j
      resultados[nombre_modelo] = diccionario_importancia
  
  return resultados
