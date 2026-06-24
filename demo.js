const states = {
  task: {
    title: "Task created",
    status: "queued",
    briefs: [
      ["company pricing", "pending"],
      ["market positioning", "pending"],
      ["traction signals", "pending"],
    ],
    evidence: [
      "No evidence yet. The task is persisted before the worker starts.",
      "The UI can reload safely because state lives in Postgres.",
    ],
    report: "Waiting for accepted findings.",
  },
  research: {
    title: "Researchers running",
    status: "running",
    briefs: [
      ["company pricing", "submitted"],
      ["market positioning", "submitted"],
      ["traction signals", "submitted"],
    ],
    evidence: [
      "Search results become sources.",
      "Source snippets become fragments.",
      "Findings keep links to the exact fragments they depend on.",
    ],
    report: "The report is not written by the researcher stage.",
  },
  critic: {
    title: "Critic review",
    status: "critic_review",
    briefs: [
      ["company pricing", "accepted"],
      ["market positioning", "accepted"],
      ["traction signals", "expand"],
    ],
    evidence: [
      "Claims with weak support are marked for expansion.",
      "Accepted findings move forward. Rejected findings stay out.",
    ],
    report: "The final answer is gated by critic verdicts.",
  },
  report: {
    title: "Report ready",
    status: "completed",
    briefs: [
      ["company pricing", "included"],
      ["market positioning", "included"],
      ["traction signals", "warning"],
    ],
    evidence: [
      "Pricing claim -> fragment-1, fragment-2",
      "Positioning claim -> fragment-3, fragment-4",
    ],
    report: "Market Scan: pricing, positioning, source list, warnings, open questions.",
  },
};

function render(stateName) {
  const state = states[stateName];
  document.querySelector("#demo-title").textContent = state.title;
  document.querySelector("#demo-status").textContent = state.status;
  document.querySelector("#briefs").innerHTML = state.briefs
    .map(([name, tag]) => `<div class="row"><strong>${name}</strong><br><span class="tag ${tag === "expand" || tag === "warning" ? "warn" : ""}">${tag}</span></div>`)
    .join("");
  document.querySelector("#evidence").innerHTML = state.evidence
    .map((item) => `<div class="row">${item}</div>`)
    .join("");
  document.querySelector("#report").textContent = state.report;
  document.querySelectorAll("[data-state]").forEach((button) => {
    button.classList.toggle("active", button.dataset.state === stateName);
  });
}

document.querySelectorAll("[data-state]").forEach((button) => {
  button.addEventListener("click", () => render(button.dataset.state));
});

render("task");
