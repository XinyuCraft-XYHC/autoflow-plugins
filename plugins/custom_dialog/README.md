# 自定义弹窗 (Custom Dialog)

AutoFlow 官方插件 · 通知&消息分类

弹出一个高度可自定义的对话框。与内置「弹出消息框」不同，本插件支持在窗口中混搭**多种交互控件**，适合需要在任务流中收集用户输入的场景。

---

## 功能块

### 显示自定义弹窗 (`custom_dialog_show`)

| 参数 | 说明 |
|------|------|
| **窗口标题** | 弹窗顶部标题，支持 `{{变量}}` |
| **控件列表** | JSON 数组，定义窗口内容（见下文） |
| **按钮列表** | JSON 数组，定义底部按钮 |
| **按钮结果存入变量** | 用户点击哪个按钮，该按钮的 `value` 就存入此变量 |
| **窗口宽度** | 像素宽度，默认 480 |
| **窗口置顶** | 是否始终在最前，默认 true |

---

## 控件类型（items 数组）

### `label` — 纯文本

```json
{"type": "label", "text": "请选择部署环境："}
```

### `separator` — 分隔线

```json
{"type": "separator"}
```

### `input` — 单行输入框

```json
{"type": "input", "label": "项目名称", "var": "proj_name", "default": "MyProject"}
```

### `textarea` — 多行输入框

```json
{"type": "textarea", "label": "备注信息", "var": "note", "default": "", "height": 4}
```

### `select` — 下拉选择

```json
{"type": "select", "label": "目标环境", "var": "env", "options": ["开发", "测试", "生产"], "default": "测试"}
```

### `checkbox` — 复选框

```json
{"type": "checkbox", "label": "我已确认以上操作", "var": "confirmed", "default": false}
```
结果为字符串 `"true"` 或 `"false"`，可用 `if_block` 判断。

### `progress` — 进度条（只读展示）

```json
{"type": "progress", "label": "当前完成度", "value": 75}
```

### `image` — 图片（需安装 Pillow）

```json
{"type": "image", "path": "C:/images/logo.png", "width": 200}
```

---

## 按钮定义（buttons 数组）

```json
[
  {"label": "确认部署", "value": "deploy"},
  {"label": "取消",     "value": "cancel"}
]
```

- `label`：按钮显示文字
- `value`：用户点击此按钮后，存入 `result_var` 的值
- 直接关闭窗口（点 ×）：存入 `"__closed__"`

---

## 完整示例

**控件列表：**
```json
[
  {"type": "label", "text": "任务：部署项目 {{proj}}"},
  {"type": "separator"},
  {"type": "select", "label": "目标环境", "var": "env", "options": ["开发","测试","生产"], "default": "测试"},
  {"type": "input",  "label": "版本号",   "var": "version", "default": "1.0.0"},
  {"type": "textarea", "label": "变更说明", "var": "changelog", "height": 3},
  {"type": "checkbox", "label": "跳过单元测试", "var": "skip_test", "default": false},
  {"type": "separator"},
  {"type": "progress", "label": "上次部署进度", "value": 100}
]
```

**按钮列表：**
```json
[{"label": "开始部署", "value": "deploy"}, {"label": "取消", "value": "cancel"}]
```

**结果变量：** `dialog_result`

执行后可用 `if_block` 判断 `{{dialog_result}} == deploy` 来决定后续步骤，  
同时 `{{env}}`、`{{version}}`、`{{changelog}}`、`{{skip_test}}` 均已填入任务变量中。

---

## 注意事项

- **无额外依赖**：使用 Python 内置 `tkinter`，无需 `pip install`
- **图片支持**：需要安装 `Pillow`（`pip install pillow`）；不安装时图片控件会显示提示文字
- **线程安全**：弹窗在调用方线程阻塞，不影响其他任务执行
- **深色主题**：界面自动适配 AutoFlow 深色风格（Catppuccin Mocha 配色）
