# Chrome Web Store 등록 정보 (Gist)

폼의 각 칸에 아래 내용을 복사해 넣으세요. (현재 화면은 **영어(en)** 리스팅 → 영문 사용. 한국어 리스팅을 추가하면 국문 사용.)

---

## 카테고리
**Productivity (생산성)**

## 언어
기본: English. (원하면 한국어 리스팅도 추가 — 같은 항목에서 언어 추가)

---

## 패키지 제목 (이미 입력됨)
```
Gist — Summarize & Translate
```

## 패키지 요약 / 짧은 설명 (132자 이내, 이미 입력됨)
```
Instantly summarize and translate any web page or selected text with AI, using your own API key.
```

---

## 설명* (Description) — 영문, 아래 전체 복사

```
Gist turns any web page into a quick, readable summary — and translates anything you select — right in your browser. No copy‑pasting into a chatbot, no separate tab. One click.

★ WHAT IT DOES
• Summarize the page you're reading in Short (3 sentences), Medium (5 bullets), or Detailed form.
• Translate selected text — or the whole page — into English, Korean, Japanese, Chinese, Spanish, French, or German.
• Right‑click any selected text to summarize or translate it instantly.
• Results stream in live, word by word.

★ BRING YOUR OWN KEY
Gist uses YOUR own OpenAI or Anthropic API key. That means:
• No subscription and no markup — you pay the AI provider directly, at cost.
• Choose your model (GPT‑5.x or Claude) and trade off speed vs. quality.
• Enter a custom model ID anytime, so you're never stuck on an old model.

★ PRIVATE BY DESIGN
• Your API key is stored only in your browser and is never sent to us.
• We run no server. Your text goes straight from your browser to the AI provider you chose.
• Gist only reads a page's text the moment you click — it does not run in the background on every site.

★ GREAT FOR
• Long articles, research papers, documentation, and reports
• Reading content in a foreign language
• Getting the gist before you commit to a full read

★ HOW TO START
1. Install Gist.
2. Open Settings and paste your OpenAI or Anthropic API key.
3. Open any article and click "Summarize this page."

Gist is free. You only ever pay your AI provider for the tokens you use.
```

---

## 설명 (국문 버전 — 한국어 리스팅 추가 시 사용)

```
Gist는 지금 보고 있는 웹페이지를 한 번의 클릭으로 읽기 쉬운 요약으로 바꿔주고, 선택한 텍스트를 원하는 언어로 번역해 줍니다. 챗봇에 복붙할 필요도, 새 탭을 열 필요도 없습니다.

★ 주요 기능
• 페이지 요약 — 짧게(3문장), 보통(불릿 5개), 자세히 중 선택
• 번역 — 선택 영역 또는 전체를 영어·한국어·일본어·중국어·스페인어·프랑스어·독일어로
• 우클릭 메뉴 — 선택한 텍스트를 바로 요약/번역
• 결과가 실시간으로 한 글자씩 표시

★ 본인 API 키 사용
Gist는 사용자 본인의 OpenAI 또는 Anthropic API 키로 동작합니다.
• 구독·중간 마진 없음 — AI 제공자에 원가로 직접 지불
• 모델 선택 가능(GPT‑5.x / Claude)으로 속도와 품질을 조절
• 모델 ID 직접 입력 지원 — 새 모델이 나와도 바로 사용

★ 프라이버시 우선
• API 키는 브라우저에만 저장되며 개발자에게 전송되지 않습니다.
• 별도 서버가 없습니다. 텍스트는 브라우저에서 선택한 AI 제공자로 직접 전송됩니다.
• 버튼을 누른 순간에만 페이지 텍스트를 읽습니다 — 모든 사이트에서 상시 실행되지 않습니다.

★ 이런 분께
• 긴 기사·논문·문서·리포트를 빠르게 파악하고 싶을 때
• 외국어 콘텐츠를 모국어로 읽고 싶을 때

★ 시작하기
1. Gist 설치
2. 설정에서 OpenAI 또는 Anthropic API 키 입력
3. 아무 기사에서 "이 페이지 요약하기" 클릭

Gist는 무료입니다. 사용한 토큰만큼 AI 제공자에만 비용이 청구됩니다.
```

---

## 개인정보 처리방침 URL (별도 페이지 게시 필요)
아래 문구를 GitHub Pages/Notion 등에 올리고 URL 입력:

```
Gist does not operate any server. Your API key and settings are stored only in your
browser (chrome.storage) and are never transmitted to the developer. Text you choose to
summarize or translate is sent directly from your browser to OpenAI or Anthropic using
your own API key, subject to each provider's privacy policy. Gist does not collect, sell,
or share any personal data.
```

## 권한 사유 (개인정보 보호 탭)
- activeTab / scripting: 사용자가 버튼을 누른 그 순간의 현재 탭에서만 본문·선택 텍스트를 읽어 요약/번역
- storage: API 키·설정 저장
- contextMenus: 우클릭 메뉴 제공
- host_permissions(api.openai.com, api.anthropic.com): 사용자 키로 AI API 호출
- 원격 코드 사용: 안 함 / 데이터 수집·판매: 안 함
