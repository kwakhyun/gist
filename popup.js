// popup.js — UI 제어, 텍스트 추출 요청, 백그라운드 스트리밍 수신

const $ = (sel) => document.querySelector(sel);
const t = (key, subs) => chrome.i18n.getMessage(key, subs);

const MAX_CHARS = 12000; // API 토큰 폭주 방지용 상한

const els = {
  noKeyBanner: $("#noKeyBanner"),
  openOptions: $("#openOptions"),
  settingsBtn: $("#settingsBtn"),
  tabs: document.querySelectorAll(".tab"),
  panels: document.querySelectorAll(".tab-panel"),
  summarizeBtn: $("#summarizeBtn"),
  translateBtn: $("#translateBtn"),
  summaryLength: $("#summaryLength"),
  summarizeSelectionOnly: $("#summarizeSelectionOnly"),
  targetLang: $("#targetLang"),
  translateSelectionOnly: $("#translateSelectionOnly"),
  status: $("#status"),
  resultWrap: $("#resultWrap"),
  result: $("#result"),
  copyBtn: $("#copyBtn"),
  copied: $("#copied"),
};

let busy = false;

// ---- 초기화 ---------------------------------------------------------------

init();

async function init() {
  const { apiKey } = await chrome.storage.sync.get("apiKey");
  if (!apiKey) els.noKeyBanner.classList.remove("hidden");

  els.settingsBtn.addEventListener("click", openOptions);
  els.openOptions.addEventListener("click", (e) => {
    e.preventDefault();
    openOptions();
  });

  els.tabs.forEach((tab) =>
    tab.addEventListener("click", () => switchTab(tab.dataset.tab))
  );

  els.summarizeBtn.addEventListener("click", () => runSummarize());
  els.translateBtn.addEventListener("click", () => runTranslate());
  els.copyBtn.addEventListener("click", copyResult);

  // 컨텍스트 메뉴에서 넘어온 대기 요청 처리
  const { pendingRequest } = await chrome.storage.session.get("pendingRequest");
  if (pendingRequest) {
    await chrome.storage.session.remove("pendingRequest");
    handlePending(pendingRequest);
  }
}

function openOptions() {
  chrome.runtime.openOptionsPage();
}

function switchTab(name) {
  els.tabs.forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  els.panels.forEach((p) =>
    p.classList.toggle("active", p.dataset.panel === name)
  );
}

async function handlePending(req) {
  if (req.action === "translate") {
    switchTab("translate");
    stream({
      action: "translate",
      text: req.text,
      targetLang: els.targetLang.value,
    });
  } else {
    switchTab("summarize");
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    stream({
      action: "summarize",
      text: req.text,
      title: tab?.title || "",
      length: els.summaryLength.value,
    });
  }
}

// ---- 텍스트 추출 ----------------------------------------------------------
// 콘텐츠 스크립트를 상시 주입하지 않고, 버튼을 누른 순간에만 활성 탭에
// 추출 함수를 실행한다(activeTab 권한 + 사용자 제스처).

async function extractFromPage(mode) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) throw new Error(t("errNoTab"));
  if (/^(chrome|edge|about|chrome-extension|view-source):/i.test(tab.url || "")) {
    throw new Error(t("errInternalPage"));
  }

  let results;
  try {
    results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: pageExtract,
      args: [mode, MAX_CHARS],
    });
  } catch (e) {
    throw new Error(t("errNoAccess", e.message || String(e)));
  }
  return results?.[0]?.result;
}

