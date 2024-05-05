# Lighthouse
监控腾讯云轻量应用服务器，实现状态推送，流量超限自动关机，流量充足自动开机。

### 1.简介

监控腾讯云轻量应用服务器流量使用情况，流量超限自动关机，流量充足自动开机，并推送至多平台。

注意：脚本主要参考[@2lifetop](https://github.com/2lifetop/LightHouse_Automatic_Shutdown)的项目！！！

### 2.获取密钥
访问https://console.cloud.tencent.com/cam/capi

建议使用子账户，点击快速创建，访问方式改为【编程访问】


用户权限改为【QcloudLighthouseFullAccess】

记得取消【AdministratorAccess】，这样，即使泄露密钥也不会对账号内其他业务产生影响。

将【SecretId】【SecretKey】复制。并填入脚本中

### 3.配置推送
执行一次脚本就会将实例的状态（包括流量、运行状态）推送至指定平台。

当执行开机，关机操作时，会推送至指定平台。

qmsg酱推送，填写key，详见https://qmsg.zendee.cn

pushplus微信推送，填写token，详见https://www.pushplus.plus

### 4.宝塔计划执行

使用宝塔计划进行执行


### 5.效果

![](https://github.com/skoy03/Lighthouse/blob/main/20240505095256.png?raw=true)

### 6.写在最后


再次感谢[@2lifetop](https://github.com/2lifetop/LightHouse_Automatic_Shutdown)的项目！！！
