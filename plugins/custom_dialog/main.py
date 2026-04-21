"""
自定义弹窗插件 - Custom Dialog
弹出高度可自定义的对话框，支持文本、输入框、下拉选择、复选框等多种控件混搭。
用户操作结果存入指定变量，可配合 if_block 进行条件判断。

依赖：Python 内置 tkinter（无需额外安装）

控件类型（items JSON 数组中每个对象的 type 字段）：
  - label       纯文本标签
  - separator   水平分隔线
  - input       单行文本输入框  → 结果存入 var
  - textarea    多行文本输入框  → 结果存入 var
  - select      下拉选择框      → 结果存入 var
  - checkbox    复选框          → 结果存入 var（"true"/"false"）
  - image       图片（本地路径）
  - progress    进度条（只读展示）

items 示例：
[
  {"type": "label",    "text": "请选择操作模式："},
  {"type": "separator"},
  {"type": "input",    "label": "项目名称", "var": "proj_name",  "default": "MyProject"},
  {"type": "textarea", "label": "备注",     "var": "note",       "default": "", "height": 4},
  {"type": "select",   "label": "环境",     "var": "env",        "options": ["开发", "测试", "生产"], "default": "开发"},
  {"type": "checkbox", "label": "确认发布", "var": "confirmed",  "default": false},
  {"type": "progress", "label": "当前进度", "value": 75}
]

buttons 示例：
[
  {"label": "确认", "value": "ok"},
  {"label": "取消", "value": "cancel"}
]
结果存入 result_var，值为用户点击的按钮的 value（关闭窗口时为 "__closed__"）。
"""

import json
import threading

try:
    from autoflow_plugin_api import AutoFlowPlugin
    PluginBase = AutoFlowPlugin
except ImportError:
    class PluginBase:
        def get_blocks(self): return []
        def execute_block(self, block_type, params, ctx): return {}


# ─────────────────────────── 弹窗实现 ───────────────────────────

