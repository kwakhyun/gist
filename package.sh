#!/usr/bin/env bash
# 크롬 웹 스토어 업로드용 zip 생성
set -euo pipefail
cd "$(dirname "$0")"

OUT_DIR="build"
ZIP="$OUT_DIR/smart-summarize-extension.zip"

mkdir -p "$OUT_DIR"
rm -f "$ZIP"

# 확장 동작에 필요한 파일만 포함 (개발/문서 파일 제외)
zip -r "$ZIP" \
  manifest.json \
  background.js \
  i18n.js \
  popup.html popup.css popup.js \
  options.html options.js \
  _locales \
  icons \
  -x "*.DS_Store"

echo ""
echo "✅ 생성 완료: $ZIP"
unzip -l "$ZIP"
