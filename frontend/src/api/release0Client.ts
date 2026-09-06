import type { Release0CapabilityManifest } from "./release0Types";

export async function fetchRelease0Capabilities(): Promise<Release0CapabilityManifest> {
  const response = await fetch("/api/release0/capabilities", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`release0 capabilities unavailable: ${response.status}`);
  }
  return (await response.json()) as Release0CapabilityManifest;
}
