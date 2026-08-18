type RiskScoreValues = {
  raw_score: number;
  capped_score: number;
};


export function formatRiskScore(score: RiskScoreValues): string {
  return `Score: ${score.capped_score}/100`;
}


export function formatRiskScoreDetails(score: RiskScoreValues): string {
  return score.raw_score === score.capped_score
    ? `Raw score: ${score.raw_score}`
    : `Raw score: ${score.raw_score} (capped at 100)`;
}
