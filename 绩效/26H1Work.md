---
title: 26H1Work
tags:
  - 绩效
  - 飞书同步
  - 2026H1
source: https://trip.larkenterprise.com/wiki/O4l9wVNe3iPojFkdn1mcB58qnGe
synced: 2026-07-07
revision_id: 224
---

> 飞书同步副本。原始文档：[26H1Work](https://trip.larkenterprise.com/wiki/O4l9wVNe3iPojFkdn1mcB58qnGe)

日报

admin优化

- [ ] 出票列表

- [ ] 新增expectedBookingTime字段

- [ ] 出票列表新增搜索条件，处理方式processType 

- [ ] 翻页操作栏目复制一份放置列表页面上面

- [ ] 退票列表

- [ ] 新增搜索条件  处理方式sub_refund_process_type

- [ ] 退票状态搜索多选

- [ ] 退票列表添加主退票单号

- [ ] 翻页操作栏目复制一份放置列表页面上面

- [ ] 退票列表页面，如果未选指定idc，支持选中的退票单按照其默认idc进行操作

26/1/12

- [ ] p2p 多子单出票失败退票有问题 修复

- [ ] applyRefund文档

- [ ] 退票重试走退票失败拦截问题，已修复

- [ ] 卡单发生产

- [ ] 退票列表供应搜索

26/1/13

- [ ] https://git.dev.sh.ctripcorp.com/global-rail-gds/gds-order-admin-be/-/merge_requests/60 修复跨idc逻辑，supplier & 异常列表更新 支持多个最终处理方式

- [ ] 出票失败退

- [ ] 退票重试退

- [ ] 190 告警忽略

● 

26/1/14

- [ ] 测试出票失败退

- [ ] 售后变更

- [ ] 退票失败

- [ ] 汽船block

- [ ] renfe特殊车次退

- [ ] 婴儿票欧星

26/1/15

26/1/19

- [ ] ant 供应商账号字段

- [ ] 发布

- [ ] 需求：sncfr选座

26/1/20

- [ ] ntv

- [ ] 选座

- [ ] 发布

26/1/21

- [ ] 分片查询

- [ ] 选座

- [ ] ntv

- [ ] 含铁

26/1/22

- [ ] 异常退失败解锁

- [ ] 查询生产

- [ ] 售后变更是否有变更字段修复

26/1/27

- [ ] block &ant

- [ ] treit 售后变更生产

- [ ] 退异常退失败解锁

- [ ] 人工通票退票下线

- [ ] 日铁转人工工单创建

26/1/28

- [ ] admin

- [ ] 工单

- [ ] 选座

26/1/29

- [ ] sncfr选座测试 

- [ ] applyRefund修复

- [ ] skill

- [ ] admin发布

26/2/2

- [ ] applyRefund日铁不可退拦截

26/2/3 

- [ ] admin x退票 产品类型字段

2/4

- [ ] apply 过滤日铁不可退

- [ ] confirmRefund 过滤婴儿

2/5

- [ ] applyRefund新增隔离层

- [ ] admin 跨idc修复

2/9

- [x] 需求：tis延误赔付流程

- [x] admin变更接入bigeye

- [x] apply refund

- [x] ti婴儿问题

- [x] 退票失败解锁 待发布

2/10 

- [x] admin发布

- [x] applyRefund对接

2/11

- [ ] admin 新增查询SupplierOrderId 权限 

- [ ] 订后邮件 区分渠道  

2/12

- [x] apply admin

- [x] apply admin 新契约

2/24

- [x] 异常未匹配&最终处理方式无 通知

- [x] 特殊退结构问题，一起退结构无

2/25

- [x] 异常退解锁发布生产

- [x] admin退票测试

- [x] 婴儿问题

- [x] confirm开关发布问题

- [x] season

2/26

- [x] admin apply

- [x] 欧信婴儿测试

- [ ] sncfr选座

2/27

- [x] 渠道公邮发布

- [x] admin相关发布

- [x] admin sky eye发布

- [x] 异常列表搜索 条件优化

- [ ] delayRepay

2/28

- [ ] delayRepay

3/2

- [ ] 异常车次退 新结构

- [ ] 出票失败原因

3/3

- [ ] delayRepay

- [ ] 欧星婴儿退

3/4

- [ ] delayRepay

- [ ] obb fix

- [ ] 需求：上线新x产品 ：ti折扣卡

- [ ] applyRefund测试

3/5

delayRepay

3/6

delayRepay

3.16

applyRefund对比

3.17

adminApplyRefund开发

3.18

adminApplyRefund生产

3.19 

人工出票 问题

applyRefund nonRefundableItem问题修复

3/23

delay发布

异常退问题

24

- [x] 异常退 测试

- [ ] 人工上传票凭证

- [ ] apply no refund

- [ ] 行程取消

- [ ] swapTrain

25

- [ ] queryExchangeInfo removeInfaints

26

- [x] sncfr

- [x] 异常退发布

27

- [x] admin飞书机器人

- [ ] swap数据库修改

- [ ] statistic加supplierOrderTag

- [x] ApplyRefun 结构化进度

3/9

- [x] delayRepay

- [x] admin skyeye

3/10

- [x] applyRefund生产

- [x] 修复问题

3/11

 sncfr 发布

applyRefund cr

变更 修复

- [ ] 3/30                

- [ ] applyRefund part过滤

- [ ] swapTrain

- [ ] 跟vc交互没问题

- [x] 飞书提醒

- [x] vcc

- [x] obbat行程变更修复

- [ ] 3/31

- [x] 机器人发布

- [x] 不可退原因

- [x] applyRefund接入机器人

- [x] applyRefund修复

- [ ] exchange乘客婴儿修复

- [ ] 4/1

- [x] supplierTag

- [x] 异常退修复

- [x] sncfr发布

- [ ] 4/2

- [ ] supplierSegmentId 缺失需要兜底

- [ ] admin缓存更换

- [ ] 4/3

- [ ] 人工改签

- [ ] 人工退走新接口

- [ ] log 跳转链接参数idc，默认unkown

- [ ] 

4/13

- [x] 婴儿乘客 ti

- [x] uktis eticket queryRefund

- [x] admin 

4/14

- [x] admin applyRefund

4/15

- [x] 人工出票

- [x] 通票生单失败会给票

4/16        

- [x] 人工出票上线

- [x] adminApply下周上线

4/7

- [x] 卡退票区分供应商

- [x] 人工出票后台 byte上传有问题吗

- [x] idc参数添加

4/8 

- [x] 退票数据 2/3 26小时才能退

- [x] 出发时间前一天发起退票，10分钟开始出结果

- [x] 出发时间当天开始退票，需要等待26小时

- [ ] 发布

- [x] 锁重试待发布

4/20

- [x] adminApplyRefund迁移上线

- [x] walk 1653711728796857

- [x] 标记一下walk

- [x] walk 能一起退吗？

- [x] 

- [x] 改签退问题 1653713991870584

4/21

- [x] 15560下线 orderSharding

- [x] 部分改

- [x] walk问题

- [ ] replace 更新ticketinginfo

- [x] delayRepay

4/22

- [ ] 15560下线调研

4/23

- [ ] dalSharding下线调研 

- [ ] 流量监控飞书代码下周发布

- [ ] legid 有很多问题 需要灰度对比开量 supplierSegment需要切后备  链接 链接

- [ ] admin 开量 还是有问题，tis同学跟进

4/28

- [x] dal sec埋点

- [x] isX 圈复杂度处理

- [x] needUpload拦截

4/29

- [x] 确认历史订单退改

- [x] pb season carnet 数据

- [x] 扫描状态待发布

- [x] 移除数据同步 查询逻辑

- [x] block改签修复

4/30

- [ ] 埋点增加OrderId

- [ ] 

https://trip.larkenterprise.com/wiki/TLIpwYaOziNfDXkVWFjcVRAHnOv

[ ]5.6

- [ ] 分支合并

- [ ] gitlab mcp

- [ ] applyRefund scanStatus

- [ ] tis admin退票

- [ ] okr

- [ ] l3

5.7

- [x] 同步老库移除

- [x] orderId check

- [x] admin 高级退 

- [x] code问题

5.8

- [x] 同步老库移除

- [x] 加密兜底

- [x] apply问题修复

- [x] admin观察

5.9

- [ ] admin支持x退票列表

- [ ] admin支持x产品重试complete

- [ ] 人工退票通知订单创建工单

- [ ] 出票成功

- [ ] applyRefund

- [ ] 异常配置

- [ ] farePackage 为空售罄需要生单失败 1207308062389777

- [ ] admin跨idc调用出退改

- [ ] season 退票申请时间补充

- [x] delayRepayresult

- [x] dal 加密问题处理

- [x] apply Refund scanstatus 测试

- [ ] l3

5.11 

- [x] obbtainticket卡单监控

- [x] delay 区分一下failProcessor

- [x] 发布

- [x] l3

- [x] dalsharding query out

5.12

- [ ] adminConfirmRefund

- [ ] block manual

5.13

- [x] block

- [x] admin conifrm

- [x] orderid生产

- [ ] admin前端

5.14

- [ ] adminApplyPartInfo问题

- [ ] adminConfirmRefund问题

- [ ] part问题？怎么传

5.15

confirm 失败，query状态继续confirm 欧星

5.18

- [ ] 开量 dal下线

5.19

- [ ] 压测

- [ ] admin apply 

- [ ] admin confirm

5.20        

adminconfirm

压测

5.21

压测

adminConfirm

5.23

- [ ] pb问题处理

- [ ] 压测

- [ ] 卡单 韩铁预约票

5.24

- [ ] block优化

5.25

5.26

- [ ] adminapply问题

- [ ] block

- [ ] 压测问题

- [ ] dal完全下线

6.1

- [ ] apply完全开量

- [ ] 数据库归档

6.2

- [ ] 改签文档

- [ ] 选座

- [ ] apply

- [ ] replace 问题修复

6.3        

- [ ] admin apply

- [ ] 选座问题

6.8

- [ ] 下线presignurl

- [ ] adminpreApply

- [ ] 退票问题agent？

6.9

- [ ] 欧铁拆票需求

- [ ] 下线presigin

- [ ] admin开量

6.10

- [ ] 异常配置界面优化

- [ ] 变更历史

- [ ] 变更审批

- [ ] 变更发布

- [ ] supplierSegmentId问题

6.11

- [ ] 卡单逻辑调整

- [ ] admin 开量

- [ ] supplierSegment 待发布

- [ ] 代码下线

6.12

- [ ] 退票问题排查skill

6.15

- [ ] presign下线

- [ ] mcp发布

- [ ] admin前端优化

- [ ] 欧铁拼票逻辑

- [ ] admin applyRefund 开量

6.16

- [ ] admin 发布

- [ ] 财务出票失败退数据补齐

6.17

- [x] 财务测试

- [x] 废弃代码移除

- [ ] 异常配置列表

6.18

- [ ] 异常配置列表

- [ ] 

6.22

- [ ] 异常配置新加

- [ ] admin全量

- [ ] 代码移除

6.23

- [ ] 异常配置

6.24

- [ ] 

6.25

- [ ] 异常配置

## 周报


12/26

1. 新票台开发
	1. [售后变更通知BI](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-1995) 测试中
	2. applyRefund升级改造
		1. 契约升级 测试环境 对比中 [‍‬‍‌﻿‌‌⁠‍‌‍﻿‍⁠‬‬⁠﻿‍‍⁠ ⁠‬‌‍﻿‌⁠ApplyRefund改造 - 飞书云文档](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)
	3. obbat 取票接入异常系统 待发布

2. admin开发
	1. admin log & 出退列表优化  [Log 1653735564535444](http://admin.order.gds.fat22.qa.nt.ctripcorp.com/order/log?orderId=1653735564535444&type=ticketLog) 测试中
		1. 新增日志页面-操作页面跳转
		2. 新增日志过滤（出票日志、退票日志），忽略日志功能

3. offline
	1. 通票转人工接入工单系统 已完成
	2. 日铁转人工操作对接 

4. 汽船
	1. 选座fare bug修复

1/9

1. 新票台开发
	1. applyRefund重构 对比测试中
	2. [卡单监控优化& 停运退唤起逻辑优化](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-3471) 测试中
		1. uktis 高级退卡退票判断逻辑优化。
		2. 新加停运退监控
		3. 停运退唤起逻辑优化
		4. 卡单job 捞取状态优化
	3. [车次停运专项2期 测试中 ](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-2377)
		1. ntv接入
	4. 退票失败允许指定code失败 开发中
	5. 改签车次推荐 开发中

2. offline
	1. 转人工接入工单系统  已发生产

1/16

1. 新票台开发
	1. applyRefund重构 对比测试中
	2. 售后变更 待发生产
		1. 支持渠道供应商开关
		2. 支持出发前多次查询变更，按渠道供应商配置
		3. 支持发送bi分析
	3. 卡单逻辑优化 代发生产
		1. 英铁高级退，电子票
	4. [车次停运专项2期 测试中 ](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-2377)
		1. ntv接入停运退
	5. 出票失败退问题优化
		1. 出票失败的部分子单没有退掉
	6. 退票失败校验移除
	7. sncfr支持选座 调研中

2. admin开发
	1. 异常列表优化

1/30


1. 新票台开发
	1. applyRefund契约改造                 测试对比中
	2. 日铁&通票 转人工接入工单系统  生产测试中
	3. 卡单逻辑优化                            已发布
	4. sncfr支持选座偏好                     测试中
	5. [英铁延误赔付](https://idev2.ctripcorp.com/issueDetail/GDS-2218)                            调研中

2. admin开发
	1. 出退列表优化                            已发布
		1. 新增处理方式筛选
		2. 新增信息展示

2/6

1. 新票台开发
	1. applyRefund契约改造                 测试对比中
		1. 添加隔离层
	2. applyRefund过滤已退子单           日铁开关开
	3. confirmRefund 移除婴儿              ti开关开         
	4. [英铁延误赔付](https://idev2.ctripcorp.com/issueDetail/GDS-2218)                             开发中

2. admin开发
	1. 接入skyeye
	2. 跳转供应搜索方案    

2/27

1. 新票台开发
	1. applyRefund 契约改造                 测试对比中
	2. applyRefund tis高级退迁移vc       开发中
	3. applyRefund欧星婴儿过滤           测试中   
	4. [英铁延误赔付](https://idev2.ctripcorp.com/issueDetail/GDS-2218)                             开发中
	5. 支持售后公邮开关细分渠道配置   待发生产
	6. 异常退退票失败未解锁问题修复   已发生产

2. admin开发
	1. 接入skyeye                                待发生产
	2. 列表优化                                    待发生产

3/6

1. 新票台开发
	1. applyRefund 契约改造                 测试对比中
	2. [英铁延误赔付](https://idev2.ctripcorp.com/issueDetail/GDS-2218)                             开发中
	3. applyRefund tis高级退迁移vc       开发中
	4. applyRefund欧星婴儿过滤           已发生产
	5. 支持售后公邮开关细分渠道配置   已发生产
	6. obbtainTicket 到达时间限制拦截   已发生产

2. admin开发
	1. 接入skyeye                                已发生产
	2. 列表优化                                   已发生产

3/13

1. applyRefund改造普通退部分已上线，灰度0% 原始结构异步对比中。

2. admin高级退几口tis切vc     开发中

3. delayRepay          开发测试

4. sncfr 座位偏好      待发布

5. renfe 车次异常退，待生产测试

6. admin 功能优化：
	1. log跳转票台日志看板
	2. skyEye变更优化，支持跳转trace详情链接

3.20

重点项目

1. applyRefund改造普通退部分已上线，已上线未开量，原始结构异步对比中。

2. admin高级退接口切vc 
	1. admin applyRefund 已上线未开量
	2. admin confirmRefund 开发中

本周工作

1. delayRepay          测试

2. sncfr 座位偏好      待发布

3. renfe 车次异常退，生产测试

4. admin 人工出票升级    待开发

5. 车次异常退问题修复  开发中

3/27

重点项目

1. applyRefund 对比中

2. admin高级退接口切vc 
	1. admin applyRefund 已上线未开量
	2. admin confirmRefund 待开发

本周工作

1. delayRepay          已发布

2. 车次异常退问题修复   已发布

3. sncfr 座位偏好      待发布

4. renfe 车次异常退，生产测试

5. 飞书消息机器人接入 开发中

6. admin 人工出票升级    待开发

7. swap车次 调研中

4/3

重点项目

1. applyRefund 对比中
	1. 接入飞书机器人
	2. nonRefundableItem leg依赖移除

2. admin高级退接口切vc 
	1. 缓存问题修复，与普通退缓存区分， 待发生产

本周工作

1. 新增supplierTag         已发布

2. 车次异常退问题修复   已发布

3. sncfr 座位偏好      已发布

4. renfe 车次异常退，生产测试

5. 飞书消息机器人接入 已发布

6. admin 人工出票升级    待开发

7. swap车次 调研中

8. applyRefund已知问题修复  测试中

4/17

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)
	1. locationCode 下线适配 已优化  待发生产
	2. nonRefundableItem leg依赖移除，新增segmentId 待发生产

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. applyRefund admin对比逻辑优化 待发生产

3. renfe 车次异常退               生产已发布

4. [admin 人工出票升级](https://trip.larkenterprise.com/wiki/CVI7wgI1AiWz5CkYxNVc6nWKnvh)&支持人工改签           已发生产 

5. 通票购买失败返回票信息     调研中

6. uktis 退票新条款适配          已发生产

7. ti 改签婴儿乘客问题优化     已发生产

8. 人工退票老接口下线           已发生产

4.24

重点项目

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)
	1. 对比问题：SupplierSegmentId和SegmentId 无法完全匹配
		1.  nonRefundableItem RefundableItem ~~ticketingInfo.leg依赖移除~~，优先使用legId匹配，SupplierSegmentId后备匹配对比 待发布

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. apply对比问题：新老接口不可退code不一致
		1. 待发布

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. 飞书监控vcc，x，p2p改签查询老库流量  待发布

工作

1. 通票购买失败返回票信息     测试中

2. delayRepay 待客查询  开发中

5/8

重点项目

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)
	1. scanStatus问题修复                             待发布

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. 对比问题                                            tis同学处理中
	2. adminConfirm切vc                               测试中

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. vcc，x，p2p改签查询老库流量  
		1. 飞书监控                                        已发布
		2. 流量下线                                        待发生产
	2. 老系统发号下线                                    已发测试
	3. 数据加密下线
		1. 未加密数据监控                               观察中
		2. 加密兜底                                         开发中

本周工作

1. 异常退锁优化             已发布

2. delayRepay 待客查询  开发中

3. 异常退需求                开发中

5/15

重点项目

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ⏳灰度中 0.05%

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. 对比问题                                            🔄 处理中                                 
	2. adminConfirm切vc                               🧪 测试中 90%

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. vcc，x，p2p改签查询老库流量  
		1. 流量下线                                       📅下周生产下线
	2. 老系统发号下线                                   ⏳灰度中 sha:0 ->1/1000
	3. 数据加密下线
		1. 票台加密兜底                                 ✅ 已发布
		2. 15560流量下线                               📅下周生产下线

本周工作

1. delayRepay 待客查询                                      ✅ 已发布

2. 卡单监控优化                                                 🟢 开发中

3. admin前端修复                                               ✅ 已完成

5/22

重点项目

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ⏳灰度中 1%

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. adminApplyRefund对比问题                  🔄 处理中                                 
	2. adminConfirm切vc                               🧪 灰度中1/w

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. vcc，x，p2p改签查询老库流量              ✅ 已下线
	2. 老系统发号下线                                   ⏳灰度中 sha:30%; sgp:30%; fra:0.1%
	3. 数据加密下线                                       ✅ 已下线

本周工作

1. orderId生成                                                ⏳开量观察

2. applyRefund admin                                      ⏳开量观察

3. 卡单监控优化                                               🟢 开发中

4. [tis 转代购压测](https://trip.larkenterprise.com/wiki/LlQMwvyTLiLkMBko6PxcK39Zn2d)                                              🟢 测试中

5.29

重点项目

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ⏳灰度中 50%

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. adminApplyRefund对比问题                🔄 处理中下周一发生产                                 
	2. adminConfirm切vc                               🧪 灰度中10%

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. vcc，x，p2p改签查询老库流量              ✅ 已下线
	2. 老系统发号下线                                   ✅ 已下线
	3. 数据加密下线                                       ✅ 已下线
	4. 代码逻辑移除                                       下周一发布

本周工作

1. 卡单监控优化                                               ⏳ 待发生产

2. [tis 转代购压测](https://trip.larkenterprise.com/wiki/LlQMwvyTLiLkMBko6PxcK39Zn2d)                                              ⏳ 问题待解决

6.6

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ✅已全量

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. adminApplyRefund对比问题                🔄 处理中下周一发生产，下周开量                                 
	2. adminConfirm切vc                               🧪 灰度中50% 下周一全量

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. 代码逻辑移除                                        ✅已全部下线

1. 卡单监控优化                                               ✅已发生产

2. admin优化                                                    待发生产

3. [欧星售后选座](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-7998)                                                开发中

6/12

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ✅已全量

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. adminApplyRefund对比问题                🔄 1%                             
	2. adminConfirm切vc                                ✅已全量

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. 代码逻辑移除                                        ✅已全部下线

1. [卡单监控优化  ](https://trip.larkenterprise.com/wiki/BdO4waj9zix0nCk5mlacooULnVe)                                             ✅已发生产

2. [下线presiginurl接口](https://trip.larkenterprise.com/wiki/YkFPwhC2NixxFsk2Xgpc1HqInre)                                     ✅已发生产

3. s[upplierSegmentId问题](https://trip.larkenterprise.com/wiki/IklzwVI2RiwwdKk7F1Fc0ZoTnXf)                               🔄 代发生产

4. [欧星售后选座](https://idev2.ctripcorp.com/team/10002849/issue/1152?issueKey=GDS-7998)                                                🔄 开发中

5. [欧铁拆票费拆分字段 ](https://trip.larkenterprise.com/wiki/D2EXwnyCSiWkrWkUgQQcf9vEnGg)                                    🔄 代发生产

6. [退票问题排查skill ](https://trip.larkenterprise.com/docx/Nc7Gdt14ooVbXExsR74c1VKtnKf)                                        🔄 开发中

6/26

1. [applyRefund 契约改造](https://trip.larkenterprise.com/wiki/VBqgwdGMgi6ChfkJDZ5ceiDOnqf)                               ✅已全量

2. [admin高级退接口切vc ](https://trip.larkenterprise.com/wiki/Jzx4wmHymiKcqNkblm1c8sA7nLh)
	1. adminApplyRefund对比问题               ✅已全量                          
	2. adminConfirm切vc                               ✅已全量

3. [15560下线](https://trip.larkenterprise.com/wiki/MU6Pw4xIhixrgGkZMwyczgzYnX3)
	1. 代码逻辑移除                                        ✅已全部下线

4. [异常配置发布升级](https://trip.larkenterprise.com/wiki/GYUgwXxBfiDoQtkzzmfcpIeznmc)                                       ✅已上线
	1. 异常配置列表支持审批功能

1. s[upplierSegmentId问题](https://trip.larkenterprise.com/wiki/IklzwVI2RiwwdKk7F1Fc0ZoTnXf)                               ✅已发生产

2. [欧铁拆票费拆分字段 ](https://trip.larkenterprise.com/wiki/D2EXwnyCSiWkrWkUgQQcf9vEnGg)                                    ✅已发生产

3. [异常配置发布升级](https://trip.larkenterprise.com/wiki/GYUgwXxBfiDoQtkzzmfcpIeznmc)                                        ✅已上线

4. 退票老逻辑代码下线                                    ✅已发生产

5. [gdpr删除通知供应商](https://trip.larkenterprise.com/wiki/XrEIwD7Nli99UBkaxracc57Snyd)                                    规划中

7/3

无

1. [415 complete 重试 & 转人工回系统](https://idev2.ctripcorp.com/issueDetail/GDS-9524) — ✅已发生产

2. [GDS-2971 TI 特殊退拆单票价](https://trip.larkenterprise.com/wiki/OBL7wVS0Gizi0QkudK3ckKtvnbf) — ✅已发生产

3. [SLA 统计并发时间分片](https://idev2.ctripcorp.com/issueDetail/GDS-9414)解决慢查询问题 — ✅已完成

4. [Ticket Log 退票对齐排查工具](https://idev2.ctripcorp.com/issueDetail/GDS-9399) — ✅已完成

5. [refundEvent 误清 subRefundId](https://trip.larkenterprise.com/wiki/OWX6wAF8Uix0IBkIQwhcG3Cdnrf) 排查结论落地、[GDS-9637](https://idev2.ctripcorp.com/issueDetail/GDS-9637) 立项 — 👀待评审

6. [obtain 票台取消到达时间拦截](https://trip.larkenterprise.com/wiki/PNFbwfRiAi41fmkTAfWczIIKn1g) 方案定稿、进入开发 — 🔄处理中

7. [GDPR ](https://trip.larkenterprise.com/wiki/XrEIwD7Nli99UBkaxracc57Snyd)【GDPR】票台删除通知技术方案 — 🔄测试中
