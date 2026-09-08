import { expect, test, type Browser, type BrowserContext, type Page } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173";
const RUN_ID = /^run_[0-9a-f]{20}$/;

const FORBIDDEN_KEYS = new Set([
  "identity_id",
  "user_id",
  "seed",
  "authorization",
  "auth_header",
  "credential",
  "credentials",
  "account_id",
  "api_key",
  "raw_request",
  "raw_response",
  "raw_tool_body",
  "raw_observation_body",
  "arguments_json",
  "idempotency_key",
  "chain_of_thought",
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

function scanForbidden(value: unknown, path: string, violations: string[]): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => scanForbidden(item, `${path}[${index}]`, violations));
    return;
  }
  if (!value || typeof value !== "object") return;
  for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
    if (FORBIDDEN_KEYS.has(key.toLowerCase())) violations.push(`${path}.${key}`);
    scanForbidden(nested, `${path}.${key}`, violations);
  }
}

function installJsonLeakAudit(page: Page) {
  const violations: string[] = [];
  const audits: Promise<void>[] = [];
  page.on("response", (response) => {
    const url = new URL(response.url());
    if (!url.pathname.startsWith("/api/") || url.pathname === "/api/stream") return;
    const contentType = response.headers()["content-type"] || "";
    if (!contentType.includes("application/json")) return;
    const audit = response
      .json()
      .then((payload) => scanForbidden(payload, url.pathname, violations))
      .catch(() => undefined);
    audits.push(audit);
  });
  return {
    async assertClean() {
      await Promise.all(audits);
      expect(violations, `forbidden safe-API keys: ${violations.join(", ")}`).toEqual([]);
    },
  };
}

async function configureActor(page: Page, user = "e2e-user-a", organization = "e2e-org-a") {
  await page.context().setExtraHTTPHeaders(actorHeaders(user, organization));
}

async function openProduct(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.locator(".task-service-state")).toContainText("Online");
  await expect(page.getByRole("heading", { name: "What do you want to understand?" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Home", exact: true })).toHaveAttribute("aria-current", "page");
}

async function openHome(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Home", exact: true }).click();
  const questionHeading = page.getByRole("heading", { name: "What do you want to understand?" });
  if (!(await questionHeading.isVisible().catch(() => false))) {
    const newAnalysis = page.getByRole("button", { name: "New analysis", exact: true });
    if (await newAnalysis.isVisible().catch(() => false)) await newAnalysis.click();
  }
  await expect(questionHeading).toBeVisible();
}

async function openHistory(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Analyses", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Analyses", exact: true })).toBeVisible();
}

async function openTechnicalSection(
  page: Page,
  section: "Current analysis" | "Verification" | "Data" | "System" | "Actions" | "Studies",
): Promise<void> {
  await page.getByRole("button", { name: "Technical", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Technical", exact: true })).toBeVisible();
  const task = page.locator(".technical-task-menu").getByRole("button", { name: new RegExp(`^${section}`) });
  await task.click();
  await expect(task).toHaveAttribute("aria-current", "page");
}

async function openCurrentResult(page: Page): Promise<void> {
  await page.getByRole("button", { name: "Home", exact: true }).click();
  const returnButton = page.getByRole("button", { name: "Return to current analysis" });
  if (await returnButton.isVisible().catch(() => false)) await returnButton.click();
}

async function openEvidence(page: Page): Promise<void> {
  await openCurrentResult(page);
  await page.getByRole("button", { name: "View evidence" }).click();
  await expect(page.getByRole("heading", { name: "Why did we reach this conclusion?" })).toBeVisible();
}

async function newActorPage(
  browser: Browser,
  user: string,
  organization: string,
): Promise<{ context: BrowserContext; page: Page }> {
  const context = await browser.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: actorHeaders(user, organization),
  });
  const page = await context.newPage();
  await openProduct(page);
  return { context, page };
}

async function submitScenario(page: Page, scenario: string): Promise<{ run_id: string; [key: string]: unknown }> {
  await openHome(page);
  await page.getByLabel("Question about your equipment").fill(scenario);
  const acceptedPromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/api/runs" && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Analyse", exact: true }).click();
  const response = await acceptedPromise;
  expect(response.status()).toBe(202);
  const accepted = (await response.json()) as { run_id: string; [key: string]: unknown };
  expect(accepted.run_id).toMatch(RUN_ID);
  return accepted;
}

