# Domain Pure Functions Plan

## Propósito

Este documento define un backlog técnico e incremental de funciones puras candidatas para la capa `domain` de PhishShield.

No es un plan para implementar todo de golpe.  
Su objetivo es mantener contexto, agrupar funciones relacionadas y permitir avanzar de forma controlada:

```text
función pura de dominio
        ↓
unit test
        ↓
posible value object / entity
        ↓
caso de uso de Application, si aplica
        ↓
puerto / adaptador de Infrastructure, si aplica
        ↓
entrypoint/API, si aplica
```

Cada grupo funcional debe trabajarse de forma aislada, con commits pequeños y verificables.

---

## Principios de pureza del dominio

Una función puede vivir en `src/domain/` si cumple estas condiciones:

- recibe valores simples o modelos de dominio;
- devuelve valores simples o modelos de dominio;
- no hace IO;
- no lee ni escribe archivos;
- no llama a red;
- no consulta DNS;
- no usa FastAPI;
- no usa Playwright;
- no usa Ollama;
- no usa YARA;
- no usa Tesseract/OCR;
- no usa parsers externos de PDF, Office o `.eml`;
- no depende de variables de entorno;
- no depende de configuración global mutable;
- produce siempre la misma salida para la misma entrada;
- puede testearse con Pytest sin mocks complejos.

Si una función necesita red, filesystem, procesos externos, SDKs, navegador, IA, OCR, YARA o librerías de parsing, no pertenece directamente a `domain`. En ese caso debe moverse a `infrastructure` detrás de un puerto definido en `application`.

---

## Flujo de trabajo por grupo

Para cada grupo funcional se seguirá este flujo:

1. Seleccionar una función o un subgrupo pequeño.
2. Definir contrato:
   - nombre,
   - firma,
   - entradas,
   - salida esperada,
   - errores o casos límite.
3. Crear unit tests.
4. Implementar la función pura.
5. Ejecutar tests.
6. Revisar si aparece necesidad real de:
   - value object,
   - entity,
   - enum,
   - domain error.
7. Solo después, decidir si se sube una capa:
   - `application/use_cases`,
   - `application/ports`,
   - `infrastructure/adapters`,
   - `infrastructure/entrypoints/api`.
8. Hacer commit pequeño.

---

## Estado general

| Grupo | Estado | Prioridad |
|---|---:|---:|
| Text normalization | Pending | Alta |
| Homoglyphs / suspicious Unicode | Pending | Alta |
| Domain analysis | Pending | Alta |
| URL analysis | Pending | Alta |
| Attachment analysis | Pending | Alta |
| Authentication result analysis | Pending | Media |
| Risk scoring | Pending | Alta |
| Social engineering heuristics | Pending | Media |
| Finding analysis | Pending | Media |
| Hash analysis | Pending | Media |

---

# 1. Text normalization

## Propósito

Funciones puras para normalizar texto antes de aplicar reglas de análisis.  
Son útiles para asuntos, remitentes, dominios visuales, texto de cuerpo, texto extraído por OCR y nombres de archivo.

## Ubicación sugerida

```text
src/domain/services/text_normalization/
```

## Funciones candidatas

### `normalize_whitespace`

```python
normalize_whitespace(text: str) -> str
```

Normaliza espacios, tabuladores y saltos de línea repetidos.

Comportamiento esperado:

- colapsa espacios consecutivos;
- elimina espacios iniciales/finales;
- mantiene el contenido textual significativo.

Tests sugeridos:

- texto con espacios múltiples;
- texto con tabs;
- texto con saltos de línea repetidos;
- string vacío;
- string ya normalizado.

---

### `normalize_unicode_text`

```python
normalize_unicode_text(text: str) -> str
```

Aplica normalización Unicode estándar usando librería estándar de Python, por ejemplo `unicodedata`.

Comportamiento esperado:

- normaliza formas Unicode equivalentes;
- mantiene texto legible;
- no elimina caracteres por sí misma.

