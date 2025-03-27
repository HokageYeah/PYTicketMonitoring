from fastapi_mail import FastMail
import logging
from typing import Dict, Any
from src.server.schemas import PlatformEnum
from fastapi_mail import MessageSchema
from fastapi import Depends
from src.server.core.confing import Settings, get_settings, get_mail_config
from fastapi_mail import ConnectionConfig
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
import asyncio
class EmailSender:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings
        print(f"EmailSender init settings: {self.settings}")
        self.mail_config = get_mail_config(settings)
        print(f"EmailSender init mail_config: {self.mail_config}")
        self.fast_mail = FastMail(self.mail_config)
        self.logger = logging.getLogger("email_service")
    async def send_three_party_api_error_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送第三方接口调用错误邮件
        
        参数:
            params: 错误参数
        
        返回:
            发送结果
        """
        print('send_three_party_api_error_email------params------', params)
        try:
            platform = params.get("error_platform")
            if platform == PlatformEnum.DM.value:
                subject = "大麦接口调用错误"
            elif platform == PlatformEnum.MY.value:
                subject = "猫眼接口调用错误"
            elif platform == WxPlatformEnum.WX_MINI.value:
                subject = "微信小程序接口调用错误"
            else:
                subject = "第三方接口调用错误"
            html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
                <h1 style="color: #333; font-size: 24px; margin-bottom: 20px;">{subject}</h1>
                <p>错误信息: {params.get("error_msg")}</p>
                <p>错误时间: {params.get("error_time")}</p>
                <p>错误平台: {params.get("error_platform")}</p>
                <p>错误接口: {params.get("error_api")}</p>
                <p>错误代码: {params.get("error_code","无")}</p>
                <p>执行时间: {params.get("execution_time","无")}</p>
                <p style="margin-top: 30px; font-size: 12px; color: #666;">此邮件由系统自动发送，请勿回复。</p>
            </div>
            """
            message = MessageSchema(
                subject=subject,
                body=html,
                recipients=[self.settings.QQ_MAIL_TO],
                subtype="html"
            )
            try:
                # 设置超时
                print('send_three_party_api_error_email------message------1')
                await asyncio.wait_for(self.fast_mail.send_message(message), timeout=15)
                print("send_three_party_api_error_email------message------2")
                return {"status": "success", "message": "邮件发送成功"}
            except asyncio.TimeoutError:
                print("send_three_party_api_error_email------message------3")
                print("send_three_party_api_error_email------邮件发送超时")
                return {"status": "error", "message": "邮件发送超时，请检查邮件服务器配置"}
        except Exception as e:
            print("send_three_party_api_error_email------message------4")
            print(f"send_three_party_api_error_email------发送邮件失败: {str(e)}")
            logging.error(f"发送第三方API错误邮件失败: {str(e)}")
            return {"status": "error", "message": str(e)}