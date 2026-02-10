import os
import requests
import json
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

PROVIDERS = [
    {"name": "SiliconFlow (硅基流动)", "key_env": "SILICONFLOW_API_KEY", "base_env": "SILICONFLOW_API_BASE"},
    {"name": "Aliyun (阿里云)", "key_env": "ALIYUN_API_KEY", "base_env": "ALIYUN_API_BASE"},
    {"name": "Gitee (模力方舟)", "key_env": "GITEE_API_KEY", "base_env": "GITEE_API_BASE"},
    {"name": "PPIO (派欧云)", "key_env": "PPIO_API_KEY", "base_env": "PPIO_API_BASE"},
    {"name": "Infini (无问苍穹)", "key_env": "INFINI_API_KEY", "base_env": "INFINI_API_BASE"},
    {"name": "Qiniu (七牛云)", "key_env": "QINIU_API_KEY", "base_env": "QINIU_API_BASE"},
    {"name": "Paratera (并行智算)", "key_env": "PARATERA_API_KEY", "base_env": "PARATERA_API_BASE"},
    {"name": "CoresHub (基石智算)", "key_env": "CORESHUB_API_KEY", "base_env": "CORESHUB_API_BASE"},
    {"name": "UCloud", "key_env": "UCLOUD_API_KEY", "base_env": "UCLOUD_API_BASE"},
]

def probe_provider(provider):
    name = provider["name"]
    api_key = os.getenv(provider["key_env"])
    api_base = os.getenv(provider["base_env"])

    if not api_key:
        print(f"⚠️  [{name}] 跳过: 未找到 API KEY ({provider['key_env']})")
        return

    if not api_base:
        # 有些服务商可能不需要 base url，或者是默认的 OpenAI，但这里我们假设都在 env 里配置了
        # 如果是阿里云，默认可能是 https://dashscope.aliyuncs.com/compatible-mode/v1
        print(f"⚠️  [{name}] 警告: 未找到 API BASE，将尝试仅使用 Key 或默认路径")
    
    # 构造请求 URL
    # OpenAI 标准通常是 /v1/models (api_base 通常包含 /v1)
    # 如果 api_base 以 /v1 结尾，直接加 /models
    # 如果没有 /v1，尝试加 /v1/models
    
    target_urls = []
    if api_base:
        clean_base = api_base.rstrip('/')
        if clean_base.endswith('/v1'):
            target_urls.append(f"{clean_base}/models")
        else:
            target_urls.append(f"{clean_base}/models") # 尝试直接加 models
            target_urls.append(f"{clean_base}/v1/models") # 尝试加 v1
    else:
        # 没有任何 base_url 时的备选（通常不会发生，因为我们都在 .env 配了）
        pass

    print(f"\n🔍 正在探测 [{name}] ...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    success = False
    for url in target_urls:
        try:
            # print(f"  - 尝试 URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    models = data.get("data", [])
                    print(f"✅ [{name}] 连接成功! 发现 {len(models)} 个模型:")
                    
                    # 打印模型列表，过滤 DeepSeek 相关
                    deepseek_models = []
                    other_models = []
                    
                    for m in models:
                        mid = m.get("id")
                        if "deepseek" in mid.lower():
                            deepseek_models.append(mid)
                        else:
                            other_models.append(mid)
                    
                    if deepseek_models:
                        print("  🎯 DeepSeek相关模型:")
                        for dm in deepseek_models:
                            print(f"     - {dm}")
                    else:
                        print("  ⚠️ 未发现名称包含 'deepseek' 的模型")
                        
                    # 如果需要看所有模型，可以取消下面注释
                    # if other_models:
                    #     print(f"  📄 其他模型 ({len(other_models)}个): {', '.join(other_models[:5])}...")

                    success = True
                    break # 成功了一个 URL 就跳出
                except Exception as e:
                    print(f"  ❌ 解析 JSON 失败: {e}")
            else:
                # 401/403 通常是 key 错，404 是路径错
                print(f"  ❌ 请求失败 (HTTP {response.status_code}): {url} - {response.text[:100]}...")
        
        except Exception as e:
            print(f"  ❌ 连接异常: {e}")

    if not success:
        print(f"❌ [{name}] 所有尝试均失败。")

if __name__ == "__main__":
    print("🚀 开始探测所有服务商的模型列表...")
    for p in PROVIDERS:
        probe_provider(p)