Tests sugeridos:

- caracteres compuestos;
- caracteres descompuestos;
- texto ASCII;
- texto con acentos;
- string vacío.

---

### `strip_invisible_chars`

```python
strip_invisible_chars(text: str) -> str
```

Elimina caracteres invisibles o de control que puedan ocultar contenido malicioso.

Comportamiento esperado:

- elimina zero-width spaces;
- elimina caracteres de control no imprimibles;
- conserva texto visible.

Tests sugeridos:

- texto con `\u200b`;
- texto con `\u200c`;
- texto con caracteres de control;
- texto sin caracteres invisibles;
- string vacío.

---

### `contains_invisible_chars`

```python
contains_invisible_chars(text: str) -> bool
```

Detecta si un texto contiene caracteres invisibles sospechosos.

Comportamiento esperado:

- devuelve `True` si encuentra caracteres invisibles;
- devuelve `False` en texto normal.

Tests sugeridos:

- texto con zero-width space;
- texto con caracteres de control;
- texto limpio;
- string vacío.

## Fuera del dominio

No debe:

- leer archivos;
- parsear `.eml`;
- ejecutar OCR;
- llamar librerías externas;
- modificar encoding de archivos en disco.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede usar estas funciones dentro de un caso de uso de análisis textual;
- `infrastructure` puede aportar texto extraído desde `.eml`, OCR, PDF u Office.

---

# 2. Homoglyphs / suspicious Unicode

## Propósito

Detectar señales puras de Unicode sospechoso, mezcla de alfabetos y caracteres visualmente confundibles.

Este grupo es crítico para detectar ataques homóglifos en dominios, remitentes, asuntos y texto visible.

## Ubicación sugerida

```text
src/domain/services/homoglyphs/
```

## Funciones candidatas

### `detect_unicode_scripts`

```python
detect_unicode_scripts(text: str) -> set[str]
```

Detecta scripts Unicode presentes en el texto.

Ejemplos de salida:

```text
{"LATIN"}
{"LATIN", "CYRILLIC"}
{"GREEK"}
```

Tests sugeridos:

- texto latino;
- texto cirílico;
- texto griego;
- texto mixto latino/cirílico;
- números y símbolos;
- string vacío.

---

### `contains_mixed_scripts`

```python
contains_mixed_scripts(text: str) -> bool
```

Detecta mezcla sospechosa de alfabetos.

Comportamiento esperado:

- `False` para texto latino normal;
- `True` para mezclas tipo latino + cirílico;
- debe tratar números y puntuación como neutrales.

Tests sugeridos:

- `microsoft.com` normal;
- dominio con una `о` cirílica;
- texto con números;
- texto con guiones;
- string vacío.

---

### `contains_confusable_characters`

```python
contains_confusable_characters(text: str) -> bool
```

Detecta caracteres potencialmente confundibles usando una tabla interna mínima.

Comportamiento esperado:

- detecta caracteres visualmente similares;
- no depende de librerías externas;
- no hace conversión IDNA completa.

Tests sugeridos:

- letras cirílicas similares a latinas;
- letras griegas similares a latinas;
- texto sin caracteres confundibles;
- string vacío.

---

### `find_confusable_characters`

```python
find_confusable_characters(text: str) -> list[str]
```

Devuelve los caracteres sospechosos encontrados.

Comportamiento esperado:

- conserva el orden de aparición;
- puede devolver duplicados o valores únicos, según se decida en el contrato;
- devuelve lista vacía si no hay hallazgos.

Tests sugeridos:

- un carácter confundible;
- varios caracteres confundibles;
- caracteres repetidos;
- texto limpio.

## Fuera del dominio

No debe:

- resolver dominios;
- consultar listas externas;
- llamar servicios de reputación;
- hacer HTTP;
- usar librerías externas de threat intelligence.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede crear un caso de uso para analizar dominios extraídos;
- `infrastructure` puede aportar dominios desde parsers `.eml`, PDFs o HTML.

