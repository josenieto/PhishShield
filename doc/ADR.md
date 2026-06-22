# Architectural Decision Record (ADR): PhishShield Complete

## 1. Context and Problem

Modern phishing bypasses traditional filters through social engineering techniques, homoglyph attacks using Unicode/Punycode lookalike characters, and hidden payloads in attachments such as Office macros, links inside PDFs, and text embedded in images.

Current enterprise solutions are often proprietary, expensive, and require sending sensitive data to third-party clouds, which weakens privacy. PhishShield needs to be a defensive, local, self-hosted, open-source, and extensible tool for visual and safe forensic analysis of `.eml` email files.

---

## 2. Adopted Technical Decisions

### 2.1 Software Architecture: Hexagonal Modular Monolith

- **Decision:** Implement **Hexagonal Architecture (Ports and Adapters)** combined with Clean Architecture in a single modular repository.
- **Rationale:** This strictly separates cybersecurity business rules in Domain/Application from external technical tools in Infrastructure. It allows analysis libraries or web frameworks to be replaced in the future without changing the system core.
- **Layer structure:**
  - `Domain`: pure data models such as `Email` and `AnalysisResult`, dependency-free rules, and pure algorithms such as homoglyph detection.
  - `Application`: use cases and `Ports`, which are abstract interfaces defining contracts, for example `LinkAnalyzerPort`.
  - `Infrastructure`: concrete technical `Adapters`, such as FastAPI, Playwright, native parsers, and API `Entrypoints`.

### 2.2 Main Technology Stack

- **Backend:** **Python + FastAPI**
  - **Rationale:** Python is a standard ecosystem for cybersecurity and has mature forensic libraries. FastAPI provides strong typing with Pydantic and native asynchronous performance for concurrent analysis workflows.
- **Frontend:** **React + TypeScript + Vite**
  - **Rationale:** This enables a modern SPA for drag-and-drop file upload and dashboard visualization of forensic reports with Tailwind CSS.

### 2.3 Deployment and Distribution Strategy

- **Model:** **Local self-hosted web application** distributed through **Docker and Docker Compose**.
- **Container architecture:**
  1. `Frontend`: serves the React web UI on port 3000.
  2. `Backend`: exposes the FastAPI API that runs security rules on port 8000.
  3. `Playwright/Browser`: runs an isolated Chromium browser container to capture screenshots of links without putting the user's host system at risk.

---

## 3. Forensic Analysis Modules

### 3.1 Headers and Identity Module

- Performs static analysis of the raw `.eml` source.
- Extracts sender information and subject.
- Validates global authentication signals: **SPF** for authorized sender server, **DKIM** for message integrity, and **DMARC** for domain policy alignment.

### 3.2 Links and Homoglyph Attacks Module

- Detects visual traps where a domain imitates a legitimate one using characters from other alphabets, for example a Cyrillic `о` inside `microsoft.com`.
- Converts links to their real network representation in **Punycode** (`xn--...`) using Python's `idna` ecosystem where appropriate.
- Resolves shortened links, for example bit.ly, through passive HTTP `HEAD` requests to discover the real destination before analysis.

### 3.3 Safe Browsing Sandbox Module

- Receives URLs from the email and opens them in an automated invisible browser.
- Uses strict security configuration: disables automatic downloads and blocks persistent cookies.
- Captures a static screenshot of the destination page and extracts the tab title so the analyst can visually check whether it clones a bank or real service.

### 3.4 Attachment Module

- **PDF files (`pdfminer` / `PyPDF2`):** automatically extracts hidden links inside documents and sends them to the sandbox module.
- **Office files (Word, Excel):** uses specialized tooling such as **`oletools`** to scan for hidden VBA macros or dangerous automatic scripts.
- **Hash calculation:** generates a SHA-256 hash for each attachment to allow optional checks against global malware databases, for example VirusTotal.
- **YARA rules:** integrates `yara-python` to scan email bodies and attachments using industry-standard signatures.

### 3.5 Images and Visual Content Module

- **OCR engine (Tesseract):** uses `pytesseract` to extract and read text embedded inside email images, preventing attackers from bypassing text filters by using image-only content.
- **EXIF metadata:** extracts hidden information from attached images, such as camera, editing software, and coordinates when present, for forensic purposes.

---

## 4. Private Local AI Engine

### 4.1 Current Approach: Ollama in Docker

- **Implementation:** integrates the official `ollama/ollama` image in `docker-compose.yml`. The Python backend connects through the official `ollama` library.
- **Environment-based control:** AI analysis is optional and controlled by `USE_AI_ANALYSIS=true/false` in `.env`. If disabled, the system skips the step cleanly through ports.
- **AI tasks using lightweight models such as Phi-3 or Llama-3:**
  1. **Social engineering analysis:** evaluates text for persuasion, emotional manipulation, or induced urgency.
  2. **Human-readable explanations:** translates raw technical findings, such as SPF failures or detected macros, into a clear paragraph that non-expert users can understand.

### 4.2 Future Lifecycle Evolution

- **Migration to native inference with ONNX:** for version `v2.0.0`, the plan is to fine-tune a lightweight classifier model such as **DistilBERT** or **RoBERTa-tiny** using a public phishing email dataset.
- **Advantage:** the model will be exported to **ONNX** and executed locally with `onnxruntime` in the backend. This removes the need for a heavy Ollama container and allows AI to run in milliseconds on most PCs without GPU requirements or extra gigabytes of RAM.

---

## 5. Quality Strategy and Repository Lifecycle

- **Testing:** strict use of **Pytest** for unit tests of algorithms such as homoglyph detection and header rules, plus integration tests for adapters such as Playwright and parsers. Mocks must be used to simulate network connections during tests.
- **GitHub Actions:** automatic pipeline that runs Pytest, verifies code formatting with tools such as Black or Flake8, and builds the final image for Docker Hub on every commit or pull request.
- **Community management:** public GitHub Issues are used for roadmap tracking with labels such as `enhancement` and `good first issue`, and Git tags are used for formal versioning such as `v1.0.0` and `v1.1.0`.