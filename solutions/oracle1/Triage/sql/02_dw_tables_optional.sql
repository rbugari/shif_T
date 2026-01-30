-- =========================================================
-- 02_dw_tables_optional.sql  (opcional) — DW mínimo en DESTINO
-- Si ya tenés tu DW, podés NO ejecutarlo.
-- =========================================================

-- Dimensions
CREATE TABLE dim_category (
  category_id   NUMBER PRIMARY KEY,
  category_name VARCHAR2(100),
  description   CLOB,
  created_at    DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE dim_customer (
  customer_id   NUMBER PRIMARY KEY,
  contact_name  VARCHAR2(200),
  city          VARCHAR2(100),
  country       VARCHAR2(100),
  address       VARCHAR2(200),
  phone         VARCHAR2(50),
  postal_code   VARCHAR2(20),
  created_at    DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE dim_employee (
  employee_id   NUMBER PRIMARY KEY,
  first_name    VARCHAR2(100),
  last_name     VARCHAR2(100),
  title         VARCHAR2(100),
  city          VARCHAR2(100),
  country       VARCHAR2(100),
  created_at    DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE dim_shipper (
  shipper_id    NUMBER PRIMARY KEY,
  company_name  VARCHAR2(200),
  phone         VARCHAR2(50),
  created_at    DATE DEFAULT SYSDATE NOT NULL
);

CREATE TABLE dim_supplier (
  supplier_id   NUMBER PRIMARY KEY,
  company_name  VARCHAR2(200),
  city          VARCHAR2(100),
  country       VARCHAR2(100),
  address       VARCHAR2(200),
  phone         VARCHAR2(50),
  postal_code   VARCHAR2(20),
  created_at    DATE DEFAULT SYSDATE NOT NULL
);

-- DimProduct SCD
CREATE TABLE dim_product (
  dim_product_key NUMBER PRIMARY KEY,
  product_id      NUMBER NOT NULL,
  product_name    VARCHAR2(200),
  supplier_id     NUMBER,
  category_id     NUMBER,
  unit_price      NUMBER(12,2),
  discontinued    NUMBER(1),
  is_current      NUMBER(1) DEFAULT 1 NOT NULL,
  effective_from  DATE DEFAULT SYSDATE NOT NULL,
  effective_to    DATE,
  CONSTRAINT uk_dim_product_current UNIQUE (product_id, is_current)
);

CREATE SEQUENCE dim_product_seq START WITH 1 INCREMENT BY 1 NOCACHE;

CREATE OR REPLACE TRIGGER trg_dim_product_key
BEFORE INSERT ON dim_product
FOR EACH ROW
BEGIN
  IF :NEW.dim_product_key IS NULL THEN
    :NEW.dim_product_key := dim_product_seq.NEXTVAL;
  END IF;
END;
/
SHOW ERRORS

CREATE OR REPLACE VIEW v_dim_product_current AS
SELECT * FROM dim_product WHERE is_current = 1;

-- Stage + Fact
CREATE TABLE stage_fact_sales (
  order_id     NUMBER,
  customer_id  NUMBER,
  employee_id  NUMBER,
  shipper_id   NUMBER,
  category_id  NUMBER,
  supplier_id  NUMBER,
  product_id   NUMBER,
  qty          NUMBER,
  unit_price   NUMBER(12,2),
  discount     NUMBER(10,4),
  order_date   DATE
);

CREATE TABLE fact_sales (
  fact_sales_key NUMBER PRIMARY KEY,
  order_id     NUMBER NOT NULL,
  customer_id  NUMBER,
  employee_id  NUMBER,
  shipper_id   NUMBER,
  category_id  NUMBER,
  supplier_id  NUMBER,
  product_id   NUMBER NOT NULL,
  qty          NUMBER,
  unit_price   NUMBER(12,2),
  discount     NUMBER(10,4),
  order_date   DATE,
  CONSTRAINT uk_fact_sales UNIQUE (order_id, product_id)
);

CREATE SEQUENCE fact_sales_seq START WITH 1 INCREMENT BY 1 NOCACHE;

CREATE OR REPLACE TRIGGER trg_fact_sales_key
BEFORE INSERT ON fact_sales
FOR EACH ROW
BEGIN
  IF :NEW.fact_sales_key IS NULL THEN
    :NEW.fact_sales_key := fact_sales_seq.NEXTVAL;
  END IF;
END;
/
SHOW ERRORS
