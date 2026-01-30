# Knowledge Drivers: El "Cerebro Técnico" de Shift-T

> [!NOTE]
> **Para No-Técnicos (For Dummies):**
> Imagina que Shift-T es un traductor universal. Pero traducir poesía (código humano) es difícil.
> Los **Knowledge Drivers** son como "diccionarios especializados" que le damos al traductor.
> *   Si el archivo es francés antiguo (.dtsx), le damos el diccionario de francés.
> *   Si es jeroglífico (.sql), le damos el de jeroglíficos.
> 
> Sin estos drivers, la IA intentaría adivinar. Con los drivers, la IA **sabe** las reglas exactas antes de empezar.

---

## 1. ¿Qué es un Knowledge Driver?

Shift-T no está "hardcodeado" para una sola tecnología. En su lugar, utiliza un sistema de **Drivers Conectables (Pluggable Drivers)**. Un driver es un pequeño módulo de código que enseña al sistema cómo manejar un tipo específico de archivo.

### ¿Cómo funciona?

1.  **Escaneo**: Cuando subes tu proyecto, el `DiscoveryService` mira cada archivo.
2.  **Selección**: Si el archivo termina en `.sql`, despierta al `SQLDriver`. Si termina en `.dtsx`, despierta al `SSISDriver`.
3.  **Extracción**: El driver lee el archivo e identifica "firmas" (pistas de qué dialecto es).
4.  **Inyección**: El driver entrega su **"Conocimiento de Agente" (Agent Knowledge)** al sistema.

---

## 2. Inyección de Contexto (Prompt Combination)

Aquí es donde ocurre la magia. La IA no usa un solo prompt gigante. Shift-T construye el prompt **dinámicamente** combinando tres capas:

1.  **Prompt del Sistema (La Personalidad)**: "Eres un experto en migración a la nube..."
2.  **Conocimiento del Proyecto (El Mapa)**: "Estás trabajando en el proyecto ClienteX..."
3.  **Conocimiento del Driver (La Técnica)**: *Aquí entra el driver.*

### Ejemplo Real (SQL Driver)

Si el `SQLDriver` detecta que tu código es **Oracle PL/SQL**, inyecta secretamente este texto en el cerebro de la IA:

> "Estás analizando Oracle. Si ves `DBMS_OUTPUT`, es un print. Si ves un `CURSOR`, es un bucle lento; conviértelo a lógica de DataFrames en PySpark. No uses bucles `for` si puedes usar operaciones vectorizadas."

**Resultado:** La IA genera código optimizado para Spark sin que tú se lo pidas.

---

## 3. Los Drivers en las Fases del Proceso

Los drivers trabajan silenciosamente en cada etapa de la migración. Aquí tienes el detalle de cómo influyen:

### Fase 1: Discovery (El Bibliotecario)
*   **Driver**: Escanea los archivos "crudos".
*   **Acción**: Clasifica el archivo. ¿Es basura o es crítico?
*   **Ejemplo**: El `SSISDriver` abre un archivo `.dtsx` (que es XML complejo) y le dice al Bibliotecario: *"Oye, esto no es texto, es un paquete ETL que mueve datos de A a B"*.

### Fase 2: Topology (El Cartógrafo)
*   **Driver**: Busca conexiones invisibles.
*   **Acción**: Encuentra dependencias.
*   **Ejemplo**: El `SQLDriver` lee un script y ve `EXEC sp_Facturacion`. Le dice al Cartógrafo: *"Este archivo depende del procedimiento 'sp_Facturacion', dibuja una flecha entre ellos en el mapa"*.

### Fase 3: Drafting (El Intérprete)
*   **Driver**: Aporta las reglas de traducción.
*   **Acción**: Guía la generación de código.
*   **Ejemplo**: Al convertir SSiS, el `SSISDriver` advierte: *"Cuidado, este componente 'Lookup' gasta mucha memoria. Al traducirlo a Python, usa un Broadcast Join de Spark"*.

---

## 4. Drivers Disponibles y Soporte

Actualmente Shift-T incluye los siguientes drivers "de caja":

### 🔵 SSIS Driver (.dtsx)
Especialista en integración de datos de Microsoft.
*   **Detecta**: Flujos de Datos, Flujos de Control, Variables, Conexiones.
*   **Regla de Oro**: "Todo DataFlow se convierte en un DataFrame de Spark".

### 🟠 SQL Driver (.sql)
Un políglota que entiende varios dialectos.
*   **Detecta**:
    *   **T-SQL (SQL Server)**: Busca `IDENTITY`, `TOP`, `USE`.
    *   **PL/SQL (Oracle)**: Busca `VARCHAR2`, `EXCEPTION`, `DUAL`.
    *   **MySQL**: Busca `AUTO_INCREMENT`, comillas invertidas (` `).
*   **Regla de Oro**: "La lógica de conjuntos (SELECT/JOIN) se mantiene. La lógica procedimental (Cursores/While) se reescribe en Python nativo".

### 🐍 Python Driver (.py) - *Genérico*
Para scripts existentes.
*   **Detecta**: Uso de librerías como `pandas`, `pyspark`, o llamadas al sistema `os.system`.

---

## 5. Ejemplo para Tontos: "La Receta de Cocina" 🍳

Imagina que estás traduciendo recetas de cocina para un robot chef moderno (**La Nube**).

**Sin Driver:**
*   **Entrada**: "Echar una pizca de sal" (Receta de la Abuela).
*   **IA (Confundida)**: "¿Qué es una pizca? ¿Cuantos gramos? Error."

**Con Driver (El Nieto que sabe cocinar):**
*   **Entrada**: "Echar una pizca de sal".
*   **Driver**: "¡Alto! 'Pizca' en el idioma de la Abuela significa exactamente 1.5 gramos."
*   **IA (Informada)**: "Añadiendo 1.5 gramos de cloruro de sodio." -> **Código Perfecto.**

### En Código:
*   **Entrada**: `SELECT TOP 10 * FROM Clientes` (SQL Server).
*   **Driver**: "En la nube no se dice `TOP`, se dice `.limit()`".
*   **Salida**: `spark.table("Clientes").limit(10)` (PySpark).

---

> [!TIP]
> **¿Quieres añadir tu propia tecnología?**
> Solo necesitas crear un archivo Python en `apps/api/services/drivers/` que diga:
> 1. Qué extensión buscar (ej. `.cob` para Cobol).
> 2. Qué reglas de traducción aplicar.
> ¡Shift-T lo cargará automáticamente!
