import os
import subprocess
import time
import requests

qmsgurl = '' #qmsg酱私有云url地址:例:https://qmsg.zendee.cn，私有云架设教程：https://qmsg.zendee.cn/docs/plus/
qkey = '' # Qmsg酱QQ推送key(不懂不要填，可空)
bot = ''
qq = ''   # 需要推送的qq号或群号 (不懂不要填，可空)

# 获取最新SDK版本号
def get_latest_sdk_version():
    url = "https://pypi.org/pypi/tencentcloud-sdk-python-lighthouse/json"
    response = requests.get(url)
    data = response.json()
    latest_version = data["info"]["version"]
    return latest_version

# 检测当前SDK版本号
def get_current_sdk_version():
    version_file = open("version.txt", "r")
    current_version = version_file.read().strip()
    version_file.close()
    return current_version

# 更新SDK包
def update_sdk(version):
    pip_command = f"/www/server/panel/pyenv/bin/pip3 install --upgrade tencentcloud-sdk-python-lighthouse"
    subprocess.run(pip_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 将 stdout 和 stderr 重定向到 /dev/null
    with open(os.devnull, 'w') as fnull:
        subprocess.run(["tee", "/dev/null"], stdin=subprocess.PIPE)
#  QMSG酱推送
def qmsg_send(msg):
    global qmsgurl, qkey, qq, bot
    if qmsgurl == '':
       qmsgurl = 'https://qmsg.zendee.cn'
    if qkey == '':
        return
    qmsg_url = str(qmsgurl) + "/send/" + str(qkey)
    #qmsg_url = str(qmsgurl) + "/group/" + str(qkey)
  
    data = {
            'qq': f'{qq}',
            'bot': f'{bot}',
            'msg': msg
        }
    requests.post(qmsg_url, data = data)
# 检测并更新SDK
def main():
    current_version = get_current_sdk_version()
    latest_version = get_latest_sdk_version()
    if current_version != latest_version:
        msg = f"检测到腾讯轻量云SDK有更新\n当前版本：{current_version}\n最新版本：{latest_version}"
        #qmsg_send(msg)
        print(msg)
        update_sdk(latest_version)
        msg = "更新完成！"
        print(msg)
        with open("version.txt", "w") as version_file:
            version_file.write(latest_version)
        # 发送qmsg酱推送通知消息
        msg = f"腾讯轻量云SDK已成功更新到版本：{latest_version}"
        #qmsg_send(msg)
        print(msg)
    else:
        msg = "当前已经是最新版本！"
        print(msg)
        
if __name__ == "__main__":
    main()