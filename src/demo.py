import asyncio
import os
from dotenv import load_dotenv
from engine import BenchmarkEngine

# 加载 .env 文件
load_dotenv()

async def main():
    print("🚀 开始运行多服务商基准测试...")
    engine = BenchmarkEngine()

    # 定义测试配置
    # 关键修正：对于兼容 OpenAI 接口的服务商（自定义 BaseURL），
    # Litellm 要求模型名称必须以 'openai/' 开头，
    # 这样它才知道要用 OpenAI 的协议格式去构造 HTTP 请求。
    test_configs = [
        # 硅基流动
        {
            "provider": "SiliconFlow",
            "model": "openai/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "api_key": os.getenv("SILICONFLOW_API_KEY"),
            "api_base": os.getenv("SILICONFLOW_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 阿里云
        {
            "provider": "Aliyun",
            "model": "openai/deepseek-v3", 
            "api_key": os.getenv("ALIYUN_API_KEY"),
            "api_base": os.getenv("ALIYUN_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # Gitee
        {
            "provider": "Gitee", 
            "model": "openai/DeepSeek-V3", 
            "api_key": os.getenv("GITEE_API_KEY"),
            "api_base": os.getenv("GITEE_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # PPIO
        {
            "provider": "PPIO",
            "model": "openai/deepseek/deepseek-v3/community",
            "api_key": os.getenv("PPIO_API_KEY"),
            "api_base": os.getenv("PPIO_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 无问苍穹 (Infini)
        {
            "provider": "Infini",
            "model": "openai/deepseek-v3", 
            "api_key": os.getenv("INFINI_API_KEY"),
            "api_base": os.getenv("INFINI_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 七牛云 (Qiniu)
        {
            "provider": "Qiniu",
            "model": "openai/deepseek-v3", 
            "api_key": os.getenv("QINIU_API_KEY"),
            "api_base": os.getenv("QINIU_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 并行智算云 (Paratera)
        # 修正：根据报错信息，Paratera 需要使用特定的版本号名称 'DeepSeek-V3-250324'
        {
            "provider": "Paratera",
            "model": "openai/DeepSeek-V3-250324", 
            "api_key": os.getenv("PARATERA_API_KEY"),
            "api_base": os.getenv("PARATERA_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 基石智算 (CoresHub)
        # 修正：去除 'deepseek-ai/' 前缀，尝试直接用 'DeepSeek-V3'
        {
            "provider": "CoresHub",
            "model": "openai/DeepSeek-V3", 
            "api_key": os.getenv("CORESHUB_API_KEY"),
            "api_base": os.getenv("CORESHUB_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # UCLOUD
        # 修正：ModelVerse 列表显示为 specific version 'deepseek-ai/DeepSeek-V3-0324'
        {
            "provider": "UCLOUD",
            "model": "openai/deepseek-ai/DeepSeek-V3-0324", 
            "api_key": os.getenv("UCLOUD_API_KEY"),
            "api_base": os.getenv("UCLOUD_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 火山方舟 (需要替换为具体的 Endpoint ID)
        {
            "provider": "Volcengine",
            "model": "openai/doubao-seed-1-8-251228", # 🔴 请在此处填入您在火山引擎控制台创建的接入点ID
            "api_key": os.getenv("VOLCENGINE_API_KEY"),
            "api_base": os.getenv("VOLCENGINE_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 快手万擎
        {
            "provider": "Kwai",
            "model": "openai/deepseek-v3",
            "api_key": os.getenv("KWAI_API_KEY"),
            "api_base": os.getenv("KWAI_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 智谱AI (GLM-4)
        {
            "provider": "Zhipu",
            "model": "openai/glm-4", 
            "api_key": os.getenv("ZHIPU_API_KEY"),
            "api_base": os.getenv("ZHIPU_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 腾讯云
        {
            "provider": "Tencent",
            "model": "openai/deepseek-v3",
            "api_key": os.getenv("TENCENT_API_KEY"),
            "api_base": os.getenv("TENCENT_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 零克云 
        {
            "provider": "LinkAI",
            "model": "openai/DeepSeek-V3.2",
            "api_key": os.getenv("LINKAI_API_KEY"),
            "api_base": os.getenv("LINKAI_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 天翼云
        {
            "provider": "CTyun",
            "model": "openai/DeepSeek-R1-昇腾版", # 尝试修正为小写 id
            "api_key": os.getenv("CTYUN_API_KEY"),
            "api_base": os.getenv("CTYUN_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # MoonShot
        {
            "provider": "MoonShot",
            "model": "openai/moonshot-v1-8k",
            "api_key": os.getenv("MOONSHOT_API_KEY"),
            "api_base": os.getenv("MOONSHOT_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 百灵大模型 (暂停测试：需开通服务)
        {
            "provider": "Bailing",
            "model": "openai/Ling-1T",
            "api_key": os.getenv("BAILING_API_KEY"),
            "api_base": os.getenv("BAILING_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # 阶跃星辰
        {
            "provider": "StepFun",
            "model": "openai/step-1-8k",
            "api_key": os.getenv("STEPFUN_API_KEY"),
            "api_base": os.getenv("STEPFUN_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # DeepSeek
        {
            "provider": "DeepSeek",
            "model": "openai/deepseek-chat",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "api_base": os.getenv("DEEPSEEK_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        },
        # SCNet
        {
            "provider": "SCNet",
            "model": "openai/Qwen3-235B-A22B", # 尝试修正为小写 id
            "api_key": os.getenv("SCNET_API_KEY"),
            "api_base": os.getenv("SCNET_API_BASE"),
            "prompt": "你好，请用一句话介绍你自己。"
        }
    ]

    print(f"\n📋 测试列表 ({len(test_configs)} 个服务商):")
    for cfg in test_configs:
        print(f"  - [{cfg['provider']}] 模型: {cfg['model']}")

    print("\n⏳ 正在并行发送请求...\n")
    
    # 运行测试
    results = await engine.run_batch(test_configs)

    # 打印结果表格
    print(f"{'服务商':<12} | {'模型':<30} | {'状态':<8} | {'首字延迟':<10} | {'吞吐量':<10} | {'价格($/M)'}")
    print("-" * 100)

    for r in results:
        status_icon = "✅" if r['status'] == 'success' else "❌"
        # 截断过长的模型名以适应表格
        model_display = (r['model'][:28] + '..') if len(r['model']) > 28 else r['model']
        
        cost_display = f"{r.get('cost', 0):.6f}"
        
        print(f"{r['provider']:<12} | {model_display:<30} | {status_icon} {r['status']:<5} | {r.get('latency_ttft', 0):<10.4f} | {r.get('throughput', 0):<10.2f} | {cost_display}")

        if r['status'] == 'error':
            print(f"  └─ 错误信息: {r.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
