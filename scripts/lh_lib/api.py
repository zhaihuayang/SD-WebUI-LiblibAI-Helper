import os
import base64
import requests
from urllib.parse import urljoin

class APIError(Exception):
    """API 请求错误"""
    pass

class LiblibAIAPI:
    """
    liblibAI API 通信模块
    
    封装与 liblibAI API 的所有通信功能，提供统一的接口
    """
    
    def __init__(self, auth):
        """
        初始化 API 通信模块
        
        Args:
            auth (LiblibAIAuth): 认证管理器实例
        """
        self.auth = auth
        self.base_url = "https://api.liblibai.com/api/v2"
        self.session = requests.Session()
        self.proxy = None
        
    def set_proxy(self, proxy):
        """
        设置代理
        
        Args:
            proxy (str): 代理地址，例如 http://127.0.0.1:7890
        """
        self.proxy = proxy
        if proxy:
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }
        else:
            self.session.proxies = {}
            
    def _request(self, method, endpoint, params=None, json_data=None, files=None):
        """
        发送 API 请求
        
        Args:
            method (str): 请求方法，'get' 或 'post'
            endpoint (str): API 端点
            params (dict, optional): 查询参数. Defaults to None.
            json_data (dict, optional): JSON 数据. Defaults to None.
            files (dict, optional): 文件数据. Defaults to None.
            
        Returns:
            dict: API 响应
            
        Raises:
            APIError: 如果 API 请求失败
        """
        url = urljoin(self.base_url, endpoint)
        
        # 生成签名参数
        auth_params = self.auth.generate_signature(params)
        
        # 发送请求
        try:
            if method.lower() == 'get':
                response = self.session.get(url, params=auth_params, timeout=30)
            elif method.lower() == 'post':
                response = self.session.post(url, params=auth_params, json=json_data, files=files, timeout=30)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            raise APIError(f"API 请求失败: {str(e)}")
            
    def text_to_image(self, model_id, prompt, negative_prompt="", width=512, height=512, **kwargs):
        """
        文生图 API
        
        Args:
            model_id (str): 模型 ID
            prompt (str): 提示词
            negative_prompt (str, optional): 负面提示词. Defaults to "".
            width (int, optional): 图像宽度. Defaults to 512.
            height (int, optional): 图像高度. Defaults to 512.
            **kwargs: 其他参数
                - steps (int): 步数
                - cfg_scale (float): CFG Scale
                - sampler (str): 采样器
                - seed (int): 种子
                
        Returns:
            dict: API 响应
        """
        endpoint = "text-to-image"
        json_data = {
            "model_id": model_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            **kwargs
        }
        return self._request('post', endpoint, json_data=json_data)
        
    def image_to_image(self, model_id, prompt, image, negative_prompt="", **kwargs):
        """
        图生图 API
        
        Args:
            model_id (str): 模型 ID
            prompt (str): 提示词
            image (str): 图像路径或 base64 编码的图像
            negative_prompt (str, optional): 负面提示词. Defaults to "".
            **kwargs: 其他参数
                - strength (float): 图像变化强度
                - steps (int): 步数
                - cfg_scale (float): CFG Scale
                - sampler (str): 采样器
                - seed (int): 种子
                
        Returns:
            dict: API 响应
        """
        endpoint = "image-to-image"
        
        # 处理图片文件
        if isinstance(image, str) and os.path.isfile(image):
            with open(image, 'rb') as f:
                image_data = f.read()
                image_b64 = base64.b64encode(image_data).decode('utf-8')
        else:
            # 假设 image 已经是 base64 编码的字符串
            image_b64 = image
            
        json_data = {
            "model_id": model_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image": image_b64,
            **kwargs
        }
        return self._request('post', endpoint, json_data=json_data)
        
    def get_task_result(self, task_id):
        """
        获取任务结果
        
        Args:
            task_id (str): 任务 ID
            
        Returns:
            dict: API 响应
        """
        endpoint = "task-result"
        params = {"task_id": task_id}
        return self._request('get', endpoint, params=params)
        
    def get_models(self, model_type=None):
        """
        获取模型列表
        
        Args:
            model_type (str, optional): 模型类型. Defaults to None.
                可选值: "base", "lora", "vae", "controlnet" 等
                
        Returns:
            dict: API 响应
        """
        endpoint = "models"
        params = {}
        if model_type:
            params["type"] = model_type
        return self._request('get', endpoint, params=params)
        
    def get_workflow_templates(self):
        """
        获取工作流模板列表
        
        Returns:
            dict: API 响应
        """
        endpoint = "workflow-templates"
        return self._request('get', endpoint)
        
    def run_workflow(self, workflow_id, params=None):
        """
        运行工作流
        
        Args:
            workflow_id (str): 工作流 ID
            params (dict, optional): 工作流参数. Defaults to None.
                
        Returns:
            dict: API 响应
        """
        endpoint = "run-workflow"
        json_data = {
            "workflow_id": workflow_id
        }
        if params:
            json_data["params"] = params
        return self._request('post', endpoint, json_data=json_data)
        
    def get_model_presets(self, model_id):
        """
        获取模型预设
        
        Args:
            model_id (str): 模型 ID
                
        Returns:
            dict: API 响应
        """
        endpoint = "model-presets"
        params = {"model_id": model_id}
        return self._request('get', endpoint, params=params)
        
    def star3_alpha(self, prompt, negative_prompt="", **kwargs):
        """
        使用星流 Star-3 Alpha
        
        Args:
            prompt (str): 提示词
            negative_prompt (str, optional): 负面提示词. Defaults to "".
            **kwargs: 其他参数
                - width (int): 图像宽度
                - height (int): 图像高度
                - steps (int): 步数
                - cfg_scale (float): CFG Scale
                - seed (int): 种子
                
        Returns:
            dict: API 响应
        """
        endpoint = "star3-alpha"
        json_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            **kwargs
        }
        return self._request('post', endpoint, json_data=json_data)