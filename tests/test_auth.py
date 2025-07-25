import os
import json
import unittest
from unittest.mock import patch, mock_open, MagicMock
import sys
import time
import uuid
import hmac
import hashlib
import base64
from urllib.parse import quote

# 添加父目录到 sys.path，以便导入 auth 模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.lh_lib.auth import LiblibAIAuth

class TestLiblibAIAuth(unittest.TestCase):
    """
    测试 LiblibAIAuth 类
    """

    def setUp(self):
        """
        测试前的设置
        """
        # 使用固定的密钥进行测试
        self.access_key = "test_access_key"
        self.secret_key = "test_secret_key"
        
        # 创建一个带有测试密钥的 auth 实例
        self.auth = LiblibAIAuth(self.access_key, self.secret_key)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_init_with_no_keys(self, mock_file, mock_exists):
        """
        测试不提供密钥时的初始化
        """
        # 模拟配置文件存在
        mock_exists.return_value = True
        
        # 模拟配置文件内容
        mock_file.return_value.read.return_value = json.dumps({
            'access_key': 'config_access_key',
            'secret_key': 'config_secret_key'
        })
        
        # 创建一个不带密钥的 auth 实例
        auth = LiblibAIAuth()
        
        # 验证是否从配置文件加载了密钥
        self.assertEqual(auth.access_key, 'config_access_key')
        self.assertEqual(auth.secret_key, 'config_secret_key')
        
        # 验证是否调用了正确的文件路径
        mock_exists.assert_called_once()
        mock_file.assert_called_once()

    @patch('os.path.exists')
    def test_init_with_no_config_file(self, mock_exists):
        """
        测试配置文件不存在时的初始化
        """
        # 模拟配置文件不存在
        mock_exists.return_value = False
        
        # 创建一个不带密钥的 auth 实例
        auth = LiblibAIAuth()
        
        # 验证密钥为空
        self.assertEqual(auth.access_key, None)
        self.assertEqual(auth.secret_key, None)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_init_with_invalid_config_file(self, mock_file, mock_exists):
        """
        测试配置文件无效时的初始化
        """
        # 模拟配置文件存在
        mock_exists.return_value = True
        
        # 模拟配置文件读取异常
        mock_file.return_value.read.side_effect = Exception("Invalid JSON")
        
        # 创建一个不带密钥的 auth 实例
        auth = LiblibAIAuth()
        
        # 验证密钥为空
        self.assertEqual(auth.access_key, None)
        self.assertEqual(auth.secret_key, None)

    def test_init_with_keys(self):
        """
        测试提供密钥时的初始化
        """
        # 验证密钥正确设置
        self.assertEqual(self.auth.access_key, self.access_key)
        self.assertEqual(self.auth.secret_key, self.secret_key)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_keys(self, mock_file, mock_exists):
        """
        测试保存密钥
        """
        # 模拟配置文件不存在
        mock_exists.return_value = False
        
        # 调用保存密钥方法
        result = self.auth.save_keys("new_access_key", "new_secret_key")
        
        # 验证返回值
        self.assertTrue(result)
        
        # 验证密钥已更新
        self.assertEqual(self.auth.access_key, "new_access_key")
        self.assertEqual(self.auth.secret_key, "new_secret_key")
        
        # 验证文件写入
        mock_file.assert_called_once()
        mock_file.return_value.write.assert_called_once()
        
        # 获取写入的内容
        written_content = mock_file.return_value.write.call_args[0][0]
        config = json.loads(written_content)
        
        # 验证写入的内容
        self.assertEqual(config['access_key'], "new_access_key")
        self.assertEqual(config['secret_key'], "new_secret_key")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_keys_with_existing_config(self, mock_file, mock_exists):
        """
        测试保存密钥到现有配置文件
        """
        # 模拟配置文件存在
        mock_exists.return_value = True
        
        # 模拟配置文件内容
        mock_file.return_value.read.return_value = json.dumps({
            'access_key': 'old_access_key',
            'secret_key': 'old_secret_key',
            'other_setting': 'value'
        })
        
        # 调用保存密钥方法
        result = self.auth.save_keys("new_access_key", "new_secret_key")
        
        # 验证返回值
        self.assertTrue(result)
        
        # 验证密钥已更新
        self.assertEqual(self.auth.access_key, "new_access_key")
        self.assertEqual(self.auth.secret_key, "new_secret_key")
        
        # 验证文件读写
        self.assertEqual(mock_file.call_count, 2)  # 一次读，一次写
        mock_file.return_value.write.assert_called_once()
        
        # 获取写入的内容
        written_content = mock_file.return_value.write.call_args[0][0]
        config = json.loads(written_content)
        
        # 验证写入的内容
        self.assertEqual(config['access_key'], "new_access_key")
        self.assertEqual(config['secret_key'], "new_secret_key")
        self.assertEqual(config['other_setting'], "value")  # 保留其他设置

    @patch('builtins.open')
    def test_save_keys_with_exception(self, mock_file):
        """
        测试保存密钥时发生异常
        """
        # 模拟文件写入异常
        mock_file.side_effect = Exception("Write error")
        
        # 调用保存密钥方法
        result = self.auth.save_keys("new_access_key", "new_secret_key")
        
        # 验证返回值
        self.assertFalse(result)
        
        # 验证密钥已更新（即使保存失败）
        self.assertEqual(self.auth.access_key, "new_access_key")
        self.assertEqual(self.auth.secret_key, "new_secret_key")

    @patch('time.time')
    @patch('uuid.uuid4')
    def test_generate_signature(self, mock_uuid, mock_time):
        """
        测试生成签名
        """
        # 模拟时间和 UUID
        mock_time.return_value = 1625097600  # 2021-07-01 00:00:00 UTC
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__.return_value = "12345678-1234-5678-1234-567812345678"
        
        # 调用生成签名方法
        params = self.auth.generate_signature()
        
        # 验证基本参数
        self.assertEqual(params['AccessKey'], self.access_key)
        self.assertEqual(params['SignatureNonce'], "12345678-1234-5678-1234-567812345678")
        self.assertEqual(params['Timestamp'], "1625097600")
        
        # 验证签名存在
        self.assertIn('Signature', params)
        
        # 验证签名计算
        # 构建规范化请求字符串
        sorted_params = sorted({
            'AccessKey': self.access_key,
            'SignatureNonce': "12345678-1234-5678-1234-567812345678",
            'Timestamp': "1625097600"
        }.items(), key=lambda x: x[0])
        
        canonicalized_query_string = '&'.join(['%s=%s' % (k, quote(str(v), safe='')) for k, v in sorted_params])
        
        # 计算签名
        string_to_sign = canonicalized_query_string
        hmac_algorithm = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        expected_signature = base64.b64encode(hmac_algorithm.digest()).decode('utf-8')
        
        # 验证签名
        self.assertEqual(params['Signature'], expected_signature)

    @patch('time.time')
    @patch('uuid.uuid4')
    def test_generate_signature_with_params(self, mock_uuid, mock_time):
        """
        测试使用额外参数生成签名
        """
        # 模拟时间和 UUID
        mock_time.return_value = 1625097600  # 2021-07-01 00:00:00 UTC
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__.return_value = "12345678-1234-5678-1234-567812345678"
        
        # 额外参数
        extra_params = {
            'param1': 'value1',
            'param2': 'value2'
        }
        
        # 调用生成签名方法
        params = self.auth.generate_signature(extra_params)
        
        # 验证基本参数
        self.assertEqual(params['AccessKey'], self.access_key)
        self.assertEqual(params['SignatureNonce'], "12345678-1234-5678-1234-567812345678")
        self.assertEqual(params['Timestamp'], "1625097600")
        
        # 验证额外参数
        self.assertEqual(params['param1'], 'value1')
        self.assertEqual(params['param2'], 'value2')
        
        # 验证签名存在
        self.assertIn('Signature', params)
        
        # 验证签名计算
        # 构建规范化请求字符串
        sorted_params = sorted({
            'AccessKey': self.access_key,
            'SignatureNonce': "12345678-1234-5678-1234-567812345678",
            'Timestamp': "1625097600",
            'param1': 'value1',
            'param2': 'value2'
        }.items(), key=lambda x: x[0])
        
        canonicalized_query_string = '&'.join(['%s=%s' % (k, quote(str(v), safe='')) for k, v in sorted_params])
        
        # 计算签名
        string_to_sign = canonicalized_query_string
        hmac_algorithm = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        expected_signature = base64.b64encode(hmac_algorithm.digest()).decode('utf-8')
        
        # 验证签名
        self.assertEqual(params['Signature'], expected_signature)

    def test_generate_signature_with_no_keys(self):
        """
        测试在没有密钥的情况下生成签名
        """
        # 创建一个没有密钥的 auth 实例
        auth = LiblibAIAuth(None, None)
        
        # 验证生成签名时抛出异常
        with self.assertRaises(ValueError):
            auth.generate_signature()

    def test_is_configured(self):
        """
        测试配置状态检查
        """
        # 创建一个带有测试密钥的 auth 实例
        auth = LiblibAIAuth(self.access_key, self.secret_key)
        
        # 验证配置状态
        self.assertTrue(auth.is_configured())
        
        # 创建一个没有密钥的 auth 实例
        auth = LiblibAIAuth(None, None)
        
        # 验证配置状态
        self.assertFalse(auth.is_configured())
        
        # 创建一个只有 access_key 的 auth 实例
        auth = LiblibAIAuth(self.access_key, None)
        
        # 验证配置状态
        self.assertFalse(auth.is_configured())
        
        # 创建一个只有 secret_key 的 auth 实例
        auth = LiblibAIAuth(None, self.secret_key)
        
        # 验证配置状态
        self.assertFalse(auth.is_configured())

    def test_test_authentication(self):
        """
        测试认证测试方法
        """
        # 测试配置了密钥的情况
        success, message = self.auth.test_authentication()
        
        # 验证返回值
        self.assertTrue(success)
        self.assertEqual(message, "API 密钥已配置")
        
        # 创建一个没有密钥的 auth 实例
        auth = LiblibAIAuth(None, None)
        
        # 测试未配置密钥的情况
        success, message = auth.test_authentication()
        
        # 验证返回值
        self.assertFalse(success)
        self.assertEqual(message, "未配置 API 密钥")

if __name__ == '__main__':
    unittest.main()