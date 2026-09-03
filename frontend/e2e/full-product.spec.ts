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
  await expect(page.getByText("API healthy")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Industrial Agent Operations" })).toBeVisible();
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
  await page.getByLabel("Industrial request").fill(scenario);
  const acceptedPromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return url.pathname === "/api/runs" && response.request().method() === "POST";
  });
  await page.getByRole("button", { name: "Start production run" }).click();
  const response = await acceptedPromise;
  expect(response.status()).toBe(202);
  const accepted = (await response.json()) as { run_id: string; [key: string]: unknown };
  expect(accepted.run_id).toMatch(RUN_ID);
  await expect(page.locator(".run-id-cell strong")).toHaveText(accepted.run_id);
  return accepted;
}

async function waitForCompleted(page: Page): Promise<void> {
  await expect(page.locator(".run-strip")).toContainText(/COMPLETED\s*\/\s*completed/i, {
    timeout: 20_000,
  });
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
  test("loading/empty, long content, constrained analytics and responsive viewport", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    await expect(page.getByText("No runtime events selected")).toBeVisible();
    await expect(page.getByText("No run selected").first()).toBeVisible();
    await assertNoHorizontalOverflow(page);

    const longRequest = `scenario:clarify ${"industrial-context ".repeat(450)}`;
    const accepted = await submitScenario(page, longRequest);
    await waitForCompleted(page);
    await expect(page.locator(".terminal-panel")).toContainText("ASK_CLARIFICATION");
    await assertNoHorizontalOverflow(page);

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
    await expect(page.getByRole("heading", { name: "Industrial Agent Operations" })).toBeVisible();

    await assertSseReplayClean(page, accepted.run_id);
    await leakAudit.assertClean();
  });

  test("real runtime, SSE reconnect/catch-up, post-runtime evaluation and live visualizations", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const accepted = await submitScenario(page, "scenario:slow investigate asset evidence");
    await expect(page.locator(".evaluation-panel")).toContainText("Not evaluated yet");
    await expect(page.locator(".run-strip")).toContainText("LIVE /");
    await expect(page.locator(".timeline-panel")).toContainText("Execute · get_asset", { timeout: 8_000 });

    await page.context().setOffline(true);
    await expect(page.locator(".run-strip")).toContainText("RECONNECTING", { timeout: 5_000 });
    await page.waitForTimeout(300);
    await page.context().setOffline(false);
    await expect(page.locator(".run-strip")).toContainText("CAUGHT_UP", { timeout: 8_000 });

    await waitForCompleted(page);
    await expect(page.locator(".terminal-panel")).toContainText("E2E_EVIDENCE_CONFIRMED");
    await expect(page.locator(".evaluation-panel")).toContainText("blocking checks passed");
    await expect(page.locator(".timeline-panel")).toContainText("Evidence · EV-e2e-asset");

    const sequences = (await page.locator(".timeline-item .sequence").allTextContents()).map((value) => Number(value));
    expect(sequences.length).toBeGreaterThan(4);
    expect(sequences).toEqual([...sequences].sort((left, right) => left - right));
    expect(new Set(sequences).size).toBe(sequences.length);

    await expect(page.getByRole("heading", { name: "Trace Graph" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Architecture Explorer" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Evidence Explorer" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Output Lineage" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Mission Control" })).toBeVisible();
    await expect(page.locator(".evidence-list")).toContainText("EV-e2e-asset");

    const toolsPanel = page.locator("article.panel").filter({
      has: page.getByRole("heading", { name: "Tools Analytics" }),
    });
    await expect(toolsPanel).toContainText("get_asset");
    await toolsPanel.getByRole("button", { name: "drill down" }).first().click();
    const dynamic = page.locator("#dynamic-data-explorer");
    await expect(dynamic.locator(".query-result-meta")).toContainText(`scope ${accepted.run_id}`);

    await expect(page.getByText(/reconnects/).first()).toBeVisible();
    await assertSseReplayClean(page, accepted.run_id);
    await leakAudit.assertClean();
  });

  test("terminal safety modes, blocked action and historical navigation are visible", async ({ page }) => {
    await configureActor(page);
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const cases = [
      ["scenario:clarify", "ASK_CLARIFICATION", "E2E_INFORMATION_REQUIRED"],
      ["scenario:abstain", "ABSTAIN", "E2E_EVIDENCE_UNAVAILABLE"],
      ["scenario:escalate", "ESCALATE_HUMAN", "E2E_AMBIGUOUS_EVIDENCE"],
      ["scenario:tool-error", "ABSTAIN", "The evidence tool failed"],
      ["scenario:blocked-action", "ABSTAIN", "high-impact action was blocked"],
    ] as const;

    let historicalRunId: string | null = null;
    for (const [scenario, decision, detail] of cases) {
      const accepted = await submitScenario(page, scenario);
      historicalRunId ??= accepted.run_id;
      await waitForCompleted(page);
      await expect(page.locator(".terminal-panel")).toContainText(decision);
      await expect(page.locator(".terminal-panel")).toContainText(detail);
      if (scenario === "scenario:blocked-action") {
        await expect(page.locator(".metric-grid")).toContainText(/Policy blocks\s*[1-9]/);
        await expect(page.locator(".action-control-panel")).toContainText("No consequential action for this run");
      }
      await assertSseReplayClean(page, accepted.run_id);
    }

    if (!historicalRunId) throw new Error("historical run was not captured");
    const historicalRow = page.locator(".run-table tbody tr").filter({
      hasText: historicalRunId.slice(0, 18),
    });
    await historicalRow.click();
    await expect(page.locator(".run-strip")).toContainText("HISTORICAL");
    await expect(page.locator(".run-id-cell strong")).toHaveText(historicalRunId);
    await leakAudit.assertClean();
  });

  test("tenant/user isolation covers run REST, SSE and action confirmation", async ({ browser, page }) => {
    await configureActor(page, "e2e-user-a", "e2e-org-a");
    const leakAudit = installJsonLeakAudit(page);
    await openProduct(page);

    const accepted = await submitScenario(page, "scenario:pending-action");
    await waitForCompleted(page);
    const actionCard = page.locator(".action-card").first();
    await expect(actionCard).toContainText("PENDING_CONFIRMATION");
    const actionId = (await actionCard.locator("dd").first().textContent())?.trim();
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

    await expect(page.locator(".run-id-cell strong")).toHaveText(confirmation.execution_run_id);
    await waitForCompleted(page);
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