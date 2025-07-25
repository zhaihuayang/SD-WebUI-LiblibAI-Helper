import os
import time
import uuid
import hmac
import hashlib
import base64
import json
from urllib.parse import quote

class LiblibAIAuth:
    """
    liblibAI 认证管理模块
    
    负责管理 API 认证相关功能，包括密钥管理和签名生成
    """
    
    def __init__(self, access_key=None, secret_key=None):
        """
        初始化认证管理器
        
        Args:
            access_key (str, optional): API 访问密钥. Defaults to None.
            secret_key (str, optional): API 密钥. Defaults to None.
        """
        self.access_key = access_key
        self.secret_key = secret_key
        
        # 如果未提供密钥，尝试从配置文件加载
        if not (self.access_key and self.secret_key):
            self._load_keys()
    
    def _load_keys(self):
        """
        从配置文件加载 API 密钥
        """
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "liblibai_helper.json"
        )
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.access_key = config.get('access_key', '')
                    self.secret_key = config.get('secret_key', '')
            except Exception as e:
                print(f"加载 API 密钥失败: {str(e)}")
        
    def save_keys(self, access_key, secret_key):
        """
        保存 API 密钥到配置文件
        
        Args:
            access_key (str): API 访问密钥
            secret_key (str): API 密钥
            
        Returns:
            bool: 是否保存成功
        """
        self.access_key = access_key
        self.secret_key = secret_key
        
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
            "liblibai_helper.json"
        )
        
        # 如果配置文件已存在，先读取现有配置
        config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        # 更新密钥
        config['access_key'] = access_key
        config['secret_key'] = secret_key
        
        # 保存配置
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存 API 密钥失败: {str(e)}")
            return False
        
    def generate_signature(self, params=None):
        """
        生成 API 请求签名
        
        Args:
            params (dict, optional): 请求参数. Defaults to None.
            
        Returns:
            dict: 包含签名的完整参数字典
            
        Raises:
            ValueError: 如果未配置 API 密钥
        """
        if not (self.access_key and self.secret_key):
            raise ValueError("未配置 API 密钥，请先设置 Access Key 和 Secret Key")
        
        # 生成时间戳和随机字符串
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        
        # 构建参数字典
        sign_params = {
            'AccessKey': self.access_key,
            'SignatureNonce': nonce,
            'Timestamp': timestamp
        }
        
        # 合并传入的参数
        if params:
            sign_params.update(params)
            
        # 按照参数名称排序
        sorted_params = sorted(sign_params.items(), key=lambda x: x[0])
        
        # 构建规范化请求字符串
        canonicalized_query_string = '&'.join(['%s=%s' % (k, quote(str(v), safe='')) for k, v in sorted_params])
        
        # 计算签名
        string_to_sign = canonicalized_query_string
        hmac_algorithm = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        )
        signature = base64.b64encode(hmac_algorithm.digest()).decode('utf-8')
        
        # 返回完整的参数字典，包含签名
        sign_params['Signature'] = signature
        return sign_params
        
    def is_configured(self):
        """
        检查是否已配置 API 密钥
        
        Returns:
            bool: 是否已配置 API 密钥
        """
        return bool(self.access_key and self.secret_key)
    
    def test_authentication(self):
        """
        测试认证是否有效
        
        Returns:
            tuple: (bool, str) 表示是否认证成功及消息
        """
        if not self.is_configured():
            return False, "未配置 API 密钥"
        
        try:
            # 这里可以调用一个简单的 API 来测试认证
            # 由于我们还没有实现 API 模块，这里只返回配置状态
            return True, "API 密钥已配置"
        except Exception as e:
            return False, f"认证测试失败: {str(e)}"