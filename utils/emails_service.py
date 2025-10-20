from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from pydantic import EmailStr

conf=ConnectionConfig(
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
    MAIL_FROM="",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_SSL_TLS=True
)

async def send_email(credits:int):
    message=MessageSchema(
        subject="DMA credits are running out",
        #Someone's email
        recipients=[""],
        body=f"DMA credits have fallen below:{credits} value"
    )
    fm=FastMail(conf)

    await fm.send_message(message)