async function waitForCompleted(page: Page): Promise<void> {
  await openCurrentResult(page);
  await expect(page.getByTestId("customer-outcome-summary")).toBeVisible({ timeout: 20_000 });
}

async function fetchJson(
  page: Page,
  path: string,
  init?: { method?: string; body?: unknown },
): Promise<{ status: number; body: unknown }> {
  return page.evaluate(
    async ({ target, requestInit }) => {
      const response = await fetch(target, {
        method: requestInit?.method,
        headers: requestInit?.body === undefined ? undefined : { "Content-Type": "application/json" },
        body: requestInit?.body === undefined ? undefined : JSON.stringify(requestInit.body),
      });
      let body: unknown = null;
      try {
        body = await response.json();
      } catch {
        body = await response.text();
      }
      return { status: response.status, body };
    },
    { target: path, requestInit: init },
  );
}

async function assertSseReplayClean(page: Page, runId: string): Promise<void> {
  const replay = await page.evaluate(async (id) => {
    const response = await fetch(`/api/stream?run_id=${encodeURIComponent(id)}&follow=false`);
    return { status: response.status, text: await response.text() };
  }, runId);
  expect(replay.status).toBe(200);
  const violations: string[] = [];
  for (const line of replay.text.split("\n")) {
    if (!line.startsWith("data: ")) continue;
    scanForbidden(JSON.parse(line.slice(6)), `sse:${runId}`, violations);
  }
  expect(violations, `forbidden SSE keys: ${violations.join(", ")}`).toEqual([]);
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 1);
}

