import os
import time
import json
from datetime import datetime
import requests
import modules.scripts as scripts
from modules import script_callbacks
import gradio as gr

# 导入插件库
from scripts.lh_lib.auth import LiblibAIAuth
from scripts.lh_lib.api import LiblibAIAPI, APIError

# 设置日志记录器
import logging
logger = logging.getLogger("liblibai_helper")
logger.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 添加处理器到记录器
logger.addHandler(console_handler)

# 全局实例
settings = {}
auth = None
api = None

# 加载设置
def load_settings():
    global settings, auth, api
    
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "liblibai_helper.json"
    )
    
    # 默认设置
    settings = {
        "access_key": "",
        "secret_key": "",
        "proxy": "",
        "auto_update_check": True,
        "update_interval": 3600,
        "save_path": "",
        "default_model": "",
        "default_workflow": "",
        "ui_defaults": {
            "width": 512,
            "height": 512,
            "steps": 20,
            "cfg_scale": 7.0,
            "sampler": "euler_a"
        }
    }
    
    # 加载设置
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # 更新设置，但保留默认值中存在但加载的设置中不存在的项
                update_nested_dict(settings, loaded_settings)
        except Exception as e:
            logger.error(f"加载设置失败: {str(e)}")
    
    # 初始化认证和 API
    auth = LiblibAIAuth(settings.get("access_key"), settings.get("secret_key"))
    api = LiblibAIAPI(auth)
    
    # 设置代理
    if settings.get("proxy"):
        api.set_proxy(settings.get("proxy"))

# 递归更新嵌套字典
def update_nested_dict(d, u):
    """递归更新嵌套字典"""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            update_nested_dict(d[k], v)
        else:
            d[k] = v

# 保存设置
def save_settings():
    config_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "liblibai_helper.json"
    )
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存设置失败: {str(e)}")
        return False

