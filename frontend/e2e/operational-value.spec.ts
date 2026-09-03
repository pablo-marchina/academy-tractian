import { expect, test, type Browser, type Page } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:5173";

const FORBIDDEN_PILOT_KEYS = [
  "pair_id",
  "scenario_id",
  "case_id",
  "group_id",
  "source_split",
  "operator_ref",
  "operator_ref_sha256",
  "host_session_id",
  "elapsed_seconds",
  "agent_runtime_seconds",
  "gold_answer",
  "private_truth",
  "oracle",
] as const;

function actorHeaders(user: string, organization = "e2e-org-a"): Record<string, string> {
  return {
    "x-e2e-user": user,
    "x-e2e-organization": organization,
  };
}

function assertPilotPayloadBlinded(payload: unknown): void {
  const serialized = JSON.stringify(payload).toLowerCase();
  for (const forbidden of FORBIDDEN_PILOT_KEYS) {
    expect(serialized, `participant payload leaked ${forbidden}`).not.toContain(`"${forbidden}"`);
  }
}

async function openParticipant(page: Page, user: string, organization = "e2e-org-a") {
  await page.context().setExtraHTTPHeaders(actorHeaders(user, organization));
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Engineer effort study" })).toBeVisible();
}

async function newActorPage(browser: Browser, user: string, organization = "e2e-org-a") {
  const context = await browser.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: actorHeaders(user, organization),
  });
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
  return { context, page };
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 1);
}

