-- =========================================================
-- 03_procedures.sql — SPs ETL
-- Oracle 10g/11g Standard compatible (sin features nuevas)
-- =========================================================

-- Helper: devuelve "SCHEMA." + "@DBLINK" (si aplica)
CREATE OR REPLACE FUNCTION etl_src_qualifier
RETURN VARCHAR2
AS
  v_schema VARCHAR2(255);
  v_dblink VARCHAR2(255);
BEGIN
  etl_get_source(v_schema, v_dblink);
  IF v_schema IS NULL OR v_schema = '' THEN
    RETURN NULL;
  END IF;

  IF v_dblink IS NULL OR v_dblink = '' THEN
    RETURN v_schema || '.';
  ELSE
    RETURN v_schema || '@' || v_dblink || '.';
  END IF;
END;
/
SHOW ERRORS

-- Helper: busca columna de "modified" en tabla origen
CREATE OR REPLACE FUNCTION etl_find_modified_column(p_table_name IN VARCHAR2)
RETURN VARCHAR2
AS
  v_schema VARCHAR2(255);
  v_dblink VARCHAR2(255);
  v_col VARCHAR2(128);
BEGIN
  etl_get_source(v_schema, v_dblink);

  -- Consultamos ALL_TAB_COLUMNS (en el mismo DB). Si usás DBLINK, igual sirve porque el diccionario es local.
  -- En caso de DBLINK, esta detección no ve el diccionario remoto; para ese caso usá el fallback por ID o definí manualmente.
  SELECT column_name INTO v_col
  FROM (
    SELECT column_name
    FROM all_tab_columns
    WHERE owner = UPPER(v_schema)
      AND table_name = UPPER(p_table_name)
      AND column_name IN ('MODIFIED_AT','UPDATED_AT','LAST_UPDATE','LAST_MODIFIED','MODIFIED_DATE','ModifiedDate')
    ORDER BY CASE column_name
      WHEN 'MODIFIED_AT' THEN 1
      WHEN 'UPDATED_AT' THEN 2
      WHEN 'LAST_UPDATE' THEN 3
      WHEN 'LAST_MODIFIED' THEN 4
      WHEN 'MODIFIED_DATE' THEN 5
      WHEN 'ModifiedDate' THEN 6
      ELSE 999 END
  )
  WHERE ROWNUM = 1;

  RETURN v_col;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    RETURN NULL;
END;
/
SHOW ERRORS