---

# 3. Domain analysis

## Propósito

Funciones puras para analizar propiedades estructurales de dominios y hosts.

## Ubicación sugerida

```text
src/domain/services/domain_analysis/
```

## Funciones candidatas

### `split_domain_labels`

```python
split_domain_labels(domain: str) -> list[str]
```

Divide un dominio en labels.

Ejemplo:

```text
login.example.com -> ["login", "example", "com"]
```

Tests sugeridos:

- dominio simple;
- subdominio;
- dominio con punto final;
- dominio vacío;
- dominio con espacios.

---

### `is_punycode_label`

```python
is_punycode_label(label: str) -> bool
```

Detecta si un label empieza por `xn--`.

Tests sugeridos:

- `xn--example`;
- `example`;
- mayúsculas/minúsculas;
- string vacío.

---

### `contains_punycode`

```python
contains_punycode(domain: str) -> bool
```

Detecta si un dominio contiene algún label Punycode.

Tests sugeridos:

- dominio con `xn--`;
- dominio sin Punycode;
- subdominio con Punycode;
- string vacío.

---

### `has_suspicious_subdomain_depth`

```python
has_suspicious_subdomain_depth(domain: str, max_depth: int = 4) -> bool
```

Detecta dominios con profundidad de subdominios sospechosa.

Tests sugeridos:

- dominio con pocos labels;
- dominio con muchos subdominios;
- valor límite;
- `max_depth` personalizado.

---

### `looks_like_ip_address_host`

```python
looks_like_ip_address_host(host: str) -> bool
```

Detecta si el host parece una IP en vez de un dominio.

Tests sugeridos:

- IPv4 válida;
- texto parecido a IPv4 pero inválido;
- dominio normal;
- host vacío.

---

### `has_suspicious_tld`

```python
has_suspicious_tld(domain: str, suspicious_tlds: set[str]) -> bool
```

Evalúa TLDs de riesgo a partir de una lista recibida como argumento.

Comportamiento esperado:

- no lee configuración global;
- no consulta listas externas;
- trabaja con datos recibidos.

Tests sugeridos:

- dominio con TLD sospechoso;
- dominio con TLD normal;
- lista vacía;
- mayúsculas/minúsculas.

## Fuera del dominio

No debe:

- resolver DNS;
- consultar WHOIS;
- llamar APIs de reputación;
- descargar listas de TLDs.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede orquestar análisis de dominios;
- `infrastructure` puede resolver redirecciones o enriquecer reputación.

---

# 4. URL analysis

## Propósito

Funciones puras para clasificar URLs o componentes de URLs ya parseados.

## Ubicación sugerida

```text
src/domain/services/url_analysis/
```

## Funciones candidatas

### `is_url_scheme_allowed`

```python
is_url_scheme_allowed(scheme: str, allowed_schemes: set[str]) -> bool
```

Comprueba si el esquema está permitido.

Tests sugeridos:

- `http`;
- `https`;
- `mailto`;
- mayúsculas;
- esquema vacío.

---

### `is_suspicious_url_scheme`

```python
is_suspicious_url_scheme(scheme: str) -> bool
```

Detecta esquemas sospechosos como:

```text
javascript
data
file
vbscript
```

Tests sugeridos:

- `javascript`;
- `data`;
- `file`;
- `https`;
- mayúsculas/minúsculas.

---

### `has_embedded_credentials`

```python
has_embedded_credentials(url: str) -> bool
```

Detecta URLs con credenciales embebidas.

Ejemplo:

```text
https://user:pass@example.com
```

Tests sugeridos:

- URL con usuario;
- URL con usuario y password;
- URL normal;
- URL malformada.

---

### `has_suspicious_query_density`

```python
has_suspicious_query_density(url: str, threshold: int) -> bool
```

Detecta query strings demasiado densas o con demasiados parámetros.

Tests sugeridos:

- URL sin query;
- URL con pocos parámetros;
- URL con muchos parámetros;
- threshold personalizado.

