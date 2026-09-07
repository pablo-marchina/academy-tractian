import { expect, test } from "@playwright/test";

async function openProduct(page: import("@playwright/test").Page) {
  await page.context().setExtraHTTPHeaders({
    "x-e2e-user": "ux-pilot-user",
    "x-e2e-organization": "ux-pilot-org",
  });
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
}

test.describe("Release 0 progressive-depth UX", () => {
  test("starts with results and progressively discloses deeper observability", async ({ page }) => {
    await openProduct(page);

    const resultsTab = page.getByRole("tab", { name: /Results/ });
    const evidenceTab = page.getByRole("tab", { name: /Evidence/ });
    const investigationTab = page.getByRole("tab", { name: /Investigation/ });
    const engineeringTab = page.getByRole("tab", { name: /Engineering/ });

    await expect(resultsTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "Answer first" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Investigate industrial evidence without guessing." })).toBeVisible();
    await expect(page.getByText("No external actions")).toBeVisible();
    await expect(page.getByText("starter examples only")).toBeVisible();
    await expect(page.getByRole("heading", { name: "What do you need to understand?" })).toBeVisible();

    await expect(page.getByRole("heading", { name: "Canonical event timeline" })).toBeHidden();
    await expect(page.getByRole("heading", { name: "Trace Graph" })).toBeHidden();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeHidden();

    const quickStart = page.getByTestId("quick-start-option").first();
    await expect(quickStart).toBeVisible();
    await quickStart.click();
    await expect(page.getByLabel("Industrial request")).not.toHaveValue("");

    await evidenceTab.click();
    await expect(evidenceTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "See why the answer is supported" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Canonical event timeline" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeHidden();
    await expect(page.getByText("starter examples only")).toBeHidden();

    await investigationTab.click();
    await expect(page.getByRole("heading", { name: "Inspect how the investigation ran" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Trace Graph" })).toBeVisible();

    await engineeringTab.click();
    await expect(page.getByRole("heading", { name: "Open the full observability surface" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeVisible();
    await expect(page.getByText("Capability contract unavailable")).toBeVisible();

    await engineeringTab.press("Home");
    await expect(resultsTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "Answer first" })).toBeVisible();

    await resultsTab.press("End");
    await expect(engineeringTab).toHaveAttribute("aria-selected", "true");
  });

  test("keeps the safe outcome primary while technical proof is available on deeper tabs", async ({ page }) => {
    await openProduct(page);

    await page.getByLabel("Industrial request").fill("scenario:clarify");
    await page.getByRole("button", { name: "Start production run" }).click();

    const outcome = page.getByTestId("customer-outcome-summary");
    await expect(outcome).toBeVisible({ timeout: 20_000 });
    await expect(outcome.getByRole("heading", { name: "More context needed" })).toBeVisible();
    await expect(outcome).toContainText("What to do next");
    await expect(outcome).toContainText("Provide the missing context");
    await expect(outcome).toContainText("SUPPORTING EVIDENCE");

    await page.getByRole("tab", { name: /Evidence/ }).click();
    await expect(page.locator(".terminal-panel")).toBeVisible();
    await expect(page.locator(".terminal-panel")).toContainText("ASK_CLARIFICATION");

    await page.getByRole("tab", { name: /Engineering/ }).click();
    await expect(page.locator(".evaluation-panel")).toBeVisible();
    await expect(page.locator(".evaluation-panel")).toContainText("blocking checks passed");
  });
});
