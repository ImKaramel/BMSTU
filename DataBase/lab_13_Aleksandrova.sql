USE master
GO
---Создать две базы данных на одном экземпляре СУБД SQL Server 2012.
IF DB_ID (N'lab13') IS NOT NULL
    DROP DATABASE lab13
GO

CREATE DATABASE lab13
ON (
    NAME = lab6dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab13dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab13log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab13log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO
----2
IF DB_ID (N'lab13_1') IS NOT NULL
    DROP DATABASE lab13_1
GO

CREATE DATABASE lab13_1
ON (
    NAME = lab13_1dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab13_1dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab13_1log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab13_1log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO


--Создать в базах данных п.1. горизонтально фрагментированные таблицы.

use lab13;
GO

IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DocId int PRIMARY KEY CHECK (DocId < 50),
    DoctorPhone char(16)  NOT NULL ,
    DoctorName nvarchar(50) NOT NULL,
    Cabinet int NOT NULL,
    Qualification nvarchar(100) NOT NULL
 
)
GO

INSERT INTO Doctor (DocId, DoctorPhone, DoctorName, Cabinet, Qualification)
VALUES 
(11,'+7(499)400-47-33', N'Доктор Иванов', 103, N'Терапевт'),
(12, '+7(499)144-75-14', N'Доктор Петров', 104, N'Хирург');
GO

use lab13_1;
GO

IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DocId int PRIMARY KEY CHECK (DocId >= 50),
    DoctorPhone char(16)  NOT NULL ,
    DoctorName nvarchar(50) NOT NULL,
    Cabinet int NOT NULL,
    Qualification nvarchar(100) NOT NULL
)
GO

INSERT INTO Doctor (DocId, DoctorPhone, DoctorName, Cabinet, Qualification)
VALUES 
(122, '+7(939)400-47-33', N'Доктор Сонин', 300, N'ЛОР'),
(124, '+7(969)144-75-14', N'Доктор Кушков', 123, N'Педиатор');
GO



---Создать секционированные представления, обеспечивающие работу с данными таблиц (выборку, вставку, изменение, удаление).

 

IF OBJECT_ID (N'DoctorView') IS NOT NULL
    DROP VIEW DoctorView;
GO


CREATE VIEW DoctorView AS
    SELECT  *  FROM lab13.dbo.Doctor
    UNION ALL
    SELECT * FROM lab13_1.dbo.Doctor;
GO


drop trigger if exists trg_InsertDoctorView
go

CREATE TRIGGER trg_InsertDoctorView
ON DoctorView
INSTEAD OF INSERT
AS
BEGIN
 
    INSERT INTO lab13.dbo.Doctor (DocId, DoctorPhone, DoctorName, Cabinet, Qualification)
    SELECT DocId, DoctorPhone, DoctorName, Cabinet, Qualification FROM INSERTED
    WHERE DocId < 50; --  условия разделения

    INSERT INTO lab13_1.dbo.Doctor (DocId, DoctorPhone, DoctorName, Cabinet, Qualification)
    SELECT DocId, DoctorPhone, DoctorName, Cabinet, Qualification FROM INSERTED
    WHERE DocId >= 50; --  условия разделения
END
GO

drop trigger if exists trg_DeleteDoctorView
go

CREATE TRIGGER trg_DeleteDoctorView
ON DoctorView
INSTEAD OF DELETE
AS
BEGIN
    DELETE FROM lab13.dbo.Doctor
    WHERE DocId IN (SELECT DocId FROM DELETED);

    DELETE FROM lab13_1.dbo.Doctor
    WHERE DocId IN (SELECT DocId FROM DELETED);
END
GO

 
 
SELECT * FROM DoctorView
GO



INSERT  INTO DoctorView (DocId, DoctorPhone, DoctorName, Cabinet, Qualification)
VALUES
    (1,'+7(495)123-45-67', N'Доктор Сидорова', 105, N'Окулист'),
    (2, '+7(495)987-65-43', N'Доктор Васильев', 106, N'Невролог'),
    (3, '+7(495)222-33-77', N'Доктор Козлов', 107, N'Педиатр'),
    (4, '+7(499)111-22-33', N'Доктор Новикова', 108, N'Акушер-гинеколог');
GO

UPDATE DoctorView
SET Cabinet = 1000 where Cabinet = 103

UPDATE DoctorView
SET DocId = 54 where DocId = 4
SELECT * FROM lab13_1.dbo.Doctor;
SELECT * FROM lab13.dbo.Doctor;

-- delete DoctorView
-- 	where DoctorName = N'Доктор Сонин'

-- SELECT * FROM DoctorView;