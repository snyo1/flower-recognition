from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from ..core.config import settings
from pathlib import Path
from aiosmtplib import SMTPResponseException

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, code: str, type: str):
    """
    发送验证码邮件
    :param email: 收件人邮箱
    :param code: 验证码
    :param type: 类型 (register 或 reset)
    """
    subject = "花世界 - 注册验证码" if type == "register" else "花世界 - 重置密码验证码"
    
    html = f"""
    <div style="background-color:#f5f5f5;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background-color:#ffffff;border-radius:8px;padding:30px;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color:#4CAF50;text-align:center;margin-bottom:30px;">花世界 {subject}</h2>
            <p style="font-size:16px;color:#333;line-height:1.6;">亲爱的用户：</p>
            <p style="font-size:16px;color:#333;line-height:1.6;">您好！您正在进行{"账号注册" if type == "register" else "密码重置"}操作。</p>
            <p style="font-size:16px;color:#333;line-height:1.6;">您的验证码是：</p>
            <div style="text-align:center;margin:30px 0;">
                <span style="display:inline-block;padding:12px 24px;background-color:#f0f9eb;color:#67c23a;font-size:24px;font-weight:bold;letter-spacing:4px;border-radius:4px;border:1px solid #e1f3d8;">{code}</span>
            </div>
            <p style="font-size:14px;color:#666;line-height:1.6;">验证码有效期为5分钟，请勿泄露给他人。</p>
            <p style="font-size:14px;color:#666;line-height:1.6;">如非本人操作，请忽略此邮件。</p>
            <div style="margin-top:40px;padding-top:20px;border-top:1px solid #eee;text-align:center;color:#999;font-size:12px;">
                <p>&copy; 2024 花世界团队 版权所有</p>
            </div>
        </div>
    </div>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
    except SMTPResponseException as e:
        # 忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应
        if e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode():
            print("忽略 QQ 邮箱 SMTP 关闭阶段的非标准响应（邮件已成功发送）")
        else:
            raise e
