# Shift-T: Arquitectura Técnica y Manual de Operaciones

Este documento detalla el funcionamiento interno de la plataforma Shift-T, desglosando la arquitectura de agentes, el flujo de datos y las transformaciones específicas en cada etapa.

---

## 1. Arquitectura del Sistema

Shift-T funciona como un **Orquestador Semántico**. No es un simple script de conversión; es un sistema que coordina múltiples "Agentes Cognitivos" para simular el flujo de trabajo de un equipo de ingeniería de datos humano.

### Los Agentes (The Cognitive Layer)

El sistema se compone de servicios especializados que actúan como roles en un equipo:

*   **Discovery Engine (Scanner):** No es IA. Es un analizador estático determinista (Python) que recorre el sistema de archivos, parsea XML (para .dtsx) y SQL, extrayendo metadatos crudos y "firmas" de código.
*   **Agent A (The Architect):** IA especializada en **Comprensión**.
    *   *Rol:* Analiza las firmas extraidas por el Scanner.
    *   *Función:* Clasifica activos (CORE/SUPPORT), infiere dependencias lógicas (quién lee a quién) y construye el Grafo Dirigido Acíclico (DAG) inicial.
*   **Migration Orchestrator (The Director):** Gestor de estado. Prepara los "paquetes de trabajo" para los agentes de desarrollo, asegurando que tengan el contexto necesario (tablas, columnas, tipos) sin ruido innecesario.
*   **Agent C (The Creator):** IA especializada en **Generación de Código**.
    *   *Rol:* Senior PySpark Developer.
    *   *Función:* Traduce lógica de negocio específica (ej: un Data Flow de SSIS) a sintaxis PySpark optimizada para Databricks.
*   **Agent F (The Fanatic):** IA especializada en **Auditoría y Calidad**.
    *   *Rol:* QA / Code Reviewer.
    *   *Función:* Analiza el código generado por Agent C buscando vulnerabilidades, anti-patrones o desviaciones de la arquitectura Medallion.

---

## 2. Desglose Fase por Fase (Input / Process / Output)

A continuación se detalla qué ocurre exactamente en cada etapa de la modernización.

### Fase 1: Discovery & Triage (Mapeo)

El objetivo es reducir la superficie de ataque y entender el legado.

| Componente | Detalles |
| :--- | :--- |
| **Input (Entrada)** | • Código Fuente Legacy (`.dtsx`, `.sql`, `.py`).<br>• Estructura de carpetas original.<br>• Cadenas de conexión (extraídas de config). |
| **Proceso (Process)** | 1. **Deep Scan:** Parsing de XML de SSIS para extraer queries SQL embebidas.<br>2. **Classification:** Agent A decide si un archivo es migrable (`CORE`) o basura (`IGNORED`).<br>3. **Graph Building:** Construcción de nodos y aristas (`READS_FROM`, `WRITES_TO`) basado en nombres de tablas. |
| **Output (Salida)** | • **Manifest.json:** Inventario técnico depurado.<br>• **Grafo de Dependencias:** Visualización topológica de la carga.<br>• **Reporte PDF:** Snapshot del estado inicial para stakeholders. |

### Fase 2: Drafting (Generación de Código)

El objetivo es obtener una versión funcional y equivalente de la lógica.

| Componente | Detalles |
| :--- | :--- |
| **Input (Entrada)** | • Manifiesto de Triage (Scope congelado).<br>• SQL extraído de los paquetes SSIS.<br>• Metadatos de columnas (Tipos de datos origen). |
| **Proceso (Process)** | 1. **Task Definition:** El orquestador crea una tarea por cada activo `CORE`.<br>2. **Context Injection:** Se inyecta al Prompt solo el SQL relevante para esa tarea.<br>3. **Code Generation:** Agent C escribe el notebook PySpark implementando lógica **SCD Type 2**, manejo de nulos y `Merge` de Delta Lake. |
| **Output (Salida)** | • **Notebooks (.py):** Scripts ejecutables en `solutions/{proy}/Drafting`.<br>• **Technical Log:** Historial de decisiones tomadas por la IA durante la traducción. |

### Fase 3: Refinement (Estandarización)

El objetivo es elevar el código a estándares corporativos (Medallion Architecture).

| Componente | Detalles |
| :--- | :--- |
| **Input (Entrada)** | • Notebooks generados en Fase 2.<br>• Reglas de Diseño (Design Registry). |
| **Proceso (Process)** | 1. **Static Analysis:** Agent F lee el código y busca hardcoding, malas prácticas o falta de comentarios.<br>2. **Optimization:** Reescritura para separar en capas: **Bronze** (Raw ingestion), **Silver** (Clean/Enriched) y **Gold** (Aggregated).<br>3. **Security Injection:** Reemplazo de credenciales por llamadas a `dbutils.secrets`. |
| **Output (Salida)** | • **Arquitectura en Capas:** Estructura de carpetas `/Bronze`, `/Silver`, `/Gold`.<br>• **Data Contracts:** Validaciones de esquema explícitas en el código. |

### Fase 4: Governance (Entrega)

El objetivo es la trazabilidad y el empaquetado final.

| Componente | Detalles |
| :--- | :--- |
| **Input (Entrada)** | • Solución Refinada completa.<br>• Logs de todo el proceso. |
| **Proceso (Process)** | 1. **Lineage Tracing:** Mapeo final de columna a columna (Source -> Target).<br>2. **Doc Generation:** Creación automática de `README.md` por cada módulo y documentación de API. |
| **Output (Salida)** | • **Solution Bundle (.zip):** Entregable final versionado.<br>• **Migration Certificate:** Documento que certifica que el código ha pasado las auditorías de Agent F. |

---

## 3. Resumen de Valor Técnico

Al finalizar el proceso, obtienes:
1.  **Código Nativo:** No "wrappers" de código legacy, sino PySpark puro.
2.  **Idempotencia:** Los scripts pueden re-ejecutarse sin duplicar datos (gracias a `Delta Merge`).
3.  **Seguridad:** Cero credenciales en el repositorio.
4.  **Documentación:** El código se auto-explica y viene acompañado de diagramas de linaje.