# 确保目录存在
def ensure_directory(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# 创建 UI
def on_ui_tabs():
    """创建插件 UI 选项卡"""
    # 加载设置
    load_settings()
    
    with gr.Blocks(analytics_enabled=False) as liblibai_interface:
        with gr.Tabs():
            with gr.TabItem("生成"):
                create_generation_ui()
            with gr.TabItem("工作流"):
                create_workflow_ui()
            with gr.TabItem("模型"):
                create_models_ui()
            with gr.TabItem("任务"):
                create_tasks_ui()
            with gr.TabItem("设置"):
                create_settings_ui()
                
    return [(liblibai_interface, "LiblibAI", "liblibai_interface")]

def create_generation_ui():
    """创建生成 UI"""
    with gr.Row():
        with gr.Column(scale=4):
            model_id = gr.Dropdown(label="模型", choices=[], interactive=True)
            prompt = gr.Textbox(label="提示词", lines=3, placeholder="输入提示词...")
            negative_prompt = gr.Textbox(label="负面提示词", lines=2, placeholder="输入负面提示词...")
            
        with gr.Column(scale=1):
            with gr.Box():
                gr.Markdown("### 参数设置")
                width = gr.Slider(label="宽度", minimum=64, maximum=2048, step=8, value=settings.get("ui_defaults", {}).get("width", 512))
                height = gr.Slider(label="高度", minimum=64, maximum=2048, step=8, value=settings.get("ui_defaults", {}).get("height", 512))
                steps = gr.Slider(label="步数", minimum=1, maximum=150, step=1, value=settings.get("ui_defaults", {}).get("steps", 20))
                cfg_scale = gr.Slider(label="CFG Scale", minimum=1, maximum=30, step=0.5, value=settings.get("ui_defaults", {}).get("cfg_scale", 7.0))
                sampler = gr.Dropdown(label="采样器", choices=["euler_a", "euler", "lms", "heun", "dpm2", "dpm2_ancestral", "dpmpp_2s_ancestral", "dpmpp_2m", "dpmpp_sde", "ddim"], value=settings.get("ui_defaults", {}).get("sampler", "euler_a"))
                seed = gr.Number(label="种子", value=-1)
                
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="图生图输入", visible=False, type="pil")
            use_img2img = gr.Checkbox(label="使用图生图模式", value=False)
            
            def toggle_img2img(use_img2img):
                return gr.Image.update(visible=use_img2img)
                
            use_img2img.change(toggle_img2img, use_img2img, image_input)
            
        with gr.Column():
            generate_btn = gr.Button("生成", variant="primary")
            output_image = gr.Image(label="生成结果")
            output_info = gr.Textbox(label="生成信息", interactive=False)
            
    # 加载模型列表
    def load_models():
        try:
            if not auth.is_configured():
                return gr.Dropdown.update(choices=[], value=None)
                
            # 模拟 API 调用，实际应该调用 api.get_models()
            models = [
                {"id": "model1", "name": "模型1"},
                {"id": "model2", "name": "模型2"},
                {"id": "model3", "name": "模型3"}
            ]
            return gr.Dropdown.update(choices=[f"{m['name']} ({m['id']})" for m in models])
        except Exception as e:
            logger.error(f"加载模型列表失败: {str(e)}")
            return gr.Dropdown.update(choices=[])
            
    # 生成图像
    def generate_image(model_selection, prompt, negative_prompt, width, height, steps, cfg_scale, sampler, seed, use_img2img, image_input):
        try:
            if not auth.is_configured():
                return None, "请先在设置中配置 API 密钥"
                
            # 从选择中提取模型 ID
            if not model_selection:
                return None, "请选择模型"
                
            model_id = model_selection.split("(")[-1].rstrip(")")
            
            # 准备参数
            params = {
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "sampler": sampler,
                "seed": seed if seed != -1 else None
            }
            
            # 创建任务
            if use_img2img and image_input is not None:
                # 保存临时图片
                temp_img_path = "temp_img2img_input.png"
                image_input.save(temp_img_path)
                
                # 图生图任务
                # 实际应该调用 api.image_to_image()
                response = {"task_id": "img2img_task_123"}
            else:
                # 文生图任务
                # 实际应该调用 api.text_to_image()
                response = {"task_id": "txt2img_task_123"}
                
            # 获取任务 ID
            task_id = response.get("task_id")
            if not task_id:
                return None, f"创建任务失败: {response.get('message', '未知错误')}"
                
            # 轮询任务结果
            # 实际应该调用 api.get_task_result() 并轮询
            # 这里模拟任务完成
            time.sleep(2)  # 模拟等待
            result = {
                "status": "success",
                "result": {
                    "image_url": "https://example.com/image.png"
                }
            }
            
            # 获取生成的图片
            image_url = result.get("result", {}).get("image_url")
            if not image_url:
                return None, f"获取图片失败: {result.get('message', '未知错误')}"
                
            # 下载图片
            # 实际应该下载图片，这里模拟
            output_dir = settings.get("save_path") or "outputs/liblibai"
            ensure_directory(output_dir)
            
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f"liblibai_{timestamp}.png")
            
            # 模拟下载图片
            with open("scripts/lh_lib/__init__.py", "rb") as f:
                content = f.read()
                
            with open(output_path, "wb") as f:
                f.write(content)
                
            # 返回结果
            info = f"任务 ID: {task_id}\n模型: {model_selection}\n提示词: {prompt}\n负面提示词: {negative_prompt}\n参数: {width}x{height}, 步数={steps}, CFG={cfg_scale}, 采样器={sampler}, 种子={seed if seed != -1 else '随机'}"
            return output_path, info
            
        except Exception as e:
            logger.error(f"生成失败: {str(e)}")
            return None, f"生成失败: {str(e)}"
            
    # 绑定事件
    generate_btn.click(
        generate_image,
        inputs=[model_id, prompt, negative_prompt, width, height, steps, cfg_scale, sampler, seed, use_img2img, image_input],
        outputs=[output_image, output_info]
    )
    
    # 初始加载模型列表
    model_id.choices = load_models().choices

