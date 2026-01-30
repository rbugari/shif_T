### TECHNOLOGY CONTEXT: SSIS -> SNOWFLAKE (SNOWPARK)
- **Format**: XML-based (.dtsx).
- **Core Components**: Control Flow (Tasks), Data Flow (Pipeline).
- **Migration Strategy**:
  - **Control Flow** -> Snowflake Tasks / Airflow DAGs (calling Snowpark).
  - **Data Flow** -> Snowpark DataFrames (`session.createDataFrame` / `df.write`).
  - **Lookups** -> `df.join()` with broadcast hints if small.
  - **Expressions** -> Python UDFs registered in Snowflake.
  - **Script Tasks** -> Port logic to Python stored procedures (`@sproc`).
