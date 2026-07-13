import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import * as analyzeEmailApi from "../src/api/analyzeEmail";
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
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
      },
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
      },
    ],
    sorted_findings: [
      {
        code: "DOMAIN_CONTAINS_PUNYCODE",
        category: "DOMAIN",
        severity: "HIGH",
      },
      {
        code: "AUTHENTICATION_RESULTS_UNKNOWN",
        category: "AUTHENTICATION",
        severity: "MEDIUM",
      },
      {
        code: "DOMAIN_HAS_SUSPICIOUS_TLD",
        category: "DOMAIN",
        severity: "MEDIUM",
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
    expect(screen.getByText(/review the local triage output for/i)).toBeInTheDocument();
    expect(screen.getByText("Evidence overview")).toBeInTheDocument();
    expect(screen.getByText("Findings by category")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "AUTHENTICATION" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "DOMAIN" })).toBeInTheDocument();
    expect(screen.getAllByText("2")[0]).toBeInTheDocument();
    expect(screen.getAllByText("DOMAIN_CONTAINS_PUNYCODE")).toHaveLength(2);
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
      expect(screen.getByText("security-review.eml")).toBeInTheDocument();
    });
  });
});
