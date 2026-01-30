# Knowledge Drivers & Matrix Architecture: El "Cerebro Modular" de Shift-T

> [!NOTE]
> **Para No-Técnicos (For Dummies):**
> Imagina que Shift-T es una **Agencia de Traducción Universal**.
> Antes, cada traductor tenía que saber todo (leer Chino y escribir Español).
> 
> Ahora, hemos separado el trabajo en dos departamentos:
> 1.  **Lectores (Drivers)**: Expertos que solo leen. Uno lee Jeroglíficos, otro lee Francés antiguo. Extraen el "significado" y se lo pasan al jefe.
> 2.  **Escritores (Estrategias)**: Expertos que solo escriben. Uno escribe Novelas, otro escribe Tweets.
> 
> **La Magia (La Matrix):**
> El jefe (Agente C) mira qué recibe y qué necesita.
> *   ¿Entrada Jeroglífico? -> Llama al Lector de Egipto.
> *   ¿Salida Novela? -> Llama al Escritor de Literatura.
> *   **Resultado:** Combinaciones infinitas sin re-entrenar a nadie.

---

## 1. La Arquitectura Matrix ($N \times M$)

Shift-T ha evolucionado de un modelo "Monolítico" a un modelo "Matricial Desacoplado".

### Entrada: Los Drivers (Lectores)
Su única misión es **entender el legado**. No saben nada sobre a dónde van los datos.
*   **Path**: `apps/api/services/drivers/*.py`
*   **Responsabilidad**: Análisis léxico, extracción de metadatos, detección de dependencias.
*   **Ejemplos**:
    *   `SSISDriver`: Lee XMLs complejos (`.dtsx`).
    *   `SQLDriver`: Lee dialectos T-SQL, PL/SQL, MySQL.

### Salida: El Conocimiento (Escritores)
Su única misión es **conocer el destino**. No saben de dónde vienen los datos.
*   **Path**: `apps/api/prompts/knowledge/*.md`
*   **Responsabilidad**: Reglas de sintaxis, mejores prácticas, optimizaciones específicas del target.
*   **Ejemplos**:
    *   `sql_pyspark.md`: Cómo convertir SQL a Databricks (PySpark).
    *   `sql_snowpark.md`: Cómo convertir SQL a Snowflake (Snowpark).

---

## 2. Inyección Dinámica de Lógica

El Agente C (Developer) actúa como el "Broker" que conecta ambos mundos en tiempo de ejecución.

1.  **Detección**: El Agente C recibe una tarea. El Driver ya dijo: "Esto es **SQL**".
2.  **Configuración**: El Agente C mira tu variable de entorno `TARGET_LANG` (ej. `snowpark`).
3.  **Carga (Load)**: Busca el archivo de conocimiento exacto para esa combinación:
    > `apps/api/prompts/knowledge/sql_snowpark.md`
4.  **Inyección**: Inyecta esas reglas específicas en el prompt del LLM.

### ¿Por qué es mejor?
Si mañana quieres migrar a **Google BigQuery**:
1.  **NO** tocas código Python.
2.  Solo creas un archivo de texto: `knowledge/sql_bigquery.md`.
3.  Cambias `.env`: `TARGET_LANG=bigquery`.
4.  ¡Listo! El sistema aprende instantáneamente.

---

## 3. Configuración

Para cambiar el destino de tu migración, simplemente edita tu archivo `.env`:

```bash
# Opción A: Databricks / Delta Lake (Por defecto)
TARGET_LANG="pyspark"

# Opción B: Snowflake / Snowpark
TARGET_LANG="snowpark"
```

---

## 4. Ejemplo Real: La Receta 🍳

**Situación**: Tienes una receta (Código) que dice "Cocer a fuego lento" (Legacy).

### Caso A: Destino "Restaurante de Lujo" (PySpark)
*   **Driver (Input)**: Lee "Cocer a fuego lento". Entiende "Cocción lenta".
*   **Knowledge (Output)**: En el Restaurante de Lujo, "Cocción lenta" se traduce como **"Sous-vide a 65°C por 4 horas"**.
*   **Resultado**: Código optimizado para precisión y calidad.

### Caso B: Destino "Comida Rápida" (Snowpark)
*   **Driver (Input)**: Lee "Cocer a fuego lento". Entiende "Cocción lenta".
*   **Knowledge (Output)**: En Comida Rápida, "Cocción lenta" se traduce como **"Olla a presión por 15 minutos"**.
*   **Resultado**: Código optimizado para velocidad nativa en la base de datos.

> **Nota**: El Driver (Lector) nunca cambió. Solo cambiamos el libro de reglas del destino.

---

## 5. Drivers Disponibles

| Tecnología (Source) | Driver | Archivos | Capacidad |
| :--- | :--- | :--- | :--- |
| **Microsoft SSIS** | `SSISDriver` | `.dtsx` | Lee Control Flow, Data Flow, Scripts VB.NET |
| **SQL (Varios)** | `SQLDriver` | `.sql` | Detecta T-SQL, PL/SQL, MySQL, DDL, DML |
| **Python Legacy** | `PythonDriver` | `.py` | Detecta Pandas antiguo, scripts OS |

---

> [!TIP]
> **¿Quieres añadir tu propia tecnología?**
> 1. Crea un **Driver** en Python que sepa *leer* tu archivo.
> 2. Crea un archivo **Markdown** en `knowledge/` que sepa *escribir* tu destino.
> 3. ¡Disfruta de la Matrix!
