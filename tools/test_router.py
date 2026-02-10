from openai import OpenAI

# 指向您的本地智能路由
client = OpenAI(
    api_key="sk-any-key", 
    base_url="http://127.0.0.1:8000/v1"
)

try:
    print("🚀 发送请求给智能路由 (deepseek-v3.2)...")
    response = client.chat.completions.create(
        model="deepseek-v3.2", 
        messages=[{"role": "user", "content": "请输出一行数字：12345"}],
        stream=False
    )
    print("✅ 收到回复:", response.choices[0].message.content)
except Exception as e:
    print("❌ 发生错误:", e)