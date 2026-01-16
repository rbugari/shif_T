# Fase 1: Triage & Discovery (Guía Completa)

## 📌 Introducción
La fase de **Triage** es el primer paso crítico en el proceso de modernización de Shift-T. Su objetivo es transformar un repositorio de código fuente "ruidoso" y complejo (como un conjunto de paquetes SSIS antiguos) en una arquitectura funcional clara, priorizando los activos que realmente generan valor de negocio.

---

## 👨‍💻 Para el Usuario: ¿Qué sucede aquí?

En esta etapa, el sistema realiza un "escaneo inteligente" de tu proyecto para ayudarte a decidir qué migrar y cómo está todo conectado.

### Conceptos Clave
*   **CORE:** Procesos vitales que contienen lógica de negocio y deben ser migrados a PySpark.
*   **SUPPORT:** Dependencias, tablas de configuración o procesos auxiliares.
*   **IGNORED:** Archivos de log, configuraciones locales o código redundante que no debe ensuciar la nueva arquitectura.

### Herramientas a tu Disposición
1.  **Vista de Gráfico:** Una visualización interactiva de tu arquitectura. Puedes arrastrar activos, borrar nodos y auto-ordenar la malla (Vertical/Horizontal) para entender el flujo de datos.
2.  **Inventario (Grilla):** Una lista detallada donde puedes editar masivamente las categorías de cada archivo.
3.  **Refinado de Prompt:** Para usuarios avanzados, puedes darle "instrucciones" a la IA (ej: "Ignora todo lo que esté en la carpeta /logs") y volver a procesar el triaje.
4.  **Modo Maximizador:** Oculta toda la interfaz para centrarte exclusivamente en el diseño de la malla técnica.

---

## ⚙️ Para el Equipo Técnico: Arquitectura y Lógica

El proceso de Triage es una orquestación entre una capa de escaneo determinista y un modelo de razonamiento agentic.

### 1. El Scanner (Discovery Engine)
Ubicado en `DiscoveryService`, este componente escrito en Python realiza un análisis estático del sistema de archivos local o del repositorio clonado.
*   **Extracción de Firmas:** No solo lee nombres; analiza el contenido XML/SQL para identificar "firmas" (ej: Tareas de SQL, Transformaciones de Datos, Scripts).
*   **Generación de Manifiesto:** Crea un JSON estructurado que resume el inventario técnico sin enviar todo el código fuente masivo a la LLM, optimizando costos y contexto.

### 2. El Agente A (Mesh Architect)
Es el "cerebro" de esta fase. Recibe el manifiesto y utiliza un **System Prompt** especializado para:
*   **Clasificar:** Decide si un archivo es `CORE`, `SUPPORT` o `IGNORED`.
*   **Relacionar:** Infiere dependencias (`READS_FROM`, `WRITES_TO`, `SEQUENTIAL`) basándose en los metadatos y nombres de los activos.
*   **Observar:** Genera "Triage Observations", que son insights sobre deudas técnicas o riesgos detectados en el código fuente.

### 3. Orquestación del Gráfico y Layout
La visualización utiliza **React Flow** en el frontend, pero la inteligencia del ordenado reside en **Dagre**:
*   **Dagre Algorithm:** Implementa un layout de gráfico jerárquico (Directed Acyclic Graph) para asegurar que las dependencias fluyan de manera lógica y sin solapamientos.
*   **Sincronización:** Cualquier cambio manual en el gráfico (como borrar un nodo) actualiza automáticamente el estado del activo a `IGNORED` en la base de datos (Supabase).

### 4. Persistencia y Reinicio
*   **PROYECTO_RESET:** Hemos implementado un endpoint `POST /projects/{id}/reset` que realiza una purga selectiva: elimina los activos (`assets`) y las transformaciones (`transformations`) asociadas, devolviendo el proyecto al estado "Discovery".
*   **Layout Saving:** Las coordenadas de cada nodo se guardan en un registro de tipo `LAYOUT` en Supabase para que tu trabajo de diseño no se pierda al recargar.

---

## 🎨 Diseño y UX
Shift-T utiliza un sistema de diseño basado en **Glassmorphism** y **Atomic Design**:
*   **Toolbars Dinámicas:** Las barras de herramientas son icon-only y se activan al hover para maximizar el "espacio de pensamiento".
*   **Modo Fullscreen:** Un estado de React que altera el Z-Index y las dimensiones del contenedor principal para cubrir el viewport (`fixed inset-0`), permitiendo una inmersión total en la arquitectura.


## ⏭️ Próximos Pasos: Hacia la Generación

Una vez que has validado tu inventario y diseñado tu malla en esta Fase 1, estás listo para "aprobar" el plan.

1.  **Lock Scope:** Al hacer clic en "Approve Triage", el sistema bloquea el inventario.
2.  **Transition:** El proyecto avanza al estado `DRAFTING` (Stage 2).
3.  **Generación:** Se habilita el motor de **Code Generation** descrito en detalle en [Fase 2: Drafting & Code Generation](PHASE_2_DRAFTING.md).

---
*Shift-T Documentation Framework v1.1*
