USE master
GO

IF DB_ID (N'lab6') IS NOT NULL
    DROP DATABASE lab6
GO

CREATE DATABASE lab6
ON (
    NAME = lab6dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/Lab6/lab6dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab6log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/Lab6/lab6log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO

USE lab6
GO

IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

-- Создать таблицу с первичным ключом на основе глобального уникального идентификатора.
CREATE TABLE Department (
	DepartmentID uniqueidentifier primary key default(newid()), 
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70) NOT NULL,
	);
GO

INSERT INTO Department ( DepartmentName, HeadDepartment) 
VALUES  
    ( N'Хирургическое отделение', N'Усачев'),
    ( N'Главное приемное отделение', N'Морозов');
GO

SELECT * FROM Department
GO
 
IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

--Создать таблицу с автоинкрементным первичным ключом.
CREATE TABLE Department (
	DepartmentID int IDENTITY(1,1) PRIMARY KEY,
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70) NOT NULL,
	);
GO

INSERT INTO Department ( DepartmentName, HeadDepartment) 
VALUES  
    ( N'Хирургическое отделение', N'Усачев'),
    ( N'Главное приемное отделение', N'Морозов');
GO

SELECT * FROM Department
GO

-- Изучить функции, предназначенные для получения сгенерированного значения IDENTITY

--последний id, вставленный в любую таблицу по всем областям 
select @@IDENTITY as id; 
--последний id, вставленный в любую таблицу в той же области 
select SCOPE_IDENTITY() as scope_id; 
--последнее значение id для конкретной таблицы
select IDENT_CURRENT('Department') as id_current;

 

USE lab6
GO

--Создать таблицу с первичным ключом на основе последовательности.
if object_id(N'Seq') is not null
	drop sequence Seq

create sequence Seq
	start with 1
	increment by 1;

IF OBJECT_ID (N'Hospital') is NOT NULL
    DROP TABLE Hospital
GO

CREATE TABLE Hospital (
    Hospital_ID int primary key,
    Name nvarchar(200) NOT NULL check (len(Name) > 1),
    HospitalAddress nvarchar(100) NOT NULL  check (len(HospitalAddress) > 10),
    HeadPhysician nvarchar(100) NOT NULL check (len(HeadPhysician) > 1),
    Phone char(16) NOT NULL check (len(Phone) = 16),
    NumDepartment int DEFAULT 1,
)
GO

INSERT INTO Hospital (Hospital_ID, Name, HospitalAddress, HeadPhysician, Phone)
VALUES 
    (next value for Seq, N'Центральная клиническая больница Российской академии наук', N'Москва, Литовский бульвар, 1А', N'Снегирев', '+7(499)400-47-33'),
    (next value for Seq, N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ', N'Москва, Староволынская улица, 10', N'Иванов','+7(499)144-75-14'),
    (next value for Seq, N'Клиническая больница управления делами президента', N'Москва, Лосиноостровская улица, 45к2А', N'Петров', '+7(499)464-44-54'),
    (next value for Seq, N'Объединенная больница с поликлиникой Управления делами Президента РФ', N'Москва, Мичуринский проспект, 6с1', N'Никитин','+7(499)333-30-00')
GO

SELECT * FROM Hospital
GO


--- 5
IF OBJECT_ID(N'Hospital') is not null
	DROP TABLE Hospital;
GO

CREATE TABLE Hospital (
    Hospital_ID 	  int primary key,
    Name nvarchar(200) NOT NULL check (len(Name) > 1),
    HospitalAddress nvarchar(100) NOT NULL  check (len(HospitalAddress) > 10),
    HeadPhysician nvarchar(100) NOT NULL check (len(HeadPhysician) > 1),
    Phone char(16) NOT NULL check (len(Phone) = 16),
    NumDepartment int NOT NULL
)
GO

INSERT INTO Hospital (Hospital_ID, Name, HospitalAddress, HeadPhysician, Phone, NumDepartment)
VALUES 
    (1, N'Центральная клиническая больница Российской академии наук', N'Москва, Литовский бульвар, 1А', N'Снегирев', '+7(499)400-47-33', 11),
    (2, N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ', N'Москва, Староволынская улица, 10', N'Иванов','+7(499)144-75-14', 10),
    (3, N'Клиническая больница управления делами президента', N'Москва, Лосиноостровская улица, 45к2А', N'Петров', '+7(499)464-44-54', 16),
    (4, N'Объединенная больница с поликлиникой Управления делами Президента РФ', N'Москва, Мичуринский проспект, 6с1', N'Никитин','+7(499)333-30-00', 3)



IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

--Создать таблицу с автоинкрементным первичным ключом.
CREATE TABLE Department (
	DepartmentID int identity(1,1) primary key,
	 
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70) NOT NULL,
	Hospital_ID int
	constraint FK_Hospital_ID foreign key (Hospital_ID) references Hospital(Hospital_ID)
	on update cascade
	-- on update no action
	--on update set null
	--on update set default

	--on delete set null
	on delete cascade
	--on delete no action
	-- on delete set default
	);
GO
INSERT INTO Department ( Hospital_ID, DepartmentName, HeadDepartment) 
VALUES  
    (1, N'Хирургическое отделение', N'Усачев'),
    (2, N'Главное приемное отделение', N'Морозов');

SELECT * FROM Hospital
GO

SELECT * FROM Department
GO
update Hospital 
    set Hospital_ID = 11
    where Hospital_ID = 1
GO

delete from Hospital 
    where Hospital_ID=2
GO

select * from Hospital
GO

select * from Department
GO




-- Изучить функции, предназначенные для получения сгенерированного значения IDENTITY.

IF OBJECT_ID (N'Patient') is NOT NULL
    DROP TABLE Patient
GO

CREATE TABLE Patient (
    PolicyNumber char(16) PRIMARY KEY NOT NULL,
    PatientName nvarchar(50) DEFAULT ('Иванов'),
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