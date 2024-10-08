import logging
import asyncio
from Clients.Timeout import TIMEOUT

# 定义统一的段落异步翻译请求函数
async def translate_paragraph_request(session, system_prompt, preset_prompt, context, model, temperature, top_p, frequency_penalty, max_retry_count, completion_tokens, retry_count=0):
    try:
        # 构建请求体
        prompt = preset_prompt + context
        data = {
            "model": model,
            "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
            "stream": False,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty
        }
        # 发送请求
        async with session.post("http://localhost:8080/v1/chat/completions", json=data, timeout=TIMEOUT) as response:
            if response.status == 200:
                result = await response.json()
                completion_tokens += result['usage']['completion_tokens']
                translated_lines = result['choices'][0]['message']['content'].split('\n')
                translated_lines = [line for line in translated_lines if line.strip() != ''] # 去除空行
                if len(translated_lines) > 1:
                    translated_lines = "\n".join(translated_lines)
                else:
                    translated_lines = translated_lines[0]
                return translated_lines, completion_tokens
            else:
                logging.error(f"请求失败，状态码：{response.status}")
                if retry_count <= max_retry_count:
                    logging.info(f"重试第 {retry_count + 1} 次")
                    await asyncio.sleep(1) # 等待1秒后重试
                    return await translate_paragraph_request(session, system_prompt, preset_prompt, context, model, temperature, top_p, frequency_penalty, max_retry_count, completion_tokens, retry_count + 1)
                else:
                    logging.error(f"重试次数已用尽，请求失败")
                    return None, None
    except Exception as e:
        logging.error(f"统一请求失败：段落翻译请求失败：{e}")
        return None, None

# 定义统一的逐行翻译请求函数
async def translate_line_request(session, system_prompt, preset_prompt, context, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens):
    try:
        context = context.split('\n')
        translated_lines = []
        for line in context:
            # 调用段落翻译函数
            translated_line, total_completion_tokens = await translate_paragraph_request(session, system_prompt, preset_prompt, line, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens)
            if translated_line is None:
                return None, None
            translated_lines.append(translated_line)
        return "\n".join(translated_lines), total_completion_tokens
    except Exception as e:
        logging.error(f"同意请求失败：逐行翻译请求失败：{e}")
        return None, None