### 项目描述

本项目是一个基于 Python 的命令行工具，利用 Google Gemini API 对 JavaScript (JS) 代码进行自动化安全分析。它支持从本地文件、本地目录或远程网站 URL 中获取 JS 代码，并能够处理超长代码，将其分块发送给 AI 进行分析，最后生成结构清晰、内容详尽的 HTML 报告。该工具旨在帮助开发者和安全研究人员快速识别 JS 代码中潜在的安全漏洞、不当的编码实践和性能问题。

### README.md

#### JS 代码安全分析器 (JS Code Security Analyzer)

**项目简介**

本项目是一个强大的自动化工具，旨在利用人工智能对 JavaScript 代码进行深度安全分析。通过集成 Google Gemini API，它可以自动识别代码中的潜在风险，如跨站脚本 (XSS)、注入漏洞、敏感信息泄露等，并提供详细的分析报告。无论您是需要分析网页上的外部 JS 文件，还是检查本地项目中的代码，本工具都能提供极大的便利。

**主要功能**

  * **多种代码来源支持**：
      * 从指定网站 URL 自动提取并下载 JS 文件进行分析。
      * 支持通过图形界面（GUI）选择单个或多个本地 JS 文件。
      * 支持通过 GUI 选择一个目录并递归扫描所有 `.js`, `.mjs`, `.jsx` 文件。
      * 支持扫描当前工作目录下的所有 JS 文件。
  * **AI 智能分析**：利用 Google Gemini 强大的代码理解能力，对 JS 代码进行全面评估，包括安全风险、代码质量、潜在漏洞和改进建议。
  * **大文件处理**：内置分块处理机制，能够智能地将超长的 JS 文件分割成小块，逐一发送给 API 分析，然后对所有分块结果进行综合总结，有效规避 API 的输入长度限制。
  * **专业报告生成**：将 AI 分析结果转换为格式美观、易于阅读的 HTML 报告，保存在本地 `reports` 文件夹中。报告包含文件信息、分析时间以及详细的 Markdown 格式分析内容。
  * **反爬虫友好**：在从网站下载文件时，支持随机 User-Agent 和请求延迟，模拟真实浏览器行为，提高抓取成功率。
  * **灵活配置**：所有关键设置，包括 Gemini API Key、使用的模型、提示词模板、代理设置等，均可通过 `config.ini` 文件轻松自定义。

-----

**环境要求**

  * Python 3.6 或更高版本
  * `pip` 包管理工具

**安装步骤**

1.  **克隆项目仓库：**
    ```bash
    git clone https://github.com/yourusername/js-security-analyzer.git
    cd js-security-analyzer
    ```
2.  **安装依赖库：**
    ```bash
    pip install -r requirements.txt
    ```
    (注意：如果 `requirements.txt` 不存在，请手动安装以下依赖：`requests`, `beautifulsoup4`, `google-generativeai`, `markdown2`, `urllib3`)
    ```bash
    pip install requests beautifulsoup4 google-generativeai markdown2 urllib3
    ```
3.  **配置 Gemini API Key：**
      * 访问 Google AI Studio 获取您的 Gemini API Key。
      * 在项目根目录下创建一个名为 `config.ini` 的文件。

**配置文件说明 (`config.ini`)**

`config.ini` 文件用于配置程序运行时的各项参数。以下是一个示例模板：

````ini
[Gemini]
# 您的 Gemini API Key，请勿泄露
api_key = YOUR_GEMINI_API_KEY
# 推荐使用的模型，例如 gemini-pro 或 gemini-1.5-pro-latest
model = gemini-pro
# 单次发送给 Gemini API 的最大代码字符数，超过此值将分块处理
max_chunk_size = 15000

[Prompt]
# 第一次或单次发送时的提示词模板
# {js_code} 是代码占位符
custom_prompt = 分析以下 JavaScript 代码，识别潜在的安全漏洞、不当的编码实践、性能问题和敏感信息泄露。请以Markdown格式输出一个结构化的报告，包含以下几个部分：
1. 风险概述：简要总结发现的风险等级和类型。
2. 发现的漏洞和问题：详细列出每个发现的问题，并提供代码行号、问题描述和安全建议。
3. 代码质量和建议：提供关于代码可读性、可维护性和性能优化的建议。
4. 总结：对该文件的整体安全状况做出评价。
---
以下是待分析的JS代码：
```javascript
{js_code}
````

# 分块处理时，发送后续块的提示词模板

# AI会根据上下文继续分析，此处的提示词应指导AI专注于寻找新问题

## chunk\_prompt = 这是上一段JS代码的延续。请继续分析以下代码块，寻找任何潜在的安全漏洞、不当的编码实践或敏感信息。请以Markdown格式列出新发现的问题，如果未发现新问题，请直接回答“无新发现。”

以下是新的代码块：

```javascript
{js_code}
```

# 分块处理完成后，用于总结所有分析结果的提示词模板

# {analysis\_reports} 是所有分块报告的占位符

## summary\_prompt = 我已经将一个大型JS文件分块并进行分析，下面是所有分块分析的结果。请根据这些结果，生成一个最终的、全面的、结构化的安全分析报告。报告格式与最初的提示词要求一致（风险概述、发现的问题、代码质量、总结），请综合所有发现，去除重复信息，形成一个连贯且完整的报告。

所有分块分析报告：
{analysis\_reports}

[Proxy]

# 可选：如果需要通过代理访问，请配置此项

# 支持 http/https/socks5，具体取决于您的代理服务

type = http
host = 127.0.0.1
port = 7890

````

**使用方法**

1.  在终端中运行 `main.py` 文件：
    ```bash
    python main.py
    ```
2.  程序将提示您选择分析模式：
    * **模式 1**：输入一个网站 URL，程序将自动扫描并下载其中的 JS 文件。
    * **模式 2**：打开文件选择器，您可以手动选择一个或多个本地 JS 文件。
    * **模式 3**：打开目录选择器，您可以选择一个文件夹，程序将递归分析其中的所有 JS 文件。
    * **模式 4**：程序将自动扫描当前运行目录下的所有 JS 文件。
3.  根据提示输入您的选择，并提供相应的 URL 或等待文件/目录选择器弹出。
4.  程序将列出找到的所有 JS 文件，您可以通过编号选择要分析的文件（支持用逗号分隔，或输入 `all` 分析全部）。
5.  分析完成后，HTML 报告将自动生成并保存在 `reports/` 目录下。程序将询问您是否在浏览器中打开报告。

**注意事项**

* **SSL 警告**：本程序在某些网络请求中禁用了 SSL 验证（`verify=False`），这可能会降低安全性，仅推荐在受信任的环境中进行测试和开发。
* **API Key 安全**：您的 Gemini API Key 是敏感信息，请妥善保管，切勿将其提交到公共代码仓库。
* **代理设置**：本程序针对 `google-generativeai` 库的 gRPC 调用进行了代理配置，请确保 `config.ini` 中的代理信息正确无误。

**鸣谢**

* **Google Gemini API**：核心分析能力提供者。
* **Requests & BeautifulSoup**：强大的网络请求和 HTML 解析库。
* **Markdown2**：将 Markdown 转换为 HTML。
````
