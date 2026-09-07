// FactMesh Frontend Application Logic
document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

let allFactsCache = [];
let selectedFiles = [];

function initApp() {
  setupTabs();
  setupUpload();
  setupPresets();
  setupSearch();
  setupModal();
  refreshAll();
}

// --- Tabs Navigation ---
function setupTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add("active");
    });
  });
}

// --- Refresh All Data ---
async function refreshAll() {
  await Promise.all([
    loadStats(),
    loadRelationships(),
    loadFailures(),
    loadFacts(),
    loadDocuments()
  ]);
}

// --- Load Stats ---
async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById("statDocs").textContent = data.total_documents;
    document.getElementById("statFacts").textContent = data.total_facts;
    document.getElementById("statCorrob").textContent = data.corroborated_count;
    document.getElementById("statContra").textContent = data.contradiction_count;
    document.getElementById("statReconciled").textContent = data.reconciled_count;
    document.getElementById("statFailures").textContent = data.failure_count;
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

// --- Load Relationships (Corroborated, Contradiction, Reconciled) ---
async function loadRelationships() {
  try {
    const res = await fetch("/api/relationships");
    if (!res.ok) return;
    const rels = await res.json();

    const corrobContainer = document.getElementById("corroboratedContainer");
    const contraContainer = document.getElementById("contradictionContainer");
    const reconContainer = document.getElementById("reconciledContainer");

    corrobContainer.innerHTML = "";
    contraContainer.innerHTML = "";
    reconContainer.innerHTML = "";

    const corrobList = rels.filter(r => r.relationship === "CORROBORATED");
    const contraList = rels.filter(r => r.relationship === "CONTRADICTION");
    const reconList = rels.filter(r => r.relationship === "CONTEXTUALLY_RECONCILED");

    if (corrobList.length === 0) {
      corrobContainer.innerHTML = `<div class="empty-hint">No corroborated pairs currently stored. Click 'Quick Load' or upload documents.</div>`;
    } else {
      corrobList.forEach(rel => corrobContainer.appendChild(createRelationshipCard(rel)));
    }

    if (contraList.length === 0) {
      contraContainer.innerHTML = `<div class="empty-hint">No genuine contradictions found.</div>`;
    } else {
      contraList.forEach(rel => contraContainer.appendChild(createRelationshipCard(rel)));
    }

    if (reconList.length === 0) {
      reconContainer.innerHTML = `<div class="empty-hint">No contextually reconciled pairs currently stored.</div>`;
    } else {
      reconList.forEach(rel => reconContainer.appendChild(createRelationshipCard(rel)));
    }
  } catch (err) {
    console.error("Failed to load relationships:", err);
  }
}

function createRelationshipCard(rel) {
  const card = document.createElement("div");
  const typeClass = {
    "CORROBORATED": "rel-card-corroborated",
    "CONTRADICTION": "rel-card-contradiction",
    "CONTEXTUALLY_RECONCILED": "rel-card-reconciled"
  }[rel.relationship] || "";

  card.className = `rel-card ${typeClass}`;

  const fa = rel.fact_a || {};
  const fb = rel.fact_b || {};

  const badgeClass = {
    "CORROBORATED": "badge-corroborated",
    "CONTRADICTION": "badge-contradiction",
    "CONTEXTUALLY_RECONCILED": "badge-reconciled"
  }[rel.relationship] || "";

  const dimBadge = rel.reconciling_dimension && rel.reconciling_dimension !== "NONE"
    ? `<span class="badge-dimension">Dimension: ${rel.reconciling_dimension}</span>`
    : "";

  card.innerHTML = `
    <div class="rel-top">
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="rel-badge ${badgeClass}">${rel.relationship}</span>
        ${dimBadge}
      </div>
      <div style="font-size:0.8rem; color:var(--text-secondary);">
        Confidence: <strong>${Math.round(rel.confidence * 100)}%</strong>
      </div>
    </div>
    <div class="rel-reason">
      <strong>Reasoning & Analysis:</strong> ${rel.reason}
    </div>
    <div class="fact-comparison-pair">
      ${renderFactBox(fa, "Source A")}
      ${renderFactBox(fb, "Source B")}
    </div>
  `;
  return card;
}

function renderFactBox(fact, label) {
  if (!fact || !fact.fact_id) {
    return `<div class="fact-box"><div class="text-muted">Fact details unavailable</div></div>`;
  }

  const ev = fact.evidence || {};
  return `
    <div class="fact-box">
      <div class="fact-box-header">
        <span class="doc-name" title="${fact.source_document}">📄 ${fact.source_document}</span>
        <span class="page-badge">Page ${fact.page_number}</span>
      </div>
      <div class="fact-main-metric">
        ${fact.subject}: <span style="color:var(--status-blue);">${fact.raw_value}</span>
      </div>
      <div class="fact-context-tags">
        <span class="ctx-tag">Metric: ${fact.predicate}</span>
        <span class="ctx-tag">Time: ${fact.time_period?.raw || 'N/A'}</span>
        <span class="ctx-tag">Scope: ${fact.scope?.segment || 'Total'}</span>
        <span class="ctx-tag">Type: ${fact.scope?.reporting_type || 'Consolidated'}</span>
      </div>
      <div class="evidence-quote-box">
        "${ev.verbatim_quote || 'Quote unavailable'}"
      </div>
    </div>
  `;
}

