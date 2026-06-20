import json
import re
from openai import AsyncOpenAI
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def reload_client(api_key: str = "", base_url: str = ""):
    global _client
    key = api_key or DEEPSEEK_API_KEY
    url = base_url or DEEPSEEK_BASE_URL
    _client = AsyncOpenAI(api_key=key, base_url=url)


async def test_connection() -> dict:
    """用当前配置发一条简单请求，验证 API Key 是否有效。"""
    try:
        client = get_client()
        resp = await client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )
        reply = resp.choices[0].message.content or ""
        return {"status": "ok", "message": f"连接成功，模型回复: {reply}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def call_agent(system_prompt: str, user_message: str, history: list[dict] = None) -> dict:
    """调用 DeepSeek API，返回 {text, proposals}"""
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
    )
    text = resp.choices[0].message.content or ""

    # 解析 [提议]...[/提议] 块
    proposals = []
    pattern = r'\[提议\](.*?)\[/提议\]'
    for match in re.finditer(pattern, text, re.DOTALL):
        try:
            proposals.append(json.loads(match.group(1).strip()))
        except json.JSONDecodeError:
            proposals.append({"raw": match.group(1).strip()})

    # 移除提议块后的纯文本
    clean_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
    return {"text": clean_text, "proposals": proposals}


async def call_agent_stream(system_prompt: str, user_message: str, history: list[dict] = None):
    """流式调用 DeepSeek"""
    client = get_client()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    stream = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
