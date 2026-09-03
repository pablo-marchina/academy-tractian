import { expect, test, type Page } from "@playwright/test";

const PRIVATE_KEYS = new Set([
  "pair_id",
  "scenario_id",
  "case_id",
  "group_id",
  "source_split",
  "operator_ref",
  "operator_ref_sha256",
  "host_session_id",
  "private_truth",
  "oracle",
  "gold",
]);

function actorHeaders(user: string, organization: string): Record<string, string> {
  return {
    "x-e2e-user": user,
    "x-e2e-organization": organization,
  };
}

function scanPrivateKeys(value: unknown, path: string, violations: string[]): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanPrivateKeys(item, `${path}[${index}]`, violations));
    return;
  }
  if (!value || typeof value !== "object") return;
  for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
    if (PRIVATE_KEYS.has(key.toLowerCase())) violations.push(`${path}.${key}`);
    scanPrivateKeys(nested, `${path}.${key}`, violations);
  }
}

async function openParticipant(page: Page, user = "e2e-pilot-user-a", organization = "e2e-org-a") {
  await page.context().setExtraHTTPHeaders(actorHeaders(user, organization));
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Engineer effort study" })).toBeVisible();
}

async function loadTask(page: Page) {
  const responsePromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/api/operational-value/tasks/next"
      && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: /Load (next assigned|another) task/ }).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  const body = await response.json() as {
    assignment_id: string;
    packet_id: string;
    task: {
      task_id: string;
      condition: "MANUAL" | "ASSISTED";
      ticket_request: string;
      assistance: unknown;
    };
  };
  const violations: string[] = [];
  scanPrivateKeys(body, "assignment", violations);
  expect(violations).toEqual([]);
  await expect(page.getByTestId("operational-value-task")).toBeVisible();
  return body;
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 1);
}

test.describe("operational value human-effort collector", () => {
  test("server-timed manual completion then assisted interruption stay blinded", async ({ page }) => {
    await openParticipant(page);

    const manual = await loadTask(page);
    expect(manual.task.condition).toBe("MANUAL");
    expect(manual.task.assistance).toBeNull();
    await expect(page.getByTestId("operational-value-manual")).toBeVisible();
    await expect(page.getByTestId("operational-value-assistance")).toHaveCount(0);
    await expect(page.locator(".pilot-panel")).not.toContainText(/\b\d+(?:\.\d+)?\s*(?:s|sec|seconds)\b/i);

    await page.getByLabel("Operational decision").selectOption("FINAL");
    await page.getByLabel("Operational conclusion").fill(
      "The available evidence supports waiting for the pending analysis before corrective action.",
    );
    const completeRequestPromise = page.waitForRequest((request) =>
      new URL(request.url()).pathname.endsWith(`/assignments/${manual.assignment_id}/complete`)
      && request.method() === "POST",
    );
    const completeResponsePromise = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${manual.assignment_id}/complete`)
      && response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "Record completed investigation" }).click();
    const completeRequest = await completeRequestPromise;
    const submitted = completeRequest.postDataJSON() as Record<string, unknown>;
    expect(submitted).toEqual({
      terminal_decision: "FINAL",
      conclusion_summary: "The available evidence supports waiting for the pending analysis before corrective action.",
    });
    expect(submitted).not.toHaveProperty("elapsed_seconds");
    const completeResponse = await completeResponsePromise;
    expect(completeResponse.status()).toBe(200);
    const completion = await completeResponse.json() as { status: string; elapsed_seconds: number | null };
    expect(completion.status).toBe("VALID");
    expect(completion.elapsed_seconds).toBeGreaterThan(0);
    await expect(page.locator(".pilot-completion")).toContainText("VALID");
    await expect(page.locator(".pilot-completion")).not.toContainText(String(completion.elapsed_seconds));

    const assisted = await loadTask(page);
    expect(assisted.task.condition).toBe("ASSISTED");
    expect(assisted.task.assistance).not.toBeNull();
    await expect(page.getByTestId("operational-value-assistance")).toBeVisible();
    await expect(page.getByTestId("operational-value-manual")).toHaveCount(0);

    const terminationRequestPromise = page.waitForRequest((request) =>
      new URL(request.url()).pathname.endsWith(`/assignments/${assisted.assignment_id}/terminate`)
      && request.method() === "POST",
    );
    const terminationResponsePromise = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${assisted.assignment_id}/terminate`)
      && response.request().method() === "POST",
    );
    await page.getByRole("button", { name: "Mark interrupted" }).click();
    const terminationRequest = await terminationRequestPromise;
    expect(terminationRequest.postDataJSON()).toEqual({ status: "INTERRUPTED" });
    const terminationResponse = await terminationResponsePromise;
    expect(terminationResponse.status()).toBe(200);
    const termination = await terminationResponse.json() as { status: string; elapsed_seconds: number | null };
    expect(termination).toMatchObject({ status: "INTERRUPTED", elapsed_seconds: null });
    await expect(page.locator(".pilot-completion")).toContainText("INTERRUPTED");

    await page.setViewportSize({ width: 390, height: 844 });
    await assertNoHorizontalOverflow(page);
  });

  test("tenant and owner isolation apply to participant assignments", async ({ browser, page }) => {
    await openParticipant(page, "e2e-pilot-user-b", "e2e-org-a");
    const assignment = await loadTask(page);

    const wrongOwnerContext = await browser.newContext({
      baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173",
      extraHTTPHeaders: actorHeaders("e2e-pilot-user-c", "e2e-org-a"),
    });
    const wrongTenantContext = await browser.newContext({
      baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173",
      extraHTTPHeaders: actorHeaders("e2e-pilot-user-b", "e2e-org-b"),
    });
    try {
      const wrongOwner = await wrongOwnerContext.request.post(
        `/api/operational-value/assignments/${assignment.assignment_id}/terminate`,
        { data: { status: "WITHDRAWN" } },
      );
      expect(wrongOwner.status()).toBe(404);

      const wrongTenant = await wrongTenantContext.request.post("/api/operational-value/tasks/next");
      expect(wrongTenant.status()).toBe(404);

      const forged = await page.request.post(
        `/api/operational-value/assignments/${assignment.assignment_id}/terminate`,
        { data: { status: "TECHNICAL_FAILURE" } },
      );
      expect(forged.status()).toBe(422);
    } finally {
      await wrongOwnerContext.close();
      await wrongTenantContext.close();
    }

    await page.getByRole("button", { name: "Withdraw trial" }).click();
    await expect(page.locator(".pilot-completion")).toContainText("WITHDRAWN");
  });
});
