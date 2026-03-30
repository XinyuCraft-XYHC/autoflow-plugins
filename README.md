# AutoFlow 社区插件仓库

[English](#english) | [中文](#中文)

---

## 中文

这是 [AutoFlow](https://github.com/XinyuCraft-XYHC/autoflow-windows) 的社区插件仓库。

### 如何在 AutoFlow 中安装插件

1. 打开 AutoFlow → 设置 → 插件
2. 点击「🛒 插件市场」按钮
3. 浏览可用插件，点击「安装」
4. 插件安装后立即生效，无需重启

### 已有插件

| 插件 | 功能 | 作者 | 状态 |
|------|------|------|------|
| 系统监控 `system_monitor` | 实时监控 CPU / 内存 / 磁盘，支持阈值触发器 | AutoFlow Community | ✅ 可用 |
| 剪贴板历史 `clipboard_history` | 记录剪贴板历史，支持搜索与快速粘贴 | AutoFlow Community | ✅ 可用 |
| HTTP 请求 `http_request` | 发送 GET/POST 请求，结果存入变量 | AutoFlow Community | ✅ 可用 |

### 开发并发布你的插件

欢迎提交 Pull Request 添加新插件！详细步骤：

1. Fork 本仓库
2. 在 `plugins/` 目录下新建 `<插件ID>/` 文件夹（如 `my_plugin`）
3. 插件目录中至少包含：
   - `plugin.json` — 插件元信息
   - `main.py` — 入口文件（需含 `register(api)` 函数）
   - `README.md` — 插件说明（推荐）
4. 在 `index.json` 中添加你的插件条目（见下方格式说明）
5. 提交 Pull Request，等待审核

**插件 ID 格式：** 全英文 `snake_case`（如 `weather_alert`、`excel_export`）

### index.json 条目格式

```json
{
  "id": "my_plugin",
  "name": "我的插件",
  "name_en": "My Plugin",
  "version": "1.0.0",
  "author": "你的名字",
  "description": "插件功能简介（中文）",
  "description_en": "Plugin description (English)",
  "tags": ["标签1", "标签2"],
  "download_url": "https://github.com/XinyuCraft-XYHC/autoflow-plugins/archive/refs/heads/master.zip",
  "plugin_dir_in_zip": "autoflow-plugins-master/plugins/my_plugin",
  "updated": "2026-03-30",
  "stars": 0,
  "downloads": 0,
  "verified": false,
  "min_autoflow_version": "4.0.0",
  "repository": "https://github.com/你的用户名/你的仓库",
  "issues_url": "https://github.com/你的用户名/你的仓库/issues"
}
```

**字段说明：**
- `id`：插件唯一标识（全局唯一，`snake_case`）
- `plugin_dir_in_zip`：ZIP 中插件所在路径（若插件在本仓库 `plugins/` 下，固定为 `autoflow-plugins-master/plugins/<id>`）
- `verified`：官方审核通过后设为 `true`
- `min_autoflow_version`：插件需要的最低 AutoFlow 版本

### 开发指南

完整的插件开发文档请参阅 [AutoFlow 插件开发指南](https://github.com/XinyuCraft-XYHC/autoflow-windows/blob/master/docs/plugin-dev-guide.md)。

---

## English

This is the community plugin repository for [AutoFlow](https://github.com/XinyuCraft-XYHC/autoflow-windows).

### How to install plugins in AutoFlow

1. Open AutoFlow → Settings → Plugins
2. Click the "🛒 Plugin Market" button
3. Browse available plugins and click "Install"
4. Plugins take effect immediately after installation

### Available Plugins

| Plugin | Description | Author | Status |
|--------|-------------|--------|--------|
| System Monitor `system_monitor` | Monitor CPU / Memory / Disk with threshold triggers | AutoFlow Community | ✅ Available |
| Clipboard History `clipboard_history` | Record clipboard history with search & quick-paste | AutoFlow Community | ✅ Available |
| HTTP Request `http_request` | Send GET/POST requests and store results to variables | AutoFlow Community | ✅ Available |

### Contributing a Plugin

1. Fork this repository
2. Create a folder `plugins/<plugin_id>/` (e.g. `my_plugin`)
3. Include at minimum: `plugin.json`, `main.py`, and a `README.md`
4. Add your entry to `index.json` (see format above)
5. Submit a Pull Request

### Development Guide

See the full [AutoFlow Plugin Development Guide](https://github.com/XinyuCraft-XYHC/autoflow-windows/blob/master/docs/plugin-dev-guide.md).
