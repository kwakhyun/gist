# 개인정보 보호 탭 입력값 (Gist)

각 칸에 아래 영문을 복사해 넣으세요. (영어 권장 — 심사팀 국제적. 한국어도 허용)

---

## 전용 목적 설명 (Single purpose)
```
Gist has a single purpose: to help users understand the web page they are viewing by generating an AI summary of the page, or of the text they select. The user supplies their own OpenAI or Anthropic API key. When the user clicks the extension or chooses "Summarize with Gist" from the right-click menu, Gist reads the current page's text (or the user's selection) and sends it to the chosen AI provider to produce a summary, which is shown in the popup. The user can optionally translate that summary into another language. The extension does not run in the background and has no other function.
```

## activeTab 사용 근거
```
activeTab is used so that, only when the user clicks the extension's "Summarize"/"Translate" button or a context-menu item, Gist can access the current tab to read its visible text for that single summarization or translation request. It is never used to read tabs in the background or without an explicit user action.
```

## scripting 사용 근거
```
scripting (chrome.scripting.executeScript) is used to run a small text-extraction function in the active tab at the exact moment the user clicks Summarize/Translate. That function reads the page's main article text, or the user's currently selected text, and returns it so it can be summarized or translated. It runs only on user action on the active tab and is not injected persistently or on other sites.
```

## storage 사용 근거
```
storage is used to save the user's own settings locally in the browser: their selected AI provider, their API key, and their preferred model. This is required so users do not have to re-enter their key on every use. The data is kept in chrome.storage and is never transmitted to the developer or any third party other than the AI provider the user chose.
```

## contextMenus 사용 근거
```
contextMenus adds a single right-click item, "Summarize with Gist", available on a page or when text is selected. It lets the user summarize the whole page, or just the selected text, directly from the context menu. This permission is used solely to provide this user-initiated shortcut.
```

## 호스트 권한 사용 근거 (host_permissions: api.openai.com, api.anthropic.com)
```
The host permissions for https://api.openai.com/ and https://api.anthropic.com/ are required so the extension can send the user's selected text or page text to the AI provider's API — using the user's own API key — and receive back the summary or translation. These two API endpoints are the only hosts the extension contacts, and access to them is essential to the core summarize/translate function. No other hosts are requested.
```

---

## 원격 코드 사용 중이신가요?
**→ "아니오, 원격 코드 권한을 사용하고 있지 않습니다." 선택**

이유: Gist는 외부 JS/Wasm을 로드하거나 eval()을 사용하지 않습니다. 모든 코드는 패키지에 포함되어 있고,
OpenAI/Anthropic 통신은 fetch()로 데이터(JSON)만 주고받습니다(원격 코드 아님).
"아니오"를 선택하면 근거 입력칸은 사라집니다.

---

## 데이터 사용 인증 (Data usage / 공개)
페이지 하단의 데이터 사용 항목에서 다음을 선택/체크하세요:
- 수집하는 사용자 데이터: **없음(None)** 으로 둘 수 있음
  (API 키·설정은 사용자의 브라우저(chrome.storage)에만 저장되고 개발자에게 전송되지 않으므로
   "수집"에 해당하지 않습니다. 단, 폼에서 "인증/공개"는 반드시 체크해야 게시 가능)
- 다음 3개 항목에 모두 동의 체크:
  1) 승인된 용도 외 제3자에게 사용자 데이터를 판매/양도하지 않음
  2) 항목의 단일 목적과 무관한 용도로 사용/양도하지 않음
  3) 신용도 판단/대출 목적으로 사용/양도하지 않음
