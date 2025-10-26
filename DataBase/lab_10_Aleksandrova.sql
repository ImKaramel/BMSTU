USE master
GO

IF DB_ID(N'lab10') IS NOT NULL
	DROP DATABASE lab10
GO

CREATE DATABASE lab10;
GO

USE lab10;
GO


IF OBJECT_ID (N'Hospital') is NOT NULL
    DROP TABLE Hospital
GO

CREATE TABLE Hospital (
    Hospital_ID int primary key IDENTITY(1, 1),
    Name nvarchar(120) UNIQUE NOT NULL,
    HospitalAddress nvarchar(100)  NULL,
    HeadPhysician nvarchar(120) UNIQUE NOT NULL,
    Phone char(16)  NULL,
    NumDepartment int DEFAULT 1,
)
GO

INSERT INTO Hospital ( Name, HeadPhysician)
VALUES 
    ( N'Центральная клиническая больница Российской академии наук',  N'Снегирев' ),
    ( N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ',   N'Иванов' )
GO


select * from Hospital
GO

SELECT @@spid AS Session2Id;
GO

--------------------

-- 1. dirty read

-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- --SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
-- BEGIN TRAN; 
-- select * from dbo.Hospital
-- COMMIT TRAN;

 

--------------------

-- 2. non-repeatable read

-- BEGIN TRAN;
--     UPDATE Hospital
--     SET NumDepartment = 3 
--     WHERE HeadPhysician = N'Снегирев'
--     -- INSERT INTO Hospital ( Name, HeadPhysician)
--     -- -- VALUES
--     -- --     ( N'Клиническая больница управления делами министра',  N'Сонин')
--     select * from dbo.Hospital

-- COMMIT TRAN;


-- --------------------

-- -- 3. phantom read

BEGIN TRAN;

INSERT INTO Hospital( Name, HeadPhysician)
    VALUES
  ( N'Клиническая больница управления делами президента',  N'Петров'),
  ( N'Клиническая больница управления делами министра',  N'Сонин')
 
COMMIT TRAN;

---second query


----Исследовать и проиллюстрировать на примерах различные уровни изоляции транзакций MS SQL Server, 
----устанавливаемые с использованием инструкции SET TRANSACTION ISOLATION LEVEL


-- Уровни изоляции транзакций в MS SQL Server могут быть установлены с помощью инструкции SET 
-- TRANSACTION ISOLATION LEVEL. Эти уровни определяют, каким образом данные будут изолированы 
-- и доступны для других транзакций. Ниже перечислены различные уровни изоляции транзакций в MS SQL Server:

--------------------
-- 1. dirty read: 

-- BEGIN TRAN;
--     select * from Hospital
--     GO
--     UPDATE Hospital
--     SET Name = N'№ 1 Управление делами Президента РФ'
--     WHERE HeadPhysician = N'Снегирев'
--     waitfor delay '00:00:10'
-- 	select * from dbo.Hospital
--     SELECT * FROM sys.dm_tran_locks
-- ROLLBACK

 
--------------------

-- 2. non-repeatable read воспроизводимое чтение (repeatable read);

-- SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- fix:
-- SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
--     BEGIN TRAN;

--         SELECT * FROM Hospital
--         WAITFOR DELAY '00:00:10';
--         SELECT * FROM Hospital
        -- SELECT * FROM sys.dm_tran_locks

--     COMMIT TRAN;

-------------------


-- 3. phantom read сериализуемость (serializable).

-- SET TRANSACTION ISOLATION LEVEL REPEATABLE READ; 
-- fix:
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
    BEGIN TRAN;
        SELECT * FROM Hospital
        -- SELECT Name, HeadPhysician FROM Hospital;
        WAITFOR DELAY '00:00:10';
		SELECT * FROM Hospital
		-- SELECT * FROM sys.dm_tran_locks
    COMMIT TRAN;


--------------------