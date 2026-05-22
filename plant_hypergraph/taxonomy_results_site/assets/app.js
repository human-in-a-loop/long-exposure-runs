const state = {
  summary: null,
  evidence: [],
  selectedTrack: null,
};

const routeLinks = Array.from(document.querySelectorAll("[data-route-target]"));
const routes = Array.from(document.querySelectorAll("[data-route]"));
const nav = document.querySelector("#site-nav");
const menuButton = document.querySelector(".menu-button");

function bySlug(slug) {
  return state.summary.tracks.find((track) => track.slug === slug);
}

function setRoute(routeName) {
  routes.forEach((route) => {
    route.classList.toggle("active", route.dataset.route === routeName);
  });
  routeLinks.forEach((link) => {
    link.classList.toggle("active", link.dataset.routeTarget === routeName);
  });
  if (nav) {
    nav.classList.remove("open");
  }
  if (menuButton) {
    menuButton.setAttribute("aria-expanded", "false");
  }
  window.scrollTo({ top: 0, left: 0 });
}

function trackCard(track) {
  return `
    <article class="quick-card">
      <h3>${track.track}: ${track.label}</h3>
      <p>${track.plain_question}</p>
      <span class="status-pill ${track.status_class}">${track.status_label}</span>
    </article>
  `;
}

function renderQuickCards() {
  document.querySelector("#quick-track-cards").innerHTML = state.summary.tracks.map(trackCard).join("");
}

function renderTrackList() {
  const list = document.querySelector("#track-list");
  list.innerHTML = state.summary.tracks
    .map(
      (track) => `
        <button class="track-button" type="button" data-track="${track.slug}">
          <strong>${track.track}: ${track.label}</strong>
          <span>${track.plain_question}</span>
          <span class="status-pill ${track.status_class}">${track.status_label}</span>
        </button>
      `,
    )
    .join("");
  list.addEventListener("click", (event) => {
    const button = event.target.closest("[data-track]");
    if (!button) return;
    selectTrack(button.dataset.track);
  });
  selectTrack(state.summary.tracks[0].slug);
}

function selectTrack(slug) {
  state.selectedTrack = slug;
  document.querySelectorAll(".track-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.track === slug);
  });
  const track = bySlug(slug);
  const detail = document.querySelector("#track-detail");
  detail.innerHTML = `
    <p class="eyebrow">${track.track}</p>
    <h2>${track.label}</h2>
    <p class="lead">${track.public_result}</p>
    <span class="status-pill ${track.status_class}">${track.status_label}</span>
    <div class="detail-grid">
      <div class="detail-box"><h3>Field focus</h3><p>${track.field_focus}</p></div>
      <div class="detail-box"><h3>Evidence basis</h3><p>${track.validated_branch_basis}</p></div>
      <div class="detail-box"><h3>Key counts</h3><p>${track.key_counts}</p></div>
      <div class="detail-box"><h3>Claim boundary</h3><p>${track.claim_boundary}</p></div>
    </div>
    <dl>
      <dt>Main blocker</dt><dd>${track.blocker}</dd>
      <dt>Future evidence</dt><dd>${track.future_data_required}</dd>
    </dl>
    <div class="hero-actions">
      <button type="button" data-route-target="evidence">Open evidence explorer</button>
      <button type="button" data-route-target="future">See future predicate</button>
    </div>
  `;
}

function renderStatusTable() {
  const tbody = document.querySelector("#status-table tbody");
  tbody.innerHTML = state.summary.tracks
    .map(
      (track) => `
        <tr>
          <td><strong>${track.track}</strong><br />${track.label}</td>
          <td><span class="status-pill ${track.status_class}">${track.status_label}</span></td>
          <td>${track.key_counts}</td>
          <td>${track.claim_boundary}</td>
        </tr>
      `,
    )
    .join("");
}

function renderFilters() {
  const select = document.querySelector("#track-filter");
  select.insertAdjacentHTML(
    "beforeend",
    state.summary.tracks.map((track) => `<option value="${track.slug}">${track.track}: ${track.label}</option>`).join(""),
  );
  select.addEventListener("change", renderEvidence);
  document.querySelector("#evidence-search").addEventListener("input", renderEvidence);
}

