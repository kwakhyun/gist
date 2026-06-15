// background.js — 서비스 워커
// 팝업/컨텍스트 메뉴로부터 요청을 받아 OpenAI 또는 Anthropic API를 스트리밍 호출한다.
// API 키는 chrome.storage.sync 에 저장된 사용자 본인의 키만 사용한다.

const DEFAULTS = {
  provider: "openai",
  openaiModel: "gpt-5.4-mini",
  anthropicModel: "claude-haiku-4-5-20251001",
};

async function getConfig() {
  const stored = await chrome.storage.sync.get([
    "provider",
    "apiKey",
    "openaiModel",
    "anthropicModel",
    "openaiModelCustom",
    "anthropicModelCustom",
  ]);
  const cfg = { ...DEFAULTS, ...stored };
  // 사용자가 직접 입력한 모델 ID가 있으면 드롭다운 선택보다 우선
  cfg.openaiModel = (cfg.openaiModelCustom || "").trim() || cfg.openaiModel;
  cfg.anthropicModel = (cfg.anthropicModelCustom || "").trim() || cfg.anthropicModel;
  return cfg;
}

// ---- 프롬프트 구성 ---------------------------------------------------------

function buildPrompt({ action, text, title, length, targetLang }) {
  if (action === "translate") {
    return {
      system:
        `You are a professional translator. Translate the user's text into ${targetLang}. ` +
        `Preserve meaning, tone, and formatting (line breaks, lists). ` +
        `Output ONLY the translation, with no explanations or quotes.`,
      user: text,
    };
  }

  // summarize
  const lengthInstruction = {
    short: "Summarize in at most 3 concise sentences.",
    medium: "Summarize as 5 short bullet points, each starting with '- '.",
    long: "Write a thorough summary: a one-line headline, then key points as bullets, then a short conclusion.",
  }[length] || "Summarize as 5 short bullet points.";

  return {
    system:
      `You are an expert at summarizing web content. ${lengthInstruction} ` +
      `Write the summary in the SAME language as the source text. ` +
      `Be faithful to the content; do not invent facts.`,
    user: `Title: ${title}\n\nContent:\n${text}`,
  };
}

// ---- 스트리밍 호출 ---------------------------------------------------------

async function* streamOpenAI({ apiKey, model, system, user, signal }) {
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    signal,
    body: JSON.stringify({
      model,
      stream: true,
      messages: [
        { role: "system", content: system },
        { role: "user", content: user },
      ],
    }),
  });

  if (!res.ok) {
    throw new Error(await readError(res, "OpenAI"));
  }

  for await (const data of readSSE(res)) {
    if (data === "[DONE]") return;
    try {
      const json = JSON.parse(data);
      const delta = json.choices?.[0]?.delta?.content;
      if (delta) yield delta;
    } catch {
      /* 부분 라인 무시 */
    }
  }
}

async function* streamAnthropic({ apiKey, model, system, user, signal }) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      // 브라우저(확장 프로그램)에서 직접 호출 허용
      "anthropic-dangerous-direct-browser-access": "true",
    },
    signal,
    body: JSON.stringify({
      model,
      max_tokens: 2048,
      stream: true,
      system,
      messages: [{ role: "user", content: user }],
    }),
  });

  if (!res.ok) {
    throw new Error(await readError(res, "Anthropic"));
  }

  for await (const data of readSSE(res)) {
    let json;
    try {
      json = JSON.parse(data);
    } catch {
      continue; // 부분 라인 무시
    }
    if (json.type === "error") {
      throw new Error(t("errAnthropicStream", json.error?.message || "stream aborted"));
    }
    if (json.type === "content_block_delta" && json.delta?.text) {
      yield json.delta.text;
    }
  }
}

// SSE 응답을 라인 단위로 파싱해 data 페이로드를 순차 반환
async function* readSSE(res) {
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  const emit = function* (chunk) {
    const lines = chunk.split("\n");
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("data:")) {
        yield trimmed.slice(5).trim();
      }
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const nl = buffer.lastIndexOf("\n");
    if (nl === -1) continue;
    yield* emit(buffer.slice(0, nl)); // 완성된 라인만 처리
    buffer = buffer.slice(nl + 1); // 미완성 라인은 다음 청크와 합침
  }
  // 스트림이 개행 없이 끝난 경우 남은 버퍼를 마지막으로 처리
  if (buffer.trim()) yield* emit(buffer);
}

const t = (key, subs) => chrome.i18n.getMessage(key, subs);

async function readError(res, label) {
  let detail = "";
  try {
    const j = await res.json();
    detail = j.error?.message || JSON.stringify(j);
  } catch {
    detail = await res.text().catch(() => "");
  }
  if (res.status === 401) return t("errAuth", label);
  if (res.status === 429) return t("errRate", label);
  return t("errGeneric", [label, String(res.status), detail || t("errUnknown")]);
}

// ---- 포트 기반 스트리밍 핸들러 --------------------------------------------

chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== "ai-stream") return;

  const controller = new AbortController();
  port.onDisconnect.addListener(() => controller.abort());

  port.onMessage.addListener(async (req) => {
    try {
      const cfg = await getConfig();
      if (!cfg.apiKey) {
        port.postMessage({ type: "error", message: t("errNoKey") });
        return;
      }

      const { system, user } = buildPrompt(req);
      const common = {
        apiKey: cfg.apiKey,
        system,
        user,
        signal: controller.signal,
      };

      const stream =
        cfg.provider === "anthropic"
          ? streamAnthropic({ ...common, model: cfg.anthropicModel })
          : streamOpenAI({ ...common, model: cfg.openaiModel });

      for await (const delta of stream) {
        port.postMessage({ type: "chunk", delta });
      }
      port.postMessage({ type: "done" });
    } catch (err) {
      if (err.name === "AbortError") return;
      port.postMessage({ type: "error", message: err.message || String(err) });
    }
  });
});

// ---- 컨텍스트 메뉴 (우클릭으로 선택 영역 요약/번역) -------------------------

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "summarize-selection",
    title: t("ctxSummarize"),
    contexts: ["selection"],
  });
  chrome.contextMenus.create({
    id: "translate-selection",
    title: t("ctxTranslate"),
    contexts: ["selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  // 컨텍스트 메뉴는 팝업을 자동으로 열 수 없으므로,
  // 선택 텍스트와 의도를 저장해 두고 팝업이 열릴 때 이어받게 한다.
  const action = info.menuItemId === "translate-selection" ? "translate" : "summarize";
  chrome.storage.session
    .set({ pendingRequest: { action, text: info.selectionText || "" } })
    .then(() => chrome.action.openPopup().catch(() => {}));
});
