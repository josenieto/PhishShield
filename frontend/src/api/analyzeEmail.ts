import type { AnalyzeEmailResponse } from "../types/api";

export async function analyzeEmail(file: File): Promise<AnalyzeEmailResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/analyze-email", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorPayload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;

    throw new Error(
      errorPayload?.detail ?? `Email analysis failed with status ${response.status}.`,
    );
  }

  return (await response.json()) as AnalyzeEmailResponse;
}
