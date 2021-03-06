USE [SCM]
GO
/****** 对象:  UserDefinedFunction [dbo].[GetCategoryName]    脚本日期: 04/27/2010 11:08:17 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:	毛凌志
-- Create date: 2010-04-27
-- Description:	由分类编号获取分类编码(递归)
-- Return: 正确返回：分类编码（101,102,103）, 错误返回 -1
-- =============================================

create FUNCTION [dbo].[GetCategoryCode] 
(
	@cartegoryid int
)
RETURNS nvarchar(100)
AS
BEGIN

DECLARE @CategoryName VARCHAR(100);SET @CategoryName='';

WITH DirectReports(ParentCategoryCode, CategoryCode,CategoryName,EmployeeLevel) AS 
(
    SELECT ParentCategoryCode,CategoryCode,CategoryName,0 AS EmployeeLevel
    FROM New_category(NOLOCK)
    WHERE CategoryCode=@cartegoryid
    
    UNION ALL   

    SELECT T1.ParentCategoryCode, T1.CategoryCode,T1.CategoryName,EmployeeLevel+1
    FROM New_category(NOLOCK)  T1
    INNER JOIN DirectReports T2 ON T1.CategoryCode=T2.ParentCategoryCode
)
SELECT @CategoryName=@CategoryName+','+ cast(CategoryCode as varchar(10))
FROM DirectReports ORDER BY EmployeeLevel DESC

IF (len(@CategoryName) < 1)
begin
    print '-1' return;
end
else begin
	select SUBSTRING(@CategoryName,2,LEN(@CategoryName)-1)
end

