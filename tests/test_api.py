import os
import base64
import unittest
from unittest.mock import patch, mock_open, MagicMock, ANY
import sys
import json

# 添加父目录到 sys.path，以便导入 api 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.lh_lib.api import LiblibAIAPI, APIError
from scripts.lh_lib.auth import LiblibAIAuth

class TestLiblibAIAPI(unittest.TestCase):
    """
    测试 LiblibAIAPI 类
    """

    def setUp(self):
        """
        测试前的设置
        """
        # 创建 auth 的模拟对象
        self.mock_auth = MagicMock(spec=LiblibAIAuth)
        self.mock_auth.generate_signature.return_value = {
            'AccessKey': 'test_access_key',
            'SignatureNonce': 'test_nonce',
            'Timestamp': '1625097600',
            'Signature': 'test_signature'
        }
        
        # 创建 API 实例
        self.api = LiblibAIAPI(self.mock_auth)

    def test_init(self):
        """
        测试初始化
        """
        # 验证属性设置
        self.assertEqual(self.api.auth, self.mock_auth)
        self.assertEqual(self.api.base_url, "https://api.liblibai.com/api/v2")
        self.assertIsNotNone(self.api.session)
        self.assertIsNone(self.api.proxy)

    def test_set_proxy(self):
        """
        测试设置代理
        """
        # 设置代理
        proxy = "http://127.0.0.1:7890"
        self.api.set_proxy(proxy)
        
        # 验证代理设置
        self.assertEqual(self.api.proxy, proxy)
        self.assertEqual(self.api.session.proxies, {
            "http": proxy,
            "https": proxy
        })
        
        # 清除代理
        self.api.set_proxy(None)
        
        # 验证代理已清除
        self.assertIsNone(self.api.proxy)
        self.assertEqual(self.api.session.proxies, {})

    @patch('requests.Session.get')
    def test_request_get(self, mock_get):
        """
        测试 GET 请求
        """
        # 模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 调用请求方法
        endpoint = "test-endpoint"
        params = {"param1": "value1"}
        result = self.api._request("get", endpoint, params)
        
        # 验证 auth.generate_signature 被调用
        self.mock_auth.generate_signature.assert_called_once_with(params)
        
        # 验证 requests.get 被调用
        mock_get.assert_called_once_with(
            "https://api.liblibai.com/api/v2/test-endpoint",
            params=self.mock_auth.generate_signature.return_value,
            timeout=30
        )
        
        # 验证返回结果
        self.assertEqual(result, {"result": "success"})

    @patch('requests.Session.post')
    def test_request_post(self, mock_post):
        """
        测试 POST 请求
        """
        # 模拟响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # 调用请求方法
        endpoint = "test-endpoint"
        params = {"param1": "value1"}
        json_data = {"data1": "value1"}
        files = {"file1": "file_content"}
        result = self.api._request("post", endpoint, params, json_data, files)
        
        # 验证 auth.generate_signature 被调用
        self.mock_auth.generate_signature.assert_called_once_with(params)
        
        # 验证 requests.post 被调用
        mock_post.assert_called_once_with(
            "https://api.liblibai.com/api/v2/test-endpoint",
            params=self.mock_auth.generate_signature.return_value,
            json=json_data,
            files=files,
            timeout=30
        )
        
        # 验证返回结果
        self.assertEqual(result, {"result": "success"})

    @patch('requests.Session.get')
    def test_request_invalid_method(self, mock_get):
        """
        测试无效的请求方法
        """
        # 调用请求方法，使用无效的方法
        with self.assertRaises(ValueError):
            self.api._request("invalid", "test-endpoint")
        
        # 验证 requests.get 未被调用
        mock_get.assert_not_called()

    @patch('requests.Session.get')
    def test_request_exception(self, mock_get):
        """
        测试请求异常
        """
        # 模拟异常
        mock_get.side_effect = Exception("Request failed")
        
        # 调用请求方法
        with self.assertRaises(APIError):
            self.api._request("get", "test-endpoint")

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_text_to_image(self, mock_request):
        """
        测试文生图方法
        """
        # 模拟响应
        mock_request.return_value = {"task_id": "test_task_id"}
        
        # 调用文生图方法
        model_id = "test_model"
        prompt = "test prompt"
        negative_prompt = "test negative prompt"
        width = 512
        height = 512
        steps = 20
        cfg_scale = 7.0
        sampler = "euler_a"
        seed = 42
        
        result = self.api.text_to_image(
            model_id, prompt, negative_prompt, width, height,
            steps=steps, cfg_scale=cfg_scale, sampler=sampler, seed=seed
        )
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "post", "text-to-image",
            json_data={
                "model_id": model_id,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "sampler": sampler,
                "seed": seed
            }
        )
        
        # 验证返回结果
        self.assertEqual(result, {"task_id": "test_task_id"})

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    @patch('builtins.open', new_callable=mock_open, read_data=b'test_image_data')
    @patch('os.path.isfile')
    def test_image_to_image_with_file(self, mock_isfile, mock_file, mock_request):
        """
        测试图生图方法（使用文件路径）
        """
        # 模拟响应
        mock_request.return_value = {"task_id": "test_task_id"}
        
        # 模拟文件存在
        mock_isfile.return_value = True
        
        # 调用图生图方法
        model_id = "test_model"
        prompt = "test prompt"
        image = "test_image.png"
        negative_prompt = "test negative prompt"
        strength = 0.75
        steps = 20
        cfg_scale = 7.0
        sampler = "euler_a"
        seed = 42
        
        result = self.api.image_to_image(
            model_id, prompt, image, negative_prompt,
            strength=strength, steps=steps, cfg_scale=cfg_scale, sampler=sampler, seed=seed
        )
        
        # 验证文件读取
        mock_file.assert_called_once_with(image, 'rb')
        
        # 验证 _request 被调用
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        # 检查请求方法和端点
        self.assertEqual(args[0], "post")
        self.assertEqual(args[1], "image-to-image")
        
        # 检查 JSON 数据
        json_data = kwargs['json_data']
        self.assertEqual(json_data["model_id"], model_id)
        self.assertEqual(json_data["prompt"], prompt)
        self.assertEqual(json_data["negative_prompt"], negative_prompt)
        self.assertEqual(json_data["strength"], strength)
        self.assertEqual(json_data["steps"], steps)
        self.assertEqual(json_data["cfg_scale"], cfg_scale)
        self.assertEqual(json_data["sampler"], sampler)
        self.assertEqual(json_data["seed"], seed)
        
        # 检查图片数据（base64 编码）
        expected_image_b64 = base64.b64encode(b'test_image_data').decode('utf-8')
        self.assertEqual(json_data["image"], expected_image_b64)
        
        # 验证返回结果
        self.assertEqual(result, {"task_id": "test_task_id"})

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    @patch('os.path.isfile')
    def test_image_to_image_with_base64(self, mock_isfile, mock_request):
        """
        测试图生图方法（使用 base64 编码）
        """
        # 模拟响应
        mock_request.return_value = {"task_id": "test_task_id"}
        
        # 模拟文件不存在
        mock_isfile.return_value = False
        
        # 调用图生图方法
        model_id = "test_model"
        prompt = "test prompt"
        image = "base64_encoded_image_data"
        negative_prompt = "test negative prompt"
        
        result = self.api.image_to_image(model_id, prompt, image, negative_prompt)
        
        # 验证 _request 被调用
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        # 检查请求方法和端点
        self.assertEqual(args[0], "post")
        self.assertEqual(args[1], "image-to-image")
        
        # 检查 JSON 数据
        json_data = kwargs['json_data']
        self.assertEqual(json_data["model_id"], model_id)
        self.assertEqual(json_data["prompt"], prompt)
        self.assertEqual(json_data["negative_prompt"], negative_prompt)
        self.assertEqual(json_data["image"], image)
        
        # 验证返回结果
        self.assertEqual(result, {"task_id": "test_task_id"})

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_get_task_result(self, mock_request):
        """
        测试获取任务结果方法
        """
        # 模拟响应
        mock_request.return_value = {
            "status": "success",
            "result": {
                "image_url": "https://example.com/image.png"
            }
        }
        
        # 调用获取任务结果方法
        task_id = "test_task_id"
        result = self.api.get_task_result(task_id)
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "get", "task-result",
            params={"task_id": task_id}
        )
        
        # 验证返回结果
        self.assertEqual(result, {
            "status": "success",
            "result": {
                "image_url": "https://example.com/image.png"
            }
        })

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_get_models(self, mock_request):
        """
        测试获取模型列表方法
        """
        # 模拟响应
        mock_request.return_value = {
            "models": [
                {"id": "model1", "name": "Model 1"},
                {"id": "model2", "name": "Model 2"}
            ]
        }
        
        # 调用获取模型列表方法（无类型）
        result = self.api.get_models()
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "get", "models",
            params={}
        )
        
        # 验证返回结果
        self.assertEqual(result, {
            "models": [
                {"id": "model1", "name": "Model 1"},
                {"id": "model2", "name": "Model 2"}
            ]
        })
        
        # 重置 mock
        mock_request.reset_mock()
        
        # 调用获取模型列表方法（指定类型）
        model_type = "lora"
        result = self.api.get_models(model_type)
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "get", "models",
            params={"type": model_type}
        )

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_get_workflow_templates(self, mock_request):
        """
        测试获取工作流模板列表方法
        """
        # 模拟响应
        mock_request.return_value = {
            "templates": [
                {"id": "template1", "name": "Template 1"},
                {"id": "template2", "name": "Template 2"}
            ]
        }
        
        # 调用获取工作流模板列表方法
        result = self.api.get_workflow_templates()
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "get", "workflow-templates"
        )
        
        # 验证返回结果
        self.assertEqual(result, {
            "templates": [
                {"id": "template1", "name": "Template 1"},
                {"id": "template2", "name": "Template 2"}
            ]
        })

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_run_workflow(self, mock_request):
        """
        测试运行工作流方法
        """
        # 模拟响应
        mock_request.return_value = {"task_id": "test_task_id"}
        
        # 调用运行工作流方法（无参数）
        workflow_id = "test_workflow"
        result = self.api.run_workflow(workflow_id)
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "post", "run-workflow",
            json_data={"workflow_id": workflow_id}
        )
        
        # 验证返回结果
        self.assertEqual(result, {"task_id": "test_task_id"})
        
        # 重置 mock
        mock_request.reset_mock()
        
        # 调用运行工作流方法（有参数）
        params = {"param1": "value1", "param2": "value2"}
        result = self.api.run_workflow(workflow_id, params)
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "post", "run-workflow",
            json_data={"workflow_id": workflow_id, "params": params}
        )

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_get_model_presets(self, mock_request):
        """
        测试获取模型预设方法
        """
        # 模拟响应
        mock_request.return_value = {
            "presets": [
                {"id": "preset1", "name": "Preset 1"},
                {"id": "preset2", "name": "Preset 2"}
            ]
        }
        
        # 调用获取模型预设方法
        model_id = "test_model"
        result = self.api.get_model_presets(model_id)
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "get", "model-presets",
            params={"model_id": model_id}
        )
        
        # 验证返回结果
        self.assertEqual(result, {
            "presets": [
                {"id": "preset1", "name": "Preset 1"},
                {"id": "preset2", "name": "Preset 2"}
            ]
        })

    @patch('scripts.lh_lib.api.LiblibAIAPI._request')
    def test_star3_alpha(self, mock_request):
        """
        测试星流 Star-3 Alpha 方法
        """
        # 模拟响应
        mock_request.return_value = {"task_id": "test_task_id"}
        
        # 调用星流 Star-3 Alpha 方法
        prompt = "test prompt"
        negative_prompt = "test negative prompt"
        width = 512
        height = 512
        steps = 20
        cfg_scale = 7.0
        seed = 42
        
        result = self.api.star3_alpha(
            prompt, negative_prompt,
            width=width, height=height, steps=steps, cfg_scale=cfg_scale, seed=seed
        )
        
        # 验证 _request 被调用
        mock_request.assert_called_once_with(
            "post", "star3-alpha",
            json_data={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "seed": seed
            }
        )
        
        # 验证返回结果
        self.assertEqual(result, {"task_id": "test_task_id"})

if __name__ == '__main__':
    unittest.main()