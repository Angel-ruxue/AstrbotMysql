import requests
import json

# APIPassword = 'VzViWTeWNklPcLosXkRg:QEpGmKjRqGBuZbmfcpLH'

APIPassword = 'jomPkbhKzIciYIwKmaxZ:sLBJrSyOVIyIQngrtObY'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {APIPassword}'
}

def make_chat_request(content):
    request_body = {
        "model": "4.0Ultra",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "temperature": 1.0,
        "max_tokens": 4096
    }

    try:
        response = requests.post(
            'https://spark-api-open.xf-yun.com/v1/chat/completions',
            headers=headers,
            data=json.dumps(request_body),
            timeout=15  # ✅ 设置超时时间（秒）
        )
        response.raise_for_status()
        data = response.json()

        code = data.get("code")
        message = data.get("message")
        reply = data["choices"][0]["message"]["content"]

        return code, message, reply
    except requests.exceptions.ReadTimeout:
        print("请求超时：星火接口未在预期时间内响应。")
        return None, None, ""
    except requests.exceptions.RequestException as e:
        print("请求错误:", e)
        return None, None, ""


# 对外暴露的命令接口
def ai_command(user_input):
    _, _, reply = make_chat_request(user_input)
    return reply
