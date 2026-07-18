import { createMarkdownReport } from "./createMarkdownReport";
import { sanitizeReportFileName } from "./reportFileName";

import type { AnalyzeEmailResponse } from "../types/api";


type DownloadMarkdownReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


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
