"""
HTTP 请求插件 - HTTP Request
发送 GET/POST 等 HTTP 请求，结果存入变量
"""
try:
    from autoflow_plugin_api import AutoFlowPlugin
    PluginBase = AutoFlowPlugin
except ImportError:
    class PluginBase:
        def get_blocks(self): return []
        def execute_block(self, block_type, params, ctx): return {}


class HttpRequestPlugin(PluginBase):
    def get_info(self):
        return {
            "id": "http_request",
            "name": "HTTP 请求",
            "version": "1.0.0",
            "author": "AutoFlow Community",
            "description": "发送 HTTP GET/POST 请求，支持 JSON/表单/自定义 Headers",
        }

    def get_blocks(self):
        return [
            {
                "type": "http_get",
                "label": "HTTP GET 请求",
                "icon": "🌐",
                "category": "HTTP 请求",
                "fields": [
                    {"name": "url", "label": "URL", "type": "text",
                     "placeholder": "https://api.example.com/data"},
                    {"name": "headers", "label": "请求头 (JSON)", "type": "textarea",
                     "default": "{}", "placeholder": '{"Authorization": "Bearer token"}'},
                    {"name": "output_var", "label": "响应存入变量", "type": "text",
                     "default": "http_response"},
                    {"name": "status_var", "label": "状态码存入变量", "type": "text",
                     "default": "http_status"},
                    {"name": "timeout", "label": "超时(秒)", "type": "number",
                     "default": "10"},
                ],
                "summary": "GET {{url}} → {{output_var}}",
            },
            {
                "type": "http_post",
                "label": "HTTP POST 请求",
                "icon": "📤",
                "category": "HTTP 请求",
                "fields": [
                    {"name": "url", "label": "URL", "type": "text",
                     "placeholder": "https://api.example.com/submit"},
                    {"name": "body_type", "label": "请求体类型", "type": "select",
                     "options": ["JSON", "表单(form)", "纯文本"], "default": "JSON"},
                    {"name": "body", "label": "请求体", "type": "textarea",
                     "default": "{}", "placeholder": '{"key": "value"}'},
                    {"name": "headers", "label": "额外请求头 (JSON)", "type": "textarea",
                     "default": "{}", "placeholder": '{"X-Custom": "value"}'},
                    {"name": "output_var", "label": "响应存入变量", "type": "text",
                     "default": "http_response"},
                    {"name": "status_var", "label": "状态码存入变量", "type": "text",
                     "default": "http_status"},
                    {"name": "timeout", "label": "超时(秒)", "type": "number",
                     "default": "10"},
                ],
                "summary": "POST {{url}} → {{output_var}}",
            },
        ]

    def execute_block(self, block_type: str, params: dict, ctx=None) -> dict:
        fields = params if isinstance(params, dict) else {}
        import urllib.request
        import urllib.parse
        import json as _json

        url = fields.get("url", "")
        if not url:
            return {"success": False, "error": "URL 不能为空"}

        timeout = int(fields.get("timeout", 10))
        output_var = fields.get("output_var", "http_response")
        status_var = fields.get("status_var", "http_status")

        # 解析 headers
        headers = {}
        try:
            headers = _json.loads(fields.get("headers", "{}") or "{}")
        except Exception:
            pass

        try:
            if block_type == "http_get":
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                    status = resp.status
                return {
                    "success": True,
                    "variables": {output_var: body, status_var: str(status)}
                }

            elif block_type == "http_post":
                body_type = fields.get("body_type", "JSON")
                body_str = fields.get("body", "{}")

                if body_type == "JSON":
                    data = body_str.encode("utf-8")
                    headers.setdefault("Content-Type", "application/json")
                elif body_type == "表单(form)":
                    # 尝试解析 JSON 为 dict，再 url encode
                    try:
                        d = _json.loads(body_str)
                    except Exception:
                        d = {}
                    data = urllib.parse.urlencode(d).encode("utf-8")
                    headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
                else:
                    data = body_str.encode("utf-8")
                    headers.setdefault("Content-Type", "text/plain")

                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    resp_body = resp.read().decode("utf-8", errors="replace")
                    status = resp.status
                return {
                    "success": True,
                    "variables": {output_var: resp_body, status_var: str(status)}
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

        return {"success": False, "error": f"未知块类型: {block_type}"}


def register(api=None):
    """
    支持新版 register(api) 和旧版 register() 两种调用方式。
    """
    plugin = HttpRequestPlugin()
    if api is not None and hasattr(api, "register_plugin"):
        api.register_plugin(plugin)
    else:
        return plugin
