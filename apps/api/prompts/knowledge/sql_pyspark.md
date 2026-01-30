### TECHNOLOGY CONTEXT: SQL (T-SQL / PL-SQL)
- **Nature**: Set-based declarative logic + Procedural extensions.
- **Core Components**: Stored Procedures, Views, Functions, Triggers.
- **Migration Strategy**:
  - **Select/Transform** -> PySpark SQL / DataFrames.
  - **DDL** -> Delta Table Creation via Spark Catalog.
  - **Cursors/Loops** -> MUST be refactored to vectorised operations (Pandas/UDFs) or mapWithState.
  - **Temp Tables** -> Spark Temporary Views or Cached DataFrames.
