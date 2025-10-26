use master;
go
drop database if exists lab14_1
create database lab14_1
go

 
use master;
go
drop database if exists lab14_2
create database lab14_2
go
 


USE lab14_1; 

IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DocId int PRIMARY KEY,
    DoctorPhone char(16),
    DoctorName nvarchar(50),
    Qualification nvarchar(100)
);
GO


USE lab14_2; 


IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DocId int PRIMARY KEY,
    Cabinet int,
    Department nvarchar(50)
);
GO


USE lab14_1; 
GO

IF OBJECT_ID (N'VerticalDoctorView') IS NOT NULL
    DROP VIEW VerticalDoctorView;
GO

CREATE VIEW VerticalDoctorView AS
    SELECT
        m.DocId,
        m.DoctorPhone,
        m.DoctorName,
        m.Qualification,
        d.Cabinet,
        d.Department
    FROM lab14_1.dbo.Doctor m
    INNER JOIN lab14_2.dbo.Doctor d ON m.DocId = d.DocId;
GO

drop trigger if exists trg_InsertVerticalDoctorView
go


CREATE TRIGGER trg_InsertVerticalDoctorView
ON VerticalDoctorView
INSTEAD OF INSERT
AS
BEGIN

    INSERT INTO lab14_1.dbo.Doctor (DocId, DoctorPhone, DoctorName, Qualification) 
    SELECT DocId, DoctorPhone, DoctorName, Qualification FROM INSERTED;

    INSERT INTO lab14_2.dbo.Doctor (DocId, Cabinet, Department) 
    SELECT DocId, Cabinet, Department FROM INSERTED;
END
GO

drop trigger if exists trg_UpdateVerticalDoctorView
go

CREATE TRIGGER trg_UpdateVerticalDoctorView
ON VerticalDoctorView
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE lab14_1.dbo.Doctor 
    SET DoctorPhone = INSERTED.DoctorPhone, DoctorName = INSERTED.DoctorName, Qualification = INSERTED.Qualification
    FROM lab14_1.dbo.Doctor m
    INNER JOIN INSERTED ON m.DocId = inserted.DocId

    UPDATE lab14_2.dbo.Doctor 
    SET Cabinet = INSERTED.Cabinet, Department = INSERTED.Department
    FROM lab14_2.dbo.Doctor d
    INNER JOIN INSERTED ON d.DocId = INSERTED.DocId
END
GO



drop trigger if exists trg_DeleteVerticalDoctorView
go

CREATE TRIGGER trg_DeleteVerticalDoctorView
ON VerticalDoctorView
INSTEAD OF DELETE
AS
BEGIN
    DELETE FROM lab14_1.dbo.Doctor
    WHERE DocId IN (SELECT DocId FROM DELETED);

    DELETE FROM lab14_2.dbo.Doctor
    WHERE DocId IN (SELECT DocId FROM DELETED);
END
GO


INSERT INTO VerticalDoctorView (DocId, DoctorPhone, DoctorName, Qualification, Cabinet, Department)
VALUES
    (1,'+7(495)123-45-67', N'Доктор Сидорова',  N'Окулист',105, N'Окулистический'),
    (2, '+7(495)111-22-33', N'Доктор Иванов', N'Терапевт', 106, N'Терапия'),
    (3, '+7(495)444-55-66', N'Доктор Петров', N'Хирург', 107, N'Хирургия'),
    (4, '+7(495)777-88-99', N'Доктор Козлов', N'Педиатр', 108, N'Педиатрия'),
    (5, '+7(495)000-11-22', N'Доктор Смирнова', N'Невролог', 109, N'Неврология'),
    (6, '+7(495)333-44-55', N'Доктор Федорова', N'Стоматолог', 110, N'Стоматология');
go

UPDATE VerticalDoctorView
SET DoctorPhone = '+7(495)111-22-30', Cabinet = 102
WHERE DocId = 2
GO

DELETE FROM VerticalDoctorView
WHERE DocId = 3
GO


SELECT * FROM VerticalDoctorView
GO