---

### `has_url_shortener_domain`

```python
has_url_shortener_domain(domain: str, known_shorteners: set[str]) -> bool
```

Detecta acortadores conocidos usando una lista pasada como argumento.

Tests sugeridos:

- dominio acortador;
- dominio no acortador;
- lista vacía;
- mayúsculas/minúsculas.

## Fuera del dominio

No debe:

- hacer HEAD;
- hacer GET;
- seguir redirecciones;
- abrir navegador;
- consultar reputación.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede definir un `LinkAnalyzerPort`;
- `infrastructure` puede implementar resolución HTTP pasiva.

---

# 5. Attachment analysis

## Propósito

Funciones puras para clasificar adjuntos a partir de metadatos disponibles, especialmente nombre de archivo y extensión.

## Ubicación sugerida

```text
src/domain/services/attachment_analysis/
```

## Funciones candidatas

### `is_executable_extension`

```python
is_executable_extension(filename: str) -> bool
```

Detecta extensiones ejecutables como:

```text
.exe
.bat
.cmd
.scr
.ps1
.vbs
.js
.jar
```

Tests sugeridos:

- `.exe`;
- `.pdf`;
- mayúsculas;
- archivo sin extensión;
- doble extensión.

---

### `is_office_document_extension`

```python
is_office_document_extension(filename: str) -> bool
```

Detecta documentos Office, especialmente formatos con macros.

Ejemplos:

```text
.doc
.docx
.docm
.xls
.xlsx
.xlsm
.ppt
.pptx
.pptm
```

Tests sugeridos:

- `.docx`;
- `.docm`;
- `.xlsm`;
- `.pdf`;
- mayúsculas.

---

### `is_pdf_extension`

```python
is_pdf_extension(filename: str) -> bool
```

Detecta PDF por extensión.

Tests sugeridos:

- `.pdf`;
- `.PDF`;
- `invoice.pdf.exe`;
- sin extensión.

---

### `has_double_extension`

```python
has_double_extension(filename: str) -> bool
```

Detecta patrones como:

```text
invoice.pdf.exe
document.docx.scr
```

Tests sugeridos:

- doble extensión peligrosa;
- doble extensión no peligrosa;
- extensión simple;
- nombre sin extensión.

---

### `has_suspicious_filename_chars`

```python
has_suspicious_filename_chars(filename: str) -> bool
```

Detecta caracteres invisibles, separadores raros o Unicode sospechoso.

Tests sugeridos:

- nombre con zero-width space;
- nombre con caracteres de control;
- nombre normal;
- nombre con Unicode mezclado.

---

### `classify_attachment_extension`

```python
classify_attachment_extension(filename: str) -> str
```

Clasifica adjuntos en categorías.

Categorías candidatas:

```text
PDF
OFFICE
EXECUTABLE
IMAGE
ARCHIVE
TEXT
UNKNOWN
```

Tests sugeridos:

- PDF;
- Office con macros;
- ejecutable;
- imagen;
- archivo comprimido;
- desconocido.

## Fuera del dominio

No debe:

- abrir archivos;
- leer bytes;
- calcular hashes leyendo disco;
- extraer macros;
- analizar PDF real;
- ejecutar YARA.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede orquestar escaneo de adjuntos;
- `infrastructure` puede implementar parsers PDF, Office, YARA y hash real.

---

# 6. Authentication result analysis

## Propósito

Interpretar resultados ya obtenidos de SPF, DKIM y DMARC.

El dominio no debe hacer DNS ni validar firmas criptográficas.  
Solo puede clasificar resultados ya calculados por infraestructura.

## Ubicación sugerida

```text
src/domain/services/authentication_analysis/
```

## Funciones candidatas

### `is_authentication_aligned`

```python
is_authentication_aligned(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool
```

Evalúa si los resultados de autenticación están alineados.

Tests sugeridos:

