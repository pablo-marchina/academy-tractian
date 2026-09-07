import { expect, test } from "@playwright/test";

async function openProduct(page: import("@playwright/test").Page) {
  await page.context().setExtraHTTPHeaders({
    "x-e2e-user": "ux-pilot-user",
    "x-e2e-organization": "ux-pilot-org",
  });
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
}

test.describe("Release 0 first-user UX", () => {
  test("explains the read-only product and guided intents before engineering detail", async ({ page }) => {
    await openProduct(page);

    await expect(page.getByRole("heading", { name: "Investigate industrial evidence without guessing." })).toBeVisible();
    await expect(page.getByText("No external actions")).toBeVisible();
    await expect(page.getByText("QUICK START")).toBeVisible();
    await expect(page.getByRole("heading", { name: "What do you need to understand?" })).toBeVisible();

    const investigate = page.locator(".experience-intents button").filter({ hasText: "INVESTIGATE" }).first();
    await expect(investigate).toBeVisible();
    await investigate.click();
    await expect(page.getByLabel("Industrial request")).not.toHaveValue("");

    await expect(page.getByText("ENGINEERING DETAILS")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Industrial capability & readiness" })).toBeVisible();
  });

  test("turns a safe terminal mode into a customer-first next step", async ({ page }) => {
    await openProduct(page);

    await page.getByLabel("Industrial request").fill("scenario:clarify");
    await page.getByRole("button", { name: "Start production run" }).click();

    const outcome = page.getByTestId("customer-outcome-summary");
    await expect(outcome).toBeVisible({ timeout: 20_000 });
    await expect(outcome.getByRole("heading", { name: "More context needed" })).toBeVisible();
    await expect(outcome).toContainText("What to do next");
    await expect(outcome).toContainText("Provide the missing context");
    await expect(outcome).toContainText("SUPPORTING EVIDENCE");

    await expect(page.locator(".terminal-panel")).toContainText("ASK_CLARIFICATION");
    await expect(page.locator(".evaluation-panel")).toContainText("blocking checks passed");
  });
});
