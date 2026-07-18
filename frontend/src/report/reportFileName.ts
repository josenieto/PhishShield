export function sanitizeReportFileName(selectedFileName: string): string {
  const normalized = selectedFileName.trim().replace(/\.[^.]+$/, "");
  const safeBaseName = normalized.replace(/[^a-zA-Z0-9-_]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");

  return safeBaseName === "" ? "selected-email" : safeBaseName;
}
