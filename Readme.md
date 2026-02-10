# AI Router

这个项目是一个多服务商 LLM 路由与基准测试工具，使用 `litellm` 调用不同厂商的 OpenAI-兼容模型并进行吞吐量/延迟测试。

主要目录结构（工作区内）:

- `src/` - 应用代码: `main.py`, `service.py`, `engine.py`, `sync_models.py`, `demo.py`, 等
- `models.json` - 模型配置
- `benchmark_*.csv` - 每次基准测试导出的 CSV 文件

快速开始

1. 安装依赖（推荐 venv / conda 环境）:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. 配置环境变量：复制 `.env.example`（若无则创建 `.env`），填入各服务商的 API_KEY/API_BASE

3. 运行演示脚本（单次验证）：

```bash
python src/demo.py
```

4. 导入各个厂商的模型:

```bash
python src/sync_models.py
```

5. 运行 Web 服务（若项目提供 `main.py` 启动器）:

```bash
python src/main.py
uvicorn src.main:app --reload
```

如果需要，我可以帮您生成 `.github/workflows/ci.yml` 自动化部署或 PR 检查。 
uvicorn src.main:app --reload
python src/demo.py
python src/sync_models.py
1、https://github.com/portkey-ai/gateway是 Portkey AI Gateway 的开源仓库，核心是为生成式 AI 应用提供一个高性能、统一的大语言模型（LLM）网关层，解决生产环境中集成多类 LLM 的可靠性、性能和扩展性问题。
2、python src/sync_models.py