function renderEvidence() {
  const selected = document.querySelector("#track-filter").value;
  const query = document.querySelector("#evidence-search").value.trim().toLowerCase();
  const cards = state.evidence.filter((row) => {
    const track = bySlug(row.slug);
    const text = Object.values(row).join(" ").toLowerCase();
    const trackMatches = selected === "all" || row.slug === selected;
    return trackMatches && (!query || text.includes(query) || track.label.toLowerCase().includes(query));
  });
  document.querySelector("#evidence-grid").innerHTML = cards
    .map((row) => {
      const track = bySlug(row.slug);
      return `
        <article class="evidence-card">
          <h3>${track.track}: ${track.label}</h3>
          <span class="status-pill ${track.status_class}">${track.status_label}</span>
          <dl>
            <dt>Source basis</dt><dd>${row.source}</dd>
            <dt>Accepted names</dt><dd>${row.accepted_name_status}</dd>
            <dt>Evidence type</dt><dd>${row.evidence_type}</dd>
            <dt>Validation use</dt><dd>${row.validation_use}</dd>
            <dt>Rejection reason</dt><dd>${row.rejection_reason}</dd>
            <dt>Future evidence</dt><dd>${row.future_evidence_predicate}</dd>
          </dl>
        </article>
      `;
    })
    .join("");
}

function renderLimits() {
  document.querySelector("#limit-list").innerHTML = state.summary.tracks
    .map(
      (track) => `
        <article class="limit-card">
          <h3>${track.track}: ${track.label}</h3>
          <p><strong>Limit:</strong> ${track.blocker}</p>
          <p><strong>Boundary:</strong> ${track.claim_boundary}</p>
        </article>
      `,
    )
    .join("");
}

function renderFuture() {
  document.querySelector("#future-list").innerHTML = state.summary.tracks
    .map(
      (track) => `
        <article class="future-card">
          <h3>${track.track}: ${track.label}</h3>
          <p>${track.future_data_required}</p>
        </article>
      `,
    )
    .join("");
}

function setupFigureModal() {
  const modal = document.querySelector("#figure-modal");
  const image = document.querySelector("#modal-image");
  const caption = document.querySelector("#modal-caption");
  const title = document.querySelector("#modal-title");
  document.querySelectorAll(".inspectable").forEach((figure) => {
    figure.addEventListener("click", () => {
      const img = figure.querySelector("img");
      const figcaption = figure.querySelector("figcaption");
      image.src = img.src;
      image.alt = img.alt;
      title.textContent = img.alt || "Figure inspection";
      caption.textContent = figcaption ? figcaption.textContent.trim() : "";
      modal.hidden = false;
    });
  });
  document.querySelector("#modal-close").addEventListener("click", () => {
    modal.hidden = true;
  });
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.hidden = true;
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      modal.hidden = true;
    }
  });
}

function setupNavigation() {
  document.body.addEventListener("click", (event) => {
    const target = event.target.closest("[data-route-target]");
    if (!target) return;
    const routeName = target.dataset.routeTarget;
    if (document.querySelector(`[data-route="${routeName}"]`)) {
      event.preventDefault();
      setRoute(routeName);
      history.replaceState(null, "", `#${routeName}`);
    }
  });
  menuButton.addEventListener("click", () => {
    const open = !nav.classList.contains("open");
    nav.classList.toggle("open", open);
    menuButton.setAttribute("aria-expanded", String(open));
  });
}

async function loadEvidence(summary) {
  const tables = await Promise.all(
    summary.tracks.map(async (track) => {
      const response = await fetch(`data/evidence_tables/${track.slug}.json`);
      const rows = await response.json();
      return rows.map((row) => ({ ...row, slug: track.slug }));
    }),
  );
  return tables.flat();
}

async function init() {
  setupNavigation();
  const response = await fetch("data/site_summary.json");
  state.summary = await response.json();
  state.evidence = await loadEvidence(state.summary);
  renderQuickCards();
  renderTrackList();
  renderStatusTable();
  renderFilters();
  renderEvidence();
  renderLimits();
  renderFuture();
  setupFigureModal();
  const initial = location.hash.replace("#", "") || "start";
  setRoute(document.querySelector(`[data-route="${initial}"]`) ? initial : "start");
}

init().catch((error) => {
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div class="load-error">The site data could not be loaded: ${error.message}</div>`,
  );
});
