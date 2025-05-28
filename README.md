# Cai-Yan 一个「猜盐」网站的脚本合集

请注意 [LICENSE](./LICENSE) 文件末额外的附加条款。

## 使用方式

1. 克隆本仓库到本地目录

   ```bash
   git clone https://github.com/CodingOIer/Cai-Yan.git
   ```

2. 安装 Python 依赖

   可选：创建虚拟环境

   ```bash
   python -m venv .venv
   ```

   激活虚拟环境 **Linux/MacOs**

   ```bash
   source .venv/bin/activate (*unix)
   ```

   激活虚拟环境 **Windows**

   ```bash
   .\.venv\Scripts\Activate.ps1 (Windows)
   ```

   安装依赖

   ```bash
   pip install -r requirements.txt
   ```

3. 运行主程序

   ```bash
   python scripts/main.py
   ```

## 开发方式

### Git 风格

本项目遵循 git-flow 分支管理流程，开发分支为 `develop`，发布分支为 `master`。

如果需要开发新功能，请创建新的开发分支，命名规则为 `feature/xxx`，例如 `feature/add-new-feature`。

如果需要修复bug，请创建新的修复分支，命名规则为 `bugfix/xxx`，例如 `bugfix/fix-bug`。

当开发完成时，创建 PR 到 `develop` 分支，并等待合并。

当 `develop` 分支合并到 `master` 分支时，自动发布新版本。

### 项目结构

`scrips` 目录下包含所有脚本，包括主程序等。

`prompt` 目录下包含所有提示词，包括 `doctor.md` 等。

### 脚本提交方式

当您创建了一个新的脚本时，请将脚本放在 `scripts` 目录下，并将其添加到 `scripts/main.py` 中。

`scripts/main.py` 中添加的部分应与其余部分保持一致的格式。

您可以在您的脚本顶部添加注释，申明版权和作者。
