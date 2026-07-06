/* ── i18n ─────────────────────────────────────────────────────── */
const T = {
  en: {
    title: "Shared Skills Dashboard",
    agents: "Agents",
    skills: "Skills",
    quickActions: "Quick Actions",
    searchPlaceholder: "Search skills...",
    filterAll: "All statuses",
    filterSynced: "Synced",
    filterOutdated: "Outdated",
    filterMissing: "Missing",
    filterDisabled: "Disabled",
    filterAllAgents: "All agents",
    colSkill: "Skill",
    colDescription: "Description",
    colAgents: "Agents",
    colStatus: "Status",
    colUpdated: "Last Updated",
    btnSyncAll: "Sync All",
    btnSyncAllCmd: "python3 sync-skills.py",
    btnSyncAllDesc: "Sync all skills to their configured agents.",
    btnCheck: "Check Status",
    btnCheckCmd: "python3 sync-skills.py --check",
    btnCheckDesc: "Compare stored hashes against current sources.",
    btnViewLog: "View Sync Log",
    btnViewLogCmd: "python3 sync-skills.py --show-log",
    btnViewLogDesc: "Show the last 20 sync events.",
    statTotal: "Total Skills",
    statSynced: "Synced",
    statOutdated: "Outdated",
    statMissing: "Missing",
    statDisabled: "Disabled",
    synced: "synced",
    outdated: "outdated",
    missing: "missing",
    disabled: "disabled",
    none: "None",
    never: "never",
    hashLabel: "Hash",
    pathLabel: "Path",
    syncLabel: "Last sync",
    expandHint: "Click a skill row to see per-agent details.",
    openclawHint: "Not in sync_to — has agent copies but not managed by sync system.",
  },
  cn: {
    title: "共享技能面板",
    agents: "Agent 总览",
    skills: "技能列表",
    quickActions: "快捷命令",
    searchPlaceholder: "搜索技能...",
    filterAll: "全部状态",
    filterSynced: "已同步",
    filterOutdated: "已过期",
    filterMissing: "缺失",
    filterDisabled: "已禁用",
    filterAllAgents: "全部 Agent",
    colSkill: "技能名称",
    colDescription: "描述",
    colAgents: "Agent",
    colStatus: "状态",
    colUpdated: "最近更新",
    btnSyncAll: "全部同步",
    btnSyncAllCmd: "python3 sync-skills.py",
    btnSyncAllDesc: "将所有技能同步到已配置的 Agent。",
    btnCheck: "检查状态",
    btnCheckCmd: "python3 sync-skills.py --check",
    btnCheckDesc: "对比存储的哈希值与当前源文件。",
    btnViewLog: "查看同步日志",
    btnViewLogCmd: "python3 sync-skills.py --show-log",
    btnViewLogDesc: "显示最近 20 条同步事件。",
    statTotal: "技能总数",
    statSynced: "已同步",
    statOutdated: "已过期",
    statMissing: "缺失",
    statDisabled: "已禁用",
    synced: "已同步",
    outdated: "已过期",
    missing: "缺失",
    disabled: "已禁用",
    none: "无",
    never: "从未",
    hashLabel: "哈希",
    pathLabel: "路径",
    syncLabel: "最近同步",
    expandHint: "点击技能行查看各 Agent 详情。",
    openclawHint: "未在 sync_to 中——Agent 中有副本但不受同步系统管理。",
  },
};

/* ── State ────────────────────────────────────────────────────── */
let data = null;
let currentLang = localStorage.getItem("shared-skills-lang") || "en";
let expandedSkill = null;

/* ── Init ─────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  applyLanguage();

  fetch("data.json")
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((json) => {
      data = json;
      renderAll();
    })
    .catch((err) => {
      document.getElementById("skillTableBody").innerHTML =
        `<tr><td colspan="5" style="color:var(--red);padding:20px;text-align:center">
          Failed to load data.json: ${err.message}<br>
          <small>Run <code>python3 webui/data.py</code> to generate it.</small>
        </td></tr>`;
    });

  document.getElementById("langToggle").addEventListener("click", toggleLanguage);
  document.getElementById("searchInput").addEventListener("input", filterSkills);
  document.getElementById("statusFilter").addEventListener("change", filterSkills);
  document.getElementById("agentFilter").addEventListener("change", filterSkills);
});

/* ── Render All ───────────────────────────────────────────────── */
function renderAll() {
  renderSummary();
  renderAgentCards();
  renderAgentFilter();
  renderSkillTable();
  renderQuickActions();
  document.getElementById("genTime").textContent = formatTime(data.generated_at);
}

/* ── Language ─────────────────────────────────────────────────── */
function toggleLanguage() {
  currentLang = currentLang === "en" ? "cn" : "en";
  localStorage.setItem("shared-skills-lang", currentLang);
  applyLanguage();
  if (data) renderAll();
}