def _show_custom_dialog(title, items, buttons, width, topmost, resolve_fn):
    """
    在独立线程中启动一个 tkinter 窗口（tkinter 支持多线程各自创建 Tk 根），
    阻塞直到用户关闭，返回 (button_value, {var: value, ...}) 二元组。
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    try:
        from PIL import Image as _PILImage, ImageTk as _PILImageTk
        _HAS_PIL = True
    except ImportError:
        _HAS_PIL = False

    result_box = {"btn": "__closed__", "vars": {}}

    root = tk.Tk()
    root.title(title)
    root.resizable(True, True)
    if topmost:
        root.attributes("-topmost", True)
    root.configure(bg="#1e1e2e")

    # ── 样式 ──
    style = ttk.Style(root)
    style.theme_use("clam")
    _BG   = "#1e1e2e"
    _FG   = "#cdd6f4"
    _ENTRY_BG = "#313244"
    _SEP_COLOR = "#45475a"
    _BTN_BG = "#585b70"
    _BTN_FG = "#cdd6f4"
    _BTN_ACTIVE = "#7f849c"
    _ACCENT = "#89b4fa"

    style.configure("TFrame",     background=_BG)
    style.configure("TLabel",     background=_BG, foreground=_FG, font=("Microsoft YaHei UI", 10))
    style.configure("TEntry",     fieldbackground=_ENTRY_BG, foreground=_FG,
                    insertcolor=_FG, borderwidth=0)
    style.configure("TSeparator", background=_SEP_COLOR)
    style.configure("TCheckbutton", background=_BG, foreground=_FG,
                    font=("Microsoft YaHei UI", 10))
    style.map("TCheckbutton",
              background=[("active", _BG)],
              foreground=[("active", _ACCENT)])
    style.configure("TCombobox",  fieldbackground=_ENTRY_BG, foreground=_FG,
                    background=_ENTRY_BG, selectbackground=_ACCENT, selectforeground="#1e1e2e")
    style.map("TCombobox",
              fieldbackground=[("readonly", _ENTRY_BG)],
              foreground=[("readonly", _FG)])
    style.configure("Horizontal.TProgressbar",
                    troughcolor=_ENTRY_BG, background=_ACCENT, borderwidth=0)

    # ── 主容器（带滚动）──
    outer = ttk.Frame(root, style="TFrame")
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, bg=_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas, style="TFrame")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(e):
        canvas.yview_scroll(-1 * (e.delta // 120), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    pad = {"padx": 16, "pady": 4}

    # ── 渲染控件 ──
    widget_vars = {}   # var_name -> tk Variable / Text widget

    for item in items:
        itype = item.get("type", "label")
        ilabel = item.get("label", "")
        ivar   = item.get("var", "")
        idefault = item.get("default", "")
        itext  = item.get("text", "")

        if itype == "label":
            ttk.Label(scroll_frame, text=resolve_fn(itext) if itext else "",
                      wraplength=width - 48, justify="left").pack(
                anchor="w", **pad)

        elif itype == "separator":
            ttk.Separator(scroll_frame, orient="horizontal").pack(
                fill="x", padx=16, pady=6)

        elif itype == "input":
            if ilabel:
                ttk.Label(scroll_frame, text=ilabel).pack(anchor="w", padx=16, pady=(6, 0))
            sv = tk.StringVar(value=resolve_fn(str(idefault)) if idefault else "")
            e = tk.Entry(scroll_frame, textvariable=sv,
                         bg=_ENTRY_BG, fg=_FG, insertbackground=_FG,
                         relief="flat", font=("Microsoft YaHei UI", 10),
                         highlightbackground=_SEP_COLOR, highlightthickness=1)
            e.pack(fill="x", padx=16, pady=(0, 4))
            if ivar:
                widget_vars[ivar] = sv

        elif itype == "textarea":
            rows = int(item.get("height", 3))
            if ilabel:
                ttk.Label(scroll_frame, text=ilabel).pack(anchor="w", padx=16, pady=(6, 0))
            txt = tk.Text(scroll_frame, height=rows,
                          bg=_ENTRY_BG, fg=_FG, insertbackground=_FG,
                          relief="flat", font=("Microsoft YaHei UI", 10),
                          wrap="word",
                          highlightbackground=_SEP_COLOR, highlightthickness=1)
            txt.pack(fill="x", padx=16, pady=(0, 4))
            default_val = resolve_fn(str(idefault)) if idefault else ""
            if default_val:
                txt.insert("1.0", default_val)
            if ivar:
                widget_vars[ivar] = txt   # Text widget，读取时用 .get("1.0","end-1c")

        elif itype == "select":
            options = [resolve_fn(str(o)) for o in item.get("options", [])]
            default_val = resolve_fn(str(idefault)) if idefault else (options[0] if options else "")
            if ilabel:
                ttk.Label(scroll_frame, text=ilabel).pack(anchor="w", padx=16, pady=(6, 0))
            sv = tk.StringVar(value=default_val)
            cb = ttk.Combobox(scroll_frame, textvariable=sv,
                               values=options, state="readonly",
                               font=("Microsoft YaHei UI", 10))
            cb.pack(fill="x", padx=16, pady=(0, 4))
            if ivar:
                widget_vars[ivar] = sv

        elif itype == "checkbox":
            default_bool = bool(idefault) if not isinstance(idefault, bool) else idefault
            if isinstance(idefault, str):
                default_bool = idefault.lower() in ("true", "1", "yes")
            bv = tk.BooleanVar(value=default_bool)
            cb = ttk.Checkbutton(scroll_frame, text=ilabel, variable=bv)
            cb.pack(anchor="w", padx=16, pady=4)
            if ivar:
                widget_vars[ivar] = bv

        elif itype == "progress":
            pval = int(item.get("value", 0))
            pval = max(0, min(100, pval))
            if ilabel:
                ttk.Label(scroll_frame, text=f"{ilabel}: {pval}%").pack(
                    anchor="w", padx=16, pady=(6, 0))
            pb = ttk.Progressbar(scroll_frame, orient="horizontal",
                                  length=width - 48, maximum=100,
                                  value=pval, mode="determinate")
            pb.pack(fill="x", padx=16, pady=(0, 6))

        elif itype == "image":
            img_path = resolve_fn(item.get("path", ""))
            img_width = int(item.get("width", 0))
            img_height = int(item.get("height", 0))
            if img_path and _HAS_PIL:
                try:
                    import os as _os
                    if _os.path.isfile(img_path):
                        pimg = _PILImage.open(img_path)
                        if img_width and img_height:
                            pimg = pimg.resize((img_width, img_height), _PILImage.LANCZOS)
                        elif img_width:
                            ratio = img_width / pimg.width
                            pimg = pimg.resize((img_width, int(pimg.height * ratio)), _PILImage.LANCZOS)
                        photo = _PILImageTk.PhotoImage(pimg)
                        lbl = tk.Label(scroll_frame, image=photo, bg=_BG)
                        lbl.image = photo   # 防止 GC
                        lbl.pack(padx=16, pady=4)
                except Exception:
                    pass
            elif img_path and not _HAS_PIL:
                ttk.Label(scroll_frame,
                          text=f"[图片: {img_path}（需安装 Pillow）]",
                          foreground="#f38ba8").pack(anchor="w", **pad)

    # ── 间距 ──
    ttk.Frame(scroll_frame, height=8, style="TFrame").pack()

    # ── 按钮区 ──
    btn_frame = tk.Frame(root, bg=_BG)
    btn_frame.pack(fill="x", padx=16, pady=12)

    def _collect_vars():
        result = {}
        for vname, wid in widget_vars.items():
            if isinstance(wid, tk.Text):
                result[vname] = wid.get("1.0", "end-1c")
            elif isinstance(wid, tk.BooleanVar):
                result[vname] = "true" if wid.get() else "false"
            else:
                result[vname] = wid.get()
        return result

    def _make_btn_cmd(bvalue):
        def _cmd():
            result_box["btn"] = bvalue
            result_box["vars"] = _collect_vars()
            root.destroy()
        return _cmd

    # 按钮从右往左排列
    effective_buttons = buttons if buttons else [{"label": "确定", "value": "ok"}]
    for bdef in reversed(effective_buttons):
        blabel = bdef.get("label", "确定")
        bvalue = bdef.get("value", blabel)
        btn = tk.Button(
            btn_frame, text=blabel,
            command=_make_btn_cmd(bvalue),
            bg=_BTN_BG, fg=_BTN_FG,
            activebackground=_BTN_ACTIVE, activeforeground=_FG,
            relief="flat", padx=18, pady=6,
            font=("Microsoft YaHei UI", 10),
            cursor="hand2",
            bd=0
        )
        btn.pack(side="right", padx=(6, 0))

    def _on_close():
        result_box["btn"] = "__closed__"
        result_box["vars"] = _collect_vars()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _on_close)

    # ── 设置窗口尺寸和位置 ──
    root.update_idletasks()
    w = max(width, 300)
    # 自动根据内容决定高度，最大 80% 屏幕高
    root.update()
    sh = root.winfo_screenheight()
    content_h = scroll_frame.winfo_reqheight() + 80   # 内容 + 按钮区
    h = min(content_h, int(sh * 0.8))
    sw = root.winfo_screenwidth()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.minsize(280, 120)

    root.mainloop()
    return result_box["btn"], result_box["vars"]


# ─────────────────────────── 插件类 ───────────────────────────

class CustomDialogPlugin(PluginBase):

    def get_info(self):
        return {
            "id": "custom_dialog",
            "name": "自定义弹窗",
            "version": "1.0.0",
            "author": "AutoFlow Official",
            "description": "弹出高度可自定义的对话框，支持文本、输入框、下拉选择、复选框等多种控件混搭",
        }

    def get_blocks(self):
        _items_placeholder = (
            '[{"type":"label","text":"请确认以下信息："},'
            '{"type":"separator"},'
            '{"type":"input","label":"项目名称","var":"proj_name","default":"MyProject"},'
            '{"type":"select","label":"环境","var":"env","options":["开发","测试","生产"],"default":"开发"},'
            '{"type":"checkbox","label":"我已确认以上信息","var":"confirmed","default":false}]'
        )
        _buttons_placeholder = (
            '[{"label":"确认","value":"ok"},{"label":"取消","value":"cancel"}]'
        )
        return [
            {
                "type": "custom_dialog_show",
                "label": "显示自定义弹窗",
                "icon": "🪟",
                "category": "通知&消息",
                "color": "#8B5CF6",
                "fields": [
                    {
                        "name": "title",
                        "label": "窗口标题",
                        "type": "text",
                        "default": "请操作",
                        "placeholder": "弹窗标题（支持 {{变量}}）",
                    },
                    {
                        "name": "items",
                        "label": "控件列表 (JSON 数组)",
                        "type": "textarea",
                        "default": _items_placeholder,
                        "placeholder": (
                            "每个对象是一个控件。type 可选：\n"
                            "  label / separator / input / textarea /\n"
                            "  select / checkbox / progress / image\n"
                            "带 var 字段的控件结果会存入对应变量名。"
                        ),
                    },
                    {
                        "name": "buttons",
                        "label": "按钮列表 (JSON 数组)",
                        "type": "textarea",
                        "default": _buttons_placeholder,
                        "placeholder": (
                            '[{"label":"确认","value":"ok"},{"label":"取消","value":"cancel"}]\n'
                            "value 是按钮被点击后存入 result_var 的值。"
                        ),
                    },
                    {
                        "name": "result_var",
                        "label": "按钮结果存入变量",
                        "type": "text",
                        "default": "dialog_result",
                        "placeholder": "点击的按钮 value 会存入此变量",
                    },
                    {
                        "name": "width",
                        "label": "窗口宽度 (px)",
                        "type": "number",
                        "default": "480",
                    },
                    {
                        "name": "topmost",
                        "label": "窗口置顶",
                        "type": "select",
                        "options": ["true", "false"],
                        "default": "true",
                    },
                ],
                "summary": "弹出「{{title}}」→ {{result_var}}",
            }
        ]

    def execute_block(self, block_type: str, params: dict, ctx=None) -> dict:
        if block_type != "custom_dialog_show":
            return {"success": False, "error": f"未知块类型: {block_type}"}

        fields = params if isinstance(params, dict) else {}

        # ── 读取参数 ──
        title      = str(fields.get("title", "请操作"))
        items_raw  = str(fields.get("items", "[]"))
        buttons_raw= str(fields.get("buttons", '[{"label":"确定","value":"ok"}]'))
        result_var = str(fields.get("result_var", "dialog_result"))
        width      = int(fields.get("width", 480) or 480)
        topmost    = str(fields.get("topmost", "true")).lower() in ("true", "1", "yes")

        # ── 变量替换辅助函数（传给弹窗用于解析 {{变量}} 占位符）──
        def _resolve(text):
            if ctx is not None and hasattr(ctx, "variables") and "{{" in text:
                import re
                def _repl(m):
                    k = m.group(1).strip()
                    v = ctx.variables.get(k, m.group(0))
                    return str(v)
                return re.sub(r"\{\{(.+?)\}\}", _repl, text)
            return text

        # ── 解析 JSON ──
        title = _resolve(title)
        try:
            items = json.loads(items_raw)
            if not isinstance(items, list):
                items = []
        except Exception as e:
            return {"success": False, "error": f"控件列表 JSON 解析失败: {e}"}

        try:
            buttons = json.loads(buttons_raw)
            if not isinstance(buttons, list):
                buttons = [{"label": "确定", "value": "ok"}]
        except Exception as e:
            return {"success": False, "error": f"按钮列表 JSON 解析失败: {e}"}

        # ── 弹出弹窗（在当前线程阻塞，tkinter 支持在非主线程创建独立 Tk 根）──
        try:
            btn_value, var_values = _show_custom_dialog(
                title=title,
                items=items,
                buttons=buttons,
                width=width,
                topmost=topmost,
                resolve_fn=_resolve,
            )
        except Exception as e:
            return {"success": False, "error": f"弹窗创建失败: {e}"}

        # ── 写回变量 ──
        out_vars = {}
        if result_var:
            out_vars[result_var] = btn_value
        out_vars.update(var_values)

        if ctx is not None and hasattr(ctx, "variables"):
            for k, v in out_vars.items():
                ctx.variables[k] = v

        return {"success": True, "variables": out_vars}


# ─────────────────────────── 注册 ───────────────────────────

def register(api=None):
    """支持新版 register(api) 和旧版 register() 两种调用方式。"""
    plugin = CustomDialogPlugin()
    if api is not None and hasattr(api, "register_plugin"):
        api.register_plugin(plugin)
    else:
        return plugin
