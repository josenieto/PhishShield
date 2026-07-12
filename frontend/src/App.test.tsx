import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import * as analyzeEmailApi from "./api/analyzeEmail";
import App from "./App";


function emailFileInput(): HTMLInputElement {
  return screen.getAllByLabelText(/email file/i, { selector: "input" })[0] as HTMLInputElement;
}


describe("App", () => {
  it("should render an empty state before any analysis result exists", () => {
    render(<App />);

    expect(screen.getByText("No analysis yet")).toBeInTheDocument();
    expect(
      screen.getByText(/upload an .*eml.* file to render the current backend findings and risk summary\./i),
    ).toBeInTheDocument();
  });

  it("should render the frontend MVP title", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Email analysis frontend MVP" })).toBeInTheDocument();
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
    vi.spyOn(analyzeEmailApi, "analyzeEmail").mockResolvedValue({
      finding_codes: ["AUTHENTICATION_RESULTS_UNKNOWN"],
      unique_finding_codes: ["AUTHENTICATION_RESULTS_UNKNOWN"],
      finding_summary: {
        findings: [
          {
            code: "AUTHENTICATION_RESULTS_UNKNOWN",
            category: "AUTHENTICATION",
            severity: "MEDIUM",
          },
        ],
        sorted_findings: [
          {
            code: "AUTHENTICATION_RESULTS_UNKNOWN",
            category: "AUTHENTICATION",
            severity: "MEDIUM",
          },
        ],
        finding_counts_by_category: {
          AUTHENTICATION: 1,
        },
        highest_severity: "MEDIUM",
        total_findings: 1,
      },
      risk_score: {
        indicators: ["AUTHENTICATION_RESULTS_UNKNOWN"],
        raw_score: 15,
        capped_score: 15,
        risk_level: "LOW",
        has_critical_indicators: false,
      },
    });

    render(<App />);

    const input = emailFileInput();
    const emailFile = new File(["sample"], "sample.eml", {
      type: "message/rfc822",
    });

    await user.upload(input, emailFile);
    await user.click(screen.getAllByRole("button", { name: "Analyze email" })[0]);

    expect(await screen.findByText("Analysis completed")).toBeInTheDocument();
    expect(screen.getByText("Results are shown below using the current backend response model.")).toBeInTheDocument();
  });
});
