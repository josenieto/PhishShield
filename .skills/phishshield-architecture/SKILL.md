---
name: phishshield-architecture
description: Guía especializada para decisiones arquitectónicas en PhishShield. Usa esta skill siempre que el usuario pida definir, modificar o revisar estructura del repositorio, arquitectura hexagonal, Clean Architecture, capas Domain/Application/Infrastructure, puertos, adaptadores, entrypoints, límites entre módulos, dependencias, integración de tecnologías externas, Docker Compose desde perspectiva arquitectónica, ADRs o cualquier decisión que pueda afectar la mantenibilidad del diseño. Úsala también en tareas aparentemente de backend, frontend, seguridad, IA o DevOps cuando haya que decidir dónde vive el código, cómo evitar acoplamiento, si hace falta un puerto/adaptador, o si una propuesta contradice doc/ADR.md.
---

# phishshield-architecture

## Propósito

Ayudar a agentes IA a tomar decisiones arquitectónicas coherentes para **PhishShield**, respetando el ADR principal del proyecto y evitando desviaciones que acoplen el dominio a frameworks, librerías o servicios externos.

PhishShield es una herramienta defensiva, local y self-hosted para análisis forense de correos `.eml`. Su arquitectura debe permitir sustituir parsers, sandbox, IA local, frontend, API o herramientas de análisis sin alterar el núcleo del sistema.

Esta skill opera por encima de una tarea backend, frontend o DevOps concreta. Su función es decidir **límites, capas, responsabilidades y dirección de dependencias**.

## Referencias que debes consultar

Antes de tomar o revisar decisiones arquitectónicas, lee:

- `AGENT.md`
- `doc/ADR.md`
- `.skills/README.md`

Si hay conflicto entre esta skill y `doc/ADR.md`, prevalece `doc/ADR.md`.

## Proceso de trabajo

Cuando esta skill se active:

1. Identifica la decisión arquitectónica real detrás de la petición.
2. Consulta `doc/ADR.md` si la tarea afecta capas, módulos, despliegue o integraciones.
3. Clasifica los elementos implicados en `Domain`, `Application`, `Infrastructure` o `Entrypoints`.
4. Detecta dependencias peligrosas o acoplamientos a frameworks/librerías.
5. Propón la frontera correcta mediante puertos y adaptadores cuando haya IO, herramientas externas o sustitución futura.
6. Indica qué skill técnica debe continuar el trabajo si la arquitectura ya queda decidida.
7. Cierra con una comprobación breve contra el checklist arquitectónico.

El objetivo no es producir más documentación, sino evitar decisiones que hagan rígido el sistema.

## Cuándo usar esta skill

Usa esta skill cuando la tarea implique:

- definir estructura inicial del repositorio;
- crear o reorganizar carpetas;
- decidir si algo pertenece a `Domain`, `Application`, `Infrastructure` o `Entrypoints`;
- crear puertos;
- crear adaptadores;
- revisar dependencias entre capas;
- añadir un nuevo módulo forense;
- integrar FastAPI, Playwright, Ollama, YARA, Tesseract, oletools, pdfminer, PyPDF2, idna u otras librerías;
- revisar propuestas técnicas;
- crear o actualizar ADRs;
- diseñar Docker Compose desde la arquitectura del sistema;
- separar backend, frontend y servicios auxiliares;
- evaluar si una implementación rompe la arquitectura hexagonal.

No uses esta skill para detalles puramente internos de un componente si la arquitectura ya está decidida. En ese caso usa la skill específica correspondiente, por ejemplo `phishshield-backend`.

## Resultado esperado de una respuesta

Cuando respondas usando esta skill, estructura la respuesta de forma breve y decisiva:

```text
1. Decisión arquitectónica
2. Capa o capas afectadas
3. Diseño recomendado
4. Puertos/adaptadores necesarios
5. Riesgos de acoplamiento evitados
6. Tests o validaciones recomendadas
7. Siguiente skill técnica a usar, si aplica
```

Si la propuesta del usuario rompe el ADR, indícalo explícitamente y ofrece una alternativa compatible.

## Modelo arquitectónico base

El ADR define un **monolito modular hexagonal** combinado con Clean Architecture.

Modelo de dependencias:

```text
Domain  <-  Application  <-  Infrastructure / Entrypoints
```

Interpretación:

- **Domain** contiene conceptos puros y reglas de negocio forense.
- **Application** contiene casos de uso y puertos.
- **Infrastructure** contiene adaptadores técnicos e integraciones.
- **Entrypoints** exponen el sistema al exterior, por ejemplo FastAPI.

La flecha indica la dirección permitida de dependencia. Las capas externas pueden depender de las internas. Las internas no deben depender de las externas.

## Reglas de arquitectura

### 1. El dominio debe permanecer puro

