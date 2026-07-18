import { sanitizeReportFileName } from "./reportFileName";

import type { AnalyzeEmailResponse } from "../types/api";


type DownloadJsonReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export function downloadJsonReport({ analysis, selectedFileName }: DownloadJsonReportParams): void {
  const reportContent = JSON.stringify(
    {
      selected_file_name: selectedFileName,
      analysis,
    },
    null,
    2,
  );
  const blob = new Blob([reportContent], { type: "application/json;charset=utf-8" });
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");

  anchor.href = objectUrl;
  anchor.download = `phishshield-analysis-${sanitizeReportFileName(selectedFileName)}.json`;
  anchor.click();

  URL.revokeObjectURL(objectUrl);
}
