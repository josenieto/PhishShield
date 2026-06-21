# Architectural Decision Record (ADR): PhishShield Complete

## 1. Contexto y Problema
El phishing moderno evade los filtros tradicionales utilizando técnicas de ingeniería social, ataques homóglifos (caracteres Unicode/Punycode simulados) y payloads ocultos en archivos adjuntos (macros de Office, enlaces en PDFs y texto en imágenes). 

Las soluciones corporativas actuales son privativas, caras y requieren enviar datos sensibles a nubes de terceros, vulnerando la privacidad. Se necesita una herramienta defensiva, local (self-hosted), de código abierto (open-source) y extensible que permita realizar un análisis forense de archivos de correo `.eml` de forma visual y segura.

---

## 2. Decisiones Técnicas Adoptadas

### 2.1 Arquitectura del Software: Monolito Modular Hexagonal
* **Decisión:** Implementar **Arquitectura Hexagonal (Puertos y Adaptadores)** combinada con Clean Architecture en un repositorio único modular (Monolito).
* **Justificación:** Separa estrictamente las reglas de negocio de la ciberseguridad (Domain/Application) de las herramientas tecnológicas externas (Infrastructure). Permite intercambiar librerías de análisis o frameworks web en el futuro sin alterar el núcleo del sistema.
* **Estructura de Capas:**
  * `Domain`: Modelos de datos puros (`Email`, `ResultadoAnalisis`) libres de dependencias y algoritmos puros (detección de homóglifos).
  * `Application`: Casos de uso y `Ports` (interfaces abstractas que definen los contratos, ej. `LinkAnalyzerPort`).
  * `Infrastructure`: `Adapters` técnicos concretos (FastAPI, Playwright, parsers nativos) y puntos de entrada (`Entrypoints` de la API).

### 2.2 Stack Tecnológico Principal
* **Backend:** **Python + FastAPI**
  * *Justificación:* Python es el estándar en ciberseguridad. Cuenta con el ecosistema forense más maduro. FastAPI proporciona tipado fuerte con Pydantic y rendimiento asíncrono nativo para la concurrencia de análisis.
* **Frontend:** **React + TypeScript + Vite**
  * *Justificación:* Permite construir una interfaz SPA moderna y fluida para gestionar la carga de archivos por arrastre (*Drag and Drop*) y visualizar el panel de control del reporte con Tailwind CSS.

### 2.3 Estrategia de Despliegue y Distribución (Docker)
* **Modelo:** **Web Local Autohospedada (Self-hosted)** distribuida mediante **Docker y Docker Compose**.
* **Arquitectura de Contenedores (3 Servicios):**
  1. `Frontend`: Sirve la interfaz web en React (Puerto 3000).
  2. `Backend`: La API en FastAPI que procesa las reglas de seguridad (Puerto 8000).
  3. `Playwright/Browser`: Un navegador Chromium aislado de forma segura en su propio contenedor, listo para tomar capturas de pantalla de enlaces sin poner en riesgo el sistema del usuario.

---

## 3. Desglose de Módulos de Análisis Forense (Artefactos)

### 3.1 Módulo de Cabeceras e Identidad
* Analiza de forma estática el código fuente del archivo `.eml`.
* Extrae quién lo envía, el asunto y valida las firmas globales **SPF** (servidor autorizado), **DKIM** (correo no modificado) y **DMARC**.

### 3.2 Módulo de Enlaces y Ataques Homóglifos (IDN)
* Detecta trampas visuales donde un dominio simula ser uno legítimo usando caracteres de otros alfabetos (ej. una "о" cirílica en `microsoft.com`).
* Convierte automáticamente los enlaces a su formato real de red **Punycode** (`xn--...`) usando la librería `idna` de Python para revelar el fraude.
* Resuelve enlaces acortados (ej. bit.ly) mediante peticiones HTTP `HEAD` pasivas para conocer el destino real antes de analizarlo.

