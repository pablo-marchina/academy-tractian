import { expect, test, type Page } from "@playwright/test";

const FORBIDDEN_REVIEW_KEYS = [
  "phase",
  "reviewer_slot",
  "scenario_id",
  "output_sha256",
  "context_sha256",
  "source_split",
  "group_id",
  "reviewer_ref_sha256",
  "user_id",
  "private_truth",
  "gold_answer",
  "chain_of_thought",
] as const;

function actorHeaders(user: string, organization = "e2e-org-a"): Record<string, string> {
  return {
    "x-e2e-user": user,
    "x-e2e-organization": organization,
  };
}

function assertReviewerPayloadBlinded(payload: unknown): void {
  const serialized = JSON.stringify(payload).toLowerCase();
  for (const forbidden of FORBIDDEN_REVIEW_KEYS) {
    expect(serialized, `semantic reviewer payload leaked ${forbidden}`).not.toContain(`"${forbidden}"`);
  }
  expect(serialized).not.toContain("sem-e2e-val-");
}

async function openReviewer(page: Page, user: string) {
  await page.context().setExtraHTTPHeaders(actorHeaders(user));
  await page.goto("/");
  await expect(page.getByText("API healthy")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Blind semantic review" })).toBeVisible();
}

async function assertNoHorizontalOverflow(page: Page): Promise<void> {
  const dimensions = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.viewport + 1);
}

test.describe("semantic review full-product acceptance", () => {
  test("explicit allocation, minimal blinded payload, canonical label, and neutral acknowledgement", async ({ page }) => {
    await page.context().setExtraHTTPHeaders(actorHeaders("semantic-e2e-reviewer-a"));
    const semanticRequests: string[] = [];
    page.on("request", (request) => {
      const pathname = new URL(request.url()).pathname;
      if (pathname.startsWith("/api/semantic-review/")) semanticRequests.push(pathname);
    });

    await page.goto("/");
    await expect(page.getByRole("heading", { name: "Blind semantic review" })).toBeVisible();
    expect(semanticRequests).toEqual([]);

    const assignmentResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname === "/api/semantic-review/tasks/next"
      && response.request().method() === "POST",
    );
    await page.getByTestId("semantic-review-start").click();
    const assignmentHttp = await assignmentResponse;
    expect(assignmentHttp.status()).toBe(200);
    const assignment = (await assignmentHttp.json()) as {
      assignment_id: string;
      task: { task_id: string; dimension: string; terminal_message: string };
    };
    assertReviewerPayloadBlinded(assignment);
    expect(assignment.task.task_id).toMatch(/^sem_[0-9a-f]{24}$/);
    await expect(page.getByTestId("semantic-review-active")).toBeVisible();
    await expect(page.getByTestId("semantic-review-output")).toContainText(assignment.task.terminal_message);

    await page.getByTestId("semantic-review-score-1").check();
    await page.locator('input[type="checkbox"][value="MISSING_NEXT_STEP"]').check();

    const completionRequest = page.waitForRequest((request) =>
      new URL(request.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/complete`)
      && request.method() === "POST",
    );
    const completionResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${assignment.assignment_id}/complete`)
      && response.request().method() === "POST",
    );
    await page.getByTestId("semantic-review-submit").click();
    expect((await completionRequest).postDataJSON()).toEqual({
      score: 1,
      reason_codes: ["MISSING_NEXT_STEP"],
    });
    const completionHttp = await completionResponse;
    expect(completionHttp.status()).toBe(200);
    const completion = await completionHttp.json();
    expect(completion.state).toBe("COMPLETED");
    assertReviewerPayloadBlinded(completion);
    expect(JSON.stringify(completion)).not.toContain("MISSING_NEXT_STEP");
    expect(JSON.stringify(completion)).not.toContain('"score"');
    await expect(page.getByTestId("semantic-review-completion")).toContainText("COMPLETED");

    await page.setViewportSize({ width: 390, height: 844 });
    await assertNoHorizontalOverflow(page);
  });

  test("score two uses canonical no-defect reason and withdrawal produces no browser label feedback", async ({ page }) => {
    await openReviewer(page, "semantic-e2e-reviewer-b");
    const firstResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname === "/api/semantic-review/tasks/next"
      && response.request().method() === "POST",
    );
    await page.getByTestId("semantic-review-start").click();
    const first = (await (await firstResponse).json()) as { assignment_id: string };

    await page.getByTestId("semantic-review-score-2").check();
    await expect(page.getByTestId("semantic-review-no-defect")).toBeVisible();
    const scoreTwoRequest = page.waitForRequest((request) =>
      new URL(request.url()).pathname.endsWith(`/assignments/${first.assignment_id}/complete`)
      && request.method() === "POST",
    );
    await page.getByTestId("semantic-review-submit").click();
    expect((await scoreTwoRequest).postDataJSON()).toEqual({
      score: 2,
      reason_codes: ["NO_MATERIAL_DEFECT"],
    });
    await expect(page.getByTestId("semantic-review-completion")).toContainText("COMPLETED");

    const secondResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname === "/api/semantic-review/tasks/next"
      && response.request().method() === "POST",
    );
    await page.getByTestId("semantic-review-next").click();
    const secondHttp = await secondResponse;
    expect(secondHttp.status()).toBe(200);
    const second = (await secondHttp.json()) as { assignment_id: string };
    assertReviewerPayloadBlinded(second);

    const withdrawResponse = page.waitForResponse((response) =>
      new URL(response.url()).pathname.endsWith(`/assignments/${second.assignment_id}/withdraw`)
      && response.request().method() === "POST",
    );
    await page.getByTestId("semantic-review-withdraw").click();
    const withdrawn = await withdrawResponse;
    expect(withdrawn.status()).toBe(200);
    const body = await withdrawn.json();
    expect(body.state).toBe("WITHDRAWN");
    assertReviewerPayloadBlinded(body);
    await expect(page.getByTestId("semantic-review-completion")).toContainText("WITHDRAWN");
  });
});