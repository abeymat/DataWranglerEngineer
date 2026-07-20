const state = {
  profile: null,
  spec: null,
  generated: null,
  execution: null,
  datasetFile: null,
  lookupLeftFile: null,
  lookupRightFile: null,
};

const demoInstruction =
  "Create one row per customer. Combine all unique addresses into a readable address list, " +
  "normalize U.S. phone numbers, calculate total purchases, retain the most recent transaction " +
  "date, remove duplicates, flag records with missing customer IDs, and prepare the output for " +
  "Salesforce import.";

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  bindTabs();
  bindDatasetControls();
  bindWorkflowControls();
  bindLookupControls();
  checkApiStatus();
});

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => activateTab(button.dataset.tab));
  });
}

function bindDatasetControls() {
  $("dataset-file").addEventListener("change", (event) => {
    state.datasetFile = event.target.files[0] ?? null;
    $("dataset-file-label").textContent = state.datasetFile?.name ?? "Choose primary CSV";
  });
  $("load-demo").addEventListener("click", () => runAction(loadDemoDataset));
  $("profile-button").addEventListener("click", () => runAction(profileDataset));
}

function bindWorkflowControls() {
  $("demo-instruction").addEventListener("click", () => {
    $("instruction").value = demoInstruction;
  });
  $("plan-button").addEventListener("click", () => runAction(createPlan));
  $("generate-button").addEventListener("click", () => runAction(generateWorkflow));
  $("execute-button").addEventListener("click", () => runAction(executeWorkflow));
}

function bindLookupControls() {
  $("lookup-left-file").addEventListener("change", (event) => {
    state.lookupLeftFile = event.target.files[0] ?? null;
    $("lookup-left-label").textContent = state.lookupLeftFile?.name ?? "No file selected";
  });
  $("lookup-right-file").addEventListener("change", (event) => {
    state.lookupRightFile = event.target.files[0] ?? null;
    $("lookup-right-label").textContent = state.lookupRightFile?.name ?? "No file selected";
  });
  $("load-lookup-samples").addEventListener("click", () => runAction(loadLookupSamples));
  $("lookup-button").addEventListener("click", () => runAction(runLookup));
}

async function runAction(action) {
  try {
    await action();
  } catch (error) {
    toast(error.message ?? "Action failed");
  }
}

async function checkApiStatus() {
  try {
    const response = await fetch("/health");
    const body = await response.json();
    $("api-status").textContent = body.status === "ok" ? "API Online" : "API Issue";
  } catch {
    $("api-status").textContent = "API Offline";
  }
}

async function loadDemoDataset() {
  state.datasetFile = await fileFromSample(
    "/samples/customer_wrangling_demo.csv",
    "customer_wrangling_demo.csv",
  );
  $("dataset-file-label").textContent = state.datasetFile.name;
  $("instruction").value = demoInstruction;
  toast("Demo dataset loaded.");
}

async function loadLookupSamples() {
  state.lookupLeftFile = await fileFromSample("/samples/lookup_orders.csv", "lookup_orders.csv");
  state.lookupRightFile = await fileFromSample(
    "/samples/lookup_customers.csv",
    "lookup_customers.csv",
  );
  $("lookup-left-label").textContent = state.lookupLeftFile.name;
  $("lookup-right-label").textContent = state.lookupRightFile.name;
  $("left-key").value = "customer_id";
  $("right-key").value = "customer_id";
  $("lookup-columns").value = "customer_name,salesforce_account_id";
  toast("Lookup samples loaded.");
}