### 3.3 Módulo Sandbox de Navegación Segura (Playwright)
* Recibe las URLs del correo y abre un navegador automatizado invisible (*Headless Browser*).
* Configuración estricta de seguridad: desactiva la ejecución de descargas automáticas y bloquea cookies persistentes.
* Toma una captura de pantalla estática de la web de destino y extrae el título de la pestaña para que el analista verifique visualmente si clona a un banco o servicio real.

### 3.4 Módulo de Archivos Adjuntos (PDF y Office)
* **Para PDFs (`pdfminer` / `PyPDF2`):** Extrae automáticamente todos los enlaces ocultos dentro del documento y los envía al módulo Sandbox.
* **Para Office (Word, Excel):** Utiliza la librería especializada **`oletools`** para escanear el archivo en milisegundos en busca de **macros de VBA** ocultas o scripts automáticos peligrosos.
* **Cálculo de Hashes:** Genera el hash SHA-256 de cada adjunto para permitir comprobaciones opcionales contra bases de datos globales de malware (ej. API de VirusTotal).
* **Reglas YARA:** Integra la librería `yara-python` para escanear el cuerpo del correo y los adjuntos utilizando firmas estándar de la industria.

### 3.5 Módulo de Imágenes y Contenido Visual (OCR y EXIF)
* **Motor OCR (Tesseract):** Utiliza `pytesseract` para extraer y "leer" el texto incrustado dentro de las imágenes del correo (evitando que los atacantes se salten filtros de texto usando imágenes completas).
* **Metadatos EXIF:** Extrae la información oculta de las imágenes adjuntas (cámara, software de edición, coordenadas si existen) con fines forenses.

---

## 4. Motor de Inteligencia Artificial Privado y Local

### 4.1 Enfoque Actual: Ollama en Docker
* **Implementación:** Integración de la imagen oficial `ollama/ollama` dentro del `docker-compose.yml`. El backend de Python se conecta mediante la librería oficial `ollama`.
* **Control por Variables de Entorno:** El análisis de IA es opcional y se controla mediante la variable `USE_AI_ANALYSIS=true/false` en el archivo `.env`. Si está desactivado, el sistema omite el paso limpiamente gracias a la arquitectura de Puertos.
* **Tareas de la IA (Modelos ligeros tipo Phi-3 o Llama-3):**
  1. *Análisis de Ingeniería Social:* Evalúa el texto buscando técnicas de persuasión, manipulación emocional o urgencia psicológica inducida.
  2. *Explicaciones en Lenguaje Humano:* Traduce los datos técnicos crudos (fallos de SPF, macros detectadas) a un párrafo sencillo que cualquier usuario común pueda entender.

### 4.2 Evolución del Ciclo de Vida (Fase Futura)
* **Migración a Inferencia Nativa (ONNX):** Para la versión v2.0.0, se planea realizar un *Fine-Tuning* (ajuste fino) de un modelo clasificador ligero (como **DistilBERT** o **RoBERTa-tiny**, ~100MB) usando un dataset público de correos fraudulentos.
* **Ventaja:** El modelo se exportará a formato **ONNX** y se ejecutará localmente con `onnxruntime` en el backend. Esto eliminará la necesidad de correr el contenedor pesado de Ollama, permitiendo que la IA funcione en milisegundos en cualquier PC sin requerir GPU ni gigas de RAM extras.

---

## 5. Estrategia de Calidad y Ciclo de Vida del Repositorio (CI/CD)
* **Testing:** Uso estricto de **Pytest** para pruebas unitarias de los algoritmos (homóglifos, cabeceras) y pruebas de integración para los adaptadores (Playwright, Parsers). Uso de *Mocks* para simular conexiones de red durante los tests.
* **GitHub Actions (SecDevOps):** Pipeline automático que ejecuta los tests de Pytest, verifica el formato del código (con Black o Flake8) ante cada *Commit* o *Pull Request*, y construye de forma automática la imagen final para subirla a **Docker Hub**.
* **Gestión de Comunidad:** Uso de GitHub Issues públicos para marcar la Hoja de Ruta del proyecto (`enhancement`, `good first issue`) y Git Tags para el control de versiones formal (`v1.0.0`, `v1.1.0`).