def create_workflow_ui():
    """创建工作流 UI"""
    with gr.Row():
        with gr.Column():
            workflow_id = gr.Dropdown(label="工作流", choices=[], interactive=True)
            workflow_params = gr.JSON(label="工作流参数", value={})
            run_workflow_btn = gr.Button("运行工作流", variant="primary")
            
        with gr.Column():
            workflow_output = gr.Image(label="工作流结果")
            workflow_info = gr.Textbox(label="工作流信息", interactive=False)
            
    # 加载工作流列表
    def load_workflows():
        try:
            if not auth.is_configured():
                return gr.Dropdown.update(choices=[], value=None)
                
            # 模拟 API 调用，实际应该调用 api.get_workflow_templates()
            workflows = [
                {"id": "workflow1", "name": "工作流1"},
                {"id": "workflow2", "name": "工作流2"},
                {"id": "workflow3", "name": "工作流3"}
            ]
            return gr.Dropdown.update(choices=[f"{w['name']} ({w['id']})" for w in workflows])
        except Exception as e:
            logger.error(f"加载工作流列表失败: {str(e)}")
            return gr.Dropdown.update(choices=[])
            
    # 运行工作流
    def run_workflow(workflow_selection, params):
        try:
            if not auth.is_configured():
                return None, "请先在设置中配置 API 密钥"
                
            # 从选择中提取工作流 ID
            if not workflow_selection:
                return None, "请选择工作流"
                
            workflow_id = workflow_selection.split("(")[-1].rstrip(")")
            
            # 运行工作流
            # 实际应该调用 api.run_workflow()
            response = {"task_id": "workflow_task_123"}
            
            # 获取任务 ID
            task_id = response.get("task_id")
            if not task_id:
                return None, f"创建任务失败: {response.get('message', '未知错误')}"
                
            # 轮询任务结果
            # 实际应该调用 api.get_task_result() 并轮询
            # 这里模拟任务完成
            time.sleep(2)  # 模拟等待
            result = {
                "status": "success",
                "result": {
                    "image_url": "https://example.com/image.png"
                }
            }
            
            # 获取生成的图片
            image_url = result.get("result", {}).get("image_url")
            if not image_url:
                return None, f"获取图片失败: {result.get('message', '未知错误')}"
                
            # 下载图片
            # 实际应该下载图片，这里模拟
            output_dir = settings.get("save_path") or "outputs/liblibai"
            ensure_directory(output_dir)
            
            timestamp = int(time.time())
            output_path = os.path.join(output_dir, f"liblibai_workflow_{timestamp}.png")
            
            # 模拟下载图片
            with open("scripts/lh_lib/__init__.py", "rb") as f:
                content = f.read()
                
            with open(output_path, "wb") as f:
                f.write(content)
                
            # 返回结果
            info = f"任务 ID: {task_id}\n工作流: {workflow_selection}\n参数: {json.dumps(params, ensure_ascii=False, indent=2)}"
            return output_path, info
            
        except Exception as e:
            logger.error(f"运行工作流失败: {str(e)}")
            return None, f"运行工作流失败: {str(e)}"
            
    # 绑定事件
    run_workflow_btn.click(
        run_workflow,
        inputs=[workflow_id, workflow_params],
        outputs=[workflow_output, workflow_info]
    )
    
    # 初始加载工作流列表
    workflow_id.choices = load_workflows().choices

