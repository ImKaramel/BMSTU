USE master
GO

IF DB_ID (N'lab55') IS NOT NULL
    DROP DATABASE lab55
GO

CREATE DATABASE lab55
ON (
    NAME = lab5dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/Lab5/lab5dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab5log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/Lab5/lab5log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO

--2

USE lab55
GO

IF OBJECT_ID (N'Hospital') is NOT NULL
    DROP TABLE Hospital
GO

CREATE TABLE Hospital (
    Hospital_ID INT IDENTITY(1, 1) PRIMARY KEY,
    Name nvarchar(200) NOT NULL,
    HospitalAddress nvarchar(100) NOT NULL,
    HeadPhysician nvarchar(100) NOT NULL, 
    Phone char(16) NOT NULL
)
GO

INSERT INTO Hospital (Name, HospitalAddress, HeadPhysician, Phone)
VALUES 
    (N'Центральная клиническая больница Российской академии наук', N'Москва, Литовский бульвар, 1А', N'Снегирев', '+7(499)400-47-33'),
    (N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ', N'Москва, Староволынская улица, 10', N'Иванов','+7(499)144-75-14'),
    (N'Клиническая больница управления делами президента', N'Москва, Лосиноостровская улица, 45к2А', N'Петров', '+7(499)464-44-54'),
    (N'Объединенная больница с поликлиникой Управления делами Президента РФ', N'Москва, Мичуринский проспект, 6с1', N'Никитин','+7(499)333-30-00')
GO

SELECT * FROM Hospital
GO

--3 Добавить файловую группу и файл данных (ALTER DATABASE...).

USE master
GO

ALTER DATABASE lab55
    ADD FILEGROUP lab5_fg
GO

ALTER DATABASE lab55
ADD FILE (
    NAME = lab5dat1,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/Lab5/lab5dat1.ndf',
    SIZE = 10MB,
    MAXSIZE = 100MB,
    FILEGROWTH = 5MB)
TO FILEGROUP lab5_fg
GO

-- 4 

ALTER DATABASE lab55
    MODIFY FILEGROUP lab5_fg DEFAULT
GO

-- 5 

USE lab55
GO

IF OBJECT_ID (N'Patient') is NOT NULL
    DROP TABLE Patient
GO

CREATE TABLE Patient (
    PolicyNumber char(16) PRIMARY KEY NOT NULL,
    PatientName nvarchar(50) NOT NULL,
    PassportNumber char(10) NOT NULL,
    Address nvarchar(50) NOT NULL,
    Gender bit
)
GO

INSERT INTO Patient(PolicyNumber, PatientName, PassportNumber, Address, Gender)
VALUES 
    ('1234567890123456', N'Сидоров', '3705456889', N'г. Москва, ул. Ленина, д. 5 кв. 10', 0),
    ('5678901234561234', N'Иванов', '1234560172', N'г. Санкт-Петербург, ул. Благодатная, д. 18, кв. 6', 0),
    ('0123456123456789', N'Ивлева', '9348627738', N'г. Санкт-Петербург, ул. Благодатная, д. 17, кв. 6', 1)  
GO

SELECT * FROM Patient
GO

-- 6  Удалить созданную вручную файловую группу.

USE master
GO

ALTER DATABASE lab55
	MODIFY FILEGROUP [primary] DEFAULT
GO

-- saving table to history before dropping
ALTER DATABASE lab55
ADD FILEGROUP HISTORY;
ALTER DATABASE lab55
ADD FILE
(
    NAME = historyData,
    FILENAME = "/Users/assistentka_professora/Desktop/DB/Lab5/historyData.mdf"
)
TO FILEGROUP HISTORY;

IF OBJECT_ID (N'Patient2') is NOT NULL
    DROP TABLE Patient2
GO
CREATE TABLE Patient2 (
    PolicyNumber char(16) PRIMARY KEY NOT NULL,
    PatientName nvarchar(50) NOT NULL,
    PassportNumber char(10) NOT NULL,
    Address nvarchar(50) NOT NULL,
    Gender bit
)
GO

USE lab55
GO
SELECT * INTO Patient2 ON HISTORY FROM Patient


DROP TABLE Patient
GO

USE master
GO

ALTER DATABASE lab55
	REMOVE FILE lab5dat1
GO

ALTER DATABASE lab55
	REMOVE FILEGROUP lab5_fg
GO


-- 7. Создать схему, переместить в нее одну из таблиц, удалить схему.

USE lab55
GO

CREATE SCHEMA lab55_schema
GO

ALTER SCHEMA lab55_schema TRANSFER Hospital
GO
IF  OBJECT_ID(N'lab55_schema.Hospital') IS NOT NULL 
DROP TABLE lab55_schema.Hospital
GO

DROP SCHEMA lab55_schema
GO