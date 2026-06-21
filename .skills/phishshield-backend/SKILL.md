---
name: phishshield-backend
description: Guía especializada para trabajar en el backend de PhishShield. Usa esta skill siempre que el usuario pida crear, modificar o revisar código Python/FastAPI, casos de uso, puertos, adaptadores, modelos Pydantic, endpoints API, parsers, módulos forenses backend, integración con Playwright/Ollama/YARA/OCR, Docker del backend o tests Pytest. También úsala cuando una tarea mencione arquitectura hexagonal, Domain/Application/Infrastructure, contratos, DTOs, validación o análisis de correos .eml desde backend, aunque el usuario no diga explícitamente "backend". Si la tarea implica decidir límites de capas o arquitectura general, aplica primero phishshield-architecture y después vuelve a esta skill para la implementación backend.
---

# phishshield-backend

## Propósito

Ayudar a agentes IA a desarrollar el backend de **PhishShield** respetando el ADR del proyecto y evitando una implementación plana acoplada a FastAPI.

PhishShield es una herramienta defensiva local/self-hosted para análisis forense de correos `.eml`. El backend concentra reglas de análisis, orquestación de casos de uso, adaptadores técnicos y entrypoints API. Por eso la separación entre dominio, aplicación e infraestructura es crítica: permite cambiar parsers, sandbox, IA local o frameworks sin romper el núcleo del sistema.

## Referencias que debes consultar

Antes de realizar cambios backend relevantes, lee:

- `AGENT.md`
- `doc/ADR.md`
- `.skills/README.md`

Si hay conflicto entre esta skill y `doc/ADR.md`, prevalece `doc/ADR.md`.

## Proceso de trabajo

Cuando esta skill se active:

1. Identifica si la tarea es implementación backend o decisión arquitectónica.
2. Si hay dudas de capas, límites o dependencias, aplica primero `phishshield-architecture`.
3. Localiza la capa afectada: `Domain`, `Application`, `Infrastructure` o `Entrypoints`.
4. Diseña contratos antes que adaptadores cuando haya IO, red, sandbox, IA, OCR, YARA o parsers externos.
5. Mantén FastAPI como entrypoint fino.
6. Añade o ajusta tests si cambia comportamiento.
7. Cierra con una comprobación breve del checklist backend.

El objetivo es producir backend implementable sin degradar la arquitectura hexagonal.

## Cuándo usar esta skill

Usa esta skill para tareas relacionadas con:

- Python y FastAPI.
- Diseño de endpoints.
- Casos de uso de aplicación.
- Puertos y adaptadores.
- Modelos de dominio.
- DTOs y validación con Pydantic.
- Parsing de `.eml`, PDF, Office, imágenes o URLs.
- Módulos SPF/DKIM/DMARC.
- Detección de homóglifos, Punycode o enlaces acortados.
- Integración backend con Playwright, Ollama, Tesseract, YARA u oletools.
- Manejo de errores backend.
- Tests unitarios o de integración con Pytest.
- Dockerización del servicio backend.

No uses esta skill para tareas puramente frontend salvo que impliquen contratos de API o modelos compartidos.

## Resultado esperado de una respuesta

Cuando respondas usando esta skill, estructura la solución así cuando sea aplicable:

```text
1. Capa afectada
2. Diseño propuesto
3. Contratos o modelos necesarios
4. Adaptadores o endpoints implicados
5. Manejo de errores, límites y seguridad
6. Tests Pytest recomendados
7. Riesgos arquitectónicos evitados
```

Si la tarea requiere una decisión arquitectónica previa, indícalo y deriva primero a `phishshield-architecture`.

## Modelo mental obligatorio

Trabaja con esta dirección de dependencias:

```text
Domain  <-  Application  <-  Infrastructure / Entrypoints
```

Interpreta las capas así:

- **Domain**: modelos puros y lógica forense libre de frameworks.
- **Application**: casos de uso y puertos que orquestan el análisis.
- **Infrastructure**: adaptadores concretos, FastAPI, parsers, Playwright, Ollama, YARA, OCR, red, filesystem y Docker.

La razón es mantener estable el núcleo del análisis aunque cambien librerías, frameworks o servicios externos.

## Reglas para Domain

En `Domain`:

