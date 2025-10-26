USE lab6;
GO

--Создать представление на основе одной из таблиц задания 6.

if OBJECT_ID(N'HospitalView') IS NOT NULL
	DROP VIEW HospitalView
GO

CREATE VIEW HospitalView AS
	SELECT * FROM Hospital
	WHERE NumDepartment > 5
GO

SELECT * FROM HospitalView
GO

-- Создать представление на основе полей обеих связанных таблиц задания 6.

IF OBJECT_ID(N'DepView') IS NOT NULL
	DROP VIEW DepView
GO

CREATE VIEW DepView AS
	SELECT h.Hospital_ID, d.DepartmentID
	FROM Hospital as h INNER JOIN Department as d
	ON h.Hospital_ID = d.Hospital_ID
GO

SELECT * FROM DepView
GO

-- Создать индекс для одной из таблиц задания 6, включив в него дополнительные неключевые поля.

IF EXISTS (SELECT * FROM sys.indexes  WHERE name = N'Specialization_Description')  
    DROP INDEX Specialization_Description ON Hospital
GO

CREATE INDEX Specialization_Description
	ON Hospital(HospitalAddress)
	INCLUDE (Name)
GO

-- Создать индексированное представление.


IF OBJECT_ID(N'HospView') IS NOT NULL
	DROP VIEW HospView
GO

CREATE VIEW HospView WITH SCHEMABINDING AS
	SELECT Hospital_ID, HeadPhysician, NumDepartment
	FROM dbo.Hospital
	WHERE NumDepartment > 10
GO


IF EXISTS (SELECT * FROM sys.indexes  WHERE name = N'IX_Main_Description')  
    DROP INDEX IX_Main_Description ON Hospital  
GO

CREATE UNIQUE CLUSTERED INDEX IX_Main_Description
    ON HospView (Hospital_ID,  HeadPhysician);
go

SELECT * FROM HospView
go