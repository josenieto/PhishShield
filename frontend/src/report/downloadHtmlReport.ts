import { createHtmlReport } from "./createHtmlReport";
import { sanitizeReportFileName } from "./reportFileName";

import type { AnalyzeEmailResponse } from "../types/api";


type DownloadHtmlReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export function downloadHtmlReport({ analysis, selectedFileName }: DownloadHtmlReportParams): void {
  const reportContent = createHtmlReport({ analysis, selectedFileName });
  const blob = new Blob([reportContent], { type: "text/html;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = objectUrl;
  anchor.download = `phishshield-report-${sanitizeReportFileName(selectedFileName)}.html`;
  anchor.click();

  URL.revokeObjectURL(objectUrl);
}