El dominio no debe importar:

- FastAPI;
- Playwright;
- Ollama;
- Docker;
- httpx/requests;
- Tesseract/pytesseract;
- oletools;
- yara-python;
- pdfminer/PyPDF2;
- frameworks de persistencia;
- variables de entorno;
- SDKs externos.

El dominio puede contener:

- entidades;
- value objects;
- reglas puras;
- algoritmos deterministas;
- clasificación de hallazgos;
- normalización sin IO;
- tipos de resultado.

Ejemplo correcto:

```text
Domain contiene la regla de detección de homóglifos.
Infrastructure usa idna o librerías externas si hace falta adaptación técnica.
```

### 2. Application orquesta mediante puertos

Application debe contener:

- casos de uso;
- contratos;
- puertos;
- coordinación de análisis;
- políticas de aplicación;
- errores de aplicación.

Application no debe conocer implementaciones concretas.

Ejemplo:

```text
AnalyzeEmailUseCase depende de LinkAnalyzerPort, AttachmentScannerPort y SandboxBrowserPort.
```

No debe depender de:

```text
PlaywrightSandboxAdapter
OllamaAiAdapter
PdfMinerParser
FastAPI UploadFile
```

### 3. Infrastructure implementa detalles técnicos

Infrastructure contiene adaptadores concretos:

- API FastAPI;
- parser `.eml`;
- parser PDF;
- scanner Office;
- scanner YARA;
- OCR;
- Playwright;
- Ollama;
- resolución HTTP;
- filesystem;
- Docker/runtime config.

Infrastructure traduce entre el mundo externo y los contratos de Application.

### 4. Entrypoints no contienen negocio

Un entrypoint debe:

- validar entrada;
- construir comandos o DTOs;
- llamar un caso de uso;
- convertir resultado a respuesta;
- mapear errores.

No debe implementar reglas forenses directamente.

## Criterios para ubicar código

Cuando no esté claro dónde ubicar una pieza, usa estas preguntas:

1. ¿Representa una regla de negocio o concepto estable del análisis?
   - Sí: `Domain`.

2. ¿Orquesta una acción del sistema usando abstracciones?
   - Sí: `Application`.

3. ¿Depende de una librería, protocolo, framework, red, filesystem o proceso externo?
   - Sí: `Infrastructure`.

4. ¿Expone una API o interfaz al usuario/sistema exterior?
   - Sí: `Entrypoints` dentro de Infrastructure.

5. ¿Podría cambiarse la librería sin afectar el núcleo?
   - Si la respuesta debe ser sí, crea un puerto y un adaptador.

## Diseño de puertos

Crea un puerto cuando una capacidad:

- requiera IO;
- dependa de una librería externa;
- pueda sustituirse;
- deba mockearse en tests;
- represente una frontera con infraestructura;
- sea opcional por configuración.

Buenos candidatos a puerto:

- análisis de enlaces;
- sandbox de navegador;
- análisis IA;
- extracción OCR;
- escaneo YARA;
- parsing de adjuntos;
- resolución de redirecciones;
- consulta opcional a servicios externos.

Los puertos deben expresar capacidades del sistema, no nombres de herramientas concretas.

Correcto:

```python
class SandboxBrowserPort(Protocol):
    async def capture(self, url: str) -> SandboxResult:
        ...
```

Menos adecuado:

```python
class PlaywrightPort(Protocol):
    ...
```

## Diseño de adaptadores

Un adaptador debe:

- implementar un puerto;
- encapsular una herramienta concreta;
- gestionar errores técnicos;
- aplicar timeouts y límites;
- traducir datos externos a modelos internos;
- ser sustituible.

Ejemplos:

```text
PlaywrightSandboxAdapter implements SandboxBrowserPort
OllamaAiAnalysisAdapter implements AiAnalysisPort
TesseractOcrAdapter implements OcrPort
YaraScannerAdapter implements MalwareSignatureScannerPort
```

## Evaluación de nuevos módulos

Al añadir un módulo nuevo, decide:

1. qué concepto pertenece a Domain;
2. qué caso de uso o puerto pertenece a Application;
3. qué adaptador pertenece a Infrastructure;
4. qué entrypoint o endpoint lo invoca;
5. qué tests garantizan la frontera.

Ejemplo: módulo OCR.

```text
Domain: hallazgos de texto extraído e indicadores.
Application: OcrPort y caso de uso que solicita extracción.
Infrastructure: TesseractOcrAdapter.
Entrypoint: endpoint o flujo de análisis que invoca el caso de uso.
Tests: dominio puro + caso de uso con mock + adaptador con fixture controlada.
```

## Reglas para IA local

El ADR define IA local opcional con Ollama.

Arquitectónicamente:

