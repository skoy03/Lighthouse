import json
import time
import requests
import pytz
from datetime import datetime
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models
#【配置开始】
#腾讯云配置，建议使用子账户！详见https://console.cloud.tencent.com/cam/capi
SecretId = ""
SecretKey = ""
#地域
regions = ["ap-beijing", "ap-chengdu", "ap-guangzhou", "ap-hongkong", "ap-jakarta", "ap-mumbai", "ap-nanjing", "ap-seoul", "ap-shanghai", "ap-singapore", "ap-tokyo", "eu-frankfurt", "na-siliconvalley", "na-toronto"]
#流量限制百分比
percent = 0.95
#以下为信息推送
qmsgurl = '' #qmsg酱私有云url地址:例:https://qmsg.zendee.cn，私有云架设教程：https://qmsg.zendee.cn/docs/plus/
qkey = '' # Qmsg酱QQ推送key(不懂不要填，可空)
bot = '' #需要推送的机器人QQ
qq = '' #需要推送QQ号 (不懂不要填，可空)
qun = ''   # 需要推送QQ群号 (不懂不要填，可空)
plustoken = '' #PUSHPLUS的token 官网为https://www.pushplus.plus/(不懂不要填，可空)
#-------------------
#【配置结束】

def qmsg_send(msg):
    global qmsgurl, qkey, qq, bot
    if qmsgurl == '':
        qmsgurl = 'https://qmsg.zendee.cn'
    if qkey == '':
        return
    qmsg_url = str(qmsgurl) + "/send/" + str(qkey)
  
    data = {
            'qq': f'{qq}',
            #'bot': f'{bot}',
            'msg': msg
        }
    requests.post(qmsg_url, data = data)
#Qmsg酱QQ群推送
def qmsg_group(msg):
    global qmsgurl, qkey, qun, bot
    if qmsgurl == '':
        qmsgurl = 'https://qmsg.zendee.cn'
    if qkey == '':
        return
    qmsg_url = str(qmsgurl) + "/group/" + str(qkey)
  
    data = {
            'qq': f'{qun}',
            #'bot': f'{bot}',
            'msg': msg
        }
    requests.post(qmsg_url, data = data)
# PUSHPLUS推送
def plus_send(msg,title ='腾讯轻量云流量包监控',template = 'txt'):
    if plustoken == '':
        return
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": plustoken,
        "title": title,
        "content": msg,
        "template":template
    }
    body = json.dumps(data).encode(encoding = 'utf-8')
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data = body, headers = headers)
    if response.status_code == 200:
        return 1
    return 0

def send_message(msg):
    qmsg_send(msg)
    plus_send(msg)

#UTC时间转换开始
def endtime(utc_time_str):
    # 创建UTC时间对象
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    # 创建北京时间时区对象
    beijing_tz = pytz.timezone('Asia/Shanghai')
    # 将UTC时间转换为北京时间
    beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
    # 格式化北京时间为字符串
    beijing_time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    return beijing_time_str
#UTC时间转换结束

def doCheck():
    try:
        # 参数
        ids = SecretId.split(",")
        keys = SecretKey.split(",")
        # print(ids)

        for i in range(len(ids)):
            for ap in regions:
                dofetch(ids[i], keys[i], ap)

    except TencentCloudSDKException as err:
        print(err)

    #-------------------