function applyLanguage() {
  document.documentElement.setAttribute("data-lang", currentLang);
  document.getElementById("langToggle").textContent =
    currentLang === "en" ? "中文" : "English";

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (T[currentLang] && T[currentLang][key]) {
      el.textContent = T[currentLang][key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (T[currentLang] && T[currentLang][key]) {
      el.setAttribute("placeholder", T[currentLang][key]);
    }
  });
}

function t(key) {
  return (T[currentLang] && T[currentLang][key]) || key;
}

/* ── Summary Bar ──────────────────────────────────────────────── */
function renderSummary() {
  const s = data.summary;
  const html = [
    statBox("synced", t("statSynced"), s.synced),
    statBox("outdated", t("statOutdated"), s.outdated),
    statBox("missing", t("statMissing"), s.missing),
    statBox("disabled", t("statDisabled"), s.disabled),
  ].join("");
  document.getElementById("summaryBar").innerHTML = html;
}

function statBox(cls, label, value) {
  return `<div class="stat ${cls}">
    <span class="stat-value">${value}</span>
    <span class="stat-label">${label}</span>
  </div>`;
}

/* ── Agent Cards ──────────────────────────────────────────────── */
function renderAgentCards() {
  const agents = data.agents;
  const html = Object.values(agents)
    .map((a) => {
      const statusParts = [];
      if (a.synced > 0) statusParts.push(`${a.synced} ${t("synced")}`);
      if (a.outdated > 0) statusParts.push(`${a.outdated} ${t("outdated")}`);
      if (a.missing > 0) statusParts.push(`${a.missing} ${t("missing")}`);
      if (a.disabled > 0) statusParts.push(`${a.disabled} ${t("disabled")}`);

      const lastSync = a.last_sync
        ? formatRelative(a.last_sync)
        : t("never");

      return `<div class="agent-card health-${a.health}">
        <div class="agent-name">
          <span class="agent-dot"></span>
          ${a.name}
        </div>
        <div class="agent-stats">${statusParts.join(" · ")}</div>
        <div class="agent-path" title="${esc(a.base_path)}">${esc(a.base_path)}</div>
        <div class="agent-sync">${t("syncLabel")}: ${lastSync}</div>
      </div>`;
    })
    .join("");

  document.getElementById("agentCards").innerHTML = html;
}

/* ── Agent Filter ─────────────────────────────────────────────── */
function renderAgentFilter() {
  const agents = Object.keys(data.agents);
  const sel = document.getElementById("agentFilter");
  sel.innerHTML =
    `<option value="all">${t("filterAllAgents")}</option>` +
    agents
      .map((a) => `<option value="${a}">${data.agents[a].name}</option>`)
      .join("");
}

/* ── Skill Table ──────────────────────────────────────────────── */
function renderSkillTable(forceSkills) {
  const skills = forceSkills || data.skills;
  const body = document.getElementById("skillTableBody");

  if (skills.length === 0) {
    body.innerHTML =
      `<tr><td colspan="5" style="text-align:center;padding:24px;color:var(--text-muted)">
        ${t("none")}
      </td></tr>`;
    return;
  }

  let html = "";
  skills.forEach((skill, idx) => {
    const rowStatus = skillRowStatus(skill);
    const rowId = `skill-${idx}`;
    const isExpanded = expandedSkill === skill.name;

    html += `<tr class="${isExpanded ? "expanded" : ""}" data-skill="${esc(skill.name)}" data-row-id="${rowId}" onclick="toggleSkillDetail('${esc(skill.name)}', ${idx})">
      <td class="skill-name">${esc(skill.name)}</td>
      <td class="skill-desc" title="${escAttr(skill.description)}">${esc(skill.description)}</td>
      <td>${renderAgentIcons(skill)}</td>
      <td><span class="badge badge-${rowStatus}">${t(rowStatus)}</span></td>
      <td>${skillLastSync(skill)}</td>
    </tr>`;

    // Detail row
    html += `<tr class="detail-row ${isExpanded ? "show" : ""}" id="${rowId}-detail">
      <td colspan="5">
        <div class="detail-grid">
          ${renderSkillDetail(skill)}
        </div>
      </td>
    </tr>`;
  });

  body.innerHTML = html;
}

function skillRowStatus(skill) {
  const statuses = Object.values(skill.agents).map((a) => a.status);
  if (statuses.every((s) => s === "disabled")) return "disabled";
  if (statuses.every((s) => s === "synced" || s === "disabled")) return "synced";
  if (statuses.some((s) => s === "outdated")) return "outdated";
  if (statuses.some((s) => s === "missing")) return "missing";
  return "synced";
}

function skillLastSync(skill) {
  const timestamps = Object.values(skill.agents)
    .map((a) => a.last_sync)
    .filter(Boolean);
  if (timestamps.length === 0) return t("never");
  return formatRelative(timestamps.sort().pop());
}

/* ── Agent Icons ──────────────────────────────────────────────── */
const AGENT_INITIALS = { hermes: "H", claude: "C", codex: "X", openclaw: "O" };
const AGENT_ORDER = ["hermes", "claude", "codex", "openclaw"];

