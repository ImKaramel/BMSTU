USE master
GO

IF DB_ID (N'lab8') IS NOT NULL
    DROP DATABASE lab8
GO

CREATE DATABASE lab8
ON (
    NAME = lab8dat,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab8dat.mdf',
    SIZE = 10,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 5%
)

LOG ON (
    NAME = lab8log,
    FILENAME = '/Users/assistentka_professora/Desktop/DB/lab8log.ldf',
    SIZE = 5MB, 
    MAXSIZE = 25MB,
    FILEGROWTH = 5MB
)
GO

IF OBJECT_ID (N'Hospital') is NOT NULL
    DROP TABLE Hospital
GO


USE lab8

CREATE TABLE Hospital (
    Hospital_ID int IDENTITY(1,1) primary key,
    Name nvarchar(200) NOT NULL check (len(Name) > 1),
    HospitalAddress nvarchar(100) NOT NULL  check (len(HospitalAddress) > 10),
    HeadPhysician nvarchar(100) NOT NULL check (len(HeadPhysician) > 1),
    Phone char(16) NOT NULL check (len(Phone) = 16),
    NumDepartment int NOT NULL,
)
GO

INSERT INTO Hospital (Name, HospitalAddress, HeadPhysician, Phone, NumDepartment)
VALUES 
    (  N'Центральная клиническая больница Российской академии наук', N'Москва, Литовский бульвар, 1А', N'Снегирев', '+7(499)400-47-33', 9),
    (  N'ФГБУ Клиническая больница № 1 Управление делами Президента РФ', N'Москва, Староволынская улица, 10', N'Иванов','+7(499)144-75-14', 10),
    (  N'Клиническая больница управления делами президента', N'Москва, Лосиноостровская улица, 45к2А', N'Петров', '+7(499)464-44-54', 12),
    (  N'Объединенная больница с поликлиникой Управления делами Президента РФ', N'Москва, Мичуринский проспект, 6с1', N'Никитин','+7(499)333-30-00', 8)
GO

SELECT * FROM Hospital
GO


---Создать хранимую процедуру, производящую выборку из некоторой таблицы и возвращающую результат выборки в виде курсора.

GO

IF OBJECT_ID(N'dbo.select_procedure') IS NOT NULL
	DROP PROCEDURE dbo.select_procedure
GO

CREATE PROCEDURE dbo.select_procedure
	@cursor CURSOR VARYING OUTPUT
AS
	SET @cursor = CURSOR
	    FORWARD_ONLY FOR 
            SELECT Name FROM Hospital
	OPEN @cursor   --open выполняет запрос, связанный с курсором, и устанавливает курсор перед первой записью результирующей таблицы.
GO

DECLARE @hospital_cursor CURSOR   --связывается имя курсора с выполняемым запросом.
EXECUTE dbo.select_procedure @cursor = @hospital_cursor OUTPUT
 
DECLARE @nameH nvarchar(200);
FETCH NEXT FROM @hospital_cursor INTO @nameH; --Оператор fetch помещает курсор на первую запись результирующей таблицы и извлекает данные из записи в локальные переменные хранимой процедуры.

--FETCH NEXT FROM @hospital_cursor  
WHILE (@@FETCH_STATUS = 0)  --Инструкция FETCH была выполнена успешно.
	BEGIN
        PRINT N'HospitalName: ' + @nameH;
		FETCH NEXT FROM @hospital_cursor INTO @nameH
	END
 

CLOSE @hospital_cursor
DEALLOCATE @hospital_cursor

GO

--Модифицировать хранимую процедуру п.1. таким образом, чтобы выборка осуществлялась с формированием столбца, значение которого формируется пользовательской функцией.

IF OBJECT_ID(N'GetPhone') IS NOT NULL
	DROP FUNCTION dbo.GetPhone;
GO


CREATE FUNCTION GetPhone (@DPhone char(16))
  RETURNS char(16)
AS
BEGIN
  RETURN @DPhone
END;
GO