- Ollama pertenece a Infrastructure.
- Application define un puerto de IA.
- Domain no conoce prompts, modelos ni SDKs.
- Si la IA está desactivada, el flujo debe continuar limpiamente.
- La IA complementa análisis deterministas, no los sustituye.

## Reglas para sandbox

Playwright/Chromium debe mantenerse como infraestructura aislada.

Arquitectónicamente:

- el dominio no abre navegadores;
- Application define el contrato;
- Infrastructure implementa Playwright;
- Docker Compose aísla el navegador;
- el caso de uso recibe resultados, no detalles de navegador.

## Reglas para Docker y servicios

Docker Compose debe reflejar límites arquitectónicos:

- `frontend`: UI React;
- `backend`: API y casos de uso;
- `playwright/browser`: sandbox aislado;
- `ollama`: IA local opcional si aplica.

No mezcles responsabilidades entre servicios. El backend orquesta, pero no debe convertir el contenedor de sandbox en parte del dominio.

## Señales de mala arquitectura

Revisa y corrige si detectas:

- imports de FastAPI en Domain;
- imports de Playwright/Ollama/YARA/OCR en Domain;
- endpoints con lógica forense extensa;
- casos de uso instanciando adaptadores concretos;
- tests que requieren red real para reglas de negocio;
- lógica de riesgo dispersa entre frontend y backend;
- DTOs externos usados como entidades de dominio sin criterio;
- ausencia de puertos para integraciones sustituibles;
- reglas de negocio dentro de Docker, scripts o entrypoints.

## Relación con otras skills

- Usa `phishshield-backend` para implementar detalles backend una vez decidida la arquitectura.
- Usa `phishshield-security-analysis` cuando el foco sea la lógica forense concreta.
- Usa `phishshield-testing` cuando el foco sea diseñar o corregir estrategia de pruebas.
- Usa `phishshield-devops` cuando exista y el foco sea CI/CD o despliegue.

Si una tarea mezcla arquitectura e implementación, empieza con esta skill y después aplica la skill técnica correspondiente.

## Criterios de rechazo

Rechaza o rediseña una propuesta si:

- requiere importar infraestructura desde `Domain`;
- hace que FastAPI, Playwright, Ollama, YARA, OCR o parsers sean dependencias del núcleo;
- impide sustituir una herramienta externa sin tocar casos de uso o dominio;
- mezcla análisis forense, transporte HTTP y presentación en el mismo componente;
- convierte Docker Compose o scripts en lugar de reglas de negocio;
- introduce red real en tests de reglas puras;
- contradice explícitamente `doc/ADR.md`.

## Checklist antes de aprobar una decisión arquitectónica

- [ ] La decisión respeta `doc/ADR.md`.
- [ ] Las dependencias apuntan hacia el dominio, no al revés.
- [ ] Domain no depende de frameworks ni SDKs.
- [ ] Application define puertos cuando cruza fronteras técnicas.
- [ ] Infrastructure implementa adaptadores sustituibles.
- [ ] Entrypoints no contienen negocio.
- [ ] Los módulos forenses son extensibles.
- [ ] El enfoque local/self-hosted y de privacidad se mantiene.
- [ ] Hay una estrategia de testing acorde al cambio.
- [ ] La solución evita complejidad accidental.

## Ejemplos de aplicación

### Propuesta de estructura inicial

Correcto:

```text
backend/
  src/
    phishshield/
      domain/
      application/
      infrastructure/
        entrypoints/
```

Incorrecto:

```text
backend/
  app.py
  services.py
  utils.py
```

si ahí se mezclan endpoints, parsers, reglas de riesgo y llamadas externas.

### Endpoint que llama directamente a Playwright

Diagnóstico:

```text
Rompe la separación de capas si el endpoint contiene lógica de sandbox.
```

Corrección:

```text
FastAPI -> UseCase -> SandboxBrowserPort -> PlaywrightSandboxAdapter
```

### Detección de homóglifos

Si es algoritmo puro:

```text
Domain
```

Si depende de librerías externas o IO:

```text
Infrastructure detrás de un puerto, manteniendo tipos y reglas estables en Domain/Application.
```

## Prompts de evaluación sugeridos

Usa estos prompts para probar si la skill guía bien al agente:

1. `Propón la estructura inicial de carpetas para PhishShield siguiendo el ADR.`
2. `Añade un nuevo módulo OCR con Tesseract sin romper la arquitectura hexagonal.`
3. `Revisa esta propuesta: el endpoint FastAPI abre Playwright directamente para capturar screenshots.`
4. `Diseña cómo integrar Ollama opcionalmente respetando puertos y adaptadores.`
5. `Decide dónde ubicar la detección de homóglifos y justifica la capa.`

Una buena respuesta debe consultar el ADR, justificar capas, definir puertos/adaptadores cuando corresponda y detectar acoplamientos indebidos.