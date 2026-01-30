### TECHNOLOGY CONTEXT: SQL (T-SQL / PL-SQL) -> SNOWFLAKE (SNOWPARK)
- **Nature**: Declarative Logic -> Snowpark Python DataFrame API.
- **Core Components**: Stored Procedures, Views, Functions, Triggers.
- **Migration Strategy**:
  - **Select/Transform** -> `session.table("...")` / Snowpark DataFrames.
  - **DDL** -> Utilize `session.sql("CREATE...")` directly or native Snowflake DDL.
  - **Cursors/Loops** -> Convert to Window Functions or Python UDFs (Vectorized if possible).
  - **Temp Tables** -> `df.create_or_replace_temp_view(...)`.
  - **Stored Procedures** -> Decorate with `@sproc` (Snowpark Stored Procedures).
