import requests
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
from src.sql.models.user import User
from src.server.services.userService import UserService
import time
from src.decorators.Res_Handler_Decorator import wx_mini_response_handler
from src.server.untiles.Email_Sender import EmailSender
from src.server.core.confing import settings
import asyncio
import logging
import httpx
user_service = UserService()

class WxService:
    def __init__(self):
        self.BASE_URL = "https://api.weixin.qq.com"
        self.data = {
            "appid": "wxcce30ba44a2065a5",
            "secret": "c49f74d704577e5842e84ab43ff3333d",
        }
        # 初始化数据
        self.access_token = ''
        self.expires_in = 0
        self.expires_time = time.time() + self.expires_in
        # 调用access_token 记录次数，超过三次返回错误
        self.access_token_count = 0
        # 初始化邮件服务
        self.email_service = EmailSender(settings)
    # 小程序登录
    @wx_mini_response_handler(api_path='/wx/mini.login.by.code', success_msg='微信登录成功', error_msg='微信登录调用失败')
    def wx_mini_login_code2Session(self, code):
        url = f"{self.BASE_URL}/sns/jscode2session"
        params = {
            **self.data,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        print('WxService---wx_mini_login_code2Session---params-----', params)
        response = requests.get(url, params=params)
        login_data = response.json()
        print('WxService---wx_mini_login_code2Session---response-----', login_data)
        session_key = login_data['session_key']
        openid = login_data['openid']
        # 判断是否是管理员
        if openid == settings.ADMIN_OPENID:
            user_role = 2
        else:
            user_role = 1
        user = User(session_key=session_key, openid=openid, user_role=user_role)
        user = user_service.create_user(user)
        tokenStr = user_service.generate_token(user).get('data',{})
        return {
                'token': "Bearer " + tokenStr,
                'user_id': user.user_id,
                # 'openid': user.openid,
                'username': user.username,
                # 'password': user.password,
                'status': user.status,
                'create_time': user.create_time,
                'update_time': user.update_time,
                'user_role': user.user_role,
            }
    # 检查access_token是否过期
    def is_access_token_expired(self):
        return time.time() >= self.expires_time
    # 微信发送订阅消息
    @wx_mini_response_handler(api_path='/wx/mini.send.subscribe.message', success_msg='微信发送订阅消息成功', error_msg='微信发送订阅消息调用失败')
    async def wx_mini_send_subscribe_message(self, params: dict, template_business_code: str):
        # 调用access_token 记录次数，超过三次返回错误
        print('WxService---wx_mini_send_subscribe_message---params-----1')
        self.access_token_count += 1
        print('WxService---wx_mini_send_subscribe_message---params-----2', self.access_token_count)
        if self.access_token_count > 3:
            self.access_token_count = 0
            return {
                'ret': ["ERROR::获取access_token超过最大次数"],
            }
        if self.is_access_token_expired():
            print('WxService---wx_mini_send_subscribe_message---access_token过期-----')
            # 异步
            await self.wx_mini_get_access_token()
            print('WxService---wx_mini_send_subscribe_message---access_token过期-----1')
            # 更新access_token后，重新调用
            return await self.wx_mini_send_subscribe_message(params, template_business_code)
        else:
            print('WxService---wx_mini_send_subscribe_message---access_token未过期-----')
            # 调用发送订阅消息
            self.access_token_count = 0
            url = f"{self.BASE_URL}/cgi-bin/message/subscribe/send?access_token={self.access_token}"
            template_info = user_service.get_user_subscribe_template(params.get('touser', ''), template_business_code).get('data',{})
            print('template_info---------', template_info)
            req_params = {
                **params,
                "template_id": template_info['template_id'],
                "page": template_info['page'],
            }
            print('WxService---wx_mini_send_subscribe_message---req_params-----', req_params)
            response = requests.post(url, json=req_params)
            res_data = response.json()
            if 'errcode' in res_data and res_data.get('errcode') != 0:
                print('WxService---wx_mini_send_subscribe_message---response-----', res_data)
                errcode = res_data.get('errcode')
                errmsg = res_data.get('errmsg')
                print('wx_notice---get_access_token---api---------', errcode, errmsg)
                return {
                    'ret': ["ERROR::"+errmsg, "ERRORCODE::"+str(errcode)],
                }
            else:
                print('WxService---wx_mini_send_subscribe_message---response-----', response)
                return response.json()
    # 微信订阅消息模板存储
    @wx_mini_response_handler(api_path='/wx/mini.save.subscribe.template', success_msg='订阅消息模板存储成功', error_msg='订阅消息模板存储调用失败')
    def wx_mini_save_subscribe_template(self, params, user):
        res = user_service.save_user_subscribe_template(params, user).get('data',{})
        return res
    # 获取access_token
    # @wx_mini_response_handler(api_path='/wx/mini.get.access.token', success_msg='获取access_token成功', error_msg='获取access_token调用失败')
    # @wx_api_error_decorator(platform=WxPlatformEnum.WX_MINI.value, api_path='https://api.weixin.qq.com/cgi-bin/token', error_msg='获取access_token调用失败')
    @wx_mini_response_handler(api_path='https://api.weixin.qq.com/cgi-bin/token', error_msg='获取access_token调用失败', error_email=True)
    async def wx_mini_get_access_token(self):
        url = f"{self.BASE_URL}/cgi-bin/token"
        params = {
            **self.data,
            "grant_type": "client_credential"
        }
        print('WxService---wx_mini_get_access_token---api---------1')
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params) 
            print('WxService---wx_mini_get_access_token---api---------2')
            access_token_data = response.json() 
            print('WxService---wx_mini_get_access_token---api---------3', access_token_data)
            # 测试
            # access_token_data = {
            #     'errcode': 40001,
            #     'errmsg': 'invalid code',
            # }

        # self.expires_in = 0
        # 判断小程序接口请求是否报错
        if 'errcode' in access_token_data and access_token_data.get('errcode') != 0:
            errcode = access_token_data.get('errcode')
            errmsg = access_token_data.get('errmsg')
            print('WxService---wx_mini_get_access_token---api---------4', errcode, errmsg)
            return {
                'ret': ["ERROR::"+errmsg, "ERRORCODE::"+str(errcode)],
            }
        self.access_token = access_token_data.get('access_token')  
        self.expires_in = access_token_data.get('expires_in')
        print('WxService---wx_mini_get_access_token---api---------5', response.json())
        self.expires_time = time.time() + self.expires_in
        print('WxService---wx_mini_get_access_token---api---------6', self.expires_time)
        # self.expires_time = time.time() + self.expires_in
        return access_token_data

    # @wx_mini_response_handler(api_path='/wx/mini.get.access.token', success_msg='获取access_token成功', error_msg='获取access_token调用失败')
    # @wx_api_error_decorator(platform=WxPlatformEnum.WX_MINI.value, 
    #                    api_path='https://api.weixin.qq.com/cgi-bin/token', 
    #                    error_msg='获取access_token调用失败')
    # async def wx_mini_get_access_token(self):
    #     url = f"{self.BASE_URL}/cgi-bin/token"
    #     params = {
    #         **self.data,
    #         "grant_type": "client_credential"
    #     }
    #     # 使用异步HTTP客户端（如aiohttp）
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(url, params=params)
    #         access_token_data = response.json()
        
    #     self.access_token = access_token_data.get('access_token')  
    #     self.expires_in = access_token_data.get('expires_in')
    #     self.expires_time = time.time() + self.expires_in
    #     return {'errcode': 40001, 'errmsg': 'invalid code'}  # 测试用错误

    
    # 发送邮件
    # def api_error_send_email(self, params):
    #     # 创建异步任务发送邮件
    #     async def send_email_async():
    #         await self.email_service.send_three_party_api_error_email(
    #             params
    #         )
    #     # 在非异步环境中运行异步函数
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     loop.run_until_complete(send_email_async())
    #     loop.close()
    #     logging.info(f"已发送邮件通知到 {self.email_settings.QQ_MAIL_FROM}")
    #     return '邮件发送成功'
    #     # loop = asyncio.new_event_loop()
    #     # asyncio.set_event_loop(loop)
    #     # result = loop.run_until_complete(self.email_service.send_three_party_api_error_email(params))
    #     # loop.close()
    #     # logging.info(f"已发送邮件通知到 {settings.QQ_MAIL_FROM}")
    #     # return result

    # 在 WxService 类中添加或修改 api_error_send_email 方法
    # def api_error_send_email(self, params):
    #     """
    #     同步版本的API错误邮件发送方法
        
    #     参数:
    #         params: 错误参数
        
    #     返回:
    #         发送结果
    #     """
    #     try:
    #         # 获取当前事件循环
    #         testloop = asyncio.get_event_loop()
    #         print('testloop---------', testloop.is_running())
    #         # 创建事件循环来运行异步函数
    #         loop = asyncio.new_event_loop()
    #         asyncio.set_event_loop(loop)
    #         try:
    #             # 运行异步函数并获取结果
    #             # 设置整体超时时间为20秒
    #             result = loop.run_until_complete(
    #                 asyncio.wait_for(
    #                     self.email_service.send_three_party_api_error_email(params),
    #                     timeout=20
    #                 )
    #             )
    #             print(f"WxService api_error_send_email result: {result}")
    #             return result
    #         finally:
    #             # 确保关闭事件循环
    #             print(f"WxService api_error_send_email loop: {loop}")
    #             loop.close()
    #     except Exception as e:
    #         logging.error(f"api_error_send_email 执行失败: {str(e)}")
    #         return {"status": "error", "message": str(e)}


    # 在 WxService 类中修改 api_error_send_email 方法
    def api_error_send_email(self, params):
        """
        同步版本的API错误邮件发送方法
        
        参数:
            params: 错误参数
        
        返回:
            发送结果
        """
        try:
            # 获取当前事件循环
            try:
                loop = asyncio.get_event_loop()
                print(f"WxService api_error_send_email loop: {loop}")
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                print(f"WxService api_error_send_email created new loop: {loop}")
            # 检查事件循环是否正在运行
            if loop.is_running():
                # 如果事件循环正在运行，我们不能再运行一个事件循环
                # 在这种情况下，我们可以选择跳过发送邮件或使用其他方式
                print(f"事件循环正在运行，使用当前事件循环")
                # 如果事件循环正在运行，创建后台任务
                asyncio.create_task(self.email_service.send_three_party_api_error_email(params))
                logging.info(f"事件循环正在运行，发送邮件通知到 {settings.QQ_MAIL_FROM}")
                return '事件循环正在运行，发送邮件成功'
            else:
                try:
                    # 如果事件循环没有运行，同步执行, 同步执行需要等待邮件发送完成
                    loop.run_until_complete(self.email_service.send_three_party_api_error_email(params))
                    logging.info(f"已发送邮件通知到 {settings.QQ_MAIL_FROM}")
                    return '邮件发送成功'
                except Exception as e:
                    logging.error(f"api_error_send_email 执行失败: {str(e)}")
                    return f'邮件发送失败: {str(e)}'
        except Exception as e:
            logging.error(f"api_error_send_email 执行失败: {str(e)}")
            return f'邮件发送失败: {str(e)}'