- todos `pass`;
- SPF fail, DKIM pass, DMARC pass;
- DMARC fail;
- valores desconocidos.

---

### `classify_authentication_risk`

```python
classify_authentication_risk(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> str
```

Clasifica riesgo de autenticación.

Categorías candidatas:

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

Tests sugeridos:

- todos pass;
- SPF fail;
- DKIM fail;
- DMARC fail;
- combinación múltiple;
- valores ausentes.

---

### `has_authentication_failure`

```python
has_authentication_failure(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> bool
```

Detecta si existe algún fallo relevante.

Tests sugeridos:

- todos pass;
- uno fail;
- varios fail;
- neutral/none;
- unknown.

---

### `summarize_authentication_findings`

```python
summarize_authentication_findings(
    spf_result: str,
    dkim_result: str,
    dmarc_result: str,
) -> list[str]
```

Devuelve hallazgos textuales o códigos de hallazgo.

Tests sugeridos:

- SPF fail;
- DKIM fail;
- DMARC fail;
- todos pass;
- resultados desconocidos.

## Fuera del dominio

No debe:

- consultar DNS;
- validar criptográficamente DKIM;
- parsear cabeceras raw;
- llamar librerías externas de autenticación.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede orquestar análisis de identidad;
- `infrastructure` puede parsear cabeceras y calcular resultados SPF/DKIM/DMARC.

---

# 7. Risk scoring

## Propósito

Funciones puras para convertir indicadores en puntuaciones y niveles de riesgo.

## Ubicación sugerida

```text
src/domain/services/risk_scoring/
```

## Funciones candidatas

### `calculate_indicator_score`

```python
calculate_indicator_score(
    indicators: list[str],
    weights: dict[str, int],
) -> int
```

Suma pesos asociados a indicadores.

Tests sugeridos:

- indicadores conocidos;
- indicadores desconocidos;
- lista vacía;
- pesos negativos si se permiten o se rechazan;
- duplicados.

---

### `classify_risk_level`

```python
classify_risk_level(score: int) -> str
```

Convierte puntuación en nivel de riesgo.

Categorías candidatas:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Tests sugeridos:

- límites exactos;
- bajo;
- medio;
- alto;
- crítico;
- score negativo.

---

### `combine_risk_scores`

```python
combine_risk_scores(scores: list[int]) -> int
```

Combina varias puntuaciones parciales.

Tests sugeridos:

- lista vacía;
- múltiples valores;
- valores negativos;
- valores extremos.

---

### `cap_risk_score`

```python
cap_risk_score(
    score: int,
    min_score: int = 0,
    max_score: int = 100,
) -> int
```

Limita la puntuación a un rango.

Tests sugeridos:

- score menor que mínimo;
- score mayor que máximo;
- score dentro de rango;
- límites personalizados.

---

### `has_critical_indicators`

```python
has_critical_indicators(
    indicators: list[str],
    critical_indicators: set[str],
) -> bool
```

Detecta si aparece algún indicador crítico.

Tests sugeridos:

- indicador crítico presente;
- ninguno crítico;
- lista vacía;
- conjunto crítico vacío.

## Fuera del dominio

No debe:

- llamar IA;
- consultar reputación externa;
- depender de pesos en configuración global;
- generar reportes API.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede componer resultados de módulos;
- `infrastructure` puede aportar hallazgos desde parsers y adaptadores.

---

# 8. Social engineering heuristics

## Propósito

Heurísticas deterministas simples sobre texto para detectar señales de ingeniería social.

La IA local puede complementar este análisis, pero no sustituye estas reglas puras.

## Ubicación sugerida

```text
src/domain/services/social_engineering/
```

## Funciones candidatas

### `contains_urgency_terms`

```python
contains_urgency_terms(text: str, terms: set[str]) -> bool
```

Detecta términos de urgencia.

Tests sugeridos:

- texto con término urgente;
- texto sin término;
- mayúsculas/minúsculas;
- lista de términos vacía.

---

