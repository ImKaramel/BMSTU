USE master
GO

IF DB_ID('Lab9') IS NOT NULL
  DROP DATABASE Lab9;
GO

CREATE DATABASE Lab9
ON (
    NAME = lab9dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab9dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab9log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab9log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO

USE Lab9;
GO

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

INSERT INTO Hospital (Hospital_ID, Name, HospitalAddress, HeadPhysician, Phone, NumDepartment)
VALUES 
    (1, N'Центральная клиническая больница Российской академии наук', N'Москва, Литовский бульвар, 1А', N'Снегирев', '+7(499)400-47-33', 11),
    (2, N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ', N'Москва, Староволынская улица, 10', N'Иванов','+7(499)144-75-14', 10),
    (3, N'Клиническая больница управления делами президента', N'Москва, Лосиноостровская улица, 45к2А', N'Петров', '+7(499)464-44-54', 16),
    (4, N'Объединенная больница с поликлиникой Управления делами Президента РФ', N'Москва, Мичуринский проспект, 6с1', N'Никитин','+7(499)333-30-00', 3)
GO

IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

 
CREATE TABLE Department (
	DepartmentID int identity(1,1) primary key,
	 
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70) NOT NULL,
	Hospital_ID int
	constraint FK_Hospital_ID foreign key (Hospital_ID) references Hospital(Hospital_ID)
	);
GO
INSERT INTO Department ( Hospital_ID, DepartmentName, HeadDepartment) 
VALUES  
    (1, N'Главное приемное отделение', N'Морозов'),
    (2, N'Хирургическое отделение', N'Усачев');

----- Для одной из таблиц пункта 2 задания 7 создать триггеры на вставку, удаление и добавление,
----- при выполнении заданных условий один из триггеров должен инициировать возникновение ошибки (RAISERROR / THROW).

drop trigger if exists delete_department_trigger
go


CREATE TRIGGER delete_department_trigger
ON Department
INSTEAD OF DELETE
AS
BEGIN
    IF EXISTS (SELECT * FROM DELETED WHERE DepartmentID = 1)
    BEGIN
        raiserror ('Cannot delete Department with ID = 1', 16, 1);
    END
    ELSE
    BEGIN
        DELETE FROM Department
        WHERE DepartmentID in
       (SELECT DepartmentID FROM deleted);
    END
END
GO

-- select * from Department;
-- delete from Department where DepartmentID = 1;
-- select * from Department;
-- delete from Department where DepartmentID = 2;
-- select * from Department;

drop trigger if exists insert_trigger
go

CREATE TRIGGER insert_trigger
ON Department
INSTEAD OF INSERT
AS
BEGIN
    -- SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM inserted i WHERE EXISTS (SELECT 1 FROM Department d WHERE d.DepartmentName = i.DepartmentName))
    BEGIN
        RAISERROR ('Department with this name already exists', 16, 2);
    END
    ELSE
    BEGIN
        INSERT INTO Department (DepartmentName, HeadDepartment, Hospital_ID)
        SELECT i.DepartmentName, i.HeadDepartment, i.Hospital_ID
        FROM inserted i;
    END
END
go

---test Insert
-- INSERT INTO  Department(Hospital_ID, DepartmentName, HeadDepartment) 
--     VALUES
--   (4, N'Отделение травмотологии', N'Иванков'),
--   (3, N'ппппп', N'Поляков');


-- INSERT INTO  Department(Hospital_ID, DepartmentName, HeadDepartment) 
--     VALUES
--   (3, N'Хирургическое отделение', N'Поляков')
-- GO

-- select * from Department
-- go

--alternate trigger for insert
-- CREATE TRIGGER  insert_department_trigger
-- ON Department
-- AFTER INSERT
-- AS
-- BEGIN
--     SET NOCOUNT ON;

--     INSERT INTO Department (DepartmentName, HeadDepartment, Hospital_ID)
--     SELECT i.DepartmentName, i.HeadDepartment, i.Hospital_ID
--     FROM inserted i;
-- END;