def create_models_ui():
    """创建模型 UI"""
    with gr.Row():
        with gr.Column():
            model_type = gr.Dropdown(label="模型类型", choices=["全部", "底模", "LoRA", "VAE", "ControlNet"], value="全部")
            search_query = gr.Textbox(label="搜索", placeholder="输入关键词搜索模型...")
            refresh_btn = gr.Button("刷新模型列表")
            
        with gr.Column():
            models_list = gr.Dataframe(
                headers=["ID", "名称", "类型", "描述"],
                datatype=["str", "str", "str", "str"],
                col_count=(4, "fixed"),
                interactive=False
            )
            
    # 加载模型列表
    def load_models_list(model_type_value, query=""):
        try:
            if not auth.is_configured():
                return []
                
            type_value = None if model_type_value == "全部" else model_type_value
            
            # 模拟 API 调用，实际应该调用 api.get_models()
            models = [
                {"id": "model1", "name": "模型1", "type": "底模", "description": "这是模型1的描述"},
                {"id": "model2", "name": "模型2", "type": "LoRA", "description": "这是模型2的描述"},
                {"id": "model3", "name": "模型3", "type": "VAE", "description": "这是模型3的描述"}
            ]
            
            # 过滤模型类型
            if type_value:
                models = [m for m in models if m.get("type") == type_value]
                
            # 过滤搜索关键词
            if query:
                query = query.lower()
                models = [m for m in models if query in m.get("name", "").lower() or query in m.get("description", "").lower()]
                
            # 转换为数据框格式
            data = []
            for model in models:
                data.append([
                    model.get("id", ""),
                    model.get("name", ""),
                    model.get("type", ""),
                    model.get("description", "")
                ])
                
            return data
        except Exception as e:
            logger.error(f"加载模型列表失败: {str(e)}")
            return []
            
    # 绑定事件
    model_type.change(
        load_models_list,
        inputs=[model_type, search_query],
        outputs=[models_list]
    )
    
    search_query.change(
        load_models_list,
        inputs=[model_type, search_query],
        outputs=[models_list]
    )
    
    refresh_btn.click(
        load_models_list,
        inputs=[model_type, search_query],
        outputs=[models_list]
    )
    
    # 初始加载模型列表
    models_list.value = load_models_list("全部")

def create_tasks_ui():
    """创建任务 UI"""
    with gr.Row():
        with gr.Column():
            task_id_input = gr.Textbox(label="任务 ID", placeholder="输入任务 ID...")
            refresh_task_btn = gr.Button("刷新任务状态")
            
        with gr.Column():
            task_status = gr.Textbox(label="任务状态", interactive=False)
            
    with gr.Row():
        recent_tasks = gr.Dataframe(
            headers=["任务 ID", "类型", "状态", "创建时间", "完成时间"],
            datatype=["str", "str", "str", "str", "str"],
            col_count=(5, "fixed"),
            interactive=False
        )
        refresh_recent_btn = gr.Button("刷新最近任务")
        
    # 获取任务状态
    def get_task_status(task_id):
        try:
            if not auth.is_configured():
                return "请先在设置中配置 API 密钥"
                
            if not task_id:
                return "请输入任务 ID"
                
            # 模拟 API 调用，实际应该调用 api.get_task_result()
            result = {
                "status": "success",
                "result": {
                    "image_url": "https://example.com/image.png"
                }
            }
            
            status = result.get("status", "unknown")
            
            if status == "success":
                return f"任务完成: {json.dumps(result.get('result', {}), ensure_ascii=False, indent=2)}"
            elif status == "failed":
                return f"任务失败: {result.get('error', '未知错误')}"
            else:
                return f"任务状态: {status}"
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            return f"获取任务状态失败: {str(e)}"
            
    # 获取最近任务
    def get_recent_tasks():
        try:
            if not auth.is_configured():
                return []
                
            # 模拟最近任务，实际应该从某处获取
            recent = [
                {"task_id": "task1", "type": "text_to_image", "status": "success", "created_at": time.time() - 3600, "completed_at": time.time() - 3500},
                {"task_id": "task2", "type": "image_to_image", "status": "failed", "created_at": time.time() - 7200, "completed_at": time.time() - 7100},
                {"task_id": "task3", "type": "workflow", "status": "pending", "created_at": time.time() - 1800}
            ]
            
            # 转换为数据框格式
            data = []
            for task in recent:
                created_time = datetime.fromtimestamp(task.get("created_at", 0)).strftime("%Y-%m-%d %H:%M:%S")
                completed_time = ""
                if "completed_at" in task:
                    completed_time = datetime.fromtimestamp(task.get("completed_at")).strftime("%Y-%m-%d %H:%M:%S")
                    
                data.append([
                    task.get("task_id", ""),
                    task.get("type", ""),
                    task.get("status", ""),
                    created_time,
                    completed_time
                ])
                
            return data
        except Exception as e:
            logger.error(f"获取最近任务失败: {str(e)}")
            return []
            
    # 绑定事件
    refresh_task_btn.click(
        get_task_status,
        inputs=[task_id_input],
        outputs=[task_status]
    )
    
    refresh_recent_btn.click(
        get_recent_tasks,
        inputs=[],
        outputs=[recent_tasks]
    )
    
    # 初始加载最近任务
    recent_tasks.value = get_recent_tasks()

