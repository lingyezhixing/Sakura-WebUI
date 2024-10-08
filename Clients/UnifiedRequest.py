import Clients

# 定义获取可用服务器的函数
def get_available_servers():
    available_servers = [
        "llama-cpp"
    ]
    return available_servers

# 定义统一的段落异步翻译请求函数
async def translate_paragraph_request(session, server, system_prompt, preset_prompt, context, model, temperature, top_p, repeat_penalty, max_retry_count, completion_tokens):
    if server == "llama-cpp":
        return await Clients.llama_cpp.translate_paragraph_request(session, system_prompt, preset_prompt, context, model, temperature, top_p, repeat_penalty, max_retry_count, completion_tokens)


# 定义统一的逐行翻译请求函数
async def translate_line_request(session, server, system_prompt, preset_prompt, context, model, temperature, top_p, repeat_penalty, max_retry_count, total_completion_tokens):
    if server == "llama-cpp":
        return await Clients.llama_cpp.translate_line_request(session, system_prompt, preset_prompt, context, model, temperature, top_p, repeat_penalty, max_retry_count, total_completion_tokens)