async function fileFromSample(url, filename) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${filename}`);
  const blob = await response.blob();
  return new File([blob], filename, { type: "text/csv" });
}

async function profileDataset() {
  if (!state.datasetFile) {
    toast("Choose a CSV or load the sample dataset.");
    return;
  }

  const formData = new FormData();
  formData.append("file", state.datasetFile);
  const body = await postForm("/api/v1/datasets/profile", formData);
  state.profile = body.profile;
  renderProfile(state.profile);
  setStep("profile", "Source extracted and profiled", true);
  activateTab("profile");
}

async function createPlan() {
  if (!state.profile) {
    await profileDataset();
  }
  if (!state.profile) return;

  const instruction = $("instruction").value.trim();
  if (!instruction) {
    toast("Enter a business request.");
    return;
  }

  const body = await postJson("/api/v1/workflows/plan", {
    instruction,
    dataset_profile: state.profile,
  });
  state.spec = body.spec;
  renderPlan(state.spec);
  setStep("plan", "Transform plan created", true);
  activateTab("plan");
}

async function generateWorkflow() {
  if (!state.spec) {
    await createPlan();
  }
  if (!state.spec) return;

  const body = await postJson("/api/v1/workflows/generate", { spec: state.spec });
  state.generated = body;
  renderGraph(body.operation_graph);
  $("code-output").textContent = body.polars_code;
  setStep("generate", "Approved Polars transform generated", true);
  activateTab("graph");
}

async function executeWorkflow() {
  if (!state.generated) {
    await generateWorkflow();
  }
  if (!state.generated || !state.datasetFile) return;

  hideExecutionError();
  let body;
  try {
    body = await executeGeneratedWorkflow();
  } catch (error) {
    if (!isStaleGraphError(error)) {
      showExecutionError(error);
      throw error;
    }

    state.generated = null;
    await generateWorkflow();
    body = await executeGeneratedWorkflow();
    toast("Regenerated the ETL graph and reran successfully.");
  }

  state.execution = body;
  renderExecution(body);
  setStep(
    "execute",
    body.salesforce_load_plan.ready_for_load
      ? "Salesforce load package ready"
      : "Salesforce load package needs review",
    body.execution_status === "passed" && body.salesforce_load_plan.ready_for_load,
  );
  activateTab("output");
}

async function executeGeneratedWorkflow() {
  const formData = new FormData();
  formData.append("file", state.datasetFile);
  formData.append("operation_graph", JSON.stringify(state.generated.operation_graph));

  return postForm("/api/v1/workflows/execute", formData);
}

async function runLookup() {
  if (!state.lookupLeftFile || !state.lookupRightFile) {
    toast("Choose lookup files or load samples.");
    return;
  }

  const formData = new FormData();
  formData.append("left_file", state.lookupLeftFile);
  formData.append("right_file", state.lookupRightFile);
  formData.append("left_key", $("left-key").value.trim());
  formData.append("right_key", $("right-key").value.trim());
  formData.append("lookup_columns", $("lookup-columns").value.trim());
  formData.append("join_type", "left");

  const body = await postForm("/api/v1/lookups/preview", formData);
  renderLookup(body);
  activateTab("lookup");
}

async function postForm(url, formData) {
  const response = await fetch(url, { method: "POST", body: formData });
  return parseResponse(response);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseResponse(response);
}

async function parseResponse(response) {
  const body = await response.json();
  if (!response.ok || body.success === false) {
    const error = new Error(body.error ?? "Request failed");
    error.category = body.category;
    error.correlationId = body.correlation_id;
    error.status = response.status;
    throw error;
  }
  return body;
}

function isStaleGraphError(error) {
  return ["invalid_graph", "unsupported_graph", "invalid_operation_graph"].includes(error.category);
}

function renderProfile(profile) {
  $("metric-rows").textContent = profile.quality.row_count;
  $("metric-columns").textContent = profile.quality.column_count;
  $("metric-duplicates").textContent = profile.quality.duplicate_row_count;
  $("metric-warnings").textContent = profile.quality.warnings.length;
  $("profile-summary").textContent = `${profile.filename} - ${profile.encoding}`;

  $("profile-table").classList.remove("empty-state");
  $("profile-table").innerHTML = tableHtml(
    ["Column", "Type", "Nulls", "Unique", "Identifier", "Warnings"],
    profile.columns.map((column) => [
      column.name,
      column.inferred_type,
      column.null_count,
      column.unique_count,
      column.likely_identifier ? "Yes" : "No",
      column.quality_warnings.join("; ") || "-",
    ]),
  );
  renderWarnings("quality-warnings", profile.quality.warnings);
}

function renderPlan(spec) {
  const loadTarget = spec.load_target ?? {
    system: "salesforce",
    object_api_name: "Account",
    operation: "upsert",
  };
  $("plan-summary").textContent = `${spec.transformation_steps.length} steps`;
  $("plan-output").classList.remove("empty-state");
  $("plan-output").innerHTML = [
    detailItem("Extract Source", spec.extract_source ?? "csv_upload"),
    detailItem(
      "Load Target",
      `${loadTarget.system} ${loadTarget.object_api_name} ${loadTarget.operation}`,
    ),
    detailItem("Objective", spec.business_objective),
    chipItem("Required Columns", spec.required_columns),
    chipItem("Output Columns", spec.output_columns),
    ...spec.transformation_steps.map((step) =>
      detailItem(`${step.step_id}: ${step.action}`, step.business_description),
    ),
    chipItem("Assumptions", spec.assumptions),
    chipItem("Warnings", spec.warnings),
  ].join("");
}

function renderGraph(graph) {
  $("graph-summary").textContent = graph.graph_id;
  $("graph-output").classList.remove("empty-state");
  $("graph-output").innerHTML = graph.operations
    .map(
      (operation) => `
        <article class="operation-item">
          <h3>${escapeHtml(operation.operation_id)} - ${escapeHtml(operation.operation_type)}</h3>
          <p>${escapeHtml(operation.description)}</p>
          ${chips(operation.output_columns)}
        </article>
      `,
    )
    .join("");
}

function renderLookup(body) {
  $("lookup-input-count").textContent = body.input_row_count;
  $("lookup-output-count").textContent = body.output_row_count;
  $("lookup-matched-count").textContent = body.matched_row_count;
  $("lookup-unmatched-count").textContent = body.unmatched_row_count;
  renderWarnings("lookup-warnings", body.warnings);

  $("lookup-table").classList.remove("empty-state");
  $("lookup-table").innerHTML = tableHtml(
    body.output_columns,
    body.preview_rows.map((row) => body.output_columns.map((column) => row[column] ?? "")),
  );
}

function renderExecution(body) {
  $("execution-summary").textContent =
    `${body.execution_status} in ${body.duration_ms}ms - ${body.graph_id}`;
  hideExecutionError();
  $("exec-input-count").textContent = body.metrics.input_row_count;
  $("exec-output-count").textContent = body.metrics.output_row_count;
  $("exec-duplicates-count").textContent = body.metrics.duplicate_rows_removed;
  $("exec-total").textContent = `$${Number(body.metrics.output_purchase_total).toFixed(2)}`;
  if (body.salesforce_load_plan) {
    renderSalesforceLoadPlan(body.salesforce_load_plan);
  }
  renderFindings("validation-findings", body.validation_findings);
  $("execution-table").classList.remove("empty-state");
  $("execution-table").innerHTML = tableHtml(
    body.output_columns,
    body.preview_rows.map((row) => body.output_columns.map((column) => row[column] ?? "")),
  );
}

function showExecutionError(error) {
  const target = $("execution-error");
  target.hidden = false;
  target.innerHTML = `
    <strong>Run ETL failed</strong>
    <p>${escapeHtml(error.message ?? "The ETL execution failed.")}</p>
    ${
      error.correlationId
        ? `<p class="subtle">Correlation ID: ${escapeHtml(error.correlationId)}</p>`
        : ""
    }
  `;
  activateTab("output");
}

function hideExecutionError() {
  const target = $("execution-error");
  if (!target) return;
  target.hidden = true;
  target.innerHTML = "";
}

function renderSalesforceLoadPlan(plan) {
  const target = plan.target ?? {
    object_api_name: "Account",
    operation: "upsert",
    external_id_field: "External_Id__c",
  };
  $("salesforce-load-plan").classList.remove("empty-state");
  $("salesforce-load-plan").innerHTML = [
    detailItem("Target", `${target.object_api_name} ${target.operation}`),
    detailItem("External ID", target.external_id_field),
    detailItem("Load Format", plan.output_format.toUpperCase()),
    detailItem("Ready", plan.ready_for_load ? "Yes" : "Needs review"),
    chipItem(
      "Mappings",
      plan.field_mappings.map((mapping) => `${mapping.source_column} -> ${mapping.target_field}`),
    ),
    chipItem("Missing Required Columns", plan.missing_output_columns),
    chipItem("Load Notes", plan.notes),
  ].join("");
}

function detailItem(title, value) {
  return `
    <article class="detail-item">
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(value)}</p>
    </article>
  `;
}

function chipItem(title, values) {
  return `
    <article class="detail-item">
      <h3>${escapeHtml(title)}</h3>
      ${chips(values)}
    </article>
  `;
}

function chips(values) {
  if (!values || values.length === 0) return "";
  return `<div class="chip-row">${values
    .map((value) => `<span class="chip">${escapeHtml(value)}</span>`)
    .join("")}</div>`;
}

function renderWarnings(targetId, warnings) {
  const target = $(targetId);
  target.innerHTML = warnings.map((warning) => `<p>${escapeHtml(warning)}</p>`).join("");
}

function renderFindings(targetId, findings) {
  const target = $(targetId);
  target.innerHTML = findings
    .map(
      (finding) =>
        `<p class="${escapeHtml(finding.status)}"><strong>${escapeHtml(
          finding.status,
        )}</strong> - ${escapeHtml(finding.message)}</p>`,
    )
    .join("");
}

function tableHtml(headers, rows) {
  return `
    <table>
      <thead>
        <tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (row) =>
              `<tr>${row.map((value) => `<td>${escapeHtml(String(value))}</td>`).join("")}</tr>`,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

function setStep(step, text, done) {
  const element = document.querySelector(`[data-step="${step}"]`);
  if (!element) return;
  element.textContent = text;
  element.classList.toggle("done", done);
}

function activateTab(name) {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === name);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `tab-${name}`);
  });
}

function toast(message) {
  const element = $("toast");
  element.textContent = message;
  element.classList.add("visible");
  window.setTimeout(() => element.classList.remove("visible"), 2600);
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