- Define modelos puros como `Email`, `ResultadoAnalisis`, artefactos, indicadores, adjuntos o hallazgos.
- Implementa lógica determinista pura cuando sea posible, por ejemplo normalización, clasificación de indicadores o detección de homóglifos.
- No importes FastAPI.
- No importes SDKs externos.
- No hagas IO de filesystem, red, base de datos ni procesos.
- No llames a Playwright, Ollama, Tesseract, oletools, YARA ni librerías de infraestructura directamente.
- No dependas de variables de entorno.

Si una función necesita red, navegador, OCR, IA o parsing con librería externa, probablemente pertenece a un adaptador de infraestructura detrás de un puerto.

## Reglas para Application

En `Application`:

- Define casos de uso que representen acciones del sistema, por ejemplo analizar un `.eml`, extraer artefactos, evaluar enlaces o generar un reporte.
- Define puertos como interfaces abstractas para capacidades externas.
- Coordina módulos, pero no implementes detalles técnicos concretos.
- Depende del dominio y de abstracciones, no de adaptadores.
- Mantén las políticas de orquestación visibles y testeables.

Ejemplos de puertos razonables:

```python
class LinkAnalyzerPort(Protocol):
    def analyze(self, links: list[str]) -> list[LinkFinding]:
        ...
```

```python
class SandboxBrowserPort(Protocol):
    async def capture(self, url: str) -> SandboxResult:
        ...
```

```python
class AiAnalysisPort(Protocol):
    async def explain(self, analysis: AnalysisResult) -> AiExplanation:
        ...
```

## Reglas para Infrastructure

En `Infrastructure`:

- Implementa adaptadores concretos de los puertos.
- Encapsula FastAPI, Playwright, Ollama, OCR, YARA, oletools, pdfminer, PyPDF2, idna, peticiones HTTP y filesystem.
- Traduce errores técnicos a errores controlados de aplicación.
- Aplica timeouts y límites de recursos.
- Trata toda entrada como hostil: `.eml`, adjuntos, URLs, PDFs, Office e imágenes.
- Evita efectos secundarios no explícitos.

Ejemplos de adaptadores:

- `FastApiEntrypoint`
- `OllamaAiAnalysisAdapter`
- `PlaywrightSandboxAdapter`
- `PdfAttachmentParserAdapter`
- `OfficeMacroScannerAdapter`
- `YaraScannerAdapter`
- `TesseractOcrAdapter`
- `HttpRedirectResolverAdapter`

## Reglas para FastAPI

FastAPI debe actuar como entrypoint, no como núcleo de negocio.

En endpoints:

- Valida entrada.
- Convierte requests a comandos o DTOs de aplicación.
- Llama a casos de uso.
- Convierte resultados a responses.
- Maneja errores HTTP.
- No implementes análisis forense directamente en el endpoint.
- No mezcles lógica de dominio con dependencias de FastAPI.

Patrón recomendado:

```text
router -> request schema -> use case -> domain/application result -> response schema
```

## Reglas para Pydantic

Usa Pydantic para contratos de entrada/salida y validación de bordes.

Distingue:

- modelos de dominio: expresan conceptos de negocio;
- DTOs o schemas Pydantic: expresan contratos externos;
- comandos de aplicación: expresan intención de un caso de uso.

Evita que los modelos Pydantic de API sustituyan automáticamente al dominio si eso acopla la lógica al framework.

## Reglas para módulos forenses backend

PhishShield analiza artefactos potencialmente maliciosos. Actúa con enfoque defensivo.

### Correos `.eml`

- Parsear de forma robusta.
- No confiar en cabeceras declaradas.
- Extraer remitente, asunto, cuerpo, adjuntos y enlaces sin ejecutar contenido.

### Cabeceras

- Mantener SPF, DKIM y DMARC como resultados verificables.
- Separar parsing de cabeceras de interpretación del riesgo.

### Enlaces

- Normalizar dominios.
- Detectar IDN/homóglifos.
- Convertir a Punycode cuando aplique.
- Resolver acortadores con peticiones pasivas y timeouts.
- Evitar seguir redirecciones sin límites.

### Sandbox

- Usar Playwright solo desde infraestructura.
- Ejecutar navegador aislado.
- Bloquear descargas y persistencia.
- Aplicar timeouts.
- Capturar screenshot y título sin exponer el host.

