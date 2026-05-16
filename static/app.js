const $ = (id) => document.getElementById(id);

const tabs = document.querySelectorAll(".tab");
const panelFile = $("panel-file");
const panelUrl = $("panel-url");
const fileInput = $("file-input");
const dropzone = $("dropzone");
const dropzoneLabel = $("dropzone-label");
const btnFile = $("btn-file");
const urlInput = $("url-input");
const btnUrl = $("btn-url");
const statusEl = $("status");
const errorEl = $("error");
const resultEl = $("result");
const previewEl = $("preview");
const btnDownloadTxt = $("btn-download-txt");
const btnDownloadDocx = $("btn-download-docx");

let selectedFile = null;
let lastText = "";

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const mode = tab.dataset.mode;
    tabs.forEach((t) => {
      const active = t.dataset.mode === mode;
      t.classList.toggle("active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    });
    panelFile.classList.toggle("hidden", mode !== "file");
    panelUrl.classList.toggle("hidden", mode !== "url");
    hideError();
  });
});

function setFile(file) {
  selectedFile = file;
  btnFile.disabled = !file;
  dropzoneLabel.textContent = file
    ? file.name
    : "Перетащите видео сюда или нажмите для выбора";
}

fileInput.addEventListener("change", () => {
  setFile(fileInput.files[0] || null);
});

dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.classList.add("dragover");
});

dropzone.addEventListener("dragleave", () => {
  dropzone.classList.remove("dragover");
});

dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    setFile(file);
  }
});

function showStatus(msg) {
  statusEl.textContent = msg;
  statusEl.classList.remove("hidden");
}

function hideStatus() {
  statusEl.classList.add("hidden");
}

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}

function hideResult() {
  resultEl.classList.add("hidden");
}

function showResult(text) {
  lastText = text;
  previewEl.textContent = text.length > 2000 ? text.slice(0, 2000) + "…" : text;
  resultEl.classList.remove("hidden");
}

function setLoading(loading) {
  btnFile.disabled = loading || !selectedFile;
  btnUrl.disabled = loading;
  document.querySelectorAll(".tab").forEach((t) => {
    t.disabled = loading;
  });
  if (loading) {
    showStatus("Обрабатываем… Это может занять несколько минут.");
    hideError();
    hideResult();
  } else {
    hideStatus();
  }
}

async function parseError(res) {
  try {
    const data = await res.json();
    const d = data.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) return d.map((x) => x.msg || String(x)).join("\n");
  } catch {
    /* ignore */
  }
  return res.statusText || "Неизвестная ошибка";
}

function downloadText() {
  const blob = new Blob([lastText], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "transcript.txt";
  a.click();
  URL.revokeObjectURL(a.href);
}

btnDownloadTxt.addEventListener("click", downloadText);

btnDownloadDocx.addEventListener("click", async () => {
  if (!lastText) return;
  try {
    const res = await fetch("/export/docx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: lastText }),
    });
    if (!res.ok) throw new Error(await parseError(res));
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "transcript.docx";
    a.click();
    URL.revokeObjectURL(a.href);
  } catch (e) {
    showError(e.message || String(e));
  }
});

btnFile.addEventListener("click", async () => {
  if (!selectedFile) return;
  setLoading(true);
  try {
    const form = new FormData();
    form.append("file", selectedFile);
    const res = await fetch("/transcribe/file", { method: "POST", body: form });
    if (!res.ok) throw new Error(await parseError(res));
    const { text } = await res.json();
    showResult(text);
  } catch (e) {
    showError(e.message || String(e));
  } finally {
    setLoading(false);
  }
});

btnUrl.addEventListener("click", async () => {
  const url = urlInput.value.trim();
  if (!url) {
    showError("Вставьте ссылку на видео");
    return;
  }
  setLoading(true);
  try {
    const res = await fetch("/transcribe/url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    if (!res.ok) throw new Error(await parseError(res));
    const { text } = await res.json();
    showResult(text);
  } catch (e) {
    showError(e.message || String(e));
  } finally {
    setLoading(false);
  }
});
