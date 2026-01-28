# Fase 2: Drafting & Code Generation (Guía Completa)

## 📌 Introducción
La fase de **Drafting (Stage 2)** es el corazón de la modernización automática en Shift-T. Una vez que el triaje ha definido QUÉ migrar, esta fase se encarga de CÓMO migrarlo. Aquí transformamos la lógica de negocio atrapada en paquetes legacy (SSIS .dtsx) en código moderno, limpio y ejecutable para **Databricks (PySpark)**.

---

## 👨‍💻 Para el Usuario: ¿Qué obtengo?

En esta etapa, verás cómo tu malla de procesos se ilumina nodo por nodo a medida que la IA genera el código.

### Entregables Clave
1.  **Notebooks PySpark (.py):** Código listo para producción. No son "esqueletos"; incluyen:
    *   **Conectividad Real:** Uso de JDBC con gestión de secretos (`dbutils.secrets.get`) para fuentes SQL.
    *   **Lógica de Negocio:** Transformaciones, Lookups y Joins convertidos a Dataframes.
    *   **Patrones de Escritura:** Implementación automática de **SCD Type 2** (Merge), manejo de **Surrogate Keys** e historización.
2.  **Reportes de Auditoría (.json):** Cada script viene acompañado de un "boletín de notas" generado por el Agente Crítico, que evalúa la calidad, seguridad y performance del código (Score 0-100).

---

## ⚙️ Arquitectura Técnica: El Pipeline de Generación

La generación no es una "caja negra". Es un proceso orquestado de varios pasos que garantiza precisión y especificidad.

### 1. Topology Service (El Traductor de Metadatos)
Antes de escribir una línea de código, el sistema "desarma" el paquete SSIS original.
*   **Extracción de SQL Real:** Recupera las consultas `SELECT` exactas embebidas en los componentes de origen.
*   **Mapeo de Tipos:** Identifica las columnas de entrada y salida y sus tipos de datos originales.
*   **Detección de Patrones:** Reconoce si el flujo es una carga incremental, un Full Load o una dimensión variante.

### 2. Migration Orchestrator (El Director)
Prepara el "Task Definition" para los agentes. Empaqueta el contexto necesario (Inputs, Outputs, Lookups, SQL Commands) en un formato estructurado que elimina la ambigüedad.
*   **Auto-Provisionamiento:** El orquestador ahora se encarga de crear automáticamente la estructura de directorios necesaria (`Drafting/`) antes de iniciar la generación, evitando errores de "Path not found".

### 3. Agent C: The Developer (El Constructor)
Es el experto en PySpark. Recibe la definición de la tarea y aplica las **Reglas de Oro de Shift-T**:
*   **Nunca Inventar:** Usa estrictamente los nombres de tablas y columnas proporcionados.
*   **Seguridad Primero:** Genera código de conexión usando *Secret Scopes*, nunca credenciales hardcodeadas.
*   **Estandarización:** Aplica formatos de lectura (`.format("jdbc")`) y escritura (`.format("delta")`) consistentes.

### 4. Agent F: The Critic (El Auditor)
Ningún código llega al usuario sin pasar por este filtro. El Agente F actúa como un *Senior Data Engineer*:
*   **Valida:** ¿El código implementa correctamente la lógica de negocio?
*   **Audita:** ¿Cumple con las reglas de plataforma (ej: manejo de nulos, claves generadas)?
*   **Rechaza:** Si el código es un "placeholder" o inseguro, lo bloquea y solicita regeneración.

---

## 🚀 Características Destacadas (State 2 Functional)

### 🔗 Conectividad Explícita
El sistema detecta automáticamente cuando una fuente es una base de datos SQL y genera el código de conexión JDBC completo:
```python
# Ejemplo Generado
jdbc_url = dbutils.secrets.get(scope="jdbc-secrets", key="hr_db_url")
df_source = spark.read.format("jdbc").option("dbtable", f"({source_query}) as src")...
```

### ⏳ Slowly Changing Dimensions (SCD Type 2)
Para tablas de dimensiones (`Dim*`), el sistema genera automáticamente lógica `MERGE` compleja para manejar la historización:
*   Detección de cambios en atributos.
*   Cierre de registros antiguos (`EndDate`, `IsCurrent = False`).
*   Inserción de nuevos registros.
*   Manejo de **Miembros Desconocidos** (-1).

### 🔑 Gestión de Identidad
Implementación de lógica para **Surrogate Keys** secuenciales, asegurando integridad referencial en el Lakehouse.

---

## 📊 Flujo de Trabajo Típico

1.  **Aprobar Triage:** Al finalizar la Fase 1, bloqueas el alcance (`Lock Scope`).
2.  **Ejecutar Pipeline:** Desde el Dashboard, inicias la migración (`Execute Pipeline`).
3.  **Monitoreo y Persistencia:**
    *   **Live Logs:** Observas el progreso en tiempo real en la consola.
    *   **Log Persistence:** Si recargas la página, el sistema recupera automáticamente el historial de ejecución (`GET /logs`), restaurando el estado de progreso al 100% si la migración terminó exitosamente.
4.  **Aprobar:** Una vez completado, el botón "Approve & Refine" se habilita, permitiendo avanzar a la Fase 3 con un solo clic.
5.  **Descarga:** Obtienes una solución completa organizada en carpetas.


## 🔮 Roadmap to Excellence: Qué falta para el "Gold Standard"

Aunque el código actual es funcional y seguro, para alcanzar un nivel **Enterprise-Grade** absoluto, evaluamos implementar las siguientes capas en futuras iteraciones:

### 1. Test Driven Generation (TDG)
*   **Actual:** Generamos el script de transformación.
*   **Futuro:** Generar un archivo compañero `test_dim_employee.py` usando `pytest` o `chispa`.
    *   *Objetivo:* Validar lógica de negocio unitaria antes del despliegue.

### 2. Data Quality & Contracts
*   **Actual:** Auditoría de código estático (Agent F).
*   **Futuro:** Inyección de checks de calidad en tiempo de ejecución (Great Expectations / Soda).
    *   *Ejemplo:* `assert df.filter(col("pk").isNull()).count() == 0` antes de escribir.

### 3. Observabilidad Estructurada
*   **Actual:** Logs básicos (`print`).
*   **Futuro:** Implementación de un Logger estandarizado que emita métricas a Azure Monitor / CloudWatch.
    *   *Métricas:* `rows_read`, `rows_written`, `execution_time_ms`.

### 4. Desacople de Configuración
*   **Actual:** Variables definidas al inicio del notebook.
*   **Futuro:** Extracción de "números mágicos" y umbrales a un archivo de configuración (`config.json` o Databricks Widgets) para cambiar parámetros sin tocar el código.

### 5. CI/CD Pipeline as Code
*   **Actual:** Archivos `.py` en carpeta.
*   **Futuro:** Generación automática de `azure-pipelines.yaml` o `github-workflows.yaml` para desplegar y testear estos notebooks automáticamente.

---
*Shift-T Documentation Framework v1.1 - Stage 2*
