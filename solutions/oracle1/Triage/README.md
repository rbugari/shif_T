# Oracle (Standard ~2008: 10gR2 / 11gR1) — ETL en PL/SQL (imitando SSIS/DTSX)

Este paquete instala un mini-framework ETL + procedimientos PL/SQL para:
- Dimensiones incrementales (con watermark por fecha si hay columna; fallback por ID)
- DimProduct SCD (Type 1 + Type 2)
- FactSales con staging + deduplicación (MERGE)
- Logging de corridas y pasos

## Concepto ORIGEN / DESTINO en Oracle
Oracle no usa "DB name" dentro de una query como MySQL/SQL Server: normalmente trabajás por **schemas**.
Por eso este paquete parametriza:
- SOURCE_SCHEMA (esquema del origen)
- SOURCE_DBLINK (opcional; si el origen está en otra DB, creás un DB LINK y lo pones acá)
Ejemplos:
- mismo DB:  SOURCE_SCHEMA = 'NORTHWIND_SRC', SOURCE_DBLINK = NULL
- otra DB:   SOURCE_SCHEMA = 'NORTHWIND_SRC', SOURCE_DBLINK = 'LNK_SRC'

DESTINO: ejecutás estos scripts conectado como el usuario/esquema del DW (por ej. NORTHWIND_DW).

## Instalación (en DESTINO)
1) (Vos afuera) creás usuarios/schemas y otorgás permisos (SELECT en origen; CREATE TABLE/PROC en destino).
2) Conectado al DESTINO, ejecutar:
   @install_all.sql

3) Configurar origen:
   BEGIN
     etl_set_source(p_source_schema => 'NORTHWIND_SRC', p_source_dblink => NULL);
   END;
   /

4) Ejecutar todo:
   BEGIN
     sp_etl_run_all;
   END;
   /

## Watermarks por fecha + fallback por ID
Para dims, el loader busca una columna de “última modificación” en el ORIGEN con este orden:
modified_at, updated_at, last_update, last_modified, modified_date, ModifiedDate
Si no encuentra, usa watermark por ID (MAX PK).

Para FactSales usa order_date (por diseño).

## Deduplicación FactSales
- Se recomienda UNIQUE(order_id, product_id) en FACT_SALES.
- El load usa MERGE (inserta solo si no existe).

## Ajustes de nombres
Se asume un origen estilo Northwind:
- CATEGORIES(category_id, category_name, description, <modcol opcional>)
- CUSTOMERS(customer_id, contact_name, city, country, address, phone, postal_code, <modcol>)
- EMPLOYEES(employee_id, first_name, last_name, title, city, country, <modcol>)
- SHIPPERS(shipper_id, company_name, phone, <modcol>)
- SUPPLIERS(supplier_id, company_name, city, country, address, phone, postal_code, <modcol>)
- PRODUCTS(product_id, product_name, supplier_id, category_id, unit_price, discontinued, <modcol>)
- ORDERS(order_id, customer_id, employee_id, shipper_id, order_date, <modcol>)
- ORDER_DETAILS(order_id, product_id, quantity, unit_price, discount)

Si tu modelo difiere, editá `sql/03_procedures.sql` (los SELECT/joins).

