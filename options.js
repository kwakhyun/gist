// options.js — 설정 저장/로드

const $ = (s) => document.querySelector(s);
const t = (key) => chrome.i18n.getMessage(key);

const KEY_HINTS = {
  openai: () => t("keyHintOpenAI"),
  anthropic: () => t("keyHintAnthropic"),
  gemini: () => t("keyHintGemini"),
};

const provider = $("#provider");
const apiKey = $("#apiKey");

async function load() {
  const cfg = await chrome.storage.sync.get([
    "provider",
    "apiKey",
    "openaiModel",
    "anthropicModel",
    "geminiModel",
    "openaiModelCustom",
    "anthropicModelCustom",
    "geminiModelCustom",
  ]);
  provider.value = cfg.provider || "openai";
  apiKey.value = cfg.apiKey || "";
  if (cfg.openaiModel) $("#openaiModel").value = cfg.openaiModel;
  if (cfg.anthropicModel) $("#anthropicModel").value = cfg.anthropicModel;
  if (cfg.geminiModel) $("#geminiModel").value = cfg.geminiModel;
  $("#openaiModelCustom").value = cfg.openaiModelCustom || "";
  $("#anthropicModelCustom").value = cfg.anthropicModelCustom || "";
  $("#geminiModelCustom").value = cfg.geminiModelCustom || "";
  syncProviderUI();
}

function syncProviderUI() {
  const p = provider.value;
  $("#keyHint").innerHTML = KEY_HINTS[p]();
  document.querySelectorAll(".provider-block").forEach((b) => {
    b.classList.toggle("hidden", b.dataset.provider !== p);
  });
}

async function save() {
  await chrome.storage.sync.set({
    provider: provider.value,
    apiKey: apiKey.value.trim(),
    openaiModel: $("#openaiModel").value,
    anthropicModel: $("#anthropicModel").value,
    geminiModel: $("#geminiModel").value,
    openaiModelCustom: $("#openaiModelCustom").value.trim(),
    anthropicModelCustom: $("#anthropicModelCustom").value.trim(),
    geminiModelCustom: $("#geminiModelCustom").value.trim(),
  });
  const saved = $("#saved");
  saved.classList.remove("hidden");
  setTimeout(() => saved.classList.add("hidden"), 1800);
}

provider.addEventListener("change", syncProviderUI);
$("#saveBtn").addEventListener("click", save);
$("#toggleKey").addEventListener("click", () => {
  const btn = $("#toggleKey");
  if (apiKey.type === "password") {
    apiKey.type = "text";
    btn.textContent = t("hideKey");
  } else {
    apiKey.type = "password";
    btn.textContent = t("showKey");
  }
});

load();