### `contains_financial_pressure_terms`

```python
contains_financial_pressure_terms(text: str, terms: set[str]) -> bool
```

Detecta presión financiera.

Tests sugeridos:

- factura urgente;
- bloqueo de cuenta;
- texto neutro;
- términos vacíos.

---

### `contains_credential_request_terms`

```python
contains_credential_request_terms(text: str, terms: set[str]) -> bool
```

Detecta solicitud de credenciales.

Tests sugeridos:

- `password`;
- `verify your account`;
- texto neutro;
- mayúsculas/minúsculas.

---

### `count_social_engineering_signals`

```python
count_social_engineering_signals(
    text: str,
    signal_terms: dict[str, set[str]],
) -> dict[str, int]
```

Cuenta señales por categoría.

Tests sugeridos:

- una categoría;
- varias categorías;
- sin señales;
- texto vacío.

---

### `classify_social_engineering_risk`

```python
classify_social_engineering_risk(
    signal_counts: dict[str, int],
) -> str
```

Clasifica riesgo a partir de conteos de señales.

Categorías candidatas:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Tests sugeridos:

- sin señales;
- pocas señales;
- múltiples señales;
- señales críticas.

## Fuera del dominio

No debe:

- llamar Ollama;
- hacer NLP externo;
- usar modelos ML;
- leer prompts;
- depender de configuración global.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede combinar heurísticas con hallazgos técnicos;
- `infrastructure` puede usar Ollama como análisis complementario.

---

# 9. Finding analysis

## Propósito

Funciones puras para componer, filtrar y ordenar hallazgos.

Más adelante estas funciones deberían operar sobre value objects o entities como `Finding`, `RiskIndicator` o `AnalysisResult`.

## Ubicación sugerida

```text
src/domain/services/finding_analysis/
```

## Funciones candidatas

### `deduplicate_findings`

```python
deduplicate_findings(findings: list[str]) -> list[str]
```

Elimina hallazgos duplicados.

Tests sugeridos:

- lista con duplicados;
- lista sin duplicados;
- lista vacía;
- preservación de orden.

---

### `sort_findings_by_severity`

```python
sort_findings_by_severity(findings: list[dict]) -> list[dict]
```

Ordena hallazgos por severidad.

Tests sugeridos:

- severidades mezcladas;
- severidad desconocida;
- lista vacía;
- estabilidad de orden.

---

### `filter_findings_by_category`

```python
filter_findings_by_category(
    findings: list[dict],
    category: str,
) -> list[dict]
```

Filtra hallazgos por categoría.

Tests sugeridos:

- categoría existente;
- categoría no existente;
- lista vacía;
- categoría con mayúsculas/minúsculas.

---

### `count_findings_by_category`

```python
count_findings_by_category(findings: list[dict]) -> dict[str, int]
```

Cuenta hallazgos por categoría.

Tests sugeridos:

- varias categorías;
- una categoría;
- lista vacía;
- hallazgos sin categoría.

## Fuera del dominio

No debe:

- renderizar reportes;
- generar JSON de API;
- acceder a base de datos;
- mezclar traducciones para UI.

## Posible siguiente capa

Después de cerrar este grupo:

- definir value objects/entities de hallazgos;
- crear un caso de uso de composición de reporte;
- exponer resultado mediante API.

---

# 10. Hash analysis

## Propósito

Funciones puras para validar y normalizar hashes ya calculados.

Calcular el hash leyendo un archivo no pertenece al dominio.  
Validar un hash recibido como string sí puede pertenecer al dominio.

## Ubicación sugerida

```text
src/domain/services/hash_analysis/
```

## Funciones candidatas

### `is_valid_sha256`

```python
is_valid_sha256(value: str) -> bool
```

Valida si un string tiene formato SHA-256.

Tests sugeridos:

- hash válido lowercase;
- hash válido uppercase;
- longitud incorrecta;
- caracteres no hexadecimales;
- string vacío.

---

### `normalize_hash`