IF OBJECT_ID(N'GetPhoneCursor') IS NOT NULL
	DROP PROC dbo.GetPhoneCursor;
GO


CREATE PROCEDURE GetPhoneCursor
  @clCur CURSOR VARYING OUTPUT
AS
  SET @clCur = CURSOR
    FORWARD_ONLY FOR
      SELECT 
        Name, 
        dbo.GetPhone(Phone) AS HospitalPhone 
      FROM Hospital;
  OPEN @clCur;
GO


DECLARE @cur CURSOR;
EXEC dbo.GetPhoneCursor @clCur = @cur OUTPUT;

DECLARE 
  @hName nvarchar(200),
  @hPh char(16);
FETCH NEXT FROM @cur INTO @hName, @hPh;

WHILE (@@FETCH_STATUS = 0)
BEGIN
  PRINT @hName + N' : ' + @hPh;
  FETCH NEXT FROM @cur INTO @hName, @hPh;
END;

CLOSE @cur;
DEALLOCATE @cur;
GO


--Создать хранимую процедуру, вызывающую процедуру п.1., осуществляющую прокрутку возвращаемого курсора и выводящую сообщения, 
-- сформированные из записей при выполнении условия, заданного еще одной пользовательской функцией.

IF OBJECT_ID(N'checkLengthHospital',N'FN') IS NOT NULL
	DROP FUNCTION checkLengthHospital
go

CREATE FUNCTION checkLengthHospital(@a nvarchar)
	RETURNS bit
	AS
		BEGIN
			DECLARE @result bit
			IF (len(@a) < 100)
				SET @result = 1
			ELSE
				SET @result = 0
			RETURN (@result)
		END
go

IF OBJECT_ID(N'checkLengthOfHospital') IS NOT NULL
  DROP PROCEDURE checkLengthOfHospital;
GO 


CREATE PROCEDURE checkLengthOfHospital
AS
BEGIN
  DECLARE @cur CURSOR;
  EXEC dbo.select_procedure @cursor = @cur OUTPUT;
  DECLARE @NameHosp nvarchar(200);

  FETCH NEXT FROM @cur INTO @NameHosp;

  WHILE (@@FETCH_STATUS = 0)
  BEGIN
    IF dbo.checkLengthHospital(@NameHosp) = 1
      PRINT N'HospitalName: ' + @NameHosp;

    FETCH NEXT FROM @cur INTO @NameHosp;
  END;

  CLOSE @cur;
  DEALLOCATE @cur;
END;
GO

EXEC checkLengthOfHospital;
GO


--Модифицировать хранимую процедуру п.2. таким образом, чтобы выборка формировалась с помощью табличной функции.

IF OBJECT_ID(N'GetHospWithPhone') IS NOT NULL
	DROP FUNCTION dbo.GetHospWithPhone;
GO


CREATE FUNCTION GetHospWithPhone()
RETURNS table
AS
  RETURN (
     SELECT 
        Name, 
        dbo.GetPhone(Phone) AS HospitalPhone 
      FROM Hospital
  );
GO

IF OBJECT_ID(N'GetHospPhone') IS NOT NULL
	DROP PROC dbo.GetHospPhone;
GO


CREATE PROCEDURE GetHospPhone
  @clCur CURSOR VARYING OUTPUT
AS
  SET @clCur = CURSOR
    FORWARD_ONLY FOR
      SELECT *
      FROM dbo.GetHospWithPhone();
  OPEN @clCur;
GO


DECLARE @cur CURSOR;
EXEC dbo.GetHospPhone @clCur = @cur OUTPUT;

DECLARE 
  @hName nvarchar(200),
  @hPh char(16);
FETCH NEXT FROM @cur INTO @hName, @hPh;

WHILE (@@FETCH_STATUS = 0)
BEGIN
  PRINT @hName + N' : ' + @hPh;
  FETCH NEXT FROM @cur INTO @hName, @hPh;
END;

CLOSE @cur;
DEALLOCATE @cur;
GO


 