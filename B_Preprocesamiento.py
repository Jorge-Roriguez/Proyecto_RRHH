# Este apartado será utilizado para realizar el proprocesamiento de los datos 

# Librerias necesarias 
import pandas as pd
import sqlite3 as sql 
import A_Funciones as funciones
import sys 

# Agregar la ruta que contiene el archivo de funciones
sys.path
sys.path.append('C:\\Users\\jorge\\Desktop\\Proyecto RRHH')  # Agregamos ruta de colaborador 1 
sys.path.append('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH') # Agregamos ruta de colaborador 2
sys.path

# ------- Agregar datos desde GitHub -------------------------------------------------------------------------

# Tabla employee (Encuesta de satisfacción laboral 2015 y 2016)
employee = ('https://raw.githubusercontent.com/EstebanCaroP/proyecto_rrhh/main/data/employee_survey_data.csv') 
df_employee = pd.read_csv(employee)
df_employee.head(10)

# Tabla general (Información general de empleados)
general = ('https://raw.githubusercontent.com/EstebanCaroP/proyecto_rrhh/main/data/general_data.csv')
df_general = pd.read_csv(general)
df_general.head(10)

# Tabla manager (Encuesta desempeño de empleados)
manager = ('https://raw.githubusercontent.com/EstebanCaroP/proyecto_rrhh/main/data/manager_survey.csv')
df_manager = pd.read_csv(manager)
df_manager.head(10)

# Tabla retirement (Retiros de empleados 2015 y 2016)
retirement = ('https://raw.githubusercontent.com/EstebanCaroP/proyecto_rrhh/main/data/retirement_info.csv')
df_retirement = pd.read_csv(retirement)
df_retirement.head(10)


# Información general de las tablas 
df_employee.info()
df_general.info()
df_manager.info()
df_retirement.info()

# Convertir formato de fecha 
df_employee['DateSurvey'] = pd.to_datetime(df_employee['DateSurvey']) #Revisar este formato
df_general['InfoDate'] = pd.to_datetime(df_general['InfoDate'])
df_manager['SurveyDate'] = pd.to_datetime(df_manager['SurveyDate'])
df_retirement['retirementDate'] = pd.to_datetime(df_retirement['retirementDate'])

# convertir los ID de los empleados a categórica
df_employee = df_employee.astype({'EmployeeID' : object})
df_general = df_general.astype({'EmployeeID' : object})
df_manager = df_manager.astype({'EmployeeID' : object})
df_retirement = df_retirement.astype({'EmployeeID' : object})

# Eliminar columnas sin información relevante
df_employee = df_employee.drop(['Unnamed: 0'], axis = 1)
df_general = df_general.drop(['Unnamed: 0', 'EmployeeCount', 'Over18'], axis = 1)
df_manager = df_manager.drop(['Unnamed: 0'], axis = 1)
df_retirement = df_retirement.drop(['Unnamed: 0.1','Unnamed: 0', 'Attrition'], axis = 1)  # Aclarar por qué se eliminaron

# ------------- Creamos conexión con SQL --------------------------#

conn = sql.connect('C:\\Users\\ESTEBAN\\Desktop\\Proyecto_RRHH\\data\\db')
curr = conn.cursor()


# Movemos las tablas a la base de datos 
df_employee.to_sql('employee', conn, if_exists='replace')
df_general.to_sql('general', conn, if_exists='replace')
df_manager.to_sql('manager', conn, if_exists= 'replace')
df_retirement.to_sql('retirement', conn, if_exists= 'replace')

# Verificamos las tablas que quedaron en la base de datos db 

curr.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
curr.fetchall()

