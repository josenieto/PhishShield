# AGENT.md

## Propósito

Este archivo orienta a cualquier agente IA que trabaje sobre este repositorio.  
Su función es servir como guía operativa breve: qué proyecto es, cómo está estructurado y qué reglas básicas debe respetar cualquier cambio.

Este documento **no sustituye** al diseño arquitectónico oficial. La referencia principal es:

- `doc/ADR.md`

Si existe conflicto entre este archivo y el ADR, **prevalece el ADR**.

---

## Proyecto

**PhishShield** es una herramienta defensiva, local (*self-hosted*) y de código abierto para el análisis forense de correos electrónicos `.eml`.

Su objetivo es detectar indicadores de phishing modernos sin depender de servicios cloud de terceros para el análisis principal, preservando privacidad, trazabilidad y extensibilidad técnica.

El sistema analiza, entre otros aspectos:

- cabeceras e identidad del correo,
- enlaces y ataques homóglifos,
- sandbox de navegación segura,
- archivos adjuntos PDF y Office,
- OCR y metadatos de imágenes,
- explicaciones asistidas por IA local cuando esté habilitado.

---

## Referencia arquitectónica obligatoria

Antes de modificar código, leer:

- `doc/ADR.md`

El proyecto sigue una **Arquitectura Hexagonal** dentro de un **monolito modular**.  
Las decisiones de diseño y los límites entre capas deben respetarse.

### Capas esperadas

- **Domain**  
  Modelos puros y lógica de negocio sin dependencias de infraestructura.

- **Application**  
  Casos de uso y puertos que definen contratos.

- **Infrastructure**  
  Adaptadores técnicos, frameworks, parsers, integraciones y entrypoints.

### Regla principal

Un agente IA **no debe introducir dependencias de infraestructura dentro del dominio**.  
Toda integración externa debe quedar encapsulada detrás de puertos y adaptadores.

---

## Stack principal

Según el ADR, la base tecnológica del proyecto es:

- **Backend:** Python + FastAPI
- **Frontend:** React + TypeScript + Vite
- **Despliegue:** Docker + Docker Compose
- **Sandbox de navegación:** Playwright en contenedor aislado
- **IA local opcional:** Ollama
- **Testing:** Pytest
- **CI/CD:** GitHub Actions

---

## Módulos funcionales del sistema

Los módulos principales descritos en el ADR son:

1. **Cabeceras e identidad**
   - extracción de remitente, asunto y validaciones SPF/DKIM/DMARC.

2. **Enlaces y ataques homóglifos**
   - detección de IDN, normalización Punycode y resolución pasiva de URLs acortadas.

3. **Sandbox de navegación segura**
   - captura visual y extracción de título mediante navegador aislado.

4. **Adjuntos**
   - análisis de PDFs, Office, macros, hashes y reglas YARA.

5. **Imágenes**
   - OCR con Tesseract y extracción de metadatos EXIF.

6. **IA local**
   - análisis complementario de ingeniería social y explicación en lenguaje natural, controlado por configuración.

---

## Reglas de trabajo para agentes IA

### 1. Revisar el ADR antes de cambios relevantes
Si el cambio afecta arquitectura, contratos, módulos o despliegue, consultar primero `doc/ADR.md`.

### 2. Respetar la separación por capas
- No mover lógica de negocio a adaptadores.
- No contaminar el dominio con SDKs, frameworks o detalles de red.
- Mantener casos de uso coordinando puertos, no implementaciones concretas.

### 3. Priorizar seguridad y privacidad
PhishShield es una herramienta defensiva.  
Cualquier cambio debe evitar exponer datos sensibles innecesariamente y mantener el enfoque local/self-hosted del proyecto.

### 4. Mantener tipado y validación
Usar modelos y validaciones consistentes con el stack del proyecto, especialmente en backend y contratos de API.

### 5. Favorecer extensibilidad
Las nuevas integraciones deben diseñarse para poder sustituirse sin romper el núcleo del sistema.

### 6. Añadir o ajustar pruebas
Si un cambio modifica comportamiento observable, añadir o actualizar tests en la capa adecuada.

### 7. No introducir complejidad gratuita
Preferir soluciones claras, modulares y coherentes con el ADR existente.

---

## Qué debe hacer un agente antes de editar

Checklist mínima:

- leer `doc/ADR.md`,
- identificar la capa afectada,
- localizar el contrato o módulo impactado,
- verificar si el cambio requiere tests,
- mantener coherencia con Docker, FastAPI, React y adaptadores existentes.

---

## Skills futuras

Las skills específicas de PhishShield se organizarán en:

- `.skills/`

La skill oficial `skill-creator` de Anthropic está instalada en el proyecto mediante el CLI `skills` y queda disponible en:

- `.agents/skills/skill-creator/`

Comando utilizado:

```bash
npx skills add anthropics/skills --skill skill-creator --yes
```

Se usará para crear, mejorar y evaluar las skills propias de PhishShield.

### Skills previstas

Las carpetas iniciales están preparadas, pero las skills se definirán más adelante con `skill-creator`.

- `phishshield-architecture`  
  Cambios arquitectónicos alineados con el ADR.

- `phishshield-backend`  
  Trabajo en FastAPI, casos de uso, puertos y adaptadores.

- `phishshield-frontend`  
  Trabajo en React, TypeScript, Vite y UI del panel forense.

- `phishshield-security-analysis`  
  Módulos de análisis de enlaces, adjuntos, OCR e indicadores forenses.

- `phishshield-testing`  
  Pruebas unitarias e integración con Pytest y mocks.

> Hasta que estas skills existan, usar este archivo, `.skills/README.md` y `doc/ADR.md` como referencia principal.

---

## Regla final

Si una decisión no está clara:

1. seguir primero `doc/ADR.md`,
2. preservar la arquitectura hexagonal,
3. priorizar seguridad, privacidad y mantenibilidad.