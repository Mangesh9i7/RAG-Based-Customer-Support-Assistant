import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav
      className="navbar navbar-expand-lg bg-white fixed-top shadow-lg
     border-bottom mb-5"
    >
      <div className="container-fluid">
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item mx-2">
              <Link className="nav-link active fs-5" to="/ChatPage">
                Chat Section
              </Link>
            </li>
            <li className="nav-item mx-2">
              <Link className="nav-link active fs-5" to="/HomePage">
                Home
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
