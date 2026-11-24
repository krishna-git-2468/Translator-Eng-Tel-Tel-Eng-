const $ = (id) => document.getElementById(id);
const input = $("input"), output = $("output"), statusEl = $("status"), go = $("go");
const NAMES = { en: "English", te: "తెలుగు" };
const TELUGU = /[\u0C00-\u0C7F]/;
let source = "en";

function setDirection(src) {
  source = src;
  $("fromLabel").textContent = NAMES[src];
  $("toLabel").textContent = NAMES[src === "en" ? "te" : "en"];
}

input.addEventListener("input", () => {
  $("count").textContent = `${input.value.length} / 2000`;
  if (input.value.trim()) setDirection(TELUGU.test(input.value) ? "te" : "en");
});

$("swap").onclick = () => {
  const t = output.dataset.text;
  if (t) { input.value = t; output.textContent = ""; output.dataset.text = ""; }
  setDirection(source === "en" ? "te" : "en");
  input.dispatchEvent(new Event("input"));
};

$("clear").onclick = () => {
  input.value = ""; output.textContent = "Translation appears here";
  output.className = "out placeholder"; output.dataset.text = "";
  statusEl.textContent = ""; $("count").textContent = "0 / 2000";
};

$("copy").onclick = async () => {
  if (!output.dataset.text) return;
  await navigator.clipboard.writeText(output.dataset.text);
  statusEl.textContent = "Copied";
};

async function translate() {
  const text = input.value.trim();
  if (!text) { statusEl.textContent = "Enter some text first."; return; }
  go.disabled = true;
  statusEl.className = "";
  statusEl.textContent = "Translating. The first request loads the model and can take a minute.";
  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, source })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    output.textContent = data.translation;
    output.className = "out";
    output.dataset.text = data.translation;
    statusEl.textContent = "";
    loadHistory();
  } catch (e) {
    statusEl.className = "error";
    statusEl.textContent = e.message;
  } finally {
    go.disabled = false;
  }
}
go.onclick = translate;
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) translate();
});

async function loadHistory() {
  const rows = await (await fetch("/api/history")).json();
  const ul = $("history");
  ul.innerHTML = "";
  if (!rows.length) {
    ul.innerHTML = '<li class="empty">Nothing yet. Your last 20 translations show up here.</li>';
    return;
  }
  for (const r of rows) {
    const li = document.createElement("li");
    const a = document.createElement("div");
    const b = document.createElement("div");
    a.textContent = r.original;
    b.textContent = r.translation;
    b.className = "t";
    li.append(a, b);
    ul.append(li);
  }
}
$("clearHistory").onclick = async () => {
  await fetch("/api/history", { method: "DELETE" });
  loadHistory();
};

output.className = "out placeholder";
loadHistory();