```python
normalize_hash(value: str) -> str
```

Normaliza un hash textual.

Comportamiento esperado:

- elimina espacios;
- convierte a minúsculas;
- no calcula hash.

Tests sugeridos:

- hash con espacios;
- uppercase;
- lowercase;
- string vacío.

---

### `is_empty_hash`

```python
is_empty_hash(value: str) -> bool
```

Detecta si un hash está vacío o no informado.

Tests sugeridos:

- string vacío;
- espacios;
- `None` si se decide aceptarlo;
- hash válido.

## Fuera del dominio

No debe:

- abrir archivos;
- leer bytes;
- calcular SHA-256 real desde contenido;
- consultar VirusTotal u otras APIs.

## Posible siguiente capa

Después de cerrar este grupo:

- `application` puede solicitar cálculo de hash a un puerto;
- `infrastructure` puede implementar cálculo sobre filesystem o bytes.

---

# Orden recomendado de implementación

No ejecutar todo de golpe.

Orden sugerido para iterar:

```text
1. text_normalization
2. homoglyphs
3. domain_analysis
4. url_analysis
5. attachment_analysis
6. risk_scoring
7. authentication_analysis
8. social_engineering
9. hash_analysis
10. finding_analysis
```

Motivo:

- los primeros grupos son simples, puros y muy testeables;
- aportan valor forense temprano;
- no requieren todavía entities complejas;
- permiten crear disciplina de tests unitarios antes de subir capas.

---

# Plantilla de iteración

Usar esta plantilla para cada grupo o subgrupo.

```md
## Iteration N - [group/function]

Status: pending | in-progress | done

### Scope

Funciones incluidas:

- ...

Funciones excluidas:

- ...

### Domain contract

Firma propuesta:

```python
...
```

### Unit tests

Casos mínimos:

- ...
- ...
- ...

### Implementation notes

- ...
- ...

### Acceptance criteria

- [ ] La función es pura.
- [ ] No hay IO.
- [ ] No hay imports de infraestructura.
- [ ] Tiene unit tests.
- [ ] Los tests pasan.
- [ ] El comportamiento está documentado.

### Next layer

¿Sube a Application?

- Sí / No / Pendiente

¿Requiere puerto?

- Sí / No / Pendiente

¿Requiere adaptador de Infrastructure?

- Sí / No / Pendiente

### Commit

```text
...
```
```

---

# Funciones explícitamente fuera de Domain

Estas funciones o responsabilidades no deben implementarse directamente en `domain`:

```python
parse_eml(...)
resolve_short_url(...)
take_screenshot(...)
scan_yara(...)
run_ocr(...)
call_ollama(...)
extract_pdf_links_from_file(...)
validate_dkim_signature(...)
check_spf_dns(...)
calculate_file_hash_from_path(...)
query_virustotal(...)
download_url(...)
```

Motivo:

- requieren IO;
- dependen de librerías externas;
- usan red;
- usan filesystem;
- ejecutan procesos;
- pertenecen a `infrastructure`;
- deben exponerse al dominio mediante puertos definidos en `application`.

---

# Criterio de avance por capas

Solo se sube una función o grupo a capas superiores cuando:

- los unit tests del dominio están cerrados;
- el contrato es estable;
- se entiende qué caso de uso lo necesita;
- se sabe si requiere puerto;
- se puede crear un adaptador sin contaminar el dominio.

Ejemplo de recorrido:

```text
contains_punycode(domain)
        ↓
unit tests de domain
        ↓
AnalyzeLinksUseCase en application
        ↓
LinkAnalyzerPort si hay resolución externa
        ↓
HttpRedirectResolverAdapter en infrastructure
        ↓
FastAPI endpoint si se expone al usuario
```

---

# Regla final

El dominio debe crecer despacio.

Cada función pura debe justificar su existencia con:

- valor forense real;
- tests unitarios;
- ausencia de dependencias externas;
- posibilidad de integrarse después mediante capas limpias.