def dofetch(id, key, region):
    cred = credential.Credential(id, key)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "lighthouse.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
    #获取实例列表
    req_instances = models.DescribeInstancesRequest()
    params = {
    
    }
    req_instances.from_json_string(json.dumps(params))
    resp_instances = client.DescribeInstances(req_instances) 
    s1 = json.loads(resp_instances.to_json_string())['InstanceSet']
    for j in range (len(s1)):
        params.setdefault("InstanceIds",[]).append(s1[j]['InstanceId'])#获取实例ID

    #获取实例地域
    req = models.DescribeRegionsRequest()
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRegions(req)
    s2 = json.loads(resp.to_json_string())["RegionSet"]
    for o in range(len(s2)):
      if s2[o]["Region"] == region:
        RegionName = s2[o]["RegionName"]

    #获取实例可用区
    req = models.DescribeZonesRequest()
    req.from_json_string(json.dumps(params))
    resp = client.DescribeZones(req)
    s2 = json.loads(resp.to_json_string())["ZoneInfoSet"]
    for u in range(len(s1)):
         Zone = s1[u]["Zone"]
         for o in range(len(s2)):
             if s2[o]["Zone"] == Zone:
                 ZoneName = s2[o]["ZoneName"]

    #获取实例流量
    req = models.DescribeInstancesTrafficPackagesRequest()
    req.from_json_string(json.dumps(params))
    resp = client.DescribeInstancesTrafficPackages(req)
    s3 = json.loads(resp.to_json_string())["InstanceTrafficPackageSet"]
    MB = 1024*1024
    GB = 1024*1024*1024
    TB = 1024*1024*1024*1024
    state_list = {"RUNNING": "运行中", "STOPPED": "已关机", "STARTING": "开机中", "STOPPING":"关机中", "REBOOTING": "重启中"}
    for i in range (len(s3)):
        InstanceId = s3[i]['InstanceId']
        InstanceName = s1[i]['InstanceName']
        s4 = s3[i]['TrafficPackageSet'][0]
        InstanceState = s1[i]["InstanceState"]
        if InstanceState in state_list:
            InstanceState = state_list[InstanceState]
        ExpiredTime = s1[i]['ExpiredTime']
        localtime = endtime(ExpiredTime)
        TrafficPackageTotal = int(round(s4['TrafficPackageTotal'] / GB, 0))
        Used = round(s4['TrafficUsed']/GB,2)
        percentageUsed = round((Used / TrafficPackageTotal) * 100,2)
        remainingpercentage = round((TrafficPackageTotal - Used) / TrafficPackageTotal * 100,2)
        #TrafficPackageRemaining = round(s3['TrafficPackageRemaining']/GB,2)
        Total = s4['TrafficPackageTotal']
        TrafficUsed = s4['TrafficUsed']
        TrafficPackageRemaining = s4['TrafficPackageRemaining']
        # 判断总流量大小，选择合适的单位
        if Total < TB:
            Totals = f"{int(round(Total / GB,0))}GB"
        else:
            Totals = f"{int(round(Total / TB,0))}TB"
                   
        if TrafficUsed < GB:
            useds = f"{round(TrafficUsed / MB,2)}MB"
        elif TrafficUsed < TB:
            useds = f"{round(TrafficUsed / GB,2)}GB"
        else:
            useds = f"{round(TrafficUsed / TB,2)}TB"
                        
        if TrafficPackageRemaining < GB:
            remaining = f"{round(TrafficPackageRemaining / MB,2)}MB"
        elif TrafficPackageRemaining < TB:
            remaining = f"{round(TrafficPackageRemaining / GB,2)}GB"
        else:
            remaining = f"{round(TrafficPackageRemaining / TB,2)}TB"
                
        #推送实例状态
        msg = f"实例名称：{InstanceName}\n实例状态：{InstanceState}\n总流量：{Totals}\n已使用：{useds} = {percentageUsed}%\n剩余：{remaining} = {remainingpercentage}%\n地域和可用区：{RegionName} | {ZoneName}\n到期时间：{localtime}\n当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        #send_message(msg)
        print(msg)

        if (Used/TrafficPackageTotal<percent):
            if (InstanceState == "运行中"):
                print("一切正常")
            else:
                req_Start = models.StartInstancesRequest()
                params_Start = {

                }
                params_Start.setdefault("InstanceIds",[]).append(InstanceId)
                req_Start.from_json_string(json.dumps(params_Start))
                resp_Start = client.StartInstances(req_Start)
                #推送开机结果
                msg = f"流量充足，尝试开机\n实例名称：{InstanceName}\n实例状态：{InstanceState}\n总流量：{TrafficPackageTotal}GB\n已使用：{useds} = {percentageUsed}%\n剩余：{remaining} = {remainingpercentage}%\n地域和可用区：{RegionName} | {ZoneName}\n到期时间：{localtime}\n当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                send_message(msg)
                print(msg)
        else:
            if (InstanceState == "运行中"):
                print(InstanceName,":","流量超出限制，自动关闭")
                req_Stop = models.StopInstancesRequest()
                params_Stop = {

                }
                params_Stop.setdefault("InstanceIds",[]).append(InstanceId)
                req_Stop.from_json_string(json.dumps(params_Stop))
                resp_Stop = client.StopInstances(req_Stop) 
                #推送关机结果
                msg = f"流量超出限制，自动关闭\n实例名称：{InstanceName}\n实例状态：{InstanceState}\n总流量：{TrafficPackageTotal}GB\n已使用：{useds} = {percentageUsed}%\n剩余：{remaining} = {remainingpercentage}%\n地域和可用区：{RegionName} | {ZoneName}\n到期时间：{localtime}\n当前时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                send_message(msg)
                print(msg)
            else:
                print("已关机")
        
        #添加时间戳
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print ("--------------------")

if __name__ == '__main__':
     doCheck()
     pass