CREATE TRIGGER trgUpdateDepartment
ON Department
AFTER UPDATE
AS
BEGIN
    -- SET NOCOUNT ON;
    UPDATE Department
    SET HeadDepartment = i.HeadDepartment
    FROM Department d
    INNER JOIN inserted i ON d.DepartmentID = i.DepartmentID
    WHERE i.HeadDepartment <> d.HeadDepartment OR (d.HeadDepartment IS NULL AND i.HeadDepartment IS NOT NULL)
END
go

UPDATE Department
  SET HeadDepartment = N'Весенин'
  WHERE DepartmentID = 2;
GO

-- select * from Department
-- go




---- Для представления пункта 2 задания 7 создать триггеры на вставку, удаление и добавление,
---- обеспечивающие возможность выполнения операций с данными непосредственно через представление.

disable trigger dbo.delete_department_trigger on Department;
go
disable trigger dbo.trgUpdateDepartment on Department;
go
disable trigger dbo.insert_trigger on Department;


IF OBJECT_ID(N'Department') is not null
	DROP TABLE Department;
GO

CREATE TABLE Department (
	DepartmentID int identity(1,1) primary key,
	 
	DepartmentName nvarchar(100) NOT NULL,
	HeadDepartment nvarchar(70)   NULL,

	
	);
GO

IF OBJECT_ID (N'Doctor') is NOT NULL
    DROP TABLE Doctor
GO

CREATE TABLE Doctor (
    DoctorPhone char(16) PRIMARY KEY,
    DoctorName nvarchar(50) NOT NULL,
    Cabinet int NOT NULL,
    Qualification nvarchar(100) NOT NULL,
    DepartmentID int
    constraint FK_Department_ID foreign key (DepartmentID) references Department(DepartmentID)
);

IF OBJECT_ID(N'DepartmentDoctors') IS NOT NULL
  DROP VIEW DepartmentDoctorView;
GO

CREATE VIEW DepartmentDoctors AS
SELECT d.DoctorPhone, d.DoctorName, d.Cabinet, d.Qualification, dp.DepartmentName
FROM Doctor d
INNER JOIN Department dp ON d.DepartmentID = dp.DepartmentID;
go




IF OBJECT_ID(N'trg_viewInsert') IS NOT NULL
  DROP VIEW trg_viewInsert;
GO

CREATE TRIGGER trg_viewInsert
ON DepartmentDoctors
INSTEAD OF INSERT
AS
        INSERT INTO Department (DepartmentName)
        SELECT DISTINCT i.DepartmentName
        FROM inserted i
        LEFT JOIN Department dp ON i.DepartmentName = dp.DepartmentName
        WHERE dp.DepartmentName IS NULL;
        --Проверяем, существует ли родительская сущность (отдел)
        IF NOT EXISTS (SELECT * FROM inserted i INNER JOIN Department dp ON i.DepartmentName = dp.DepartmentName)
        BEGIN
            RAISERROR ('Нельзя вставить дочернюю сущность (врача) без существующей родительской сущности (отдела)', 16, 4);
            ROLLBACK TRANSACTION;
            RETURN;
        END
        ELSE
 
        -- Проверяем существование врача во входных данных
     BEGIN
        -- Вставляем врача, если DoctorPhone не пуст
        INSERT INTO Doctor (DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentID)
        SELECT i.DoctorPhone, i.DoctorName, i.Cabinet, i.Qualification, dp.DepartmentID
        FROM inserted i
        INNER JOIN Department dp ON i.DepartmentName = dp.DepartmentName
        WHERE i.DoctorPhone IS NOT NULL;
    END;
        
GO

INSERT INTO DepartmentDoctors ( DepartmentName)
VALUES 
(  N'Отделение терапии')
-- (  N'Отделение терапии');
GO