### Adjuntos

- Tratar PDFs, Office e imágenes como entrada hostil.
- Calcular hash SHA-256 cuando aplique.
- Extraer enlaces de PDFs sin ejecutar contenido.
- Detectar macros con herramientas especializadas.
- Ejecutar YARA de forma controlada.

### IA local

- La IA es opcional mediante configuración.
- Ollama pertenece a infraestructura.
- La IA complementa resultados deterministas; no debe ser la única fuente de verdad.
- Si `USE_AI_ANALYSIS=false`, el caso de uso debe continuar limpiamente sin IA.

## Testing esperado

Cuando cambies comportamiento backend, añade o actualiza tests.

Usa Pytest con esta estrategia:

- Tests unitarios para dominio y algoritmos puros.
- Tests de aplicación usando mocks de puertos.
- Tests de adaptadores con fixtures controladas.
- Tests de integración solo cuando sea necesario.
- No dependas de red real en tests unitarios.
- No dependas de servicios externos reales para validar reglas de negocio.
- Usa fixtures de `.eml`, URLs, cabeceras y adjuntos sintéticos.

Casos que merecen tests:

- homóglifos y Punycode;
- SPF/DKIM/DMARC parseados;
- extracción de enlaces;
- PDFs con enlaces embebidos;
- Office con macros simuladas;
- fallos de adaptadores;
- IA desactivada;
- timeouts de sandbox o red.

## Criterios de rechazo

Rechaza o rediseña una solución backend si:

- implementa análisis forense directamente en un endpoint FastAPI;
- importa FastAPI, Playwright, Ollama, OCR, YARA, HTTP o filesystem desde `Domain`;
- instancia adaptadores concretos dentro de casos de uso sin inyección;
- añade red real a tests unitarios;
- usa IA local como única fuente de verdad del análisis;
- mezcla DTOs de API con entidades de dominio sin justificación;
- ignora timeouts, límites o entrada hostil en adaptadores.

## Checklist antes de finalizar una tarea backend

Antes de entregar cambios:

- [ ] He leído `doc/ADR.md` si la tarea afecta arquitectura o módulos principales.
- [ ] La capa Domain no importa infraestructura.
- [ ] Los casos de uso dependen de puertos, no de adaptadores concretos.
- [ ] FastAPI solo actúa como entrypoint.
- [ ] Las integraciones externas están encapsuladas en Infrastructure.
- [ ] La entrada hostil se valida y limita.
- [ ] Hay manejo de errores y timeouts donde corresponde.
- [ ] Se añadieron o actualizaron tests si cambió comportamiento.
- [ ] La solución mantiene el enfoque local/self-hosted y de privacidad del ADR.

## Ejemplos de aplicación

### Endpoint para subir `.eml`

Correcto:

```text
FastAPI router recibe archivo -> construye comando -> llama a AnalyzeEmailUseCase -> devuelve response.
```

Incorrecto:

```text
FastAPI router parsea cabeceras, resuelve enlaces, llama Playwright y calcula riesgo directamente.
```

### Nuevo analizador de enlaces

Correcto:

```text
Application define LinkAnalyzerPort.
Infrastructure implementa IdnaLinkAnalyzerAdapter o HttpRedirectResolverAdapter.
Domain contiene tipos y reglas puras.
```

Incorrecto:

```text
Domain importa requests/httpx para resolver redirecciones.
```

### Integración con Ollama

Correcto:

```text
Application define AiAnalysisPort.
Infrastructure implementa OllamaAiAnalysisAdapter.
El caso de uso omite IA limpiamente si está desactivada.
```

Incorrecto:

```text
El dominio llama directamente a la librería ollama.
```

## Prompts de evaluación sugeridos

Usa estos prompts para probar si la skill guía bien al agente:

1. `Crea un endpoint FastAPI para subir un archivo .eml y lanzar el análisis forense completo.`
2. `Implementa un puerto y un adaptador para resolver URLs acortadas sin romper la arquitectura hexagonal.`
3. `Añade tests Pytest para la detección de dominios homóglifos y conversión a Punycode.`
4. `Integra Ollama como análisis IA opcional controlado por USE_AI_ANALYSIS.`

Una buena respuesta debe mantener la separación de capas, proponer puertos/adaptadores y añadir pruebas cuando cambie comportamiento.