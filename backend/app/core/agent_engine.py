import json
import re
from openai import AsyncOpenAI
from ..config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


async def call_agent(system_prompt: str, user_message: str, history: list[dict] = None) -> dict:
    """调用 DeepSeek API，返回 {text, proposals}"""
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