function renderAgentIcons(skill) {
  return AGENT_ORDER.map((agent) => {
    const info = skill.agents[agent];
    if (!info) return "";
    const cls = `ai-${info.status}`;
    const title = `${data.agents[agent].name}: ${t(info.status)}`;
    return `<span class="agent-icon ${cls}" title="${escAttr(title)}">${AGENT_INITIALS[agent]}</span>`;
  }).join("");
}

/* ── Skill Detail (expand) ───────────────────────────────────── */
function toggleSkillDetail(skillName, idx) {
  expandedSkill = expandedSkill === skillName ? null : skillName;

  // Toggle row highlight
  const rows = document.querySelectorAll(`[data-skill]`);
  rows.forEach((r) => {
    r.classList.toggle("expanded", r.getAttribute("data-skill") === expandedSkill);
  });

  // Toggle detail rows
  document.querySelectorAll(".detail-row").forEach((r) => r.classList.remove("show"));
  if (expandedSkill) {
    const detailRow = document.getElementById(`skill-${idx}-detail`);
    if (detailRow) detailRow.classList.add("show");
  }
}

function renderSkillDetail(skill) {
  return AGENT_ORDER.map((agent) => {
    const info = skill.agents[agent];
    if (!info) return "";
    const agentName = data.agents[agent].name;
    const isTarget = skill.sync_to.includes(agent);

    let extra = "";
    if (!isTarget) {
      extra = `<span style="font-size:0.75rem;color:var(--text-dim);display:block;margin-top:4px">${t("openclawHint")}</span>`;
    }

    return `<div class="detail-agent">
      <div class="da-header">
        <span class="agent-icon ai-${info.status}" style="width:16px;height:16px;font-size:0.55rem">${AGENT_INITIALS[agent]}</span>
        ${agentName}
        <span class="badge badge-${info.status}" style="margin-left:auto">${t(info.status)}</span>
      </div>
      <div class="da-body">
        ${info.stored_hash ? `<span><span class="da-label">${t("hashLabel")}:</span> ${info.stored_hash}</span>` : ""}
        ${info.path ? `<span><span class="da-label">${t("pathLabel")}:</span> ${esc(info.path)}</span>` : ""}
        <span><span class="da-label">${t("syncLabel")}:</span> ${info.last_sync ? formatTime(info.last_sync) : t("never")}</span>
      </div>
      ${extra}
    </div>`;
  }).join("");
}

/* ── Filter ───────────────────────────────────────────────────── */
function filterSkills() {
  if (!data) return;

  const search = document.getElementById("searchInput").value.toLowerCase().trim();
  const status = document.getElementById("statusFilter").value;
  const agent = document.getElementById("agentFilter").value;

  let filtered = data.skills;

  // Text search
  if (search) {
    filtered = filtered.filter(
      (s) =>
        s.name.toLowerCase().includes(search) ||
        s.description.toLowerCase().includes(search)
    );
  }

  // Status filter
  if (status !== "all") {
    filtered = filtered.filter((s) => {
      const statuses = Object.values(s.agents).map((a) => a.status);
      if (status === "synced")
        return statuses.every((st) => st === "synced" || st === "disabled");
      if (status === "outdated") return statuses.includes("outdated");
      if (status === "missing") return statuses.includes("missing");
      if (status === "disabled")
        return statuses.every((st) => st === "disabled");
      return true;
    });
  }

  // Agent filter
  if (agent !== "all") {
    filtered = filtered.filter((s) => {
      const info = s.agents[agent];
      return info && info.status !== "disabled";
    });
  }

  // Reset expanded state when filtering
  expandedSkill = null;

  renderSkillTable(filtered);
}

/* ── Quick Actions ────────────────────────────────────────────── */
function renderQuickActions() {
  const actions = [
    ["btnSyncAll", "btnSyncAllCmd", "btnSyncAllDesc"],
    ["btnCheck", "btnCheckCmd", "btnCheckDesc"],
    ["btnViewLog", "btnViewLogCmd", "btnViewLogDesc"],
  ];

  const html = actions
    .map(([titleKey, cmdKey, descKey]) => {
      return `<div class="action-card">
        <div class="action-title">${t(titleKey)}</div>
        <code>${t(cmdKey)}</code>
        <div class="action-desc">${t(descKey)}</div>
      </div>`;
    })
    .join("");

  document.getElementById("quickActions").innerHTML = html;
}

/* ── Format Helpers ───────────────────────────────────────────── */
function formatTime(iso) {
  if (!iso) return t("never");
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString(currentLang === "cn" ? "zh-CN" : "en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatRelative(iso) {
  if (!iso) return t("never");
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const now = new Date();
  const diff = now - d;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (currentLang === "cn") {
    if (minutes < 1) return "刚刚";
    if (minutes < 60) return `${minutes} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 30) return `${days} 天前`;
  } else {
    if (minutes < 1) return "just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 30) return `${days}d ago`;
  }
  return formatTime(iso);
}

/* ── Escape ───────────────────────────────────────────────────── */
function esc(s) {
  if (!s) return "";
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(s));
  return div.innerHTML;
}

function escAttr(s) {
  return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
