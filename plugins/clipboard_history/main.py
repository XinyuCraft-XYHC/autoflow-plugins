"""
剪贴板历史插件 - Clipboard History
记录并管理剪贴板历史
"""
import threading
import time
from autoflow_plugin_api import PluginBase


class ClipboardHistoryPlugin(PluginBase):
    def __init__(self):
        self._history = []          # list of str
        self._max_items = 50
        self._monitor_thread = None
        self._running = False
        self._last_text = ""

    def get_info(self):
        return {
            "id": "clipboard_history",
            "name": "剪贴板历史",
            "version": "1.0.0",
            "author": "AutoFlow Community",
            "description": "记录剪贴板历史，支持搜索、快速粘贴指定历史条目",
        }

    def on_load(self):
        self._start_monitor()

    def on_unload(self):
        self._running = False

    def _start_monitor(self):
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        try:
            import win32clipboard
        except ImportError:
            return

        while self._running:
            try:
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                if isinstance(text, str) and text and text != self._last_text:
                    self._last_text = text
                    self._history.insert(0, text)
                    if len(self._history) > self._max_items:
                        self._history = self._history[:self._max_items]
            except Exception:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            time.sleep(0.5)

    def get_blocks(self):
        return [
            {
                "type": "cb_get_history",
                "label": "获取剪贴板历史条目",
                "icon": "📋",
                "category": "剪贴板历史",
                "fields": [
                    {"name": "index", "label": "历史索引（0=最新）", "type": "number",
                     "default": "0"},
                    {"name": "output_var", "label": "输出变量名", "type": "text",
                     "default": "cb_text"},
                ],
                "summary": "剪贴板历史[{{index}}] → {{output_var}}",
            },
            {
                "type": "cb_get_count",
                "label": "获取历史条目数量",
                "icon": "🔢",
                "category": "剪贴板历史",
                "fields": [
                    {"name": "output_var", "label": "输出变量名", "type": "text",
                     "default": "cb_count"},
                ],
                "summary": "剪贴板历史数量 → {{output_var}}",
            },
            {
                "type": "cb_clear_history",
                "label": "清空剪贴板历史",
                "icon": "🗑",
                "category": "剪贴板历史",
                "fields": [],
                "summary": "清空剪贴板历史记录",
            },
            {
                "type": "cb_paste_history",
                "label": "粘贴历史条目",
                "icon": "📌",
                "category": "剪贴板历史",
                "fields": [
                    {"name": "index", "label": "历史索引（0=最新）", "type": "number",
                     "default": "0"},
                ],
                "summary": "将历史[{{index}}]复制到剪贴板",
            },
        ]

    def execute_block(self, block_type: str, fields: dict, variables: dict) -> dict:
        if block_type == "cb_get_history":
            idx = int(fields.get("index", 0))
            output_var = fields.get("output_var", "cb_text")
            if idx < len(self._history):
                return {"success": True, "variables": {output_var: self._history[idx]}}
            return {"success": True, "variables": {output_var: ""}}

        elif block_type == "cb_get_count":
            output_var = fields.get("output_var", "cb_count")
            return {"success": True, "variables": {output_var: str(len(self._history))}}

        elif block_type == "cb_clear_history":
            self._history.clear()
            return {"success": True}

        elif block_type == "cb_paste_history":
            idx = int(fields.get("index", 0))
            if idx >= len(self._history):
                return {"success": False, "error": f"历史索引 {idx} 超出范围"}
            text = self._history[idx]
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return {"success": True}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"未知块类型: {block_type}"}


def register():
    return ClipboardHistoryPlugin()
