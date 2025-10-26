use master;
go
drop database if exists lab15_1;
go
create database lab15_1
go


use master;
go
drop database if exists lab15_2;
go
create database lab15_2
go

USE lab15_1;

IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

CREATE TABLE Department (
	DepartmentID int identity(1,1) primary key,
	 
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70) NOT NULL,
	 
	);
GO

INSERT INTO Department (DepartmentName, HeadDepartment) 
VALUES  
    ( N'Главное приемное отделение', N'Морозов'),
    ( N'Хирургическое отделение', N'Усачев');



USE lab15_2;

IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DoctorPhone char(16) PRIMARY KEY,
    DoctorName nvarchar(50) NOT NULL,
    Cabinet int NOT NULL,
    Qualification nvarchar(100) NOT NULL,
    DepartmentID int NOT NULL unique
);




USE lab15_1;
GO

IF OBJECT_ID(N'dbo.vwDepartment') IS NOT NULL
    DROP VIEW dbo.vwDepartment
GO

CREATE VIEW dbo.vwDepartment
AS
SELECT DepartmentID, DepartmentName, HeadDepartment
FROM Department
GO

USE lab15_2;
GO

IF OBJECT_ID(N'dbo.vwDoctor') IS NOT NULL
    DROP VIEW dbo.vwDoctor
GO

CREATE VIEW dbo.vwDoctor
AS
SELECT DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID
FROM Doctor
GO

USE lab15_1;
GO

IF OBJECT_ID (N'trgDepartmentInsert') is NOT NULL
    DROP TABLE trgDepartmentInsert
GO


CREATE TRIGGER trgDepartmentInsert
ON Department
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO Department (DepartmentName, HeadDepartment)
    SELECT DepartmentName, HeadDepartment FROM INSERTED
END
GO

IF OBJECT_ID (N'trgDepartmentUpdate') is NOT NULL
    DROP TABLE trgDepartmentUpdate
GO


CREATE TRIGGER trgDepartmentUpdate
ON  Department
INSTEAD OF UPDATE
AS
BEGIN
    -- Проверяем, было ли обновление первичного ключа
    IF UPDATE(DepartmentID)
    BEGIN
        RAISERROR('Нельзя обновлять суррогатный ключ.', 16, 1)
        ROLLBACK TRANSACTION
    END
    ELSE
    BEGIN
        UPDATE Department
        SET DepartmentName = INSERTED.DepartmentName,
            HeadDepartment = INSERTED.HeadDepartment
        FROM Department
        INNER JOIN INSERTED ON Department.DepartmentID = INSERTED.DepartmentID
    END
END
GO

IF OBJECT_ID (N'trgDepartmentDelete') is NOT NULL
    DROP TABLE trgDepartmentDelete
GO


CREATE TRIGGER trgDepartmentDelete
ON  Department
INSTEAD OF DELETE
AS
 IF (SELECT COUNT(*) FROM lab15_2..Doctor WHERE DepartmentID IN (SELECT DepartmentID FROM DELETED)) > 0
    BEGIN
        RAISERROR('Нельзя удалить родителя, если у него есть доктора', 16, 2)
        ROLLBACK TRANSACTION
    END
    ELSE
    BEGIN
        DELETE FROM Department
        WHERE DepartmentID IN (SELECT DepartmentID FROM DELETED)
    END
GO


USE lab15_2;


IF OBJECT_ID (N'trgDoctorInsert') is NOT NULL
    DROP TABLE trgDoctorInsert
GO


CREATE TRIGGER trgDoctorInsert
ON  Doctor
INSTEAD OF INSERT
AS
BEGIN
    IF EXISTS (SELECT 1 FROM INSERTED i LEFT JOIN lab15_1..Department d ON i.DepartmentID = d.DepartmentID WHERE d.DepartmentID IS NULL)
    BEGIN
        RAISERROR('Доктора можно вставлять только если существует родительский отдел.', 16, 5)
        ROLLBACK TRANSACTION
    END
    ELSE
    BEGIN
        INSERT INTO Doctor (DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID)
        SELECT DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID FROM INSERTED
    END
END
GO


IF OBJECT_ID (N'trgDoctorUpdate') is NOT NULL
    DROP TABLE trgDoctorInsert
GO
 
CREATE TRIGGER trgDoctorUpdate
ON Doctor
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE Doctor
    SET DoctorName = INSERTED.DoctorName,
        Cabinet = INSERTED.Cabinet,
        Qualification = INSERTED.Qualification,
        DepartmentID = INSERTED.DepartmentID
    FROM Doctor
    INNER JOIN INSERTED ON Doctor.DoctorPhone = INSERTED.DoctorPhone
END
GO

IF OBJECT_ID (N'trgDoctorDelete') is NOT NULL
    DROP TABLE trgDoctorInsert
GO

CREATE TRIGGER trgDoctorDelete
ON lab15_2..Doctor
INSTEAD OF DELETE
AS
BEGIN
    DELETE FROM Doctor
    WHERE DoctorPhone IN (SELECT DoctorPhone FROM DELETED)
END
GO

 
--------------------------------------------
--TESTS

USE lab15_1;
INSERT INTO Department (DepartmentName, HeadDepartment) VALUES (N'Отделение терапии', N'Иванов И.И.');
SELECT * from Department;
-- SELECT * from Doctor;
go



USE lab15_2;
 
INSERT INTO Doctor (DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID) 
VALUES ('+7(495)111-22-33', N'Доктор Иванович', 101, N'Терапевт', 3);
GO

INSERT INTO Doctor (DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID) 
VALUES ('+7(495)222-33-44', N'Доктор Неизвестный', 102, N'Неизвестно', 100); ---Отделения не существует
GO

SELECT * from Doctor;
GO

USE lab15_1;
GO

UPDATE Department SET DepartmentID = DepartmentID + 1 WHERE DepartmentName = N'Отделение терапии';
 
DELETE FROM Department WHERE DepartmentName = N'Отделение терапии'; --Ошибка - отделение с докторами
go

SELECT * from Department
go