INSERT INTO DepartmentDoctors (DoctorPhone, DoctorName, Cabinet, Qualification, DepartmentName)
VALUES 
('+7(499)400-47-33', N'Доктор Иванов', 103, N'Терапевт', N'Отделение терапии'),
('+7(499)144-75-14', N'Доктор Петров', 104, N'Хирург', N'Отделение терапии'),
('+7(479)144-75-14', N'Доктор Сонин', 106, N'Хирург', N'Отделение хирургии'),
('+7(479)884-75-14', N'Доктор Ленин', 107, N'Окулист', N'Отделение глаза');

GO

-- select * from Department;
-- GO
-- select * from Doctor;
-- GO
-- select * from DepartmentDoctors
-- GO



IF OBJECT_ID(N'trg_UpdateView') IS NOT NULL
  DROP trigger trg_UpdateView;
GO


CREATE TRIGGER trg_UpdateView
ON DepartmentDoctors
INSTEAD OF UPDATE
AS
BEGIN
    -- Отменяем обновление столбца DepartmentName
    IF UPDATE(DepartmentName)
    BEGIN
        RAISERROR('Нельзя обновлять столбец DepartmentName в этом представлении', 16, 1)
        ROLLBACK TRANSACTION
        RETURN
    END

    IF UPDATE(DoctorPhone)
    BEGIN
        RAISERROR('Нельзя обновлять столбец DoctorPhone в этом представлении', 16, 1)
        ROLLBACK TRANSACTION
        RETURN
    END

    -- Если обновление других столбцов разрешено, просто обновляем представление
    UPDATE d
    SET  
        DoctorName = i.DoctorName,
        Cabinet = i.Cabinet,
        Qualification = i.Qualification
    FROM DepartmentDoctors d
    INNER JOIN inserted i ON d.DoctorPhone = i.DoctorPhone
END




UPDATE DepartmentDoctors
SET DoctorName = N'Новое имя врача', Cabinet = 105
WHERE DoctorPhone = '+7(499)400-47-33';
-- SELECT * from DepartmentDoctors;
-- go


-- UPDATE DepartmentDoctors
-- SET DepartmentName = N'Новое название отделения'
-- WHERE DepartmentName = 'Отделение терапии';
-- go

-- UPDATE DepartmentDoctors
-- SET DepartmentName = N'Новое название отделения'
-- WHERE DoctorPhone = '+7(499)400-47-33';
-- go



-- SELECT * from DepartmentDoctors;
-- UPDATE DepartmentDoctors
-- SET DoctorName = DoctorName 
-- SELECT * from DepartmentDoctors;
-- go



IF OBJECT_ID(N'trgDeleteDepartmentDoctors') IS NOT NULL
  DROP VIEW trgDeleteDepartmentDoctors;
GO


CREATE TRIGGER trgDeleteDepartmentDoctors
ON DepartmentDoctors
INSTEAD OF DELETE
AS
BEGIN
--  Удаляем доктора, если он существует
    DELETE FROM Doctor
    WHERE DoctorPhone IN (SELECT DoctorPhone FROM deleted);

    -- — Проверяем, есть ли другие доктора в том же отделе
    IF NOT EXISTS (SELECT * FROM Doctor WHERE DepartmentID IN (SELECT DepartmentID FROM deleted))
    BEGIN
    -- — Если нет других докторов, удаляем отдел
    DELETE FROM Department
    WHERE DepartmentID IN (SELECT DepartmentID FROM deleted);
    END
END;
GO

-- DELETE FROM DepartmentDoctors
--   WHERE DoctorPhone = '+7(479)144-75-14';
-- go
-- DELETE FROM DepartmentDoctors
--   WHERE DoctorPhone = '+7(479)884-75-14';
-- go
SELECT * from DepartmentDoctors;
SELECT * from Department;
go

-- DELETE FROM DepartmentDoctors
--   WHERE DepartmentName = N'Отделение терапии';
-- GO

SELECT * from Department;
SELECT * from Doctor;

-- SELECT * from Department;
-- SELECT * from Doctor;
-- SELECT * from DepartmentDoctors;








 












 

 