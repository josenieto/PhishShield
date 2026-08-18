import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as analyzeEmailApi from "../src/api/analyzeEmail";
import * as analyzeEmailModelAssessmentApi from "../src/api/analyzeEmailModelAssessment";
import * as copyMarkdownReportModule from "../src/report/copyMarkdownReport";
import * as downloadHtmlReportModule from "../src/report/downloadHtmlReport";
import * as downloadJsonReportModule from "../src/report/downloadJsonReport";
import * as downloadMarkdownReportModule from "../src/report/downloadMarkdownReport";
import App from "../src/App";


function emailFileInput(): HTMLInputElement {
  return screen.getAllByLabelText(/email file/i, { selector: "input" })[0] as HTMLInputElement;
}


const SAMPLE_ANALYSIS = {
  finding_codes: [
    "AUTHENTICATION_RESULTS_UNKNOWN",
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "DOMAIN_CONTAINS_PUNYCODE",
  ],
  unique_finding_codes: [
    "AUTHENTICATION_RESULTS_UNKNOWN",
    "DOMAIN_HAS_SUSPICIOUS_TLD",
    "DOMAIN_CONTAINS_PUNYCODE",
  ],
  finding_summary: {
    findings: [
      {
        code: "AUTHENTICATION_RESULTS_UNKNOWN",
        category: "AUTHENTICATION",
        severity: "MEDIUM",
        explanation: "Authentication results were unavailable or could not be extracted, which reduces trust in sender validation.",
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
        explanation: "The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
      },
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
        explanation: "The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
      },
    ],
    sorted_findings: [
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
        explanation: "The domain contains Punycode, which can be used to create visually deceptive lookalike domains.",
      },
      {
        code: "AUTHENTICATION_RESULTS_UNKNOWN",
        category: "AUTHENTICATION",
        severity: "MEDIUM",
        explanation: "Authentication results were unavailable or could not be extracted, which reduces trust in sender validation.",
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
        explanation: "The domain uses a top-level domain that is more commonly associated with abuse or impersonation.",
      },
    ],
    finding_counts_by_category: {
      AUTHENTICATION: 1,
      DOMAIN: 2,
    },
    highest_severity: "HIGH",
    total_findings: 3,
  },
  risk_score: {
    indicators: [
      "AUTHENTICATION_RESULTS_UNKNOWN",
      "DOMAIN_HAS_SUSPICIOUS_TLD",
      "DOMAIN_CONTAINS_PUNYCODE",
    ],
    raw_score: 65,
    capped_score: 65,
    risk_level: "HIGH",
    has_critical_indicators: false,
  },
  extracted_evidence: {
    sender_domain: "example.zip",
    subject: "Urgent account notice",
    urls: ["https://example.com/login"],
    attachment_filenames: ["invoice.pdf.exe"],
    authentication_results: {
      spf_result: "fail",
      dkim_result: "pass",
      dmarc_result: "fail",
    },
  },
};


const SAMPLE_ANALYSIS_WITH_EMPTY_EVIDENCE = {
  ...SAMPLE_ANALYSIS,
  extracted_evidence: {
    sender_domain: "",
    subject: "",
    urls: [],
    attachment_filenames: [],
    authentication_results: {
      spf_result: "unknown",
      dkim_result: "",
      dmarc_result: "unknown",
    },
  },
};


afterEach(() => {
  vi.restoreAllMocks();
});


