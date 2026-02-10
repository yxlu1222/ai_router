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
    """
    根据实际的模型ID猜测它的通用别名
    """
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
    """
    从服务商 API 拉取模型列表
    """
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
            resp = httpx.get(url, headers=headers, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                data_list = data.get("data", [])
                
                # 兼容部分 API 返回格式差异
                if not isinstance(data_list, list) and "list" in data:
                     data_list = data["list"]

                print(f"✅ [{name}] 连接成功，发现 {len(data_list)} 个模型")
                return [m["id"] for m in data_list if isinstance(m, dict) and "id" in m]
        except Exception:
            pass
            
    print(f"❌ [{name}] 探测失败或不支持 /models 端点")
    return []

def main():
    existing_models = load_json()
    
    # 记录已有的 Full API Model Name，防止完全重复
    # 格式: "provider_name|api_model_name"
    existing_keys = set()
    for m in existing_models:
        key = f"{m['provider']}|{m['api_model_name']}"
        existing_keys.add(key)
    
    total_added = 0
    
    for conf in PROVIDERS_CONFIG:
        remote_ids = fetch_models_from_provider(conf)
        
        for rid in remote_ids:
            alias = identify_model_alias(rid)
            if not alias:
                continue # 暂时只关心我们定义好的核心模型 (DeepSeek/Qwen等)
            
            full_api_name = f"openai/{rid}"
            unique_key = f"{conf['name']}|{full_api_name}"
            
            if unique_key in existing_keys:
                continue
                
            # --- 构造新记录 ---
            
            # 生成一个唯一的 ID (slugify)
            # 例如 rid="deepseek-ai/DeepSeek-V3", prefix="siliconflow"
            # id -> "siliconflow-deepseek-ai-deepseek-v3"
            safe_rid = rid.replace("/", "-").replace(".", "-").replace(" ", "-").lower()
            # 移除可能重复的前缀
            if safe_rid.startswith("openai-"): safe_rid = safe_rid[7:]
            
            internal_id = f"{conf['prefix']}-{safe_rid}"
            
            # 显示名称：为了区分，保留部分 rid 的特征
            # 如果是标准版: DeepSeek-V3
            # 如果是变体: DeepSeek-V3 (Pro) / DeepSeek-V3 (Terminus)
            display_name = f"DeepSeek-{alias.split('-')[-1].upper()}"
            
            # 给显示名称加一点后缀以区分
            if "pro" in rid.lower():
                display_name += " (Pro)"
            elif "terminus" in rid.lower():
                display_name += " (Terminus)"
            elif "distill" in rid.lower():
                 display_name += " (DistiLL)"
            
            # 再次检查内部 ID 是否重复，如果重复加随机数或递增
            # 这里简单起见，如果 internal_id 已存在于 existing_models ids 中，就跳过或者改名
            # 为了简单，我们只依赖 unique_key 去重，internal_id 如果冲突可能需要处理
            # 实际 json list 中 id 应该是唯一的
            
            while any(m['id'] == internal_id for m in existing_models):
                internal_id += "-copy"

            print(f"   ➕ 新增模型: [{conf['name']}] {rid} -> {display_name}")
            
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
        print(f"\n🎉 更新完成！新加入了 {total_added} 个模型变体。")
        print("💡 提示：这可能会包含很多 Pro/VIP 模型，如果无法访问，请在网页上手动禁用或忽略报错。")
    else:
        print("\n✨ 检查完成，未发现符合条件的新模型变体。")

if __name__ == "__main__":
    main()
