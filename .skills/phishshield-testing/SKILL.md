---
name: phishshield-testing
description: Guía especializada para testing y TDD en PhishShield. Usa esta skill siempre que el usuario pida crear, modificar o revisar tests, aplicar TDD, diseñar casos Pytest, probar funciones puras de dominio, validar casos de uso, mockear puertos, probar adaptadores, revisar cobertura o implementar una nueva función con enfoque Red-Green-Refactor. Úsala también cuando el usuario pida implementar lógica nueva, aunque no mencione tests, porque en PhishShield el desarrollo debe empezar por pruebas cuando el comportamiento sea verificable.
---

# phishshield-testing

## Propósito

Guiar a agentes IA para desarrollar PhishShield con una disciplina de testing clara, incremental y compatible con arquitectura hexagonal.

Esta skill existe para evitar implementar lógica primero y probar después de forma superficial. En especial, debe usarse antes de empezar las primeras funciones puras de `domain`.

El objetivo es trabajar en ciclos pequeños:

```text
Red -> Green -> Refactor
```

Y aplicar patrones clásicos de TDD cuando correspondan:

- Fake it till you make it
- Triangulation
- Obvious implementation
- Arrange / Act / Assert
- Given / When / Then
- Make it work, make it right, make it fast

## Referencias que debes consultar

Antes de diseñar tests relevantes, lee:

- `AGENT.md`
- `doc/ADR.md`
- `doc/DOMAIN_PURE_FUNCTIONS_PLAN.md`
- `.skills/README.md`

Si la tarea afecta arquitectura o límites entre capas, usa primero `phishshield-architecture`.

Si la tarea afecta implementación backend, combina esta skill con `phishshield-backend`.

## Cuándo usar esta skill

Usa esta skill cuando la tarea implique:

- crear tests;
- aplicar TDD;
- implementar una función nueva;
- modificar comportamiento existente;
- probar funciones puras de dominio;
- diseñar tests Pytest;
- crear fixtures;
- revisar tests frágiles;
- probar casos de uso de Application;
- mockear puertos;
- probar adaptadores de Infrastructure;
- validar errores, límites o entradas hostiles;
- refactorizar con seguridad;
- añadir cobertura a módulos forenses.

También debe activarse cuando el usuario diga algo como:

```text
vamos a implementar esta función
```

porque el flujo esperado del proyecto es empezar por el comportamiento esperado y los tests.

## Proceso TDD obligatorio

Cuando el comportamiento sea verificable, trabaja así:

1. Define el comportamiento esperado en lenguaje claro.
2. Escribe el test más pequeño que falle.
3. Ejecuta el test o indica claramente que debe ejecutarse.
4. Confirma el estado **Red**.
5. Implementa lo mínimo para pasar.
6. Ejecuta el test afectado.
7. Confirma el estado **Green**.
8. Refactoriza solo si mejora claridad sin cambiar comportamiento.
9. Ejecuta de nuevo los tests afectados.
10. Repite con el siguiente caso.

No agrupes demasiados casos en una sola iteración. Mantén cambios pequeños.

## Resultado esperado de una respuesta

Cuando respondas usando esta skill, estructura la respuesta así cuando sea aplicable:

```text
1. Behaviour under test
2. Test scope
3. Red test to add
4. Minimal implementation needed for Green
5. Refactor considerations
6. Test command
7. Next test case
```

Si todavía no se debe implementar código, entrega solo el plan de tests.

## Patrones de TDD

### Red-Green-Refactor

Usa este ciclo por defecto.

```text
Red: test falla porque el comportamiento no existe.
Green: implementación mínima para pasar.
Refactor: limpieza sin cambiar comportamiento.
```

### Fake it till you make it

Útil para la primera prueba de una función.

Ejemplo:

```python
def contains_invisible_chars(text: str) -> bool:
    return True
```

Solo es aceptable como paso temporal para pasar un primer test muy estrecho. Debe evolucionar con más tests.

### Triangulation

Añade nuevos casos para obligar a generalizar.

Ejemplo:

1. detecta `\u200b`;
2. detecta `\u200c`;
3. no detecta texto limpio;
4. maneja string vacío.

### Obvious implementation

Si la solución es trivial y el riesgo es bajo, implementa directamente la versión clara después de escribir tests.

### Arrange / Act / Assert

Estructura recomendada para Pytest:

```python
def test_should_detect_zero_width_space():
    # Arrange
    text = "paypa\u200bl.com"

    # Act
    result = contains_invisible_chars(text)

    # Assert
    assert result is True
```

### Given / When / Then

Útil cuando el comportamiento expresa una regla de negocio:

```python
def test_given_clean_text_when_checking_invisible_chars_then_returns_false():
    text = "paypal.com"

    result = contains_invisible_chars(text)

    assert result is False
```

## Reglas para tests de Domain

Los tests de `domain` deben ser:

- unitarios;
- rápidos;
- deterministas;
- sin red;
- sin filesystem;
- sin FastAPI;
- sin Playwright;
- sin Ollama;
- sin YARA;
- sin OCR;
- sin parsers externos;
- sin mocks complejos.

Si necesitas mocks complejos para probar una función de dominio, probablemente esa lógica no pertenece al dominio.

## Reglas para tests de Application

Los tests de `application` deben:

- probar casos de uso;
- usar fakes o mocks de puertos;
- verificar orquestación;
- no depender de adaptadores reales;
- cubrir errores de aplicación;
- cubrir flujos opcionales como IA desactivada.

Ejemplo:

```text
AnalyzeEmailUseCase -> mocked EmailParserPort + mocked LinkAnalyzerPort
```

## Reglas para tests de Infrastructure

Los tests de `infrastructure` pueden usar fixtures y dobles de prueba, pero deben controlar efectos externos.

Para adaptadores:

- mockear red;
- usar fixtures locales controladas;
- aplicar timeouts;
- evitar servicios reales en unit tests;
- mover pruebas reales a integración si son imprescindibles.

Ejemplos:

- no resolver URLs reales en unit tests;
- no abrir Chromium real en unit tests de dominio;
- no llamar Ollama real en tests unitarios;
- no depender de Tesseract real salvo test de integración explícito.

## Reglas para tests de Entrypoints / FastAPI

Los tests de API deben:

- verificar validación de request;
- verificar códigos HTTP;
- verificar serialización de respuesta;
- mockear casos de uso;
- no ejecutar análisis forense completo desde el endpoint.

FastAPI debe probarse como borde del sistema, no como lugar de reglas de negocio.

## Naming recomendado

Usa nombres de test orientados a comportamiento.

Correcto:

```python
def test_should_strip_zero_width_space_from_text():
    ...
```

```python
def test_should_return_false_when_text_has_no_invisible_chars():
    ...
```

Incorrecto:

```python
def test_regex_works():
    ...
```

```python
def test_internal_loop():
    ...
```

## Organización sugerida de tests

Cuando se cree la estructura de tests, usar:

```text
tests/
  unit/
    domain/
      services/
    application/
  integration/
    infrastructure/
    entrypoints/
  fixtures/
```

Para la primera función pura de dominio:

```text
tests/unit/domain/services/text_normalization/test_invisible_characters.py
```

## Primer caso recomendado para PhishShield

Primera iteración sugerida:

```text
Text normalization - invisible characters
```

Funciones:

```python
contains_invisible_chars(text: str) -> bool
strip_invisible_chars(text: str) -> str
```

Tests iniciales:

- detects zero-width space;
- detects zero-width non-joiner;
- detects zero-width joiner;
- returns false for clean text;
- strips invisible chars without changing visible text;
- handles empty string.

## Criterios de rechazo

Rechaza o rediseña un enfoque de testing si:

- implementa código antes de definir comportamiento;
- añade tests que dependen de red real sin ser integración explícita;
- prueba detalles internos en vez de comportamiento;
- usa Playwright/Ollama/YARA/OCR en tests unitarios de dominio;
- mezcla tests de dominio con FastAPI;
- necesita mocks complejos para una función pura;
- no cubre casos límite básicos;
- no verifica errores o entradas hostiles cuando aplican.

## Checklist antes de finalizar una tarea de testing

- [ ] El comportamiento esperado está claro.
- [ ] Hay al menos un test que falla antes de implementar cuando se aplica TDD.
- [ ] Los tests son deterministas.
- [ ] Los tests están en la capa correcta.
- [ ] Los tests no dependen de infraestructura real salvo integración explícita.
- [ ] Los nombres de tests describen comportamiento.
- [ ] Se cubren casos normales y límites.
- [ ] Se ejecutaron los tests afectados o se indicó el comando exacto.
- [ ] La implementación mínima no rompe arquitectura hexagonal.

## Relación con otras skills

- Usa `phishshield-architecture` antes si hay dudas de capa, dependencia o frontera.
- Usa `phishshield-backend` junto con esta skill para endpoints, casos de uso, puertos o adaptadores backend.
- Usa `phishshield-security-analysis` cuando exista y el foco sea una regla forense concreta.
- Usa esta skill siempre que haya comportamiento verificable.

## Prompts de evaluación sugeridos

Usa estos prompts para comprobar si la skill guía bien al agente:

1. `Crea tests TDD para contains_invisible_chars antes de implementar la función.`
2. `Diseña los tests unitarios para strip_invisible_chars siguiendo Red-Green-Refactor.`
3. `Queremos probar un adaptador que resuelve URLs acortadas sin usar red real.`
4. `Revisa estos tests porque dependen de Playwright en una función de dominio.`
5. `Añade una nueva regla de riesgo y diseña primero los tests Pytest.`

Una buena respuesta debe empezar por comportamiento, proponer tests pequeños, respetar la capa correspondiente y evitar dependencias externas en unit tests de dominio.