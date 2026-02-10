# 替换原来的 requests.py
# 增加数据库写入和配置读取逻辑

import json
import os
import asyncio
from typing import List, Dict
from .engine import BenchmarkEngine
from .database import save_result, init_db, get_aggregated_stats
from dotenv import load_dotenv

# 确保数据库已初始化
init_db()
load_dotenv()

class Service:
    def __init__(self):
        self.engine = BenchmarkEngine()
        # 使用相对路径以兼容 WSL/Windows/Linux
        import pathlib
        current_dir = pathlib.Path(__file__).parent.resolve()
        json_path = current_dir / "models.json"
        
        with open(json_path, "r", encoding='utf-8') as f:
            self.models_config = json.load(f)

    def get_models_data(self):
        """
        合并静态配置和动态测试数据
        """
        stats = get_aggregated_stats()
        
        data = []
        for model in self.models_config:
            m_id = model["id"]
            stat = stats.get(m_id, {})
            
            # 合并数据
            merged = model.copy()
            merged["avg_ttft"] = round(stat.get("avg_ttft", 0), 4) # 首字延迟
            merged["avg_throughput"] = round(stat.get("avg_throughput", 0), 2) # 吞吐量
            merged["success_count"] = stat.get("success_count", 0)
            
            data.append(merged)
            
        # 按吞吐量排序
        data.sort(key=lambda x: x["avg_throughput"], reverse=True)
        return data

    def _get_api_config(self, provider_name: str):
        """Helper to get API key/base from env"""
        api_key = None
        api_base = None
        
        if "SiliconFlow" in provider_name:
            api_key = os.getenv("SILICONFLOW_API_KEY")
            api_base = os.getenv("SILICONFLOW_API_BASE")
        elif "阿里云" in provider_name:
            api_key = os.getenv("ALIYUN_API_KEY")
            api_base = os.getenv("ALIYUN_API_BASE")
        elif "Gitee" in provider_name:
            api_key = os.getenv("GITEE_API_KEY")
            api_base = os.getenv("GITEE_API_BASE")
        elif "PPIO" in provider_name:
            api_key = os.getenv("PPIO_API_KEY")
            api_base = os.getenv("PPIO_API_BASE")
        elif "无问苍穹" in provider_name:
            api_key = os.getenv("INFINI_API_KEY")
            api_base = os.getenv("INFINI_API_BASE")
        elif "七牛云" in provider_name:
            api_key = os.getenv("QINIU_API_KEY")
            api_base = os.getenv("QINIU_API_BASE")
        elif "并行智算" in provider_name:
            api_key = os.getenv("PARATERA_API_KEY")
            api_base = os.getenv("PARATERA_API_BASE")
        elif "基石智算" in provider_name:
            api_key = os.getenv("CORESHUB_API_KEY")
            api_base = os.getenv("CORESHUB_API_BASE")
        elif "UCloud" in provider_name or "UCLOUD" in provider_name:
            api_key = os.getenv("UCLOUD_API_KEY")
            api_base = os.getenv("UCLOUD_API_BASE")
        elif "讯飞" in provider_name or "Xunfei" in provider_name:
            api_key = os.getenv("XUNFEI_API_KEY")
            api_base = os.getenv("XUNFEI_API_BASE")
        elif "火山" in provider_name or "Volcengine" in provider_name:
            api_key = os.getenv("VOLCENGINE_API_KEY")
            api_base = os.getenv("VOLCENGINE_API_BASE")
        elif "快手" in provider_name or "Kwai" in provider_name:
            api_key = os.getenv("KWAI_API_KEY")
            api_base = os.getenv("KWAI_API_BASE")
        elif "智谱" in provider_name or "Zhipu" in provider_name:
            api_key = os.getenv("ZHIPU_API_KEY")
            api_base = os.getenv("ZHIPU_API_BASE")
        elif "腾讯" in provider_name or "Tencent" in provider_name:
            api_key = os.getenv("TENCENT_API_KEY")
            api_base = os.getenv("TENCENT_API_BASE")
        elif "零克" in provider_name or "LinkAI" in provider_name:
            api_key = os.getenv("LINKAI_API_KEY")
            api_base = os.getenv("LINKAI_API_BASE")
        elif "天翼" in provider_name or "CTyun" in provider_name:
            api_key = os.getenv("CTYUN_API_KEY")
            api_base = os.getenv("CTYUN_API_BASE")
        elif "MoonShot" in provider_name:
            api_key = os.getenv("MOONSHOT_API_KEY")
            api_base = os.getenv("MOONSHOT_API_BASE")
        elif "百灵" in provider_name or "Bailing" in provider_name:
            api_key = os.getenv("BAILING_API_KEY")
            api_base = os.getenv("BAILING_API_BASE")
        elif "阶跃" in provider_name or "StepFun" in provider_name:
            api_key = os.getenv("STEPFUN_API_KEY")
            api_base = os.getenv("STEPFUN_API_BASE")
        elif "DeepSeek" in provider_name:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            api_base = os.getenv("DEEPSEEK_API_BASE")
        elif "SCNet" in provider_name:
            api_key = os.getenv("SCNET_API_KEY")
            api_base = os.getenv("SCNET_API_BASE")

        return api_key, api_base

    async def route_chat_completion(self, request_dict: Dict):
        """
        智能路由核心逻辑
        1. 接收 OpenAI 格式请求
        2. 根据 model (alias) 查找所有可用服务商
        3. 根据策略 (Latency/Throughput) 选择最佳服务商
        4. 转发请求
        """
        target_alias = request_dict.get("model")
        
        # 重新加载配置，确保 models.json 的最新修改生效
        # 在生产环境中应该用 cache，但开发调试时方便
        import pathlib
        current_dir = pathlib.Path(__file__).parent.resolve()
        json_path = current_dir / "models.json"
        with open(json_path, "r", encoding='utf-8') as f:
            current_config = json.load(f)

        candidates = [m for m in current_config if m.get("routing_alias") == target_alias]
        
        if not candidates:
            # 如果没有 alias 匹配，尝试直接匹配 id
            candidates = [m for m in current_config if m.get("id") == target_alias]
            
        if not candidates:
             raise Exception(f"Model '{target_alias}' not found in router config.")

        # 获取性能统计
        stats = get_aggregated_stats()
        
        # 评分策略：优先选择吞吐量高的 (可以改成 latency_ttft 低的)
        # 如果没有数据 (count=0)，则认为是 0 分
        scored_candidates = []
        for cand in candidates:
            cand_id = cand["id"]
            stat = stats.get(cand_id, {})
            score = stat.get("avg_throughput", 0) 
            # 简单的故障规避：如果最近成功率很低，降低分数
            # 这里简单处理：如果没有成功记录，或者 throughput 为 0，就排在后面
            scored_candidates.append((score, cand))
            
        # 按分数降序排序 (High throughput first)
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # 选择最佳
        best_candidate = scored_candidates[0][1]
        print(f"🔄 Routing '{target_alias}' to provider: {best_candidate['provider']} (Score: {scored_candidates[0][0]})")

        # 构造请求参数
        api_key, api_base = self._get_api_config(best_candidate["provider"])
        
        # 深拷贝请求参数，避免修改原对象
        litellm_kwargs = request_dict.copy()
        litellm_kwargs["model"] = best_candidate["api_model_name"]
        
        if api_key: litellm_kwargs["api_key"] = api_key
        if api_base: litellm_kwargs["api_base"] = api_base
        
        # 必须显式传递 messages，因为 request_dict 可能包含 extra fields
        # Litellm 的 acompletion 接受 **kwargs
        
        try:
            import litellm
            # 注册模型以防价格报错
            try:
                litellm.register_model({
                    best_candidate["api_model_name"]: {
                        "litellm_provider": "openai", 
                        "mode": "chat"
                    }
                })
            except: pass

            response = await litellm.acompletion(**litellm_kwargs)
            return response
            
        except Exception as e:
            # FIXME: 这里可以做 Fallback 逻辑，尝试 scored_candidates[1]
            print(f"Routing Error on {best_candidate['provider']}: {e}")
            raise e

    async def run_refresh(self):
        """
        运行一轮测试并存入数据库
        """
        tasks = []
        
        # 构建测试配置
        test_configs = []
        for model in self.models_config:
            api_key, api_base = self._get_api_config(model["provider"])

            test_configs.append({
                "model_id": model["id"], 
                "provider": model["provider"],
                "model": model["api_model_name"], 
                "api_key": api_key,
                "api_base": api_base,
                "prompt": "写一个关于人工智能未来的50字短评。" 
            })

        # 运行测试
        print("开始新一轮测试...")
        results = await self.engine.run_batch(test_configs)
        
        # 存库
        saved_count = 0
        csv_data = []

        for i, res in enumerate(results):
            # 把 config 里的 model_id 塞回去，因为 engine 只有 model name
            res["model_id"] = test_configs[i]["model_id"]
            save_result(res)
            saved_count += 1
            csv_data.append(res)
            
        print(f"测试完成，已保存 {saved_count} 条记录")

        # 导出结果到 CSV
        try:
            import csv
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_{timestamp}.csv"
            
            # 使用 utf-8-sig 以便 Excel 正确显示中文
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if csv_data:
                    # 获取所有可能的字段名为 Header
                    fieldnames = ["model_id", "provider", "model", "status", "latency_ttft", "latency_total", "throughput", "output_tokens", "error", "timestamp"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(csv_data)
            print(f"📊 结果已导出至文件: {filename}")
        except Exception as e:
            print(f"⚠️ 导出CSV失败: {e}")

        return results
