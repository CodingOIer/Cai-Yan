pyinstaller `
  --onefile `
  --name CaiYanTool `
  --runtime-hook "scripts/hook/hook_runtime.py" `
  --add-data "README.md;." `
  --add-data "LICENSE;." `
  --add-data "requirements.txt;." `
  --add-data "charset;charset" `
  --add-data "prompt;prompt" `
  --add-data "scripts;scripts" `
  --add-data "settings.json;." `
  scripts/main.py