describe("App", () => {
  it("should render an empty state before any analysis result exists", () => {
    render(<App />);

    expect(screen.getByText("No analysis loaded")).toBeInTheDocument();
    expect(
      screen.getByText(/render the current backend findings, risk score, and grouped indicators\./i),
    ).toBeInTheDocument();
  });

  it("should render the frontend MVP title", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Local email triage workbench" })).toBeInTheDocument();
    expect(screen.getByText(/use a trusted local or internal deployment for confidential email/i)).toBeInTheDocument();
  });

  it("should keep the analyze button disabled until a file is selected", () => {
    render(<App />);

    const buttons = screen.getAllByRole("button", { name: "Analyze email" });

    expect(buttons[0]).toBeDisabled();
  });

  it("should show an error for files that are not .eml", async () => {
    const user = userEvent.setup({ applyAccept: false });
    render(<App />);

    const input = emailFileInput();
    const invalidFile = new File(["hello"], "notes.txt", { type: "text/plain" });

    await user.upload(input, invalidFile);

    expect(
      await screen.findByText(/only \.eml files are supported/i),
    ).toBeInTheDocument();
  });

  it("should enable the analyze button when a .eml file is selected", async () => {
    const user = userEvent.setup();
    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);

    const buttons = screen.getAllByRole("button", { name: "Analyze email" });

    expect(buttons[0]).toBeEnabled();
  });

  it("should select a supported .eml file when it is dropped on the upload form", () => {
    render(<App />);

    const uploadForm = screen.getByRole("form", { name: "Email upload" });
    const emailFile = new File(["sample"], "dropped-message.eml", {
      type: "message/rfc822",
    });

    fireEvent.drop(uploadForm, { dataTransfer: { files: [emailFile] } });

    expect(screen.getByText("Selected: dropped-message.eml")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze email" })).toBeEnabled();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("should replace the visible filename when a new email is dropped", () => {
    render(<App />);

    const uploadForm = screen.getByRole("form", { name: "Email upload" });
    const firstFile = new File(["first"], "first-message.eml", { type: "message/rfc822" });
    const secondFile = new File(["second"], "second-message.eml", { type: "message/rfc822" });

    fireEvent.drop(uploadForm, { dataTransfer: { files: [firstFile] } });
    fireEvent.drop(uploadForm, { dataTransfer: { files: [secondFile] } });

    expect(screen.getByText("Selected: second-message.eml")).toBeInTheDocument();
    expect(screen.queryByText("Selected: first-message.eml")).not.toBeInTheDocument();
  });

  it("should reject a dropped file that is not an .eml message", () => {
    render(<App />);

    const uploadForm = screen.getByRole("form", { name: "Email upload" });
    const invalidFile = new File(["sample"], "dropped-message.pdf", {
      type: "application/pdf",
    });

    fireEvent.drop(uploadForm, { dataTransfer: { files: [invalidFile] } });

    expect(screen.getByRole("alert")).toHaveTextContent(/only \.eml files are supported/i);
    expect(screen.getByText("No file selected")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyze email" })).toBeDisabled();
  });

  it("should render a success state after analysis completes", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);

    expect(await screen.findByText("Analysis completed")).toBeInTheDocument();
    expect(screen.getByRole("status", { name: /analysis completed/i })).toBeInTheDocument();
    const workbench = screen.getByRole("main").querySelector(".workbench-grid");
    const sidebar = workbench?.querySelector(".workbench-sidebar");
    const results = workbench?.querySelector(".workbench-main");
    expect(sidebar).toBeInTheDocument();
    expect(results).toBeInTheDocument();
    expect(workbench).toHaveClass("workbench-grid-analysis-ready");
    expect(screen.getByText(/review the local triage output for/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Report actions" })).toBeInTheDocument();
    expect(screen.getByText("Risk assessment")).toBeInTheDocument();
    expect(screen.getByText("Score: 65/100")).toBeInTheDocument();
    expect(screen.getByRole("region", { name: "Risk assessment" })).toHaveClass("risk-summary-high");
    expect(screen.getAllByText("Highest severity: HIGH")).toHaveLength(2);
    expect(
      screen.getByText("No critical indicators were observed, but the returned findings still require analyst review."),
    ).toBeInTheDocument();
    expect(screen.getByText("Extracted evidence")).toBeInTheDocument();
    expect(screen.getByRole("article", { name: "Sender domain evidence" })).toHaveClass("evidence-card-identity");
    expect(screen.getByRole("article", { name: "URL evidence" })).toHaveClass("evidence-card-has-content");
    expect(screen.getByRole("article", { name: "Attachment evidence" })).toHaveClass("evidence-card-has-content");
    expect(screen.getByRole("article", { name: "Authentication evidence" })).toBeInTheDocument();
    expect(screen.getAllByText("1 extracted")).toHaveLength(2);
    expect(screen.getByText("https://example.com/login")).toHaveClass("evidence-code");
    expect(screen.getAllByText("DOMAIN_CONTAINS_PUNYCODE").at(-1)?.closest("span")).toHaveClass("indicator-chip-code");
    expect(screen.getByText("example.zip")).toBeInTheDocument();
    expect(screen.getByText("Urgent account notice")).toBeInTheDocument();
    expect(screen.getByText("https://example.com/login")).toBeInTheDocument();
    expect(screen.getByText("invoice.pdf.exe")).toBeInTheDocument();
    expect(screen.getByText("SPF")).toBeInTheDocument();
    expect(screen.getAllByText("fail")).toHaveLength(2);
    expect(screen.getByText("pass")).toBeInTheDocument();
    expect(screen.getByText("Indicator distribution")).toBeInTheDocument();
    expect(screen.getAllByText("Highest severity: HIGH")).toHaveLength(2);
    expect(screen.getAllByText("Highest severity: MEDIUM")).toHaveLength(2);
    expect(screen.getByText("Findings by category")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AUTHENTICATION" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "DOMAIN" })).toBeInTheDocument();
    expect(screen.getByText(/The domain contains Punycode/i)).toBeInTheDocument();
    expect(screen.getAllByText("2")[0]).toBeInTheDocument();
    expect(screen.getAllByText("DOMAIN_CONTAINS_PUNYCODE")).toHaveLength(2);
    expect(screen.getByLabelText("Unique indicator codes")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download HTML" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Preview Markdown report" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download JSON" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy Markdown report" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Download Markdown report" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Model-assisted assessment" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Assess with model" })).toBeInTheDocument();
  });

  it("should show a not configured model assessment after requesting the model view", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);
    vi.spyOn(analyzeEmailModelAssessmentApi, "analyzeEmailModelAssessment").mockResolvedValue({
      model_assessment: {
        status: "not_configured",
        label: "unknown",
        confidence: null,
        summary: "",
        signals: [],
        model_name: "",
        model_version: "",
        error_message: "",
      },
    });

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Assess with model" }));

    expect(await screen.findByText("Model assessment is not configured yet.")).toBeInTheDocument();
    expect(screen.getByText(/no experimental local model is configured/i)).toBeInTheDocument();
    expect(screen.getByText(/does not replace deterministic findings/i)).toBeInTheDocument();
  });

  it("should surface model assessment failures separately from deterministic analysis", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);
    vi.spyOn(analyzeEmailModelAssessmentApi, "analyzeEmailModelAssessment").mockRejectedValue(
      new Error("Uploaded email could not be assessed by the model."),
    );

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Assess with model" }));

    expect(await screen.findByText("Uploaded email could not be assessed by the model.")).toBeInTheDocument();
    expect(screen.getByText(/deterministic analysis remains available and authoritative/i)).toBeInTheDocument();
    expect(screen.getByText("Risk assessment")).toBeInTheDocument();
  });

  it("should render completed model assessment as advisory result", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);
    vi.spyOn(analyzeEmailModelAssessmentApi, "analyzeEmailModelAssessment").mockResolvedValue({
      model_assessment: {
        status: "completed",
        label: "suspicious",
        confidence: 0.84,
        summary: "The message resembles an account verification lure.",
        signals: ["Credential wording"],
        model_name: "local-baseline",
        model_version: "test-version",
        error_message: "",
      },
    });

    render(<App />);
    await user.upload(emailFileInput(), new File(["sample"], "sample.eml", { type: "message/rfc822" }));
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");
    await user.click(screen.getByRole("button", { name: "Assess with model" }));

    expect(await screen.findByText("Advisory model result")).toBeInTheDocument();
    expect(screen.getByText("suspicious")).toBeInTheDocument();
    expect(screen.getByText("Confidence: 0.84")).toBeInTheDocument();
    expect(screen.getByText("local-baseline")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Analyze email" }));

    expect(screen.queryByText("Advisory model result")).not.toBeInTheDocument();
  });

  it("should explain why an inconclusive model assessment abstained", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);
    vi.spyOn(analyzeEmailModelAssessmentApi, "analyzeEmailModelAssessment").mockResolvedValue({
      model_assessment: {
        status: "inconclusive",
        label: "unknown",
        confidence: 0.42,
        summary: "The message requires analyst review.",
        signals: [],
        model_name: "local-baseline",
        model_version: "test-version",
        abstention_reason: "out_of_scope",
        error_message: "",
      },
    });

    render(<App />);
    await user.upload(emailFileInput(), new File(["sample"], "sample.eml", { type: "message/rfc822" }));
    await user.click(screen.getByRole("button", { name: "Analyze email" }));
    await screen.findByText("Analysis completed");
    await user.click(screen.getByRole("button", { name: "Assess with model" }));

    expect(await screen.findByText(/the email is outside the model's supported scope/i)).toBeInTheDocument();
  });

  it("should use API category counts instead of counting visible findings", async () => {
    const user = userEvent.setup();
    const analysisWithAuthoritativeCounts = {
      ...SAMPLE_ANALYSIS,
      finding_summary: {
        ...SAMPLE_ANALYSIS.finding_summary,
        finding_counts_by_category: {
          AUTHENTICATION: 4,
          DOMAIN: 1,
        },
      },
    };
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(analysisWithAuthoritativeCounts);

    render(<App />);
    await user.upload(emailFileInput(), new File(["sample"], "sample.eml", { type: "message/rfc822" }));
    await user.click(screen.getByRole("button", { name: "Analyze email" }));
    await screen.findByText("Analysis completed");

    expect(screen.getByText("4", { selector: "strong" })).toBeInTheDocument();
  });

  it("should trigger HTML report download from the success state", async () => {
    const user = userEvent.setup();
    const downloadHtmlReportSpy = vi.spyOn(
      downloadHtmlReportModule,
      "downloadHtmlReport",
    ).mockImplementation(() => {
      return;
    });
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Download HTML" }));

    expect(downloadHtmlReportSpy).toHaveBeenCalledWith({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });
  });

  it("should show and hide the Markdown report preview from the success state", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Preview Markdown report" }));

    expect(await screen.findByRole("heading", { name: "Markdown report preview" })).toBeInTheDocument();
    expect(screen.getByText(/# PhishShield Analysis Report/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hide Markdown preview" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Hide Markdown preview" }));

    expect(screen.queryByRole("heading", { name: "Markdown report preview" })).not.toBeInTheDocument();
  });

  it("should trigger JSON report download from the success state", async () => {
    const user = userEvent.setup();
    const downloadJsonReportSpy = vi.spyOn(
      downloadJsonReportModule,
      "downloadJsonReport",
    ).mockImplementation(() => {
      return;
    });
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Download JSON" }));

    expect(downloadJsonReportSpy).toHaveBeenCalledWith({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });
  });

  it("should trigger Markdown report copy from the success state", async () => {
    const user = userEvent.setup();
    const copyMarkdownReportSpy = vi.spyOn(
      copyMarkdownReportModule,
      "copyMarkdownReport",
    ).mockResolvedValue();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Copy Markdown report" }));

    expect(copyMarkdownReportSpy).toHaveBeenCalledWith({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });
    expect(await screen.findByText("Markdown report copied")).toBeInTheDocument();
  });

  it("should show an error when Markdown report copy fails", async () => {
    const user = userEvent.setup();
    vi.spyOn(copyMarkdownReportModule, "copyMarkdownReport").mockRejectedValue(
      new Error("Clipboard is unavailable."),
    );
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Copy Markdown report" }));

    expect(await screen.findByText("Markdown report could not be copied")).toBeInTheDocument();
  });

  it("should trigger Markdown report download from the success state", async () => {
    const user = userEvent.setup();
    const downloadMarkdownReportSpy = vi.spyOn(
      downloadMarkdownReportModule,
      "downloadMarkdownReport",
    ).mockImplementation(() => {
      return;
    });
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);
    await screen.findByText("Analysis completed");

    await user.click(screen.getByRole("button", { name: "Download Markdown report" }));

    expect(downloadMarkdownReportSpy).toHaveBeenCalledWith({
      analysis: SAMPLE_ANALYSIS,
      selectedFileName: "security-review.eml",
    });
  });

  it("should render an analysis in progress state while waiting for the backend", async () => {
    const user = userEvent.setup();
    let resolveAnalysis: ((value: typeof SAMPLE_ANALYSIS) => void) | undefined;
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockImplementation(
      () => new Promise((resolve) => {
        resolveAnalysis = resolve;
      }),
    );

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getByRole("button", { name: "Analyze email" }));

    expect(await screen.findByText("Analysis in progress")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Analyzing local email..." })).toBeDisabled();
    expect(emailFileInput()).toBeDisabled();

    resolveAnalysis?.(SAMPLE_ANALYSIS);

    expect(await screen.findByText("Analysis completed")).toBeInTheDocument();
  });

  it("should surface backend failures and remove stale results", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockRejectedValue(
      new Error("The backend is not reachable. Start the API and try again."),
    );

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getByRole("button", { name: "Analyze email" }));

    expect(
      await screen.findByText("The backend is not reachable. Start the API and try again."),
    ).toBeInTheDocument();
    expect(screen.queryByText("Analysis completed")).not.toBeInTheDocument();
  });

  it("should show the selected filename before submission", async () => {
    const user = userEvent.setup();
    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "security-review.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);

    await waitFor(() => {
       expect(screen.getByText("Selected: security-review.eml")).toBeInTheDocument();
    });
  });

  it("should clear the native file input when an unsupported file is selected", async () => {
    const user = userEvent.setup({ applyAccept: false });
    render(<App />);

    const input = emailFileInput();
    const invalidFile = new File(["hello"], "notes.txt", { type: "text/plain" });

    await user.upload(input, invalidFile);

    expect(input.files).toHaveLength(0);
    expect(screen.getByText("No file selected")).toBeInTheDocument();
  });

  it("should render empty evidence states when extracted evidence is missing", async () => {
    const user = userEvent.setup();
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue(SAMPLE_ANALYSIS_WITH_EMPTY_EVIDENCE);

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "empty-evidence.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getByRole("button", { name: "Analyze email" }));

    expect(await screen.findByText("Extracted evidence")).toBeInTheDocument();
    expect(screen.getAllByText("Not available")).toHaveLength(3);
    expect(screen.getByText("No URLs extracted")).toBeInTheDocument();
    expect(screen.getByText("No attachments extracted")).toBeInTheDocument();
    expect(screen.getAllByText("unknown")).toHaveLength(2);
  });
});
