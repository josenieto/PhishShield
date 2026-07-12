import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import App from "./App";


function emailFileInput(): HTMLInputElement {
  return screen.getAllByLabelText(/email file/i, { selector: "input" })[0] as HTMLInputElement;
}


describe("App", () => {
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
    const user = userEvent.setup();
    render(<App />);

    const input = emailFileInput();
    const invalidFile = new File(["hello"], "notes.txt", { type: "text/plain" });

    await user.upload(input, invalidFile);

    expect(
      await screen.findByText("Only .eml files are supported in the current frontend MVP."),
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
});