// 활성 탭 페이지 컨텍스트에서 실행되는 자기완결적 추출 함수.
// (외부 변수를 참조하면 안 됨 — executeScript가 직렬화해 주입한다.)
function pageExtract(mode, maxChars) {
  const NOISE = "script,style,noscript,nav,header,footer,aside,form,svg,iframe,button";

  function selectionText() {
    const sel = window.getSelection();
    return sel ? sel.toString().trim() : "";
  }

  function articleText() {
    const candidates = Array.from(
      document.querySelectorAll(
        "article, main, [role='main'], .post, .article, #content, .content, body"
      )
    );
    let best = null;
    let bestScore = 0;
    for (const el of candidates) {
      const clone = el.cloneNode(true);
      clone.querySelectorAll(NOISE).forEach((n) => n.remove());
      const len = (clone.innerText || "").replace(/\s+/g, " ").trim().length;
      const weight = /article|main/i.test(el.tagName) ? 1.3 : 1;
      const score = len * weight;
      if (score > bestScore) {
        bestScore = score;
        best = clone;
      }
    }
    const source = best || document.body.cloneNode(true);
    if (!best) source.querySelectorAll(NOISE).forEach((n) => n.remove());
    return (source.innerText || "")
      .replace(/\n{3,}/g, "\n\n")
      .replace(/[ \t]{2,}/g, " ")
      .trim();
  }

  const text = mode === "selection" ? selectionText() : articleText();
  return {
    text: text.slice(0, maxChars),
    truncated: text.length > maxChars,
    title: document.title || "",
    empty: text.length === 0,
  };
}

// ---- 실행 ----------------------------------------------------------------

async function runSummarize() {
  if (busy) return;
  const mode = els.summarizeSelectionOnly.checked ? "selection" : "article";
  await withExtraction(mode, (data) =>
    stream({
      action: "summarize",
      text: data.text,
      title: data.title,
      length: els.summaryLength.value,
    })
  );
}

async function runTranslate() {
  if (busy) return;
  const mode = els.translateSelectionOnly.checked ? "selection" : "article";
  await withExtraction(mode, (data) =>
    stream({
      action: "translate",
      text: data.text,
      targetLang: els.targetLang.value,
    })
  );
}

async function withExtraction(mode, run) {
  setStatus(t("statusExtracting"), false, true);
  try {
    const data = await extractFromPage(mode);
    if (!data || data.empty) {
      setStatus(t(mode === "selection" ? "errNoSelection" : "errNoExtract"), true);
      return;
    }
    run(data);
  } catch (err) {
    setStatus(err.message || String(err), true);
  }
}

// ---- 백그라운드 스트리밍 --------------------------------------------------

function stream(request) {
  busy = true;
  toggleButtons(true);
  setStatus(t("statusWorking"), false, true);
  els.result.textContent = "";
  els.resultWrap.classList.remove("hidden");
  els.copied.classList.add("hidden");

  const port = chrome.runtime.connect({ name: "ai-stream" });
  let received = false;

  port.onMessage.addListener((msg) => {
    if (msg.type === "chunk") {
      received = true;
      hideStatus();
      els.result.textContent += msg.delta;
      els.result.scrollTop = els.result.scrollHeight;
    } else if (msg.type === "done") {
      finish();
      if (!received) setStatus(t("errEmptyResponse"), true);
    } else if (msg.type === "error") {
      setStatus(msg.message, true);
      els.resultWrap.classList.toggle("hidden", !received);
      finish();
    }
  });

  port.onDisconnect.addListener(finish);

  function finish() {
    busy = false;
    toggleButtons(false);
  }

  port.postMessage(request);
}

// ---- UI 헬퍼 --------------------------------------------------------------

function toggleButtons(disabled) {
  els.summarizeBtn.disabled = disabled;
  els.translateBtn.disabled = disabled;
}

function setStatus(text, isError = false, spinner = false) {
  els.status.classList.remove("hidden");
  els.status.classList.toggle("error", isError);
  els.status.innerHTML = spinner ? '<span class="spinner"></span>' : "";
  els.status.append(document.createTextNode(text));
}

function hideStatus() {
  els.status.classList.add("hidden");
}

async function copyResult() {
  try {
    await navigator.clipboard.writeText(els.result.textContent);
    els.copied.classList.remove("hidden");
    setTimeout(() => els.copied.classList.add("hidden"), 1500);
  } catch {
    /* 무시 */
  }
}
