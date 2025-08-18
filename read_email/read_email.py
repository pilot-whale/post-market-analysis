import os
import poplib
from datetime import datetime
from email import policy
from email.parser import BytesParser

# 获取当前脚本的文件名（包括扩展名）
script_name = os.path.basename(__file__)
print("Script name:", script_name)


def get_email_content():
    # 配置信息
    email = 'taobaobang123@sina.com'
    password = 'cb414602f4395114'
    pop3_server = "pop3.sina.com"

    try:
        now = datetime.now()
        print("------------------------------ connect to email server --------------------------- @", now)
        # 连接到POP3服务器
        server = poplib.POP3_SSL(pop3_server)
        server.user(email)
        server.pass_(password)

        # 获取邮件总数
        num_messages = len(server.list()[1])

        no_repeat_list = []  # 存放已经读取的邮件主题
        strategy_name = '每日整点天气播报'

        for i in range(num_messages, 0, -1):
            # 从最新的邮件开始获取邮件原始字节
            resp, lines, octets = server.retr(i)
            msg_content = b'\r\n'.join(lines)
            msg = BytesParser(policy=policy.default).parsebytes(msg_content)

            print("Subject:", msg['Subject'], "From:", msg['From'])

            if strategy_name in str(msg['Subject']) and 'ants2016@vip.163.com' in str(msg['From']):
                if strategy_name in no_repeat_list:
                    continue  # 可改为 break，如果只取最新一封
                no_repeat_list.append(strategy_name)

                def get_body_and_charset(part):
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        return None, 'unknown'
                    # 获取字符集
                    charset = part.get_content_charset()
                    if charset is None:
                        charset = 'utf-8'  # 默认 fallback
                    return payload, charset

                def decode_safely(payload, charset):
                    # 安全解码，尝试多种编码
                    if isinstance(charset, str):
                        charsets = [charset]
                    else:
                        charsets = ['utf-8', 'gbk', 'gb2312', 'latin1', 'iso-8859-1']

                    for cs in charsets:
                        try:
                            return payload.decode(cs)
                        except (UnicodeDecodeError, LookupError):
                            continue
                    # 如果都失败，用 errors='replace' 强制解码
                    return payload.decode('utf-8', errors='replace')

                def get_body(msg):
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in disposition:
                                payload, charset = get_body_and_charset(part)
                                if payload:
                                    return decode_safely(payload, charset)
                    else:
                        payload, charset = get_body_and_charset(msg)
                        if payload:
                            return decode_safely(payload, charset)
                    return None

                body = get_body(msg)
                if body:
                    server.quit()
                    return body  # 已经是字符串，无需再 decode

        server.quit()
        return None  # 没有找到匹配的邮件

    except Exception as e:
        print("- e:", e)
        try:
            server.quit()
        except:
            pass
        return None


if __name__ == '__main__':
    content = get_email_content()
    if content:
        print("邮件内容：")
        print(content)
        # 过滤掉'--'及之后的内容
        if '--' in content:
            content = content.split('--')[0].rstrip()
        # 确保目标目录存在
        # 获取当前文件所在目录的父目录（即项目根目录）
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        target_dir = os.path.join(parent_dir, 'text', 'target')
        os.makedirs(target_dir, exist_ok=True)
        # 保存内容到文件
        target_file = os.path.join(target_dir, 'latest.txt')
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"内容已保存到: {target_file}")
    else:
        print("未能获取邮件内容")