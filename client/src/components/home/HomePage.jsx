import { useNavigate } from "react-router-dom";
import "./HomePage.css";

const helpTopics = [
  ["01", "Orders & delivery"],
  ["02", "Returns & refunds"],
  ["03", "Account help"],
];

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <main className="support-home">
      <header className="home-header">
        <a className="home-brand" href="/" aria-label="Customer care home">
          <span className="home-brand-mark" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none">
              <path
                d="M8 16.5 13.2 22 24 10"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span>Customer care</span>
        </a>
        <button
          className="home-header-link"
          type="button"
          onClick={() => navigate("/chat")}
        >
          Go to support <span aria-hidden="true">&rarr;</span>
        </button>
      </header>

      <section className="home-hero">
        <div className="home-hero-copy">
          <span className="home-eyebrow">HERE WHEN YOU NEED US</span>
          <h1>A little help,<br />right when you need it.</h1>
          <p>
            Get clear guidance on orders, returns, and your account. Tell us
            what’s going on and we’ll help you find the next step.
          </p>
          <button
            className="home-primary-button"
            type="button"
            onClick={() => navigate("/chat")}
          >
            Ask us a question
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path
                d="M3.5 10h12m-5-5 5 5-5 5"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <span className="home-response-note">
            No forms to fill out. Just tell us what you need.
          </span>
        </div>

        <aside className="home-topics" aria-label="Support topics">
          <div className="home-topics-heading">
            <span className="home-topics-mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 7.5h14M5 12h9M5 16.5h11"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                />
              </svg>
            </span>
            <div>
              <span className="home-topics-overline">A GOOD PLACE TO START</span>
              <h2>We can help with</h2>
            </div>
          </div>
          <ul className="home-topic-list">
            {helpTopics.map(([number, label]) => (
              <li key={number}>
                <span className="home-topic-number">{number}</span>
                <span>{label}</span>
                <span className="home-topic-arrow" aria-hidden="true">
                  &rarr;
                </span>
              </li>
            ))}
          </ul>
          <p className="home-topics-note">
            Not sure where to begin? That’s okay. Ask in your own words.
          </p>
        </aside>
      </section>

      <footer className="home-footer">
        <span>Thoughtful help, without the runaround.</span>
        <span>Customer care</span>
      </footer>
    </main>
  );
}
