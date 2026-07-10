export default function App() {
  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">PhishShield</p>
        <h1>Email analysis frontend MVP</h1>
        <p className="lede">
          The backend is ready. This frontend scaffold will become the upload and
          results flow for `.eml` analysis.
        </p>

        <div className="status-grid">
          <article>
            <h2>Backend API</h2>
            <p>`POST /api/analyze-email` proxied to `http://127.0.0.1:8000`.</p>
          </article>
          <article>
            <h2>Next Step</h2>
            <p>Add the first upload form and render risk score plus findings.</p>
          </article>
        </div>
      </section>
    </main>
  );
}
