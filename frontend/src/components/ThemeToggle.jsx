import { useTheme } from "../hooks/useTheme";

const SunIcon = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 14 14"
    fill="none"
    aria-hidden="true"
  >
    <circle cx="7" cy="7" r="3" stroke="currentColor" strokeWidth="1.5" />
    <line
      x1="7"
      y1="0.5"
      x2="7"
      y2="2.5"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <line
      x1="7"
      y1="11.5"
      x2="7"
      y2="13.5"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <line
      x1="0.5"
      y1="7"
      x2="2.5"
      y2="7"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
    <line
      x1="11.5"
      y1="7"
      x2="13.5"
      y2="7"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

const MoonIcon = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 14 14"
    fill="none"
    aria-hidden="true"
  >
    <path
      d="M12 7.5A5.5 5.5 0 0 1 6.5 2a5.5 5.5 0 1 0 5.5 5.5z"
      fill="currentColor"
      opacity="0.85"
    />
  </svg>
);

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      onClick={toggle}
      aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
      className="theme-toggle"
      type="button"
    >
      {isDark ? <SunIcon /> : <MoonIcon />}
      {isDark ? "Light" : "Dark"}
    </button>
  );
}