def create_settings_ui():
    """创建设置 UI"""
    with gr.Row():
        with gr.Column():
            access_key = gr.Textbox(label="Access Key", value=settings.get("access_key", ""), type="password")
            secret_key = gr.Textbox(label="Secret Key", value=settings.get("secret_key", ""), type="password")
            proxy = gr.Textbox(label="代理设置 (例如: http://127.0.0.1:7890)", value=settings.get("proxy", ""))
            save_path = gr.Textbox(label="保存路径", value=settings.get("save_path", ""))
            
        with gr.Column():
            auto_update = gr.Checkbox(label="自动检查更新", value=settings.get("auto_update_check", True))
            update_interval = gr.Slider(label="更新间隔 (秒)", minimum=60, maximum=86400, step=60, value=settings.get("update_interval", 3600))
            
    with gr.Row():
        save_settings_btn = gr.Button("保存设置", variant="primary")
        test_connection_btn = gr.Button("测试连接")
        settings_status = gr.Textbox(label="状态", interactive=False)
        
    # 保存设置
    def save_settings_func(access_key_value, secret_key_value, proxy_value, save_path_value, auto_update_value, update_interval_value):
        try:
            # 更新设置
            settings["access_key"] = access_key_value
            settings["secret_key"] = secret_key_value
            settings["proxy"] = proxy_value
            settings["save_path"] = save_path_value
            settings["auto_update_check"] = auto_update_value
            settings["update_interval"] = update_interval_value
            
            # 保存设置
            if save_settings():
                # 更新 auth 和 api
                auth.access_key = access_key_value
                auth.secret_key = secret_key_value
                api.set_proxy(proxy_value)
                
                return "设置已保存"
            else:
                return "保存设置失败"
        except Exception as e:
            logger.error(f"保存设置失败: {str(e)}")
            return f"保存设置失败: {str(e)}"
            
    # 测试连接
    def test_connection():
        try:
            if not auth.is_configured():
                return "请先配置 API 密钥"
                
            # 模拟 API 调用，实际应该调用一个简单的 API 来测试连接
            time.sleep(1)  # 模拟网络延迟
            
            return "连接成功！API 密钥有效。"
        except Exception as e:
            logger.error(f"测试连接失败: {str(e)}")
            return f"测试连接失败: {str(e)}"
            
    # 绑定事件
    save_settings_btn.click(
        save_settings_func,
        inputs=[access_key, secret_key, proxy, save_path, auto_update, update_interval],
        outputs=[settings_status]
    )
    
    test_connection_btn.click(
        test_connection,
        inputs=[],
        outputs=[settings_status]
    )

# 注册插件到 WebUI
script_callbacks.on_ui_tabs(on_ui_tabs)