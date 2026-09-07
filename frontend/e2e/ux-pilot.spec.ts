import { expect, test, type Page } from "@playwright/test";

async function openProduct(page: Page) {
  await page.context().setExtraHTTPHeaders({
    "x-e2e-user": "ux-pilot-user",
    "x-e2e-organization": "ux-pilot-org",
  });
  await page.goto("/");
  await expect(page.locator(".task-service-state")).toContainText("Online");
  await expect(page.getByRole("heading", { name: "What do you want to understand?" })).toBeVisible();
}

async function submitScenario(page: Page, scenario: string) {
  await page.getByRole("button", { name: "Home", exact: true }).click();
  await page.getByLabel("Question about your equipment").fill(scenario);
  await page.getByRole("button", { name: "Analyse" }).click();
  await expect(page.getByTestId("customer-outcome-summary")).toBeVisible({ timeout: 20_000 });
}

async function openTechnicalSection(
  page: Page,
  section: "Current analysis" | "Quality" | "Data" | "System" | "Actions" | "Studies",
) {
  await page.getByRole("button", { name: "Technical", exact: true }).click();
  const task = page.locator(".technical-task-menu").getByRole("button", { name: new RegExp(`^${section}`) });
  await task.click();
  await expect(task).toHaveAttribute("aria-current", "page");
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 1);
}

test.describe("task-driven low-literacy UX", () => {
  test("keeps entry focused on one question and one primary action", async ({ page }) => {
    await openProduct(page);

    await expect(page.getByRole("button", { name: "Home", exact: true })).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("button", { name: "Analyses", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Technical", exact: true })).toBeVisible();
    await expect(page.getByLabel("Question about your equipment")).toBeVisible();
    await expect(page.getByRole("button", { name: "Analyse" })).toBeVisible();

    await expect(page.getByText("Checks live data")).toHaveCount(0);
    await expect(page.getByText("Shows its evidence")).toHaveCount(0);
    await expect(page.getByText("Does not guess")).toHaveCount(0);
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toHaveCount(0);
    await expect(page.getByRole("heading", { name: "Trace" })).toHaveCount(0);

    const examples = page.getByText("See example questions");
    await expect(examples).toBeVisible();
    await expect(page.getByText("Which equipment needs attention today, and why?")).toBeHidden();
    await examples.click();
    const example = page.getByRole("button", { name: "Which equipment needs attention today, and why?" });
    await expect(example).toBeVisible();
    await example.click();
    await expect(page.getByLabel("Question about your equipment")).toHaveValue("Which equipment needs attention today, and why?");

    await page.getByRole("button", { name: "Analyses", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Analyses", exact: true })).toBeVisible();
    await expect(page.locator("table")).toHaveCount(0);

    await page.setViewportSize({ width: 390, height: 844 });
    await assertNoHorizontalOverflow(page);
  });

  test("shows result, next step and evidence as a contextual sequence", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:clarify");

    const outcome = page.getByTestId("customer-outcome-summary");
    await expect(outcome.getByRole("heading", { name: "More information is needed" })).toBeVisible();
    await expect(outcome).toContainText("What to do next");
    await expect(outcome).toContainText("Add the information requested");
    await expect(outcome).not.toContainText("ASK_CLARIFICATION");
    await expect(outcome.getByRole("button", { name: "View evidence" })).toBeVisible();

    await outcome.getByRole("button", { name: "View evidence" }).click();
    await expect(page.getByRole("heading", { name: "Why did we reach this conclusion?" })).toBeVisible();
    await expect(page.getByRole("button", { name: "← Result" })).toBeVisible();
    await expect(page.locator("main")).not.toContainText("ASK_CLARIFICATION");

    await openTechnicalSection(page, "Quality");
    await expect(page.locator(".evaluation-panel")).toContainText("blocking checks passed");
  });

  test("history is a keyboard-focusable recognition list", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:clarify");

    await page.getByRole("button", { name: "Analyses", exact: true }).click();
    const firstAnalysis = page.locator(".task-run-button").first();
    await expect(firstAnalysis).toBeVisible();
    await firstAnalysis.focus();
    await expect(firstAnalysis).toBeFocused();
    await firstAnalysis.press("Enter");
    await expect(page.getByTestId("customer-outcome-summary")).toBeVisible();
  });

  test("technical depth is grouped by task instead of shown all at once", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:slow investigate asset evidence");
    await expect(page.getByTestId("customer-outcome-summary")).toBeVisible({ timeout: 20_000 });

    await openTechnicalSection(page, "Current analysis");
    await expect(page.getByRole("heading", { name: "Trace" })).toBeVisible();
    await expect(page.getByText("Read the process as a list")).toBeVisible();
    await page.getByText("Read the process as a list").click();
    await expect(page.locator(".trace-text-alternative li").first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Production health" })).toHaveCount(0);

    await openTechnicalSection(page, "System");
    await expect(page.getByRole("heading", { name: "Production health" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture" })).toBeVisible();
    await expect(page.locator(".architecture-component-button").first()).toBeVisible();
    await page.locator(".architecture-component-button").first().focus();
    await expect(page.locator(".architecture-component-button").first()).toBeFocused();
    await expect(page.getByRole("heading", { name: "Output lineage" })).toHaveCount(0);

    await openTechnicalSection(page, "Data");
    const dynamic = page.locator("#dynamic-data-explorer");
    await expect(dynamic.getByRole("heading", { name: "Dynamic Data Explorer" })).toBeVisible();
    await expect(dynamic.getByText("2. Optional filter")).toBeVisible();
  });

  test("consequential actions keep consequence before confirmation", async ({ page }) => {
    await openProduct(page);
    await submitScenario(page, "scenario:pending-action");
    await openTechnicalSection(page, "Actions");

    const actionCard = page.locator(".action-card").first();
    await expect(actionCard).toContainText("Before you confirm");
    await expect(actionCard).toContainText("Confirm only if this is the intended action");
    await expect(actionCard.getByText("Technical identifiers")).toBeVisible();
    await expect(actionCard.getByText("Fingerprint", { exact: true })).toBeHidden();
    await expect(actionCard.getByRole("button", { name: "Confirm exact action" })).toBeVisible();
  });
});
