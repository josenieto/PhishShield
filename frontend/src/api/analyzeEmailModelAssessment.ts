import type { AnalyzeEmailModelAssessmentResponse } from "../types/api";


function buildModelAssessmentErrorMessage(status: number, detail?: string): string {
  if (status === 413) {
    return "The selected email exceeds the configured upload limit.";
  }

  if (status === 422) {
    return detail ?? "The uploaded email could not be assessed by the model.";
  }

  return detail ?? `Model assessment failed with status ${status}.`;
}


export async function analyzeEmailModelAssessment(
  file: File,
): Promise<AnalyzeEmailModelAssessmentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;

  try {
    response = await fetch("/api/analyze-email-model-assessment", {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error("The backend is not reachable. Start the API and try again.");
  }

  if (!response.ok) {
    const errorPayload = (await response.json().catch(() => null)) as
      | { detail?: string }
      | null;

    throw new Error(buildModelAssessmentErrorMessage(response.status, errorPayload?.detail));
  }

  return (await response.json()) as AnalyzeEmailModelAssessmentResponse;
}
