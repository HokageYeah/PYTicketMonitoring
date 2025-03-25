import smtplib
from email.mime.text import MIMEText

def test_smtp_connection():
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login('2410292164@qq.com', 'acfmhesqnkyzdjcc')
        print("连接成功！")
        server.quit()
    except Exception as e:
        print(f"连接失败：{e}")

if __name__ == "__main__":
    test_smtp_connection()