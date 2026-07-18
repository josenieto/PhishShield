import { createMarkdownReport } from "./createMarkdownReport";

import type { AnalyzeEmailResponse } from "../types/api";


type CopyMarkdownReportParams = {
  analysis: AnalyzeEmailResponse;
  selectedFileName: string;
};


export async function copyMarkdownReport({
  analysis,
  selectedFileName,
}: CopyMarkdownReportParams): Promise<void> {
  const reportContent = createMarkdownReport({ analysis, selectedFileName });

  await navigator.clipboard.writeText(reportContent);
}