// --- Load Failures (Requirement 4) ---
async function loadFailures() {
  try {
    const res = await fetch("/api/failures");
    if (!res.ok) return;
    const failures = await res.json();
    const container = document.getElementById("failuresContainer");
    container.innerHTML = "";

    if (failures.length === 0) {
      container.innerHTML = `<div class="empty-hint">No anomalies or failures logged.</div>`;
      return;
    }

    failures.forEach(f => {
      const card = document.createElement("div");
      card.className = "failure-card";
      card.innerHTML = `
        <div class="failure-top">
          <span class="fail-type-badge">${f.stage.toUpperCase()}: ${f.failure_type}</span>
          <span class="page-badge">📄 ${f.source_document} (Page ${f.page_number || 'N/A'})</span>
        </div>
        <div class="failure-desc">${f.description}</div>
        ${f.raw_snippet ? `<div class="evidence-quote-box" style="margin-bottom:10px;">"${f.raw_snippet}"</div>` : ''}
        <div class="mitigation-box">
          <strong>Handling & Mitigation:</strong> ${f.mitigation_strategy}
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load failures:", err);
  }
}

// --- Load Facts Table ---
async function loadFacts() {
  try {
    const res = await fetch("/api/facts");
    if (!res.ok) return;
    allFactsCache = await res.json();
    renderFactsTable(allFactsCache);
  } catch (err) {
    console.error("Failed to load facts:", err);
  }
}

function renderFactsTable(facts) {
  const tbody = document.getElementById("factsTableBody");
  tbody.innerHTML = "";

  if (facts.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:20px; color:var(--text-muted);">No facts extracted yet.</td></tr>`;
    return;
  }

  facts.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${f.subject}</strong></td>
      <td>${f.predicate}</td>
      <td style="font-family:var(--font-mono); color:var(--status-blue); font-weight:600;">${f.raw_value}</td>
      <td><span class="ctx-tag">${f.time_period?.raw || 'N/A'}</span></td>
      <td><span class="ctx-tag">${f.scope?.segment || 'Total'}</span></td>
      <td style="font-family:var(--font-mono); font-size:0.75rem;">${f.source_document}</td>
      <td><span class="page-badge">${f.page_number}</span></td>
      <td>
        <span class="badge-verified">
          ${f.evidence?.verified ? '✓ Verified' : '⚠ Unverified'}
        </span>
      </td>
      <td>
        <button class="btn btn-secondary btn-sm btn-inspect" data-id="${f.fact_id}">Inspect</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  document.querySelectorAll(".btn-inspect").forEach(b => {
    b.addEventListener("click", () => {
      const fid = b.getAttribute("data-id");
      const fact = allFactsCache.find(x => x.fact_id === fid);
      if (fact) showEvidenceModal(fact);
    });
  });
}

// --- Load Documents ---
async function loadDocuments() {
  try {
    const res = await fetch("/api/documents");
    if (!res.ok) return;
    const docs = await res.json();
    const container = document.getElementById("documentsList");
    container.innerHTML = "";

    if (docs.length === 0) {
      container.innerHTML = `<div class="empty-hint">No documents registered.</div>`;
      return;
    }

    docs.forEach(d => {
      const card = document.createElement("div");
      card.className = "doc-card";
      card.innerHTML = `
        <h4>📄 ${d.filename}</h4>
        <div class="doc-card-meta">
          <span>Pages: <strong>${d.page_count}</strong></span>
          <span>Status: <strong>${d.status}</strong></span>
          <span>Facts: <strong>${d.fact_count}</strong></span>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load documents:", err);
  }
}

// --- Setup File Upload ---
function setupUpload() {
  const fileInput = document.getElementById("pdfFileInput");
  const btnSelect = document.getElementById("btnSelectFiles");
  const btnUpload = document.getElementById("btnUpload");
  const statusSpan = document.getElementById("uploadStatus");
  const listDiv = document.getElementById("fileSelectionList");

  btnSelect.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    selectedFiles = Array.from(e.target.files);
    listDiv.innerHTML = "";

    if (selectedFiles.length > 0) {
      btnUpload.style.display = "inline-flex";
      selectedFiles.forEach(f => {
        const pill = document.createElement("span");
        pill.className = "file-pill";
        pill.textContent = `📄 ${f.name} (${(f.size / (1024*1024)).toFixed(1)} MB)`;
        listDiv.appendChild(pill);
      });
      statusSpan.textContent = `${selectedFiles.length} PDF(s) ready for processing.`;
    } else {
      btnUpload.style.display = "none";
      statusSpan.textContent = "";
    }
  });

  btnUpload.addEventListener("click", async () => {
    if (selectedFiles.length === 0) return;

    btnUpload.disabled = true;
    statusSpan.textContent = "Processing PDFs with PyMuPDF & Extracting Grounded Facts...";

    const formData = new FormData();
    selectedFiles.forEach(file => formData.append("files", file));

    try {
      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        statusSpan.textContent = "Pipeline completed successfully!";
        selectedFiles = [];
        fileInput.value = "";
        btnUpload.style.display = "none";
        listDiv.innerHTML = "";
        await refreshAll();
      } else {
        const err = await res.json();
        statusSpan.textContent = `Error: ${err.detail || 'Upload failed'}`;
      }
    } catch (err) {
      statusSpan.textContent = `Upload error: ${err.message}`;
    } finally {
      btnUpload.disabled = false;
    }
  });
}

// --- Setup Presets ---
function setupPresets() {
  const btnDelhivery = document.getElementById("btnLoadDelhivery");
  const btnMacro = document.getElementById("btnLoadMacro");
  const btnReset = document.getElementById("btnReset");

  btnDelhivery.addEventListener("click", async () => {
    btnDelhivery.disabled = true;
    btnDelhivery.textContent = "Loading Delhivery...";
    try {
      await fetch("/api/dataset-presets/delhivery", { method: "POST" });
      await refreshAll();
    } finally {
      btnDelhivery.disabled = false;
      btnDelhivery.textContent = "📦 Delhivery Logistics";
    }
  });

  btnMacro.addEventListener("click", async () => {
    btnMacro.disabled = true;
    btnMacro.textContent = "Loading Macro...";
    try {
      await fetch("/api/dataset-presets/india-macroeconomy", { method: "POST" });
      await refreshAll();
    } finally {
      btnMacro.disabled = false;
      btnMacro.textContent = "📊 India Macroeconomy";
    }
  });

  btnReset.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to clear all indexed facts and documents?")) return;
    await fetch("/api/reset", { method: "POST" });
    await refreshAll();
  });
}

// --- Setup Search ---
function setupSearch() {
  const input = document.getElementById("factSearchInput");
  input.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderFactsTable(allFactsCache);
      return;
    }
    const filtered = allFactsCache.filter(f =>
      f.subject.toLowerCase().includes(q) ||
      f.predicate.toLowerCase().includes(q) ||
      f.raw_value.toLowerCase().includes(q) ||
      f.source_document.toLowerCase().includes(q)
    );
    renderFactsTable(filtered);
  });
}

// --- Evidence Modal ---
function setupModal() {
  const modal = document.getElementById("evidenceModal");
  const btnClose = document.getElementById("btnCloseModal");

  btnClose.addEventListener("click", () => {
    modal.style.display = "none";
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });
}

function showEvidenceModal(fact) {
  const modal = document.getElementById("evidenceModal");
  const body = document.getElementById("modalBody");
  const ev = fact.evidence || {};

  body.innerHTML = `
    <div style="margin-bottom:14px;">
      <h4 style="font-size:1.1rem; color:var(--text-primary); margin-bottom:4px;">${fact.subject} — ${fact.predicate}</h4>
      <div style="font-size:0.85rem; color:var(--text-secondary);">
        Extracted Value: <strong style="color:var(--status-blue); font-size:1rem;">${fact.raw_value}</strong>
      </div>
    </div>

    <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-color); border-radius:var(--radius-md); padding:14px; margin-bottom:14px;">
      <div style="font-size:0.8rem; text-transform:uppercase; color:var(--text-muted); font-weight:600; margin-bottom:6px;">Source Document & Provenance</div>
      <div style="font-family:var(--font-mono); font-size:0.82rem; color:var(--status-blue); margin-bottom:4px;">📄 ${fact.source_document}</div>
      <div style="font-size:0.82rem; color:var(--text-secondary);">
        Printed/Physical Page: <strong>${fact.page_number}</strong> | Grounding Verification: 
        <strong style="color:var(--status-green);">${ev.verified ? '100% Verbatim Match' : 'Unverified'}</strong>
      </div>
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:0.8rem; text-transform:uppercase; color:var(--text-muted); font-weight:600; margin-bottom:6px;">Verbatim Source Evidence Quote</div>
      <div class="evidence-quote-box" style="font-size:0.9rem; line-height:1.6; padding:12px;">
        "${ev.verbatim_quote || 'Quote text unavailable'}"
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:0.82rem;">
      <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:var(--radius-sm);">
        <span style="color:var(--text-muted);">Normalized Time:</span>
        <div><strong>${fact.time_period?.raw || 'N/A'}</strong> (Year: ${fact.time_period?.normalized_year || 'N/A'})</div>
      </div>
      <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:var(--radius-sm);">
        <span style="color:var(--text-muted);">Scope:</span>
        <div><strong>${fact.scope?.segment || 'Total'}</strong> (${fact.scope?.reporting_type || 'Consolidated'})</div>
      </div>
    </div>
  `;

  modal.style.display = "flex";
}
