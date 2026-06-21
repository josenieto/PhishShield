# Skills de PhishShield

Esta carpeta contiene las skills específicas del proyecto **PhishShield**.

La skill oficial `skill-creator` de Anthropic ya está instalada en el proyecto mediante el CLI `skills` y queda disponible en:

```text
.agents/skills/skill-creator/
```

Comando oficial utilizado:

```bash
npx skills add anthropics/skills --skill skill-creator --yes
```

`skill-creator` debe usarse como herramienta de apoyo para crear, mejorar, evaluar y mantener las skills propias de este repositorio.

## Regla obligatoria para crear skills

Toda nueva skill de PhishShield debe crearse siguiendo como modelo la skill oficial:

```text
.agents/skills/skill-creator/
```

Flujo mínimo obligatorio:

1. capturar la intención de la skill,
2. definir cuándo debe activarse,
3. redactar `SKILL.md` con frontmatter `name` y `description`,
4. mantener la skill accionable, específica y alineada con PhishShield,
5. crear evals iniciales cuando la skill sea verificable,
6. revisar alineación con `AGENT.md` y `doc/ADR.md`,
7. actualizar este índice.

No se deben crear skills manualmente sin seguir este proceso.

## Referencias obligatorias

Toda skill de PhishShield debe respetar:

- `AGENT.md`
- `doc/ADR.md`

Si una skill propone una práctica que contradice el ADR, prevalece el ADR.

## Convenciones

Cada skill propia del proyecto debe vivir en su propia carpeta:

```text
.skills/
  nombre-de-la-skill/
    SKILL.md
```

El archivo `SKILL.md` se creará más adelante con `skill-creator` y deberá incluir:

- frontmatter con `name` y `description`,
- propósito de la skill,
- cuándo debe usarse,
- reglas específicas para el agente,
- referencias internas relevantes,
- criterios de calidad o checklist.

## Skills previstas

Las carpetas iniciales quedan preparadas, pero las skills todavía no están definidas.  
Cada `SKILL.md` se creará más adelante usando `skill-creator`.

- `phishshield-architecture`  
  Para guiar cambios arquitectónicos, separación de capas, decisiones sobre puertos/adaptadores y alineación con `doc/ADR.md`.  
  Estado: definida en `.skills/phishshield-architecture/SKILL.md` con evals iniciales en `.skills/phishshield-architecture/evals/evals.json`.

- `phishshield-backend`  
  Para guiar trabajo en Python, FastAPI, casos de uso, contratos, validación y adaptadores backend.  
  Estado: definida en `.skills/phishshield-backend/SKILL.md` con evals iniciales en `.skills/phishshield-backend/evals/evals.json`.

- `phishshield-frontend`  
  Para guiar trabajo en React, TypeScript, Vite y visualización del panel forense.

- `phishshield-security-analysis`  
  Para guiar módulos de análisis de phishing: cabeceras, enlaces, homóglifos, adjuntos, OCR, EXIF, YARA y sandbox.

- `phishshield-testing`  
  Para guiar pruebas unitarias, integración, mocks, Pytest y validación de módulos forenses.

## Nota

No rellenar las skills manualmente hasta que se diseñen con `skill-creator`.

Skills creadas con este flujo:

- `phishshield-backend`
- `phishshield-architecture`
