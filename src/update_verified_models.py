import json
import pathlib

# From user's verified "demo.py" run
VERIFIED_ENTRIES = [
    {
        "provider": "硅基流动 (SiliconFlow)",
        "keyword": "SiliconFlow",
        "api_model_name": "openai/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "display_name": "DeepSeek-R1-Distill-Qwen-14B",
        "routing_alias": "deepseek-r1-distill",
        "input_price": 0.0, # Adjust as per known pricing or keep generic placeholder
        "output_price": 0.0
    },
    {
        "provider": "阿里云百炼 (Aliyun)",
        "keyword": "Aliyun",
        "api_model_name": "openai/deepseek-v3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 2.0,
        "output_price": 8.0
    },
    {
        "provider": "模力方舟 (Gitee)",
        "keyword": "Gitee", 
        "api_model_name": "openai/DeepSeek-V3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 0.0,
        "output_price": 0.0
    },
    {
        "provider": "PPIO派欧云",
        "keyword": "PPIO",
        "api_model_name": "openai/deepseek/deepseek-v3/community",
        "display_name": "DeepSeek-V3 (Community)",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "无问苍穹 (Infini)",
        "keyword": "Infini",
        "api_model_name": "openai/deepseek-v3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 2.0,
        "output_price": 6.0
    },
    {
        "provider": "七牛云 (Qiniu)",
        "keyword": "Qiniu",
        "api_model_name": "openai/deepseek-v3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "并行智算云 (Paratera)",
        "keyword": "Paratera",
        "api_model_name": "openai/DeepSeek-V3-250324",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 1.0
    },
    {
        "provider": "基石智算 (CoresHub)",
        "keyword": "CoresHub",
        "api_model_name": "openai/DeepSeek-V3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0, 
        "output_price": 1.0
    },
    {
        "provider": "UCLOUD",
        "keyword": "UCLOUD",
        "api_model_name": "openai/deepseek-ai/DeepSeek-V3-0324",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "火山方舟 (Volcengine)",
        "keyword": "Volcengine",
        "api_model_name": "openai/doubao-seed-1-8-251228", # Using the ID from working demo
        "display_name": "Doubao-Seed (DeepSeek-V3)",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "快手万擎 (Kwai)",
        "keyword": "Kwai",
        "api_model_name": "openai/deepseek-v3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "智谱AI (Zhipu)",
        "keyword": "Zhipu",
        "api_model_name": "openai/glm-4",
        "display_name": "GLM-4",
        "routing_alias": "glm-4",
        "input_price": 5.0,
        "output_price": 5.0
    },
    {
        "provider": "腾讯云 (Tencent)",
        "keyword": "Tencent",
        "api_model_name": "openai/deepseek-v3",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 1.0,
        "output_price": 2.0
    },
    {
        "provider": "零克云 (LinkAI)",
        "keyword": "LinkAI",
        "api_model_name": "openai/DeepSeek-V3.2",
        "display_name": "DeepSeek-V3.2",
        "routing_alias": "deepseek-v3.2",
        "input_price": 1.0,
        "output_price": 1.0
    },
    {
        "provider": "天翼云 (CTyun)",
        "keyword": "CTyun",
        "api_model_name": "openai/DeepSeek-R1-昇腾版",
        "display_name": "DeepSeek-R1 (Ascend)",
        "routing_alias": "deepseek-r1",
        "input_price": 1.0,
        "output_price": 1.0
    },
    {
        "provider": "MoonShot AI",
        "keyword": "MoonShot",
        "api_model_name": "openai/moonshot-v1-8k",
        "display_name": "Moonshot V1",
        "routing_alias": "moonshot-v1",
        "input_price": 15.0,
        "output_price": 15.0
    },
    {
        "provider": "百灵大模型 (Bailing)",
        "keyword": "Bailing",
        "api_model_name": "openai/Ling-1T",
        "display_name": "Ling-1T",
        "routing_alias": "ling-1t",
        "input_price": 1.0,
        "output_price": 1.0
    },
    {
        "provider": "阶跃星辰 (StepFun)",
        "keyword": "StepFun",
        "api_model_name": "openai/step-1-8k",
        "display_name": "Step-1",
        "routing_alias": "step-1",
        "input_price": 5.0,
        "output_price": 5.0
    },
    {
        "provider": "DeepSeek (Official)",
        "keyword": "DeepSeek",
        "api_model_name": "openai/deepseek-chat",
        "display_name": "DeepSeek-V3",
        "routing_alias": "deepseek-v3",
        "input_price": 4.0, # Official price (approx)
        "output_price": 16.0 
    },
    {
        "provider": "SCNet",
        "keyword": "SCNet",
        "api_model_name": "openai/Qwen3-235B-A22B",
        "display_name": "Qwen3",
        "routing_alias": "qwen3",
        "input_price": 1.0,
        "output_price": 1.0
    }
]

def main():
    current_dir = pathlib.Path(__file__).parent.resolve()
    json_path = current_dir / "models.json"
    
    models = []
    if json_path.exists():
        with open(json_path, "r", encoding='utf-8') as f:
            models = json.load(f)

    # Convert existing models to dict for easy lookup
    # Key: provider_keyword + api_model_name
    model_map = {}
    for m in models:
        # Try to find which provider keyword fits
        key = f"{m.get('provider')}-{m.get('api_model_name')}"
        model_map[key] = m

    # Add/Update verified entries
    new_count = 0
    updated_count = 0
    
    for v in VERIFIED_ENTRIES:
        # Construct a unique ID
        safe_keyword = v['keyword'].lower().replace(" ", "")
        safe_model = v['api_model_name'].split('/')[-1].lower() # e.g. deepseek-v3
        safe_model = safe_model.replace(".", "-").encode('ascii', 'ignore').decode('ascii') # remove weird chars
        
        internal_id = f"{safe_keyword}-{safe_model}"
        
        # Check if exists by id
        existing = next((m for m in models if m["id"] == internal_id), None)
        
        entry = {
            "id": internal_id,
            "display_name": v["display_name"],
            "routing_alias": v['routing_alias'],
            "provider": v["provider"],
            "api_model_name": v["api_model_name"],
            "context_window": "64k" if "v3" in v['routing_alias'] else "32k",
            "max_output": "8k",
            "input_price_cny_1m": v["input_price"],
            "output_price_cny_1m": v["output_price"]
        }
        
        if existing:
            # Update existing
            existing.update(entry)
            updated_count += 1
        else:
            # Add new
            models.append(entry)
            new_count += 1
            
    with open(json_path, "w", encoding='utf-8') as f:
        json.dump(models, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Updated models.json: {new_count} added, {updated_count} updated.")

if __name__ == "__main__":
    main()