test.describe("provider-free full product acceptance", () => {
  test("simple entry, constrained analytics and responsive viewport", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    await expect(page.getByRole("button", { name: "Home", exact: true })).toHaveAttribute("aria-current", "page");
    await expect(page.getByRole("button", { name: "Analyses", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Technical", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toHaveCount(0);
    await assertNoHorizontalOverflow(page);

    await openHistory(page);
    await expect(page.getByText("No analyses yet. Start from Home and completed analyses will appear here.")).toBeVisible();

    await openTechnicalSection(page, "Current analysis");
    await expect(page.getByRole("heading", { name: "How did this analysis run?" })).toBeVisible();
    await expect(page.getByText("No analysis selected").first()).toBeVisible();

    const longRequest = `scenario:clarify ${"industrial-context ".repeat(450)}`;
    const accepted = await submitScenario(page, longRequest);
    await waitForCompleted(page);
    const outcome = page.getByTestId("customer-outcome-summary");
    await expect(outcome).toContainText("More information is needed");
    await expect(outcome).toContainText("What to do next");
    await expect(outcome).not.toContainText("ASK_CLARIFICATION");

    await openEvidence(page);
    await expect(page.getByRole("heading", { name: "Why did we reach this conclusion?" })).toBeVisible();
    await expect(page.locator("main")).not.toContainText("ASK_CLARIFICATION");

    await openTechnicalSection(page, "Data");
    const dynamic = page.locator("#dynamic-data-explorer");
    await expect(dynamic.getByRole("heading", { name: "Dynamic Data Explorer" })).toBeVisible();
    const chartOptions = await dynamic.getByLabel("Chart").locator("option").allTextContents();
    expect(chartOptions).not.toContain("pie");
    const rejected = await fetchJson(page, "/api/query", {
      method: "POST",
      body: {
        dataset: "events",
        run_id: accepted.run_id,
        dimensions: ["event_type"],
        measure: "count",
        chart_type: "pie",
        filters: [],
        limit: 20,
      },
    });
    expect(rejected.status).toBe(422);

    await page.setViewportSize({ width: 390, height: 844 });
    await assertNoHorizontalOverflow(page);
    await expect(page.getByText("Academy × TRACTIAN")).toBeVisible();

    await assertSseReplayClean(page, accepted.run_id);
    await leakAudit.assertClean();
  });

  test("real runtime, SSE reconnect/catch-up, verification and technical drilldown", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const accepted = await submitScenario(page, "scenario:slow investigate asset evidence");

    await openTechnicalSection(page, "Verification");
    await expect(page.locator(".evaluation-panel")).toContainText("Verification waits for terminal state");

    await openCurrentResult(page);
    await page.context().setOffline(true);
    await expect(page.getByText(/Connection status: reconnecting/i)).toBeAttached({ timeout: 5_000 });
    await page.waitForTimeout(300);
    await page.context().setOffline(false);
    await expect(page.getByText(/Connection status: caught_up/i)).toBeAttached({ timeout: 8_000 });

    await waitForCompleted(page);
    const completedRun = await fetchJson(page, `/api/runs/${accepted.run_id}`);
    expect(completedRun.status).toBe(200);
    expect((completedRun.body as { terminal_reason_code?: string }).terminal_reason_code).toBe("E2E_EVIDENCE_CONFIRMED");
    const completedOutcome = page.getByTestId("customer-outcome-summary");
    await expect(completedOutcome).toContainText("Asset evidence was inspected through the production tool boundary");
    await expect(completedOutcome).not.toContainText("E2E_EVIDENCE_CONFIRMED");

    await openEvidence(page);
    await expect(page.locator(".task-evidence-list")).toBeVisible();
    await expect(page.getByRole("heading", { name: "Equipment details" })).toBeVisible();

    await openTechnicalSection(page, "Current analysis");
    await expect(page.getByRole("heading", { name: "Trace" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Evidence references" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Output lineage" })).toBeVisible();
    await expect(page.locator(".evidence-list")).toContainText("EV-e2e-asset");
    await expect(page.getByRole("heading", { name: "Production health" })).toHaveCount(0);

    const toolsPanel = page.locator("article.panel").filter({
      has: page.getByRole("heading", { name: "Tool activity" }),
    });
    await expect(toolsPanel).toContainText("get_asset");
    await toolsPanel.getByRole("button", { name: "Explore data" }).first().click();
    const dynamic = page.locator("#dynamic-data-explorer");
    await expect(dynamic).toBeVisible();
    await expect(dynamic.locator(".query-result-meta")).toContainText(`scope ${accepted.run_id}`);

    await openTechnicalSection(page, "Verification");
    await expect(page.getByRole("heading", { name: "Selected analysis verification" })).toBeVisible();
    await expect(page.locator(".evaluation-panel")).toContainText("overall hard-gate status");
    await expect(page.locator(".evaluation-panel")).toContainText("Runtime Integrity");
    await expect(page.locator(".evaluation-panel")).toContainText("Functional Success");
    await expect(page.locator(".evaluation-panel")).toContainText("Evidence Sufficiency");
    await expect(page.locator(".evaluation-panel")).not.toContainText("Quality 100%");
    await expect(page.getByRole("heading", { name: "Evaluation metrics" })).toBeVisible();

    await openTechnicalSection(page, "System");
    await expect(page.getByRole("heading", { name: "Production health" })).toBeVisible();
    await expect(page.getByText(/reconnects/).first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Output lineage" })).toHaveCount(0);

    await assertSseReplayClean(page, accepted.run_id);
    await leakAudit.assertClean();
  });

  test("terminal safety modes, blocked action and historical navigation remain inspectable", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const cases = [
      {
        scenario: "scenario:clarify",
        decision: "ASK_CLARIFICATION",
        reasonCode: "E2E_INFORMATION_REQUIRED",
        detail: "Please provide the missing asset identifier",
      },
      {
        scenario: "scenario:abstain",
        decision: "ABSTAIN",
        reasonCode: "E2E_EVIDENCE_UNAVAILABLE",
        detail: "Required evidence is unavailable",
      },
      {
        scenario: "scenario:escalate",
        decision: "ESCALATE_HUMAN",
        reasonCode: "E2E_AMBIGUOUS_EVIDENCE",
        detail: "Collected evidence remains contradictory",
      },
      {
        scenario: "scenario:tool-error",
        decision: "ABSTAIN",
        reasonCode: null,
        detail: "The evidence tool failed",
      },
      {
        scenario: "scenario:blocked-action",
        decision: "ABSTAIN",
        reasonCode: null,
        detail: "high-impact action was blocked",
      },
    ] as const;

    let historicalRunId: string | null = null;
    for (const { scenario, decision, reasonCode, detail } of cases) {
      const accepted = await submitScenario(page, scenario);
      historicalRunId ??= accepted.run_id;
      await waitForCompleted(page);

      const runResponse = await fetchJson(page, `/api/runs/${accepted.run_id}`);
      expect(runResponse.status).toBe(200);
      const safeRun = runResponse.body as {
        terminal_decision?: string;
        terminal_reason_code?: string;
        terminal_message?: string;
      };
      expect(safeRun.terminal_decision).toBe(decision);
      if (reasonCode) expect(safeRun.terminal_reason_code).toBe(reasonCode);
      expect(safeRun.terminal_message).toContain(detail);
      const outcome = page.getByTestId("customer-outcome-summary");
      await expect(outcome).not.toContainText(decision);
      if (reasonCode) await expect(outcome).not.toContainText(reasonCode);

      if (scenario === "scenario:blocked-action") {
        await openTechnicalSection(page, "Current analysis");
        const policyPanel = page.locator("article.panel").filter({ has: page.getByRole("heading", { name: "Policy checks" }) });
        await expect(policyPanel).toContainText(/blocked/i);
        await openTechnicalSection(page, "Actions");
        await expect(page.locator(".action-control-panel")).toContainText("No consequential action for this run");
      }
      await assertSseReplayClean(page, accepted.run_id);
    }

    if (!historicalRunId) throw new Error("historical run was not captured");
    await openHistory(page);
    const historicalItem = page.locator(".task-run-item").filter({ hasText: historicalRunId });
    await expect(historicalItem).toHaveCount(1);
    await historicalItem.getByRole("button").click();
    await expect(page.getByTestId("customer-outcome-summary")).toBeVisible();

    await openTechnicalSection(page, "Current analysis");
    await expect(page.locator(".analytics-scope-banner")).toContainText(historicalRunId);
    await leakAudit.assertClean();
  });

  test("tenant/user isolation covers run REST, SSE and action confirmation", async ({ browser, page }) => {
    await configureActor(page, "e2e-user-a", "e2e-org-a");
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const accepted = await submitScenario(page, "scenario:pending-action");
    await waitForCompleted(page);
    await openTechnicalSection(page, "Actions");

    const actionCard = page.locator(".action-card").first();
    await expect(actionCard).toContainText("Waiting for your confirmation");
    const actionId = (await actionCard.locator(".visually-hidden dd").first().textContent())?.trim();
    if (!actionId) throw new Error("pending action id not rendered");

    const otherUser = await newActorPage(browser, "e2e-user-b", "e2e-org-a");
    const otherTenant = await newActorPage(browser, "e2e-user-a", "e2e-org-b");
    try {
      for (const deniedPage of [otherUser.page, otherTenant.page]) {
        expect((await fetchJson(deniedPage, `/api/runs/${accepted.run_id}`)).status).toBe(404);
        expect((await fetchJson(deniedPage, `/api/runs/${accepted.run_id}/actions`)).status).toBe(404);
        expect(
          (await fetchJson(deniedPage, `/api/actions/${actionId}/confirm`, {
            method: "POST",
            body: { confirm: true },
          })).status,
        ).toBe(404);
        const deniedStream = await deniedPage.evaluate(async (runId) => {
          const response = await fetch(`/api/stream?run_id=${encodeURIComponent(runId)}&follow=false`);
          return response.status;
        }, accepted.run_id);
        expect(deniedStream).toBe(404);
        await expect(deniedPage.locator("main")).not.toContainText(accepted.run_id.slice(0, 18));
      }
    } finally {
      await otherUser.context.close();
      await otherTenant.context.close();
    }

    const confirmResponsePromise = page.waitForResponse((response) =>
      new URL(response.url()).pathname === `/api/actions/${actionId}/confirm`
      && response.request().method() === "POST",
    );
    await actionCard.getByRole("button", { name: "Confirm exact action" }).click();
    const confirmResponse = await confirmResponsePromise;
    expect(confirmResponse.status()).toBe(202);
    const confirmation = (await confirmResponse.json()) as { execution_run_id: string };
    expect(confirmation.execution_run_id).toMatch(RUN_ID);
    expect(confirmation.execution_run_id).not.toBe(accepted.run_id);

    await waitForCompleted(page);
    await openTechnicalSection(page, "Current analysis");
    await expect(page.locator(".analytics-scope-banner")).toContainText(confirmation.execution_run_id);
    await expect.poll(async () => {
      const detail = await fetchJson(page, `/api/actions/${actionId}`);
      return (detail.body as { state?: string }).state;
    }).toBe("ACCEPTED");

    const duplicate = await fetchJson(page, `/api/actions/${actionId}/confirm`, {
      method: "POST",
      body: { confirm: true },
    });
    expect(duplicate.status).toBe(409);

    await assertSseReplayClean(page, accepted.run_id);
    await assertSseReplayClean(page, confirmation.execution_run_id);
    await leakAudit.assertClean();
  });
});