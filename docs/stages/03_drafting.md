# Fase 3: Deep Analysis & Drafting (Interpreter)

El corazón de la transpilación. Aquí los Agentes C y D entran en el "interior" del código para generar la primera versión funcional en la nube.

## 🎯 Objetivo
Generar código PySpark de alta fidelidad que mantenga la semántica original pero adaptada al motor de destino.

## 🤖 El Flujo de Transpilación

```mermaid
graph TD
    A[Nodo de Malla Seleccionado] --> B(Agente C: Interpreter)
    B --> C{Extracción de Semántica}
    C --> D[Mapeo de Tipos de Datos]
    C --> E[Lógica de Transformación]
    D & E --> F(Agente D: Developer)
    F --> G[Código Draft (PySpark)]
    G --> H[Intelligence Hub Audit]
```

### El "Intelligence Hub"
Integrado en esta fase, permite al usuario auditar los **Compiled Prompts**. Aquí se puede ver exactamente qué instrucciones técnicas se pasaron a la IA, incluyendo el contexto del proyecto y el conocimiento inyectado por los Drivers.

### Resultado de la Fase
Un **Draft Funcional** del código en formato Notebook o Script PySpark.
