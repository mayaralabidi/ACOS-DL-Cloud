import { Link, useLocation } from "react-router-dom";

import { ThemeToggle } from "./ThemeToggle";

export function Header({
  sessionId,
  runningTotal,
  env = "dev",
  isHealthy = true,
}) {
  const location = useLocation();

  return (
    <header className="app-header">
      <span className="brand">ACOS</span>

      <span className="env-pill">{env.toUpperCase()}</span>

      <nav className="top-nav" aria-label="Primary">
        <Link
          className={location.pathname === "/checkout" ? "active" : ""}
          to="/checkout"
        >
          Checkout
        </Link>
        <Link
          className={location.pathname === "/history" ? "active" : ""}
          to="/history"
        >
          History
        </Link>
      </nav>

      <div className="header-spacer" />

      {sessionId ? (
        <span className="header-session-id">{sessionId.slice(0, 8)}</span>
      ) : null}

      {runningTotal !== null ? (
        <span className="header-total">{runningTotal.toFixed(3)} TND</span>
      ) : null}

      <ThemeToggle />

      <div className="health-dot" data-healthy={isHealthy} />
    </header>
  );
}
