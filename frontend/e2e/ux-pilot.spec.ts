import { expect, test } from "@playwright/test";

async function openProduct(page: import("@playwright/test").Page) {
  await page.context().setExtraHTTPHeaders({
    "x-e2e-user": "ux-pilot-user",
    "x-e2e-organization": "ux-pilot-org",
  });
  await page.goto("/");
  await expect(page.getByText("System online")).toBeVisible();
}

async function submitScenario(page: import("@playwright/test").Page, scenario: string) {
  await page.getByRole("tab", { name: /Overview/ }).click();
  await page.getByLabel("What would you like to understand?").fill(scenario);
  await page.getByRole("button", { name: "Start analysis" }).click();
  await expect(page.getByTestId("customer-outcome-summary")).toBeVisible({ timeout: 20_000 });
}

test.describe("user-first progressive disclosure UX", () => {
  test("keeps the primary path understandable without runtime vocabulary", async ({ page }) => {
    await openProduct(page);

    const overviewTab = page.getByRole("tab", { name: /Overview/ });
    const evidenceTab = page.getByRole("tab", { name: /Why this answer/ });
    const historyTab = page.getByRole("tab", { name: /History/ });
    const technicalTab = page.getByRole("tab", { name: /Technical details/ });

    await expect(overviewTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "What would you like to understand?" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Ask about your equipment in your own words." })).toBeVisible();
    await expect(page.getByText("You do not need to know technical commands or internal IDs.")).toBeVisible();
    await expect(page.getByText("Does not guess")).toBeVisible();
    await expect(page.getByText("Does not change equipment")).toBeVisible();
    await expect(page.getByLabel("What would you like to understand?")).toBeVisible();

    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeHidden();
    await expect(page.getByRole("heading", { name: "Trace graph" })).toBeHidden();
    await expect(page.locator(".metric-grid")).toBeHidden();

    const quickStart = page.getByTestId("quick-start-option").first();
    await expect(quickStart).toBeVisible();
    await quickStart.click();
    await expect(page.getByLabel("What would you like to understand?")).not.toHaveValue("");

    await evidenceTab.click();
    await expect(evidenceTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "See what the assistant checked" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "What happened during the analysis" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeHidden();

    await historyTab.click();
    await expect(page.getByRole("heading", { name: "Review previous analyses" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Previous analyses", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Trace graph" })).toBeHidden();
    await page.getByText("Show how this analysis ran").click();
    await expect(page.getByRole("heading", { name: "Trace graph" })).toBeVisible();

    await technicalTab.click();
    await expect(page.getByRole("heading", { name: "Engineering and evaluation" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeVisible();
    await expect(page.getByText("Capability contract unavailable")).toBeVisible();

    await technicalTab.press("Home");
    await expect(overviewTab).toHaveAttribute("aria-selected", "true");
    await expect(page.getByRole("heading", { name: "What would you like to understand?" })).toBeVisible();

    await overviewTab.press("End");
    await expect(technicalTab).toHaveAttribute("aria-selected", "true");
  });

  test("shows a plain-language outcome while raw codes stay opt-in", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:clarify");

    const outcome = page.getByTestId("customer-outcome-summary");
    await expect(outcome.getByRole("heading", { name: "More information needed" })).toBeVisible();
    await expect(outcome).toContainText("What to do next");
    await expect(outcome).toContainText("Add the information requested");
    await expect(outcome).toContainText("INFORMATION CHECKED");
    await expect(outcome).not.toContainText("ASK_CLARIFICATION");

    await page.getByRole("button", { name: "See why this answer" }).click();
    await expect(page.locator(".terminal-panel")).toBeVisible();
    await expect(page.locator(".terminal-panel")).toContainText("More information needed");
    await expect(page.getByText("ASK_CLARIFICATION", { exact: true })).toBeHidden();

    await page.getByText("Show internal result codes").click();
    await expect(page.getByText("ASK_CLARIFICATION", { exact: true })).toBeVisible();

    await page.getByRole("tab", { name: /Technical details/ }).click();
    await expect(page.locator(".evaluation-panel")).toBeVisible();
    await expect(page.locator(".evaluation-panel")).toContainText("blocking checks passed");
  });

  test("history uses explicit keyboard-focusable controls instead of clickable rows", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:clarify");

    await page.getByRole("tab", { name: /History/ }).click();
    const firstAnalysis = page.getByRole("button", { name: /Analysis 1/ }).first();
    await expect(firstAnalysis).toBeVisible();
    await firstAnalysis.focus();
    await expect(firstAnalysis).toBeFocused();
    await firstAnalysis.press("Enter");
    await expect(page.getByRole("tab", { name: /Overview/ })).toHaveAttribute("aria-selected", "true");
  });

  test("technical visualizations retain readable keyboard-accessible alternatives", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:slow investigate asset evidence");

    await page.getByRole("tab", { name: /History/ }).click();
    await page.getByText("Show how this analysis ran").click();
    await expect(page.getByText("Read the process as a list")).toBeVisible();
    await page.getByText("Read the process as a list").click();
    await expect(page.locator(".trace-text-alternative li").first()).toBeVisible();

    await page.getByRole("tab", { name: /Technical details/ }).click();
    await expect(page.locator(".architecture-component-button").first()).toBeVisible();
    await page.locator(".architecture-component-button").first().focus();
    await expect(page.locator(".architecture-component-button").first()).toBeFocused();

    const dynamic = page.locator("#dynamic-data-explorer");
    await expect(dynamic.getByRole("heading", { name: "Dynamic Data Explorer" })).toBeVisible();
    await expect(dynamic.getByText("2. Optional filter")).toBeVisible();
  });

  test("consequential actions explain the consequence before confirmation", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:pending-action");
    await page.getByRole("tab", { name: /Technical details/ }).click();

    const actionCard = page.locator(".action-card").first();
    await expect(actionCard).toContainText("Before you confirm");
    await expect(actionCard).toContainText("Confirm only if this is the intended action");
    await expect(actionCard.getByText("Technical identifiers")).toBeVisible();
    await expect(actionCard.getByText("Fingerprint", { exact: true })).toBeHidden();
    await expect(actionCard.getByRole("button", { name: "Confirm exact action" })).toBeVisible();
  });
});
