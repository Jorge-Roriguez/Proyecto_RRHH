-- Crear tabla empleados 2015
CREATE TABLE employee1 AS
SELECT * 
FROM employee
WHERE DateSurvey = '2015-12-31 00:00:00';

-- Crear tabla empleados 2016
CREATE TABLE employee2 AS 
SELECT * 
FROM employee
WHERE DateSurvey = '2016-12-31 00:00:00';

-- Crear tabla general 2015
CREATE TABLE general1 AS 
SELECT * 
FROM general
WHERE InfoDate = '2015-12-31 00:00:00';

-- Crear tabla general 2016
CREATE TABLE general2 AS 
SELECT * 
FROM general
WHERE InfoDate = '2016-12-31 00:00:00';

-- Crear tabla manager 2015
CREATE TABLE manager1 AS
SELECT * 
FROM manager
WHERE SurveyDate = '2015-12-31 00:00:00';

-- Crear tabla manager 2016
CREATE TABLE manager2 AS
SELECT * 
FROM manager
WHERE SurveyDate = '2016-12-31 00:00:00';

-- Crear tabla retiros 2015
CREATE TABLE retirement1 AS
SELECT *
FROM retirement
WHERE strftime('%Y', retirementDate) = '2015';

-- Crear tabla retiros 2016
CREATE TABLE retirement2 AS
SELECT *
FROM retirement
WHERE strftime('%Y', retirementDate) = '2016';

-- Unimos y creamos una tabla de la información sobre 2015
CREATE TABLE tabla1 AS
SELECT * 
FROM general1 g1
JOIN employee1 e1
	ON g1.EmployeeID = e1.EmployeeID
JOIN manager1 m1
	ON g1.EmployeeID = m1.EmployeeID
LEFT JOIN retirement1 r1
	ON g1.EmployeeID = r1.EmployeeID;


-- Unimos y creamos una tabla de la información sobre 2016
CREATE TABLE tabla2 AS
SELECT * 
FROM general2 g2 
JOIN employee2 e2
	ON g2.EmployeeID = e2.EmployeeID
JOIN manager2 m2
	ON g2.EmployeeID = m2.EmployeeID
LEFT JOIN retirement2 r2
	ON g2.EmployeeID = r2.EmployeeID;


-- Creamos variable objetivo para 2015
CREATE TABLE retiros_2016 AS
SELECT EmployeeID, retirementType AS retiro_2016
FROM tabla2;

-- Creamos una tabla auxliar para unir la variable objetivo y datos del 2015
CREATE TABLE tabla_20150 AS
SELECT * 
FROM tabla1 t1
JOIN retiros_2016 r1
	ON t1.EmployeeID = r1.EmployeeID;
	
-- Creamos otra tabla para convertir la variable objetivo a binaria, 1 -> Se retira 0 -> No se retira	
CREATE TABLE tabla_2015 AS
SELECT *,
CASE
	WHEN retiro_2016 = 'Resignation' THEN 1
	ELSE 0
END AS renuncia2016
FROM tabla_20150;


-- Creamos una tabla con las renuncias del 2015 
CREATE TABLE renuncias_2015 AS 
SELECT * FROM tabla_2015
WHERE retirementType = 'Resignation';

-- Se borran de los datos del 2015
DELETE FROM tabla_2015
WHERE retirementType = 'Resignation';

-- Borramos columnas innecesarias en los datos 2015
ALTER TABLE tabla_2015
DROP COLUMN InfoDate;

ALTER TABLE tabla_2015
DROP COLUMN 'EmployeeID:1';

ALTER TABLE tabla_2015
DROP COLUMN DateSurvey;

ALTER TABLE tabla_2015
DROP COLUMN 'EmployeeID:2';

ALTER TABLE tabla_2015
DROP COLUMN SurveyDate;

ALTER TABLE tabla_2015
DROP COLUMN 'EmployeeID:3';

ALTER TABLE tabla_2015
DROP COLUMN retirementDate;

ALTER TABLE tabla_2015
DROP COLUMN resignationReason;

ALTER TABLE tabla_2015
DROP COLUMN retirementType;

ALTER TABLE tabla_2015
DROP COLUMN 'EmployeeID:4';

ALTER TABLE tabla_2015
DROP COLUMN retiro_2016;

ALTER TABLE tabla_2015
DROP COLUMN StandardHours;


-- Eliminaron los registros que renunciaron desde el 2015 en la tabla 2016
DELETE FROM tabla2
WHERE EXISTS (
    SELECT *
    FROM renuncias_2015 r
    WHERE r.EmployeeID = tabla2.EmployeeID
);


-- Borramos columnas innecesarias en los datos 2016
ALTER TABLE tabla2
DROP COLUMN InfoDate;

ALTER TABLE tabla2
DROP COLUMN 'EmployeeID:1';

ALTER TABLE tabla2
DROP COLUMN DateSurvey;

ALTER TABLE tabla2
DROP COLUMN 'EmployeeID:2';

ALTER TABLE tabla2
DROP COLUMN SurveyDate;

ALTER TABLE tabla2
DROP COLUMN 'EmployeeID:3';

ALTER TABLE tabla2
DROP COLUMN retirementDate;

ALTER TABLE tabla2
DROP COLUMN resignationReason;

ALTER TABLE tabla2
DROP COLUMN StandardHours;

-- Renombramos la tabla2 a tabla_2016
ALTER TABLE tabla2 RENAME TO tabla_2016;

-- Borramos la variable objetivo de la tabla 2016, estos datos serán para predecir 2017
ALTER TABLE tabla_2016
DROP COLUMN retirementType;
