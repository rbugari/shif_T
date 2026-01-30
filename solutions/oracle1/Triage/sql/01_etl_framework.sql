-- =========================================================
-- 01_etl_framework.sql  (Oracle 10g/11g Standard compatible)
-- Ejecutar en el schema DESTINO
-- =========================================================

-- Settings
CREATE TABLE etl_settings (
  setting_key   VARCHAR2(100) PRIMARY KEY,
  setting_value VARCHAR2(4000) NOT NULL
);

CREATE OR REPLACE PROCEDURE etl_set_source(
  p_source_schema IN VARCHAR2,
  p_source_dblink IN VARCHAR2 DEFAULT NULL
) AS
BEGIN
  MERGE INTO etl_settings t
  USING (SELECT 'SOURCE_SCHEMA' AS k, UPPER(TRIM(p_source_schema)) AS v FROM dual) s
  ON (t.setting_key = s.k)
  WHEN MATCHED THEN UPDATE SET t.setting_value = s.v
  WHEN NOT MATCHED THEN INSERT (setting_key, setting_value) VALUES (s.k, s.v);

  MERGE INTO etl_settings t
  USING (SELECT 'SOURCE_DBLINK' AS k, NVL(UPPER(TRIM(p_source_dblink)), '') AS v FROM dual) s
  ON (t.setting_key = s.k)
  WHEN MATCHED THEN UPDATE SET t.setting_value = s.v
  WHEN NOT MATCHED THEN INSERT (setting_key, setting_value) VALUES (s.k, s.v);
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_get_source(
  p_source_schema OUT VARCHAR2,
  p_source_dblink OUT VARCHAR2
) AS
BEGIN
  SELECT setting_value INTO p_source_schema FROM etl_settings WHERE setting_key = 'SOURCE_SCHEMA';
  SELECT setting_value INTO p_source_dblink FROM etl_settings WHERE setting_key = 'SOURCE_DBLINK';
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    p_source_schema := NULL;
    p_source_dblink := NULL;
END;
/
SHOW ERRORS

-- Runs / steps
CREATE TABLE etl_run (
  run_id      NUMBER PRIMARY KEY,
  started_at  DATE NOT NULL,
  ended_at    DATE,
  status      VARCHAR2(20) NOT NULL,
  notes       VARCHAR2(500)
);

CREATE SEQUENCE etl_run_seq START WITH 1 INCREMENT BY 1 NOCACHE;

CREATE TABLE etl_step (
  step_id        NUMBER PRIMARY KEY,
  run_id         NUMBER NOT NULL,
  step_name      VARCHAR2(100) NOT NULL,
  started_at     DATE NOT NULL,
  ended_at       DATE,
  status         VARCHAR2(20) NOT NULL,
  rows_inserted  NUMBER,
  message        VARCHAR2(500),
  CONSTRAINT fk_etl_step_run FOREIGN KEY (run_id) REFERENCES etl_run(run_id)
);

CREATE SEQUENCE etl_step_seq START WITH 1 INCREMENT BY 1 NOCACHE;

-- Watermarks
CREATE TABLE etl_watermark (
  entity_name VARCHAR2(100) PRIMARY KEY,
  wm_dt       DATE NOT NULL,
  wm_id       NUMBER NOT NULL,
  updated_at  DATE NOT NULL
);

CREATE OR REPLACE PROCEDURE etl_watermark_init(p_entity IN VARCHAR2) AS
  v_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_cnt FROM etl_watermark WHERE entity_name = p_entity;
  IF v_cnt = 0 THEN
    INSERT INTO etl_watermark(entity_name, wm_dt, wm_id, updated_at)
    VALUES (p_entity, TO_DATE('1900-01-01','YYYY-MM-DD'), 0, SYSDATE);
  END IF;
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_watermark_get(
  p_entity IN VARCHAR2,
  p_wm_dt  OUT DATE,
  p_wm_id  OUT NUMBER
) AS
BEGIN
  etl_watermark_init(p_entity);
  SELECT wm_dt, wm_id INTO p_wm_dt, p_wm_id
  FROM etl_watermark WHERE entity_name = p_entity;
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_watermark_set_dt(p_entity IN VARCHAR2, p_wm_dt IN DATE) AS
BEGIN
  UPDATE etl_watermark SET wm_dt = p_wm_dt, updated_at = SYSDATE WHERE entity_name = p_entity;
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_watermark_set_id(p_entity IN VARCHAR2, p_wm_id IN NUMBER) AS
BEGIN
  UPDATE etl_watermark SET wm_id = p_wm_id, updated_at = SYSDATE WHERE entity_name = p_entity;
END;
/
SHOW ERRORS

-- Run helpers
CREATE OR REPLACE PROCEDURE etl_run_start(p_run_id OUT NUMBER) AS
BEGIN
  p_run_id := etl_run_seq.NEXTVAL;
  INSERT INTO etl_run(run_id, started_at, status) VALUES (p_run_id, SYSDATE, 'RUNNING');
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_run_end(p_run_id IN NUMBER, p_status IN VARCHAR2, p_notes IN VARCHAR2) AS
BEGIN
  UPDATE etl_run
  SET ended_at = SYSDATE, status = p_status, notes = p_notes
  WHERE run_id = p_run_id;
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_step_start(p_run_id IN NUMBER, p_step_name IN VARCHAR2, p_step_id OUT NUMBER) AS
BEGIN
  p_step_id := etl_step_seq.NEXTVAL;
  INSERT INTO etl_step(step_id, run_id, step_name, started_at, status)
  VALUES (p_step_id, p_run_id, p_step_name, SYSDATE, 'RUNNING');
END;
/
SHOW ERRORS

CREATE OR REPLACE PROCEDURE etl_step_end(p_step_id IN NUMBER, p_status IN VARCHAR2, p_rows IN NUMBER, p_message IN VARCHAR2) AS
BEGIN
  UPDATE etl_step
  SET ended_at = SYSDATE, status = p_status, rows_inserted = p_rows, message = p_message
  WHERE step_id = p_step_id;
END;
/
SHOW ERRORS

-- GTT para SCD (lista de productos con cambio Type2)
CREATE GLOBAL TEMPORARY TABLE etl_changed_products (
  product_id NUMBER PRIMARY KEY
) ON COMMIT DELETE ROWS;

