type IndicatorCodesProps = {
  findingCodes: string[];
};


export function IndicatorCodes({ findingCodes }: IndicatorCodesProps) {
  return (
    <section className="findings-panel">
      <div className="panel-heading">
        <h2>Indicator codes</h2>
        <p>Unique finding codes returned by the backend for the selected message.</p>
      </div>

      <div className="indicator-chip-grid">
        {findingCodes.length === 0 ? (
          <span className="indicator-chip indicator-chip-safe">No findings</span>
        ) : (
          findingCodes.map((findingCode) => (
            <span key={findingCode} className="indicator-chip">
              {findingCode}
            </span>
          ))
        )}
      </div>
    </section>
  );
}
