// i18n.js — data-i18n 속성을 chrome.i18n 메시지로 치환 (정적 UI 텍스트 현지화)
(function () {
  const msg = (k) => (k ? chrome.i18n.getMessage(k) : "");

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const t = msg(el.dataset.i18n);
    if (t) el.textContent = t;
  });
  // HTML(링크 등)을 포함하는 메시지
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const t = msg(el.dataset.i18nHtml);
    if (t) el.innerHTML = t;
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const t = msg(el.dataset.i18nPh);
    if (t) el.placeholder = t;
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const t = msg(el.dataset.i18nTitle);
    if (t) el.title = t;
  });

  const docTitleKey = document.documentElement.dataset.i18nTitle;
  if (docTitleKey) document.title = msg(docTitleKey);
})();
