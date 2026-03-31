"""
系统监控插件 - System Monitor
提供 CPU、内存、磁盘信息获取功能块

兼容 AutoFlow v4.0+ 新版插件 API。
"""
try:
    from autoflow_plugin_api import AutoFlowPlugin
    PluginBase = AutoFlowPlugin
except ImportError:
    class PluginBase:
        def get_blocks(self): return []
        def execute_block(self, block_type, params, ctx): return {}


class SystemMonitorPlugin(PluginBase):

    def get_info(self):
        return {
            "id": "system_monitor",
            "name": "系统监控",
            "version": "2.0.0",
            "author": "AutoFlow Community",
            "description": "实时监控 CPU、内存、磁盘使用率",
        }

    def get_blocks(self):
        return [
            {
                "type": "sys_get_cpu",
                "label": "获取 CPU 使用率",
                "icon": "🖥",
                "category": "系统监控",
                "fields": [
                    {"name": "output_var", "label": "输出变量名", "type": "text",
                     "default": "cpu_usage", "placeholder": "变量名（不含 {{}}）"},
                    {"name": "interval", "label": "采样间隔(秒)", "type": "number",
                     "default": "1", "placeholder": "1"},
                ],
                "summary": "CPU 使用率 → {{output_var}}",
            },
            {
                "type": "sys_get_memory",
                "label": "获取内存使用率",
                "icon": "💾",
                "category": "系统监控",
                "fields": [
                    {"name": "output_var", "label": "输出变量名", "type": "text",
                     "default": "mem_usage", "placeholder": "变量名"},
                    {"name": "unit", "label": "单位", "type": "select",
                     "options": ["percent", "MB", "GB"], "default": "percent"},
                ],
                "summary": "内存使用 → {{output_var}}",
            },
            {
                "type": "sys_get_disk",
                "label": "获取磁盘使用情况",
                "icon": "💿",
                "category": "系统监控",
                "fields": [
                    {"name": "path", "label": "磁盘路径", "type": "text",
                     "default": "C:\\", "placeholder": "C:\\"},
                    {"name": "output_var", "label": "输出变量名", "type": "text",
                     "default": "disk_usage"},
                    {"name": "unit", "label": "单位", "type": "select",
                     "options": ["percent", "GB", "MB"], "default": "percent"},
                ],
                "summary": "磁盘 {{path}} → {{output_var}}",
            },
        ]

    def execute_block(self, block_type: str, params: dict, ctx=None) -> dict:
        # 兼容旧版 execute_block(block_type, fields, variables) 签名
        fields = params if isinstance(params, dict) else {}

        try:
            import psutil
        except ImportError:
            return {"success": False, "error": "需要安装 psutil：pip install psutil"}

        output_var = fields.get("output_var", "result")

        if block_type == "sys_get_cpu":
            interval = float(fields.get("interval", 1))
            val = psutil.cpu_percent(interval=interval)
            return {"success": True, "variables": {output_var: str(val)}}

        elif block_type == "sys_get_memory":
            mem = psutil.virtual_memory()
            unit = fields.get("unit", "percent")
            if unit == "percent":
                val = mem.percent
            elif unit == "MB":
                val = round(mem.used / 1024 / 1024, 1)
            else:
                val = round(mem.used / 1024 / 1024 / 1024, 2)
            return {"success": True, "variables": {output_var: str(val)}}

        elif block_type == "sys_get_disk":
            path = fields.get("path", "C:\\")
            disk = psutil.disk_usage(path)
            unit = fields.get("unit", "percent")
            if unit == "percent":
                val = disk.percent
            elif unit == "GB":
                val = round(disk.used / 1024 ** 3, 2)
            else:
                val = round(disk.used / 1024 ** 2, 1)
            return {"success": True, "variables": {output_var: str(val)}}

        return {"success": False, "error": f"未知块类型: {block_type}"}


def register(api=None):
    """
    支持新版 register(api) 和旧版 register() 两种调用方式。
    """
    plugin = SystemMonitorPlugin()
    if api is not None and hasattr(api, "register_plugin"):
        api.register_plugin(plugin)
    else:
        return plugin
