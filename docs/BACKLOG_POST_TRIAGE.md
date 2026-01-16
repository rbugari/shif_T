# Backlog de Triage - Mejoras Pendientes (Post-R1)

Este documento detalla las funcionalidades de la fase de **Triage (Discovery)** que han sido identificadas pero pospuestas para lanzamientos futuros (Future Releases), para mantener el foco en la transpilación y refinamiento actual.

## 1. Seguridad y Privacidad
- [ ] **Filtro de Anonimización**: Implementar una capa de pre-procesamiento que detecte y enmascare IPs, nombres de servidores, usuarios y contraseñas en los snippets de código antes de enviarlos a los LLMs (Ref. Instrucción 3 de implementación).

## 2. Inteligencia de Escaneo
- [ ] **Informe de Huella Tecnológica**: Generar una lista detallada de componentes no soportados nativamente (ej. componentes de terceros en SSIS) para gestionar expectativas mediante el "Paso 1" del workflow.
- [ ] **Identificación de Riesgos (Script Tasks)**: Marcar explícitamente paquetes que contienen lógica personalizada en C# o VB.NET para que el Agente F realice una auditoría manual o profunda.
- [ ] **Validación de Esquema (XSD)**: Incorporar validación formal por esquemas XSD para archivos `.dtsx` antes del parseo semántico (Ref. Instrucción 1).

## 3. Integración y Orquestación
- [ ] **Persistencia de Estado (Heartbeat)**: Implementar el guardado automático de `MigrationState` cada 10-30 segundos para permitir recuperación ante fallos en procesos largos (Ref. Instrucción 2).

## 4. Interfaz de Usuario e Interacción
- [ ] **Edición Manual de la Malla**: Endpoints para permitir que el usuario suba ajustes al grafo (nodos y edges) realizados en la UI de React Flow.
- [ ] **Aprobación de Fase**: Mecanismo de "Check-off" para que el usuario apruebe formalmente el Triage antes de iniciar la transpilación masiva.
