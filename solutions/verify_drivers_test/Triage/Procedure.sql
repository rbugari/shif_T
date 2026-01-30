
        CREATE PROCEDURE SP_TEST AS
        BEGIN
            MERGE INTO TargetTable T
            USING SourceTable S ON (T.ID = S.ID)
            WHEN MATCHED THEN UPDATE SET T.Val = S.Val;
        END;
        