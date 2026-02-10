import os
import json
import httpx
import pathlib
import time
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# 基础路径
CURRENT_DIR = pathlib.Path(__file__).parent.resolve()
MODELS_JSON_PATH = CURRENT_DIR / "models.json"

# 服务商配置 (名称, Key环境变量, BaseUrl环境变量, 内部ID前缀)
PROVIDERS_CONFIG = [
    {"name": "硅基流动 (SiliconFlow)", "key": "SILICONFLOW_API_KEY", "base": "SILICONFLOW_API_BASE", "prefix": "siliconflow"},
    {"name": "阿里云百炼 (Aliyun)", "key": "ALIYUN_API_KEY", "base": "ALIYUN_API_BASE", "prefix": "aliyun"},
    {"name": "Gitee (模力方舟)", "key": "GITEE_API_KEY", "base": "GITEE_API_BASE", "prefix": "gitee"},
    {"name": "PPIO (派欧云)", "key": "PPIO_API_KEY", "base": "PPIO_API_BASE", "prefix": "ppio"},
    {"name": "无问苍穹 (Infini)", "key": "INFINI_API_KEY", "base": "INFINI_API_BASE", "prefix": "infini"},
    {"name": "七牛云 (Qiniu)", "key": "QINIU_API_KEY", "base": "QINIU_API_BASE", "prefix": "qiniu"},
    {"name": "并行智算 (Paratera)", "key": "PARATERA_API_KEY", "base": "PARATERA_API_BASE", "prefix": "paratera"},
    {"name": "基石智算 (CoresHub)", "key": "CORESHUB_API_KEY", "base": "CORESHUB_API_BASE", "prefix": "coreshub"},
    {"name": "UCloud", "key": "UCLOUD_API_KEY", "base": "UCLOUD_API_BASE", "prefix": "ucloud"},
]

