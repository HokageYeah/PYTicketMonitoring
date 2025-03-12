from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum

class CustomServiceException(Exception):
    """自定义服务异常基类"""
    def __init__(self, message, platform="unknown", api="unknown", data=None):
        self.message = message
        self.platform = platform
        self.api = api
        self.data = data or {}
        super().__init__(self.message)
        
    def to_response(self):
        """转换为标准响应格式"""
        return {
            'platform': self.platform,
            'ret': [f"ERROR::{self.message}"],
            'data': self.data,
            'v': 1,
            'api': self.api
        }


class SaveSubscribeTemplateException(CustomServiceException):
    """订阅消息模板存储异常"""
    def __init__(self, openid, platform=WxPlatformEnum.WX_MINI.value, api="/wx/mini.save.subscribe.template"):
        message = f"订阅消息模板存储异常 (openid: {openid})"
        super().__init__(message, platform, api)

class SendSubscribeMsgUserException(CustomServiceException):
    """订阅消息模板获取异常"""
    def __init__(self, openid, platform=WxPlatformEnum.WX_MINI.value, api="/wx/mini.send.subscribe.message"):
        message = f"未找到用户订阅消息模板"
        super().__init__(message, platform, api)