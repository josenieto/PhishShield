export type FindingResponse = {
  code: string;
  category: string;
  severity: string;
};

export type FindingSummaryResponse = {
  findings: FindingResponse[];
  sorted_findings: FindingResponse[];
  finding_counts_by_category: Record<string, number>;
  highest_severity: string;
  total_findings: number;
};

export type RiskScoreResponse = {
  indicators: string[];
  raw_score: number;
  capped_score: number;
  risk_level: string;
  has_critical_indicators: boolean;
};

export type AuthenticationResultsResponse = {
  spf_result: string;
  dkim_result: string;
  dmarc_result: string;
};

export type ExtractedEvidenceResponse = {
  sender_domain: string;
  subject: string;
  urls: string[];
  attachment_filenames: string[];
  authentication_results: AuthenticationResultsResponse;
};

export type AnalyzeEmailResponse = {
  finding_codes: string[];
  unique_finding_codes: string[];
  finding_summary: FindingSummaryResponse;
  risk_score: RiskScoreResponse;
  extracted_evidence: ExtractedEvidenceResponse;
};
