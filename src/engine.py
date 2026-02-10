import os
import time
import asyncio
from typing import List, Dict, Optional
import litellm
from litellm import completion, embedding

# 启用详细日志以便调试 (生产环境可关闭)
# litellm.set_verbose = True

class BenchmarkEngine:
    def __init__(self):
        # 这里可以初始化数据库连接等
        pass

    async def run_benchmark(self, 
                          provider: str, 
                          model: str, 
                          prompt: str, 
                          api_key: Optional[str] = None, 
                          api_base: Optional[str] = None):
        """
        运行单个模型的基准测试
        """
        start_time = time.time()
        result = {
            "model": model,
            "provider": provider,
            "status": "pending",
            "latency_ttft": 0,    # Time to First Token
            "latency_total": 0,   # Total Latency
            "throughput": 0,      # Tokens per second
            "cost": 0,
            "output_tokens": 0,
            "timestamp": start_time
        }

        try:
            # 准备参数
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True, # 强制开启流式以计算 TTFT
            }
            
            # 如果提供了特定的 key 或 base url (覆盖环境变量)
            if api_key:
                kwargs["api_key"] = api_key
            if api_base:
                kwargs["api_base"] = api_base
            
            # 注册/更新模型价格信息 (防止 "model not mapped" 错误)
            # 这里简单演示一种通用的 DeepSeek 价格 (输入 $0.1/1M, 输出 $0.2/1M - 仅供参考)
            # 您可以稍后在配置文件中做得更精细
            try:
                litellm.register_model({
                    model: {
                        "input_cost_per_token": 0.0000001, # $0.1 / 1M
                        "output_cost_per_token": 0.0000002, # $0.2 / 1M
                        "litellm_provider": "openai", 
                        "mode": "chat"
                    }
                })
            except Exception:
                pass # 忽略注册重复等错误

            # 发起请求
            response = await litellm.acompletion(**kwargs)

            first_token_received = False
            first_token_time = 0
            collected_content = []
            
            # 处理流式响应
            async for chunk in response:
                # 记录首字时间
                if not first_token_received:
                    first_token_time = time.time()
                    result["latency_ttft"] = round(first_token_time - start_time, 4)
                    first_token_received = True
                
                content = chunk.choices[0].delta.content or ""
                collected_content.append(content)

            end_time = time.time()
            full_response = "".join(collected_content)

            # 计算指标
            total_duration = end_time - start_time
            result["latency_total"] = round(total_duration, 4)
            
            # 计算 Token (litellm 内置工具)
            # 注意：某些 API 可能直接返回 usage，但流式通常需要自己算或最后合并
            # 这里简单使用 litellm 的 tokenizer 估算
            input_tokens = len(litellm.encode(model=model, text=prompt))
            output_tokens = len(litellm.encode(model=model, text=full_response))
            
            result["output_tokens"] = output_tokens
            
            # 计算吞吐量 (Output Tokens / (Total Time - TTFT)) 
            # 减去 TTFT 是因为生成是在首字之后才开始的，这样算生成速度更准
            generation_time = total_duration - result["latency_ttft"]
            if generation_time > 0:
                result["throughput"] = round(output_tokens / generation_time, 2)
            
            # 计算成本
            try:
                # 注意：cost_per_token 可能会根据 litellm 版本更新
                cost = litellm.completion_cost(
                    completion_response=full_response,
                    model=model,
                    prompt=prompt
                )
                result["cost"] = float(cost) # 转换为 float
            except Exception as e:
                print(f"Cost calculation failed: {e}")
                result["cost"] = 0

            result["status"] = "success"
            # result["response_text"] = full_response # 可选：是否保存具体回复

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["latency_total"] = round(time.time() - start_time, 4)

        return result

    async def run_batch(self, configs: List[Dict], concurrency: int = 5):
        """
        并行运行多个测试，限制并发数
        """
        sem = asyncio.Semaphore(concurrency)
        
        async def run_with_sem(config):
            async with sem:
                return await self.run_benchmark(
                    provider=config.get("provider", "openai"), # litellm 通常只需要 model 名字，但这里保留 provider 字段用于前端展示
                    model=config["model"],
                    prompt=config["prompt"],
                    api_key=config.get("api_key"),
                    api_base=config.get("api_base")
                )

        tasks = [run_with_sem(config) for config in configs]
        return await asyncio.gather(*tasks)
