USE master
GO

IF DB_ID('lab11') IS NOT NULL
  DROP DATABASE lab11;
GO

create database lab11
go

USE lab11;
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