-- ----------------------------
-- DimCategory (watermark fecha si existe, si no por ID)
-- ----------------------------
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_category(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_modcol VARCHAR2(128);
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
  v_new_id NUMBER;
BEGIN
  etl_step_start(p_run_id, 'dim_category', v_step_id);

  etl_watermark_get('dim_category', v_wm_dt, v_wm_id);
  v_modcol := etl_find_modified_column('CATEGORIES');

  etl_get_source(v_src_prefix, v_src_prefix); -- dummy to ensure settings exist (not used)
  v_src_prefix := etl_src_qualifier(); -- e.g. NORTHWIND_SRC.

  IF v_src_prefix IS NULL THEN
    etl_step_end(v_step_id, 'FAILED', 0, 'SOURCE not configured');
    RAISE_APPLICATION_ERROR(-20001, 'SOURCE not configured. Run etl_set_source(...)');
  END IF;

  IF v_modcol IS NOT NULL THEN
    v_sql := 'INSERT INTO dim_category(category_id, category_name, description) '||
             'SELECT c.category_id, c.category_name, c.description '||
             'FROM '||v_src_prefix||'categories c '||
             'WHERE c.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_dt;
    v_rows := SQL%ROWCOUNT;

    v_sql := 'SELECT MAX(c.'||v_modcol||') FROM '||v_src_prefix||'categories c WHERE c.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql INTO v_new_dt USING v_wm_dt;
    IF v_new_dt IS NOT NULL THEN
      etl_watermark_set_dt('dim_category', v_new_dt);
    END IF;
  ELSE
    v_sql := 'INSERT INTO dim_category(category_id, category_name, description) '||
             'SELECT c.category_id, c.category_name, c.description '||
             'FROM '||v_src_prefix||'categories c '||
             'WHERE c.category_id > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_id;
    v_rows := SQL%ROWCOUNT;

    SELECT NVL(MAX(category_id),0) INTO v_new_id FROM dim_category;
    etl_watermark_set_id('dim_category', v_new_id);
    etl_watermark_set_dt('dim_category', SYSDATE);
  END IF;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- DimCustomer
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_customer(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_modcol VARCHAR2(128);
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
  v_new_id NUMBER;
BEGIN
  etl_step_start(p_run_id, 'dim_customer', v_step_id);
  etl_watermark_get('dim_customer', v_wm_dt, v_wm_id);
  v_modcol := etl_find_modified_column('CUSTOMERS');
  v_src_prefix := etl_src_qualifier();

  IF v_modcol IS NOT NULL THEN
    v_sql := 'INSERT INTO dim_customer(customer_id, contact_name, city, country, address, phone, postal_code) '||
             'SELECT c.customer_id, c.contact_name, c.city, c.country, c.address, c.phone, c.postal_code '||
             'FROM '||v_src_prefix||'customers c WHERE c.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_dt;
    v_rows := SQL%ROWCOUNT;

    v_sql := 'SELECT MAX(c.'||v_modcol||') FROM '||v_src_prefix||'customers c WHERE c.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql INTO v_new_dt USING v_wm_dt;
    IF v_new_dt IS NOT NULL THEN
      etl_watermark_set_dt('dim_customer', v_new_dt);
    END IF;
  ELSE
    v_sql := 'INSERT INTO dim_customer(customer_id, contact_name, city, country, address, phone, postal_code) '||
             'SELECT c.customer_id, c.contact_name, c.city, c.country, c.address, c.phone, c.postal_code '||
             'FROM '||v_src_prefix||'customers c WHERE c.customer_id > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_id;
    v_rows := SQL%ROWCOUNT;

    SELECT NVL(MAX(customer_id),0) INTO v_new_id FROM dim_customer;
    etl_watermark_set_id('dim_customer', v_new_id);
    etl_watermark_set_dt('dim_customer', SYSDATE);
  END IF;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- DimEmployee
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_employee(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_modcol VARCHAR2(128);
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
  v_new_id NUMBER;
BEGIN
  etl_step_start(p_run_id, 'dim_employee', v_step_id);
  etl_watermark_get('dim_employee', v_wm_dt, v_wm_id);
  v_modcol := etl_find_modified_column('EMPLOYEES');
  v_src_prefix := etl_src_qualifier();

  IF v_modcol IS NOT NULL THEN
    v_sql := 'INSERT INTO dim_employee(employee_id, first_name, last_name, title, city, country) '||
             'SELECT e.employee_id, e.first_name, e.last_name, e.title, e.city, e.country '||
             'FROM '||v_src_prefix||'employees e WHERE e.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_dt;
    v_rows := SQL%ROWCOUNT;

    v_sql := 'SELECT MAX(e.'||v_modcol||') FROM '||v_src_prefix||'employees e WHERE e.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql INTO v_new_dt USING v_wm_dt;
    IF v_new_dt IS NOT NULL THEN
      etl_watermark_set_dt('dim_employee', v_new_dt);
    END IF;
  ELSE
    v_sql := 'INSERT INTO dim_employee(employee_id, first_name, last_name, title, city, country) '||
             'SELECT e.employee_id, e.first_name, e.last_name, e.title, e.city, e.country '||
             'FROM '||v_src_prefix||'employees e WHERE e.employee_id > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_id;
    v_rows := SQL%ROWCOUNT;

    SELECT NVL(MAX(employee_id),0) INTO v_new_id FROM dim_employee;
    etl_watermark_set_id('dim_employee', v_new_id);
    etl_watermark_set_dt('dim_employee', SYSDATE);
  END IF;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- DimShipper
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_shipper(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_modcol VARCHAR2(128);
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
  v_new_id NUMBER;
BEGIN
  etl_step_start(p_run_id, 'dim_shipper', v_step_id);
  etl_watermark_get('dim_shipper', v_wm_dt, v_wm_id);
  v_modcol := etl_find_modified_column('SHIPPERS');
  v_src_prefix := etl_src_qualifier();

  IF v_modcol IS NOT NULL THEN
    v_sql := 'INSERT INTO dim_shipper(shipper_id, company_name, phone) '||
             'SELECT s.shipper_id, s.company_name, s.phone '||
             'FROM '||v_src_prefix||'shippers s WHERE s.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_dt;
    v_rows := SQL%ROWCOUNT;

    v_sql := 'SELECT MAX(s.'||v_modcol||') FROM '||v_src_prefix||'shippers s WHERE s.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql INTO v_new_dt USING v_wm_dt;
    IF v_new_dt IS NOT NULL THEN
      etl_watermark_set_dt('dim_shipper', v_new_dt);
    END IF;
  ELSE
    v_sql := 'INSERT INTO dim_shipper(shipper_id, company_name, phone) '||
             'SELECT s.shipper_id, s.company_name, s.phone '||
             'FROM '||v_src_prefix||'shippers s WHERE s.shipper_id > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_id;
    v_rows := SQL%ROWCOUNT;

    SELECT NVL(MAX(shipper_id),0) INTO v_new_id FROM dim_shipper;
    etl_watermark_set_id('dim_shipper', v_new_id);
    etl_watermark_set_dt('dim_shipper', SYSDATE);
  END IF;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- DimSupplier
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_supplier(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_modcol VARCHAR2(128);
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
  v_new_id NUMBER;
BEGIN
  etl_step_start(p_run_id, 'dim_supplier', v_step_id);
  etl_watermark_get('dim_supplier', v_wm_dt, v_wm_id);
  v_modcol := etl_find_modified_column('SUPPLIERS');
  v_src_prefix := etl_src_qualifier();

  IF v_modcol IS NOT NULL THEN
    v_sql := 'INSERT INTO dim_supplier(supplier_id, company_name, city, country, address, phone, postal_code) '||
             'SELECT s.supplier_id, s.company_name, s.city, s.country, s.address, s.phone, s.postal_code '||
             'FROM '||v_src_prefix||'suppliers s WHERE s.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_dt;
    v_rows := SQL%ROWCOUNT;

    v_sql := 'SELECT MAX(s.'||v_modcol||') FROM '||v_src_prefix||'suppliers s WHERE s.'||v_modcol||' > :1';
    EXECUTE IMMEDIATE v_sql INTO v_new_dt USING v_wm_dt;
    IF v_new_dt IS NOT NULL THEN
      etl_watermark_set_dt('dim_supplier', v_new_dt);
    END IF;
  ELSE
    v_sql := 'INSERT INTO dim_supplier(supplier_id, company_name, city, country, address, phone, postal_code) '||
             'SELECT s.supplier_id, s.company_name, s.city, s.country, s.address, s.phone, s.postal_code '||
             'FROM '||v_src_prefix||'suppliers s WHERE s.supplier_id > :1';
    EXECUTE IMMEDIATE v_sql USING v_wm_id;
    v_rows := SQL%ROWCOUNT;

    SELECT NVL(MAX(supplier_id),0) INTO v_new_id FROM dim_supplier;
    etl_watermark_set_id('dim_supplier', v_new_id);
    etl_watermark_set_dt('dim_supplier', SYSDATE);
  END IF;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- ----------------------------
-- DimProduct SCD (Type2: supplier/category; Type1: name/price/discontinued)
-- ----------------------------
CREATE OR REPLACE PROCEDURE sp_etl_load_dim_product_scd(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
BEGIN
  etl_step_start(p_run_id, 'dim_product_scd', v_step_id);
  v_src_prefix := etl_src_qualifier();

  -- limpiar lista de cambios
  DELETE FROM etl_changed_products;

  -- detectar cambios Type2 y guardarlos
  v_sql := 'INSERT INTO etl_changed_products(product_id) '||
           'SELECT d.product_id '||
           'FROM dim_product d '||
           'JOIN '||v_src_prefix||'products p ON p.product_id = d.product_id '||
           'WHERE d.is_current = 1 '||
           'AND (NVL(d.supplier_id,-1) <> NVL(p.supplier_id,-1) OR NVL(d.category_id,-1) <> NVL(p.category_id,-1))';
  EXECUTE IMMEDIATE v_sql;

  -- expirar actuales
  UPDATE dim_product d
  SET d.is_current = 0,
      d.effective_to = SYSDATE
  WHERE d.is_current = 1
    AND EXISTS (SELECT 1 FROM etl_changed_products c WHERE c.product_id = d.product_id);

  -- insertar nueva versión para cambiados
  v_sql := 'INSERT INTO dim_product(product_id, product_name, supplier_id, category_id, unit_price, discontinued, is_current, effective_from, effective_to) '||
           'SELECT p.product_id, p.product_name, p.supplier_id, p.category_id, p.unit_price, p.discontinued, 1, SYSDATE, NULL '||
           'FROM '||v_src_prefix||'products p '||
           'JOIN etl_changed_products c ON c.product_id = p.product_id';
  EXECUTE IMMEDIATE v_sql;
  v_rows := SQL%ROWCOUNT;

  -- Type1 update (solo current)
  v_sql := 'UPDATE dim_product d '||
           'SET (d.product_name, d.unit_price, d.discontinued) = '||
           ' (SELECT p.product_name, p.unit_price, p.discontinued FROM '||v_src_prefix||'products p WHERE p.product_id = d.product_id) '||
           'WHERE d.is_current = 1 '||
           'AND EXISTS (SELECT 1 FROM '||v_src_prefix||'products p '||
           '            WHERE p.product_id = d.product_id '||
           '              AND (NVL(d.product_name,'' '') <> NVL(p.product_name,'' '') '||
           '                OR NVL(d.unit_price,0) <> NVL(p.unit_price,0) '||
           '                OR NVL(d.discontinued,0) <> NVL(p.discontinued,0)))';
  EXECUTE IMMEDIATE v_sql;

  -- nuevos productos
  v_sql := 'INSERT INTO dim_product(product_id, product_name, supplier_id, category_id, unit_price, discontinued, is_current, effective_from, effective_to) '||
           'SELECT p.product_id, p.product_name, p.supplier_id, p.category_id, p.unit_price, p.discontinued, 1, SYSDATE, NULL '||
           'FROM '||v_src_prefix||'products p '||
           'WHERE NOT EXISTS (SELECT 1 FROM dim_product d WHERE d.product_id = p.product_id AND d.is_current = 1)';
  EXECUTE IMMEDIATE v_sql;
  v_rows := v_rows + SQL%ROWCOUNT;

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- ----------------------------
-- FactSales: stage + watermark por fecha (order_date) + dedup (MERGE)
-- ----------------------------
CREATE OR REPLACE PROCEDURE sp_etl_load_fact_sales(p_run_id IN NUMBER) AS
  v_step_id NUMBER;
  v_wm_dt DATE;
  v_wm_id NUMBER;
  v_rows NUMBER := 0;
  v_src_prefix VARCHAR2(4000);
  v_sql VARCHAR2(4000);
  v_new_dt DATE;
BEGIN
  etl_step_start(p_run_id, 'fact_sales', v_step_id);
  etl_watermark_get('fact_sales', v_wm_dt, v_wm_id);
  v_src_prefix := etl_src_qualifier();

  EXECUTE IMMEDIATE 'TRUNCATE TABLE stage_fact_sales';

  -- llenar stage con órdenes nuevas por fecha
  v_sql := 'INSERT INTO stage_fact_sales(order_id, customer_id, employee_id, shipper_id, category_id, supplier_id, product_id, qty, unit_price, discount, order_date) '||
           'SELECT o.order_id, o.customer_id, o.employee_id, o.shipper_id, p.category_id, p.supplier_id, od.product_id, od.quantity, od.unit_price, od.discount, o.order_date '||
           'FROM '||v_src_prefix||'orders o '||
           'JOIN '||v_src_prefix||'order_details od ON od.order_id = o.order_id '||
           'JOIN '||v_src_prefix||'products p ON p.product_id = od.product_id '||
           'WHERE o.order_date > :1';
  EXECUTE IMMEDIATE v_sql USING v_wm_dt;

  -- dedup: MERGE inserta solo si no existe (order_id, product_id)
  MERGE INTO fact_sales f
  USING (
    SELECT order_id, customer_id, employee_id, shipper_id, category_id, supplier_id, product_id, qty, unit_price, discount, order_date
    FROM stage_fact_sales
  ) s
  ON (f.order_id = s.order_id AND f.product_id = s.product_id)
  WHEN NOT MATCHED THEN
    INSERT (order_id, customer_id, employee_id, shipper_id, category_id, supplier_id, product_id, qty, unit_price, discount, order_date)
    VALUES (s.order_id, s.customer_id, s.employee_id, s.shipper_id, s.category_id, s.supplier_id, s.product_id, s.qty, s.unit_price, s.discount, s.order_date);

  v_rows := SQL%ROWCOUNT;

  SELECT NVL(MAX(order_date), v_wm_dt) INTO v_new_dt FROM stage_fact_sales;
  etl_watermark_set_dt('fact_sales', v_new_dt);

  etl_step_end(v_step_id, 'OK', v_rows, NULL);
EXCEPTION
  WHEN OTHERS THEN
    etl_step_end(v_step_id, 'FAILED', v_rows, SQLERRM);
    RAISE;
END;
/
SHOW ERRORS

-- ----------------------------
-- Orquestador
-- ----------------------------
CREATE OR REPLACE PROCEDURE sp_etl_run_all AS
  v_run_id NUMBER;
  v_schema VARCHAR2(255);
  v_dblink VARCHAR2(255);
BEGIN
  etl_get_source(v_schema, v_dblink);
  IF v_schema IS NULL OR v_schema = '' THEN
    RAISE_APPLICATION_ERROR(-20001, 'Falta configurar SOURCE. Ejecutá etl_set_source(...)');
  END IF;

  etl_run_start(v_run_id);

  BEGIN
    sp_etl_load_dim_category(v_run_id);
    sp_etl_load_dim_customer(v_run_id);
    sp_etl_load_dim_employee(v_run_id);
    sp_etl_load_dim_shipper(v_run_id);
    sp_etl_load_dim_supplier(v_run_id);
    sp_etl_load_dim_product_scd(v_run_id);
    sp_etl_load_fact_sales(v_run_id);

    etl_run_end(v_run_id, 'OK', NULL);
  EXCEPTION
    WHEN OTHERS THEN
      etl_run_end(v_run_id, 'FAILED', 'Falló algún paso. Ver ETL_STEP. '||SQLERRM);
      RAISE;
  END;
END;
/
SHOW ERRORS
