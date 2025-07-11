# JavaScript代码安全分析工具

一个基于Google Gemini AI的JavaScript代码安全分析工具，支持从网站提取JS文件或分析本地JS文件，并生成详细的安全分析报告。

## 功能特点

- 🔍 **多种分析模式**：支持网站JS文件提取、本地文件选择、目录扫描
- 🤖 **AI驱动分析**：使用Google Gemini AI进行深度代码安全分析
- 📊 **智能分块处理**：自动处理大型JS文件，支持分块分析
- 📄 **HTML报告生成**：生成美观的HTML格式分析报告
- 🛡️ **反爬虫机制**：内置随机User-Agent和延迟机制
- 🔧 **灵活配置**：通过配置文件自定义分析参数
- 🌐 **代理支持**：支持HTTP/HTTPS代理配置

## 安装要求

### Python版本
- Python 3.7+

### 依赖包
```bash
pip install -r requirements.txt
```

或手动安装：
```bash
pip install configparser requests beautifulsoup4 google-generativeai markdown2 urllib3
```

### 系统要求
- 支持tkinter的Python环境（用于GUI文件选择）
- 网络连接（用于访问Gemini API）

## 配置设置

### 1. 创建配置文件
复制并重命名 `config.ini.example` 为 `config.ini`：

```ini
[Gemini]
api_key = YOUR_GEMINI_API_KEY
model = gemini-pro
max_chunk_size = 15000

[Proxy]
type = http
host = 127.0.0.1
port = 8080

[Prompt]
custom_prompt = 请分析以下JavaScript代码的安全问题...
chunk_prompt = 请继续分析以下JavaScript代码片段...
summary_prompt = 基于以下分析报告，生成最终总结...
```

### 2. 获取Gemini API Key
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API密钥
3. 将API密钥填入 `config.ini` 文件的 `api_key` 字段

### 3. 配置代理（可选）
如果需要使用代理访问Gemini API，请在配置文件中设置代理信息。

## 使用方法

### 启动程序
```bash
python main.py
```

### 选择分析模式
程序启动后会提示选择分析模式：

1. **从网站URL提取JS文件**
   - 输入网站URL
   - 自动提取页面中的所有JS文件链接
   - 获取文件大小信息

2. **选择本地JS文件**
   - 通过GUI文件选择器选择特定JS文件
   - 支持多文件选择

3. **选择本地目录扫描JS文件**
   - 通过GUI选择目录
   - 递归扫描目录中的所有JS文件

4. **当前目录扫描JS文件**
   - 自动扫描当前工作目录
   - 包含子目录中的JS文件

### 选择要分析的文件
- 输入文件编号（用逗号分隔）
- 或输入 `all` 分析所有文件

### 查看分析结果
- 分析完成后会生成HTML报告
- 报告保存在 `reports` 目录中
- 可选择在浏览器中直接打开报告

## 项目结构

```
js-security-analyzer/
├── main.py                 # 主程序文件
├── config.ini              # 配置文件
├── config.ini.example      # 配置文件示例
├── requirements.txt        # 依赖包列表
├── README.md              # 说明文档
└── reports/               # 生成的分析报告目录
    ├── report_*.html      # HTML格式的分析报告
    └── ...
```

## 配置文件详解

### [Gemini] 部分
- `api_key`: Gemini API密钥
- `model`: 使用的AI模型（推荐 gemini-pro）
- `max_chunk_size`: 单次分析的最大字符数

### [Proxy] 部分
- `type`: 代理类型（http/https）
- `host`: 代理服务器地址
- `port`: 代理端口

### [Prompt] 部分
- `custom_prompt`: 主分析提示模板
- `chunk_prompt`: 分块分析提示模板
- `summary_prompt`: 总结分析提示模板

## 安全特性

### 反爬虫机制
- 随机User-Agent轮换
- 请求间随机延迟
- 完整的HTTP头模拟

### SSL/TLS处理
- 自动处理SSL证书问题
- 支持自签名证书
- 可配置的SSL验证

### 文件处理
- 多编码支持（UTF-8, GBK, Latin-1）
- 安全的文件名生成
- 文件大小检查和格式化

## 输出报告

### HTML报告特点
- 响应式设计
- 代码高亮显示
- 表格和图表支持
- 文件信息摘要
- 时间戳记录

### 报告内容
- 代码安全漏洞分析
- 潜在风险评估
- 改进建议
- 详细的技术分析

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   错误: 请在 config.ini 文件中配置您的Gemini API key。
   ```
   解决：检查配置文件中的API密钥是否正确

2. **网络连接问题**
   ```
   调用Gemini API时出错: ...
   ```
   解决：检查网络连接和代理设置

3. **文件读取错误**
   ```
   读取文件时出错: ...
   ```
   解决：检查文件路径和权限

4. **SSL证书问题**
   程序已内置SSL证书问题的处理机制

### 调试模式
程序包含详细的错误日志和异常处理，可以通过控制台输出查看详细信息。

## 注意事项

1. **API配额限制**：注意Gemini API的使用配额
2. **文件大小限制**：超大文件会自动分块处理
3. **网络安全**：建议在安全的网络环境中使用
4. **隐私保护**：分析的代码会发送到Gemini API

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多种分析模式
- 集成Gemini AI分析
- HTML报告生成
- 反爬虫机制

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个工具。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 项目讨论区

---

**免责声明**：本工具仅用于学习和研究目的，使用者需要遵守相关法律法规和网站的使用条款。