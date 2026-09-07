export type PrimaryDestination = "home" | "history" | "technical";

const DESTINATIONS: Array<{ id: PrimaryDestination; label: string }> = [
  { id: "home", label: "Home" },
  { id: "history", label: "Analyses" },
];

export function PrimaryNavigation({
  current,
  onNavigate,
}: {
  current: PrimaryDestination;
  onNavigate: (destination: PrimaryDestination) => void;
}) {
  return (
    <nav className="primary-navigation" aria-label="Main navigation">
      <div className="primary-navigation-main">
        {DESTINATIONS.map((destination) => (
          <button
            key={destination.id}
            type="button"
            className={current === destination.id ? "is-active" : undefined}
            aria-current={current === destination.id ? "page" : undefined}
            onClick={() => onNavigate(destination.id)}
          >
            {destination.label}
          </button>
        ))}
      </div>
      <button
        type="button"
        className={`technical-navigation-link ${current === "technical" ? "is-active" : ""}`}
        aria-current={current === "technical" ? "page" : undefined}
        onClick={() => onNavigate("technical")}
      >
        Technical
      </button>
    </nav>
  );
}
