# liblibAI Stable Diffusion WebUI 插件

一个用于在 Stable Diffusion WebUI 中集成 liblibAI 服务的插件，让您可以直接在 WebUI 中使用 liblibAI 的各种功能。

## 功能特点

- 🖼️ **文生图**：使用 liblibAI 的模型生成图像
- 🎨 **图生图**：基于输入图像生成新图像
- 🔄 **ComfyUI 工作流**：支持使用和管理 liblibAI 的 ComfyUI 工作流
- 📚 **模型管理**：浏览、搜索和使用 liblibAI 提供的各种模型
- 📋 **任务管理**：查看和管理生成任务
- ⚙️ **设置管理**：配置 API 密钥、代理等设置
- 🔌 **WebUI 集成**：与 WebUI 的无缝集成，增强模型卡片和提示词输入框
- 🌟 **星流 Star-3 Alpha 支持**：支持使用 liblibAI 的星流 Star-3 Alpha 模型

## 系统要求

- Stable Diffusion WebUI v1.5.0 或更高版本
- Python 3.8 或更高版本
- 有效的 liblibAI API 密钥（Access Key 和 Secret Key）
- 互联网连接

## 安装方法

### 自动安装

1. 在 Stable Diffusion WebUI 中，进入 "Extensions" 选项卡
2. 点击 "Install from URL"
3. 输入本仓库的 URL
4. 点击 "Install"
5. 重启 WebUI

### 手动安装

1. 关闭 WebUI（如果正在运行）
2. 进入 WebUI 的 `extensions` 目录
3. 克隆本仓库：`git clone https://github.com/yourusername/stable-diffusion-webui-liblibai-plugin.git`
4. 重启 WebUI

## 依赖项

本插件依赖以下 Python 库：

- requests
- pillow
- gradio
- numpy
- pycryptodome (用于 HMAC-SHA1 签名)

这些依赖项会在插件安装过程中自动安装。

## 使用方法

### 初始设置

1. 安装插件后，在 WebUI 中会出现 "LiblibAI" 选项卡
2. 进入 "设置" 子选项卡
3. 输入您的 liblibAI API 密钥（Access Key 和 Secret Key）
4. 如果需要，配置代理设置
5. 点击 "保存设置"

### 生成图像

1. 进入 "生成" 子选项卡
2. 选择要使用的模型
3. 输入提示词和负面提示词
4. 调整参数（宽度、高度、步数等）
5. 点击 "生成" 按钮
6. 等待生成完成，结果将显示在右侧

### 使用工作流

1. 进入 "工作流" 子选项卡
2. 选择要使用的工作流
3. 配置工作流参数
4. 点击 "运行工作流" 按钮
5. 等待执行完成，结果将显示在右侧

### 浏览模型

1. 进入 "模型" 子选项卡
2. 选择模型类型（全部、底模、LoRA 等）
3. 使用搜索框搜索特定模型
4. 在列表中查看模型信息

### 管理任务

1. 进入 "任务" 子选项卡
2. 输入任务 ID 查询特定任务状态
3. 查看最近任务列表
4. 点击 "刷新" 按钮更新任务状态

## 与 WebUI 的集成

### 模型卡片增强

插件会为 WebUI 中的模型卡片添加 "使用 LiblibAI" 按钮，点击后会自动切换到 LiblibAI 选项卡并搜索相应模型。

### 提示词输入框增强

插件会为 WebUI 中的提示词输入框添加 "发送到 LiblibAI" 按钮，点击后会自动切换到 LiblibAI 选项卡并填入提示词和负面提示词。

## 配置选项

插件的配置文件位于 `extensions/stable-diffusion-webui-liblibai-plugin/liblibai_helper.json`，包含以下选项：

- `access_key`：liblibAI API 的 Access Key
- `secret_key`：liblibAI API 的 Secret Key
- `proxy`：代理服务器地址（如果需要）
- `auto_update_check`：是否自动检查更新
- `update_interval`：更新检查间隔（秒）
- `save_path`：生成图像的保存路径
- `default_model`：默认使用的模型
- `default_workflow`：默认使用的工作流
- `ui_defaults`：UI 默认参数（宽度、高度、步数等）

## 常见问题

### API 密钥在哪里获取？

您需要在 [liblibAI 官网](https://liblibai.com) 注册账号并创建 API 密钥。

### 为什么生成图像失败？

可能的原因：
- API 密钥无效或过期
- 网络连接问题
- 参数设置不正确
- 服务器繁忙

请检查设置和网络连接，或查看任务状态获取详细错误信息。

### 如何更新插件？

在 WebUI 的 "Extensions" 选项卡中，找到本插件并点击 "Check for updates"，然后按照提示操作。

### 为什么我看不到某些模型？

liblibAI 的模型访问权限可能受到账户类型和权限的限制。请确保您的账户有权访问相应的模型。

### 如何提高生成图像的质量？

- 使用更详细和具体的提示词
- 增加采样步数（通常 20-30 步效果较好）
- 尝试不同的采样器（例如 euler_a、dpm2_ancestral）
- 调整 CFG Scale（通常 7-12 效果较好）
- 使用更高的分辨率（如 512x768 或 768x768）

## 故障排除

### 插件不显示在 WebUI 中

- 确保插件安装在正确的目录
- 检查 WebUI 的日志是否有错误信息
- 尝试重新安装插件

### 无法连接到 liblibAI API

- 检查 API 密钥是否正确
- 检查网络连接
- 如果使用代理，确保代理设置正确
- 检查 liblibAI 服务是否可用

### 生成图像时出错

- 检查参数是否在有效范围内
- 确保选择了有效的模型
- 查看任务状态获取详细错误信息

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Civitai Helper](https://github.com/butaixianran/Stable-Diffusion-Webui-Civitai-Helper)
- [liblibAI](https://liblibai.com)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系我们：

- GitHub Issues：[提交问题](https://github.com/yourusername/stable-diffusion-webui-liblibai-plugin/issues)
- 电子邮件：your.email@example.com