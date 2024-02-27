CREATE TABLE employee1 AS
SELECT * 
FROM employee
WHERE DateSurvey = '2015-12-31 00:00:00';

CREATE TABLE employee2 AS 
SELECT * 
FROM employee
WHERE DateSurvey = '2016-12-31 00:00:00';

CREATE TABLE general1 AS 
SELECT * 
FROM general
WHERE InfoDate = '2015-12-31 00:00:00';

CREATE TABLE general2 AS 
SELECT * 
FROM general
WHERE InfoDate = '2016-12-31 00:00:00';

CREATE TABLE manager1 AS
SELECT * 
FROM manager
WHERE SurveyDate = '2015-12-31 00:00:00';

CREATE TABLE manager2 AS
SELECT * 
FROM manager
WHERE SurveyDate = '2016-12-31 00:00:00';

SELECT * FROM retirement1;


CREATE TABLE retirement1 AS
SELECT *
FROM retirement
WHERE strftime('%Y', retirementDate) = '2015';


CREATE TABLE retirement2 AS
SELECT *
FROM retirement
WHERE strftime('%Y', retirementDate) = '2016';

CREATE TABLE tablal AS
SELECT * 
FROM general1 g1
JOIN employee1 e1
	ON g1.EmployeeID = e1.EmployeeID
JOIN manager1 m1
	ON g1.EmployeeID = m1.EmployeeID
LEFT JOIN retirement1 r1
	ON g1.EmployeeID = r1.EmployeeID;


SELECT * FROM tablal;
	
CREATE TABLE tabla2 AS
SELECT * 
FROM general2 g2 
JOIN employee2 e2
	ON g2.EmployeeID = e2.EmployeeID
JOIN manager2 m2
	ON g2.EmployeeID = m2.EmployeeID
LEFT JOIN retirement2 r2
	ON g2.EmployeeID = r2.EmployeeID;
	
SELECT * FROM tabla2;