test.describe("operational value collector full-product acceptance", () => {
  test("explicit start, blinded completion, and server-owned timing", async ({ page }) => {
    await page.context().setExtraHTTPHeaders(actorHeaders("pilot-valid-user"));
    const pilotRequests: string[] = [];
    page.on("request", (request) => {
      const pathname = new URL(request.url()).pathname;
      if (pathname.startsWith("/api/operational-value/")) pilotRequests.push(pathname);
    });

    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Engineer effort study" })).toBeVisible();
    await expect(page.getByTestId("pilot-start")).toBeVisible();
    expect(pilotRequests).toEqual([]);

    const assignmentResponse = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return url.pathname === "/api/operational-value/tasks/next"
        && response.request().method() === "POST";
    });
    await page.getByTestId("pilot-start").click();
    const assignmentHttp = await assignmentResponse;
    expect(assignmentHttp.status()).toBe(200);
    const assignment = (await assignmentHttp.json()) as {
      assignment_id: string;
      task: { assistance: unknown | null };
    };
    assertPilotPayloadBlinded(assignment);
    await expect(page.getByTestId("pilot-active-task")).toBeVisible();

    if (assignment.task.assistance === null) {
      await expect(page.getByTestId("pilot-manual")).toBeVisible();
      await expect(page.getByTestId("pilot-assistance")).toHaveCount(0);
    } else {
      await expect(page.getByTestId("pilot-assistance")).toBeVisible();
    }

    const tampered = await page.evaluate(async (assignmentId) => {
      const response = await fetch(
        `/api/operational-value/assignments/${encodeURIComponent(assignmentId)}/complete`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            terminal_decision: "ORIENT",
            conclusion_summary: "The browser must not be allowed to provide measured duration.",
            elapsed_seconds: 0.001,
          }),
        },
      );
      return { status: response.status, body: await response.json() };
    }, assignment.assignment_id);
    expect(tampered.status).toBe(422);
    await expect(page.getByTestId("pilot-active-task")).toBeVisible();

    const noncanonical = await page.evaluate(async (assignmentId) => {
      const response = await fetch(
        `/api/operational-value/assignments/${encodeURIComponent(assignmentId)}/complete`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            terminal_decision: "FINAL",
            conclusion_summary: "Controller kinds must not replace canonical operational decisions.",
          }),
        },
      );
      return response.status;
    }, assignment.assignment_id);
    expect(noncanonical).toBe(422);
    await expect(page.getByTestId("pilot-active-task")).toBeVisible();

    await page.getByTestId("pilot-decision").selectOption("ORIENT");
    await page.getByTestId("pilot-summary").fill(
      "The available operational evidence supports waiting for the current analysis before corrective action.",
    );
    const completionRequest = page.waitForRequest((request) =>
      new URL(request.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/complete`)
      && request.method() === "POST",
    );
    const completionResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/complete`)
      && response.request().method() === "POST",
    );
    await page.getByTestId("pilot-submit").click();
    const request = await completionRequest;
    expect(request.postDataJSON()).toEqual({
      terminal_decision: "ORIENT",
      conclusion_summary: "The available operational evidence supports waiting for the current analysis before corrective action.",
    });
    const completionHttp = await completionResponse;
    expect(completionHttp.status()).toBe(200);
    const completion = await completionHttp.json();
    expect(completion.status).toBe("VALID");
    assertPilotPayloadBlinded(completion);

    await expect(page.getByTestId("pilot-completion")).toContainText("VALID");
    await expect(page.getByTestId("pilot-completion")).not.toContainText(/\b\d+(?:\.\d+)?\s*(?:s|sec|seconds|min|minutes)\b/i);
    await page.setViewportSize({ width: 390, height: 844 });
    await assertNoHorizontalOverflow(page);
  });

  test("human interruption is persisted without participant timing feedback", async ({ browser }) => {
    const actor = await newActorPage(browser, "pilot-interrupt-user");
    try {
      const assignmentResponse = actor.page.waitForResponse((response) =>
        new URL(response.url()).pathname === "/api/operational-value/tasks/next"
        && response.request().method() === "POST",
      );
      await actor.page.getByTestId("pilot-start").click();
      const assignmentHttp = await assignmentResponse;
      expect(assignmentHttp.status()).toBe(200);
      const assignment = (await assignmentHttp.json()) as { assignment_id: string };
      assertPilotPayloadBlinded(assignment);

      const terminationRequest = actor.page.waitForRequest((request) =>
        new URL(request.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/terminate`)
        && request.method() === "POST",
      );
      const terminationResponse = actor.page.waitForResponse((response) =>
        new URL(response.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/terminate`)
        && response.request().method() === "POST",
      );
      await actor.page.getByTestId("pilot-interrupt").click();
      expect((await terminationRequest).postDataJSON()).toEqual({ status: "INTERRUPTED" });
      const terminationHttp = await terminationResponse;
      expect(terminationHttp.status()).toBe(200);
      const termination = await terminationHttp.json();
      expect(termination.status).toBe("INTERRUPTED");
      assertPilotPayloadBlinded(termination);
      await expect(actor.page.getByTestId("pilot-completion")).toContainText("INTERRUPTED");
    } finally {
      await actor.context.close();
    }
  });

  test("tenant and owner isolation apply to participant assignments", async ({ browser, page }) => {
    await openParticipant(page, "pilot-owner-user", "e2e-org-a");
    const assignmentResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname === "/api/operational-value/tasks/next"
      && response.request().method() === "POST",
    );
    await page.getByTestId("pilot-start").click();
    const assignmentHttp = await assignmentResponse;
    expect(assignmentHttp.status()).toBe(200);
    const assignment = (await assignmentHttp.json()) as { assignment_id: string };

    const wrongOwner = await newActorPage(browser, "pilot-other-user", "e2e-org-a");
    const wrongTenant = await newActorPage(browser, "pilot-owner-user", "e2e-org-b");
    try {
      const wrongOwnerResponse = await wrongOwner.context.request.post(
        `/api/operational-value/assignments/${assignment.assignment_id}/terminate`,
        { data: { status: "WITHDRAWN" } },
      );
      expect(wrongOwnerResponse.status()).toBe(404);

      const wrongTenantResponse = await wrongTenant.context.request.post(
        "/api/operational-value/tasks/next",
      );
      expect(wrongTenantResponse.status()).toBe(404);

      const forged = await page.request.post(
        `/api/operational-value/assignments/${assignment.assignment_id}/terminate`,
        { data: { status: "TECHNICAL_FAILURE" } },
      );
      expect(forged.status()).toBe(422);
    } finally {
      await wrongOwner.context.close();
      await wrongTenant.context.close();
    }

    const withdrawalResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/terminate`)
      && response.request().method() === "POST",
    );
    await page.getByTestId("pilot-withdraw").click();
    const withdrawal = await withdrawalResponse;
    expect(withdrawal.status()).toBe(200);
    assertPilotPayloadBlinded(await withdrawal.json());
    await expect(page.getByTestId("pilot-completion")).toContainText("WITHDRAWN");
    await expect(page.getByTestId("pilot-next")).toHaveCount(0);
  });
});