def load_json():
    if not MODELS_JSON_PATH.exists():
        return []
    try:
        with open(MODELS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_json(models):
    with open(MODELS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=4, ensure_ascii=False)

def identify_model_alias(model_id):
    mid = model_id.lower()
    
    # DeepSeek 系列
    if "deepseek" in mid:
        if "v3" in mid:
            # 区分 V3 和 V3.2
            if "3.2" in mid:
                return "deepseek-v3.2"
            return "deepseek-v3"
        if "r1" in mid:
            return "deepseek-r1"
    
    # Qwen 系列
    if "qwen" in mid:
        if "plus" in mid: return "qwen-plus"
        if "max" in mid: return "qwen-max"
        if "turbo" in mid: return "qwen-turbo"
        if "2.5" in mid and "72b" in mid: return "qwen-2.5-72b"
        
    return None

def fetch_models_from_provider(provider_conf):
    name = provider_conf["name"]
    api_key = os.getenv(provider_conf["key"])
    api_base = os.getenv(provider_conf["base"])
    
    if not api_key: 
        print(f"⚠️  [{name}] 跳过: 未设置 API Key")
        return []

    urls_to_try = []
    if api_base:
        clean = api_base.rstrip('/')
        if clean.endswith('/v1'):
            urls_to_try.append(f"{clean}/models")
        else:
            urls_to_try.append(f"{clean}/models")
            urls_to_try.append(f"{clean}/v1/models")
            
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"🔄 正在探测 [{name}] ...")
    
    for url in urls_to_try:
        try:
            resp = httpx.get(url, headers=headers, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                data_list = []
                if isinstance(data, list):
                    data_list = data
                elif isinstance(data, dict):
                    data_list = data.get("data", data.get("list", []))
                
                print(f"✅ [{name}] 连接成功，发现 {len(data_list)} 个模型")
                return [m["id"] for m in data_list if isinstance(m, dict) and "id" in m]
        except Exception:
            pass
            
    print(f"❌ [{name}] 探测失败")
    return []

def main():
    existing_models = load_json()
    
    # 建立唯一键索引，防止重复添加完全相同的 (provider+api_model_name)
    existing_keys = set()
    for m in existing_models:
        key = f"{m['provider']}|{m['api_model_name']}"
        existing_keys.add(key)
    
    # 定义过滤关键词：通常这些关键词代表需要特殊权限、企业版或极不稳定的版本
    # 如果您确实购买了 Pro 版权限，可以将 "pro" 从此列表中移除
    SKIP_KEYWORDS = ["pro", "enterprise", "terminus", "sandbox", "test", "deprecated"]

    total_added = 0
    
    for conf in PROVIDERS_CONFIG:
        remote_ids = fetch_models_from_provider(conf)
        
        for rid in remote_ids:
            # 1. 基础别名识别
            alias = identify_model_alias(rid)
            if not alias:
                continue 
            
            # 2. 智能过滤：跳过不适合普通用户的模型
            model_lower = rid.lower()
            if any(k in model_lower for k in SKIP_KEYWORDS):
                print(f"   ⚠️  跳过特殊/付费模型: [{conf['name']}] {rid}")
                continue

            full_api_name = f"openai/{rid}"
            unique_key = f"{conf['name']}|{full_api_name}"
            
            if unique_key in existing_keys:
                continue
                
            # 构造 ID
            safe_rid = rid.replace("/", "-").replace(".", "-").replace(" ", "-").lower()
            if safe_rid.startswith("openai-"): safe_rid = safe_rid[7:]
            
            internal_id = f"{conf['prefix']}-{safe_rid}"
            
            # 显示名称处理：直接使用原始 Model ID，仅做简单的格式清理
            # 移除一些冗余的前缀如 "openai/", "deepseek-ai/" 等，让名字更清爽但保持原意
            clean_name = rid
            prefixes_to_clean = ["openai/", "deepseek-ai/", "Qwen/", "google/"]
            for prefix in prefixes_to_clean:
                if clean_name.startswith(prefix):
                    clean_name = clean_name[len(prefix):]
            
            # 也可以选择完全保留 rid，或者只做首字母大写等
            # 这里按照您的要求，如果 rid 是 Qwen/Qwen2.5-72B-Instruct，
            # 上面的逻辑会清理成 Qwen2.5-72B-Instruct，或者您可以选择不清理，直接: display_name = rid
            
            # 最终决定：直接用 rid 作为基础显示名称，这样最准确
            display_name = rid
            
            model_lower = rid.lower()
            
            # 提取变体特征 - 这些保留在括号里作为补充信息还是很有用的
            variants = []
            if "pro" in model_lower: variants.append("Pro")
            if "plus" in model_lower: variants.append("Plus")
            if "max" in model_lower: variants.append("Max")
            if "turbo" in model_lower: variants.append("Turbo")
            if "terminus" in model_lower: variants.append("Terminus")
            if "distill" in model_lower: variants.append("Distill")
            if "thinking" in model_lower: variants.append("Think")
            if "exp" in model_lower: variants.append("Exp")
            
            if variants:
                display_name += f" ({'/'.join(variants)})"
            
            # 避免 internal_id 重复
            base_id = internal_id
            counter = 1
            while any(m['id'] == internal_id for m in existing_models):
                internal_id = f"{base_id}-{counter}"
                counter += 1

            print(f"   ➕ 新增变体: [{conf['name']}] {rid} -> {display_name}")
            
            new_entry = {
                "id": internal_id,
                "display_name": display_name,
                "routing_alias": alias,
                "provider": conf["name"],
                "api_model_name": full_api_name,
                "context_window": "64k" if "v3" in alias else "32k",
                "max_output": "8k",
                "input_price_cny_1m": 1.0, 
                "output_price_cny_1m": 2.0
            }
            existing_models.append(new_entry)
            existing_keys.add(unique_key)
            total_added += 1

    if total_added > 0:
        save_json(existing_models)
        print(f"\n🎉 更新完成！新加入了 {total_added} 个模型配置。")
    else:
        print("\n✨ 检查完成，现有配置已包含探测到的所有模型变体。")

if __name__ == "__main__":
    main()
