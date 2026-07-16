import { createMarkdownReport } from "./createMarkdownReport";

import type { AnalyzeEmailResponse } from "../types/api";


type DownloadMarkdownReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


function sanitizeReportFileName(selectedFileName: string): string {
  const normalized = selectedFileName.trim().replace(/\.[^.]+$/, "");
  const safeBaseName = normalized.replace(/[^a-zA-Z0-9-_]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");

  return safeBaseName === "" ? "selected-email" : safeBaseName;
}


export function downloadMarkdownReport({ analysis, selectedFileName }: DownloadMarkdownReportParams): void {
  const reportContent = createMarkdownReport({ analysis, selectedFileName });
  const blob = new Blob([reportContent], { type: "text/markdown;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = objectUrl;
  anchor.download = `phishshield-report-${sanitizeReportFileName(selectedFileName)}.md`;
  anchor.click();

  URL.revokeObjectURL(objectUrl);
}
