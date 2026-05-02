import { useNavigate } from "react-router-dom";
import "./HomePage.css";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      {/* Navigation */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">
            {/* Font Awesome Robot Icon */}
            <i className="fa-solid fa-robot" style={{ fontSize: "28px" }}></i>
          </div>
          <h1>Support AI</h1>
        </div>
        <div className="navbar-links">
          <a href="#features">Features</a>
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              navigate("/chat");
            }}
          >
            Chat
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="hero-badge-dot"></span>
            AI-Powered Assistant
          </div>

          <h1>Intelligent Customer Support, Powered by RAG</h1>

          <p className="hero-description">
            Experience the next generation of customer support. Our AI assistant
            combines advanced retrieval-augmented generation with your existing
            knowledge base to provide instant, accurate, and context-aware
            responses to every customer query.
          </p>

          <div className="hero-cta">
            <button className="btn-primary" onClick={() => navigate("/chat")}>
              {/* Font Awesome Chat Icon */}
              <i
                className="fa-solid fa-comment-dots"
                style={{ marginRight: "8px" }}
              ></i>
              Start Chat
            </button>

            <button
              className="btn-secondary"
              onClick={() =>
                document
                  .getElementById("features")
                  .scrollIntoView({ behavior: "smooth" })
              }
            >
              Learn More
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <div className="features-container">
          <div className="features-header">
            <h2>Why Choose Our Assistant?</h2>
            <p>
              Built with cutting-edge AI technology to transform how you handle
              customer inquiries.
            </p>
          </div>

          <div className="features-grid">
            {/* Feature 1 */}
            <div className="feature-card">
              <div className="feature-icon">
                <i
                  className="fa-solid fa-bolt"
                  style={{ fontSize: "32px" }}
                ></i>
              </div>
              <h3>Instant Answers</h3>
              <p>
                Get immediate responses to customer questions. No more waiting
                in queue or searching through endless documentation.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="feature-card">
              <div className="feature-icon">
                <i
                  className="fa-solid fa-database"
                  style={{ fontSize: "32px" }}
                ></i>
              </div>
              <h3>Knowledge Powered</h3>
              <p>
                Leverages your entire knowledge base—documentation, FAQ files,
                and past support tickets. Every answer is grounded in your data.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="feature-card">
              <div className="feature-icon">
                <i
                  className="fa-solid fa-brain"
                  style={{ fontSize: "32px" }}
                ></i>
              </div>
              <h3>Smart Context</h3>
              <p>
                Remembers conversation history and understands context. Ask
                follow-up questions naturally, just like a human agent.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 RAG Customer Support Assistant. All rights reserved.</p>
      </footer>
    </div>
  );
}
