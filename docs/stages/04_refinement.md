# Fase 4: Architectural Refinement (Critic)

En esta etapa, el Agente F (**The Critic**) actúa como un arquitecto senior para elevar el código del "Draft" a un nivel empresarial.

## 🎯 Objetivo
Optimizar el código para rendimiento (Spark Better Practices), seguridad y alineación con la arquitectura Medallion.

## 🤖 El Bucle de Refinamiento (Shift-T Loop)

```mermaid
graph TD
    A[Draft Code] --> B(Agente F: Critic)
    B --> C{Evaluación de Calidad}
    C -- "Mejora Sugerida" --> D[Aplicación de Patrón Medallion]
    C -- "Vulnerabilidad" --> E[Saneamiento de Código]
    D & E --> F[Optimización de Shuffles/Joins]
    F --> G[Código Refinado]
    G --> H[Workbench Review]
```

### El Modelo Medallion
Shift-T organiza automáticamente la salida en tres capas:
1.  **Bronze:** Ingesta cruda de orígenes.
2.  **Silver:** Limpieza, filtrado y normalización.
3.  **Gold:** Agregaciones finales y lógica de negocio lista para consumo.

### Resultado de la Fase
Código **Refinado y Optimizado**, listo para ser auditado por el equipo de seguridad y cumplimiento.
