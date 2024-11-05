import aiohttp
from datetime import datetime
import asyncio
from loguru import logger

# 读取配置文件
def load_config():
    config = {}
    try:
        with open("config.txt", "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                config[key] = value
    except FileNotFoundError:
        logger.error("配置文件 config.txt 未找到，请检查文件路径")
    except ValueError:
        logger.error("配置文件格式错误，请确保每一行格式为 KEY=VALUE")
    return config

# 加载配置
config = load_config()
API_URL = config.get("API_URL", "http://default_url_if_missing")
USER_ID = config.get("USER_ID", "default_user_id_if_missing")
INTERVAL = int(config.get("INTERVAL", 1800))  # 从配置文件获取间隔时间，默认1800秒

ACCOUNTS_FILE_PATH = "account.txt"

# 解析代理信息为指定格式
def format_proxy(proxy):
    proxy_parts = proxy.split(":")
    if len(proxy_parts) == 4:
        account, password, ip, port = proxy_parts
        return f"{USER_ID}==socks5://{account}:{password}@{ip}:{port}"
    elif len(proxy_parts) == 2:
        ip, port = proxy_parts
        return f"{USER_ID}==socks5://{ip}:{port}"
    else:
        logger.warning(f"代理格式不正确: {proxy}")
        return None


all_proxies = set()
# 获取并写入代理信息
async def fetch_proxies():
    global all_proxies
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, ssl=False) as response:
                response_text = await response.text()
                proxies = response_text.splitlines()

                # 格式化代理并去除已存在的代理
                new_proxies = set()
                for proxy in proxies:
                    formatted_proxy = format_proxy(proxy)
                    if formatted_proxy and formatted_proxy not in all_proxies:
                        new_proxies.add(formatted_proxy)

                # 更新全局代理集合
                all_proxies.update(new_proxies)

                # 将新的唯一代理写入 account.txt
                with open(ACCOUNTS_FILE_PATH, "w") as f:
                    for proxy in new_proxies:
                        f.write(f"{proxy}\n")

                # 日志输出获取到的代理数量和新增代理数量
                logger.info(f"<green>代理获取成功，总数量: {len(proxies)}</green>")
                logger.info(f"<yellow>新增代理数量: {len(new_proxies)}</yellow>")

    except aiohttp.ClientError as e:
        logger.error(f"获取代理失败：{e}")

API_UPLOAD_URL = "http://127.0.0.1:8000/upload/"

# 上传代理信息
async def upload_to_ui():
    logger.info(f"{datetime.now()} - 正在上传代理到 UI 界面...")

    try:
        with open(ACCOUNTS_FILE_PATH, "rb") as f:
            file_data = f.read()
    except FileNotFoundError:
        logger.error(f"代理文件 {ACCOUNTS_FILE_PATH} 未找到")
        return

    try:
        async with aiohttp.ClientSession() as session:
            files = {"file": file_data}
            async with session.post(API_UPLOAD_URL, data=files) as response:
                if response.status == 200:
                    upload_count = len(file_data.splitlines())
                    logger.success(f"<blue>上传完成，上传代理数量: {upload_count}</blue>")
                else:
                    logger.error(f"上传失败，状态码: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"上传失败，错误: {e}")

# 主循环，使用配置文件中的间隔时间
async def main():
    while True:
        await fetch_proxies()
        await upload_to_ui()
        await asyncio.sleep(INTERVAL)  # 使用配置文件中的间隔时间

if __name__ == "__main__":
    asyncio.run(main())
