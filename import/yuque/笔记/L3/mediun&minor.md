

# Code Review L3 Medium / Minor 问题速记

本文基于《代码评审L3考试赋能》文档中的 Medium/Minor 部分整理，重点帮助区分：哪些只是格式建议，哪些已经影响可维护性、可读性和长期质量。

## 一、Medium / Minor 的判断标准

Medium / Minor 通常不是马上导致线上事故的问题，但会持续累积技术债，降低代码可读性、可维护性和可测试性。

简单判断：

|  |  |  |
| --- | --- | --- |
| 级别 | 判断标准 | 常见表现 |
| Medium | 已经影响理解、扩展、统一性，后续维护容易出错 | 条件复杂、公共组件不统一、重复逻辑较多、异常边界不清晰 |
| Minor | 局部风格或清洁度问题，修复成本低 | 无用注释、格式缩进、命名不清晰、空格缺失 |

考试评论仍建议按这个结构写：

```
问题是什么 → 造成什么影响 → 修复建议
```
不要只写“格式问题”“代码不优雅”，要写出为什么影响阅读或维护。

## 二、文档中提到的典型 Medium / Minor

### 1. 冗余代码未删除

文档截图中的评论重点：

```
MINOR: 无用代码直接删除，不要注释。
```
错误示例：

```
public List<Order> queryOrders(QueryRequest request) {
    // List<Order> orders = oldQuery(request);
    // return orders;
    return newQuery(request);
}
```
问题：

1. 被注释的旧代码会干扰阅读。
2. 不知道它是历史遗留、临时调试，还是未来要恢复。
3. 真需要找历史实现可以看 Git，不应留在业务代码里。

标准评论：

```
MINOR: 这里保留了无用注释代码，会干扰后续阅读和维护。历史实现可以通过 Git 追溯，不建议在业务代码中保留。
建议直接删除无用代码，只保留当前有效逻辑。
```
什么时候会升级到 Medium：

1. 大段废弃代码包围核心逻辑，明显影响理解。
2. 注释代码中包含过期配置、错误逻辑或敏感字段。
3. 多处残留导致维护者难以判断真实流程。

### 2. 条件语句复杂度高

文档截图中的例子：

```
if (star == 0 || star == 1 || star == 2 || star == 3) {
    // ...
}
```
文档评论：多个逻辑语句，可用 Set 数据结构改善。

标准评论：

```
MEDIUM: 这里多个条件通过 || 串联，可读性和可扩展性较差。后续新增枚举值时容易漏改或写错。
建议使用 Set、枚举方法或独立判断函数表达业务含义，提升可读性和维护性。
```
错误示例：

```
if (status == 1 || status == 2 || status == 3 || status == 6) {
    allowRefund(order);
}
```
正确示例：

```
private static final Set<Integer> REFUNDABLE_STATUS_SET =
        Sets.newHashSet(1, 2, 3, 6);

if (REFUNDABLE_STATUS_SET.contains(status)) {
    allowRefund(order);
}
```
更好的方式是用枚举承载业务语义：

```
public enum OrderStatus {
    CREATED(1, true),
    PAID(2, true),
    TICKETED(3, true),
    CANCELLED(4, false);

    private final int code;
    private final boolean refundable;

    public boolean isRefundable() {
        return refundable;
    }
}
```
什么时候算 Medium：

1. 条件表达式长到需要反复读。
2. 多个业务规则混在一个 `if` 中。
3. 新增枚举值时需要到处找 `||`。
4. 条件判断重复出现在多处。

什么时候可能升级成 Major：

如果复杂条件控制的是支付、出票、退款、权限、状态流转等核心动作，并且容易导致错误状态或越权，就不只是可读性问题，可能是 Major。

### 3. 公共组件使用未统一

文档截图中的例子是日志组件未统一，评论提到 log 组件统一化。

标准评论：

```
MEDIUM: 这里使用的日志组件与项目/团队统一规范不一致，会导致日志格式、链路字段、检索方式和监控接入不统一，后续排查问题成本较高。
建议改为项目统一日志组件，并按规范输出必要的业务标识和异常信息。
```
错误示例：

```
System.out.println("create order success");
LOGGER.info("create order success");
CLogManager.info("create order success");
```
同一个项目里多套日志混用，问题不是“能不能打印”，而是：

1. 日志平台字段不统一。
2. traceId、spanId、appId 等链路字段可能丢失。
3. 告警和检索规则不统一。
4. 后续迁移成本高。

正确方向：

```
log.info("create order success, orderId={}, requestId={}", orderId, requestId);
```
在本项目中，还要注意：

1. 日志文案使用英文。
2. 关键分支和异常场景要有日志。
3. 不输出敏感信息。
4. 与项目现有 `@Slf4j` 或 `CLogger` 用法保持一致。

什么时候是 Medium：

1. 公共组件不统一，但暂未直接造成故障。
2. 影响日志检索、监控接入、链路追踪、配置管理。
3. 多个模块各写一套工具逻辑。

什么时候可能是 Major：

如果因为组件使用不统一导致关键日志缺失、异常不可追踪、监控失效，影响线上故障定位，可能提高严重级别。

### 4. 缩进、格式、大段 lambda 可读性差

文档截图中的评论重点：

```
MINOR: 大段的 lambda 表达式，可读性差。大量的格式问题，如没有空格。
```
错误示例：

```
requests.forEach(request -> LogUtil.transactionAndThrow("Job","send",() -> {
CloseableHttpClient httpClient=HttpClientManager.getHttpClient();
String result=httpClient.execute(buildRequest(request),responseHandler);
return result;}));
```
问题：

1. 缩进错误导致代码结构不清晰。
2. 大段 lambda 让异常处理、资源关闭、返回值难以看清。
3. Review 时容易漏看关键逻辑。

标准评论：

```
MINOR: 这里 lambda 表达式过长且格式不规范，可读性较差，后续维护时不容易快速理解执行边界。
建议按项目格式化规范调整缩进和空格，并将复杂 lambda 提取为独立方法。
```
正确示例：

```
for (String request : requests) {
    sendRequest(request);
}

private String sendRequest(String request) {
    return LogUtil.transactionAndThrow("Job", "send", () -> {
        CloseableHttpClient httpClient = HttpClientManager.getHttpClient();
        return httpClient.execute(buildRequest(request), responseHandler);
    });
}
```
什么时候是 Minor：

1. 主要是缩进、空格、换行问题。
2. 逻辑本身简单，只是不好看。
3. 修复后不改变行为。

什么时候是 Medium：

1. lambda 里包含多层业务逻辑、异常处理、资源管理。
2. 可读性差到影响 Review 判断。
3. 同类格式问题大量出现，说明代码质量控制不足。

## 三、常见扩展 Medium / Minor 清单

### 1. 命名不表达业务含义

错误示例：

```
public void handle(String type, String flag, Map<String, Object> map) {
}
```
标准评论：

```
MINOR: 当前变量命名过于泛化，不能表达业务含义，阅读时需要反复追上下文。
建议使用能体现业务语义的命名，例如 operationType、needRetry、orderContext 等。
```
如果这是核心流程入口，参数又多又弱语义，可能升到 Medium 或 Major。

### 2. 重复代码未抽取

错误示例：

```
if (order.getPassenger() != null && order.getPassenger().getName() != null) {
    name = order.getPassenger().getName();
}

if (refund.getPassenger() != null && refund.getPassenger().getName() != null) {
    refundName = refund.getPassenger().getName();
}
```
标准评论：

```
MEDIUM: 这里存在重复的判空和取值逻辑，后续规则变更时容易漏改。
建议抽取通用方法或复用已有工具方法，保持同一业务规则只有一个实现位置。
```
### 3. 魔法值未抽常量或枚举

错误示例：

```
if ("T".equals(retryFlag)) {
}

if (status == 3) {
}
```
标准评论：

```
MEDIUM: 这里直接使用魔法值判断业务状态，可读性较差，也容易在多处复制后产生不一致。
建议抽取常量或枚举，并通过有业务语义的方法表达判断逻辑。
```
### 4. 注释缺失或注释与代码不一致

错误示例：

```
// 只查询成功订单
List<Order> orders = orderRepository.queryAll();
```
标准评论：

```
MINOR: 这里注释与实际代码行为不一致，容易误导后续维护者。
建议修正注释或调整代码逻辑，避免注释描述和实现偏离。
```
注释错误比没有注释更危险，因为它会让维护者相信错误的信息。

### 5. 单个方法过长但未到 Major

标准评论：

```
MEDIUM: 当前方法包含多段不同层次的逻辑，阅读成本较高。虽然暂未看到明显线上风险，但后续维护容易引入问题。
建议按校验、组装参数、调用下游、处理结果等步骤拆分私有方法。
```
### 6. 异常信息不利于排查

错误示例：

```
throw new RuntimeException("failed");
```
标准评论：

```
MEDIUM: 这里异常信息过于泛化，缺少关键业务上下文，线上排查时难以定位具体订单或调用链路。
建议补充必要的业务标识，并保留原始异常原因。
```
注意：日志和异常运行时文案按项目规范使用英文。

### 7. 测试覆盖不足

标准评论：

```
MEDIUM: 本次改动涉及状态判断/边界分支，但没有看到对应单测覆盖。后续修改时容易产生回归。
建议补充关键分支、异常场景和边界值测试。
```
如果改动的是支付、出票、退款等核心链路，缺测试也可能更严重。

## 四、Medium / Minor 快速判断口诀

```
能出事故看 Major；
影响维护看 Medium；
局部清洁看 Minor。
```
更具体一点：

```
废代码要删除，复杂条件要命名；
组件使用要统一，格式混乱要整理；
魔法值要枚举，重复逻辑要抽取；
注释不能骗人，测试覆盖关键分支。
```
## 五、答题时的注意点

1. Medium/Minor 不要写得像 Major 一样夸大线上事故。
2. 但也不要只写“建议优化”，要说明影响。
3. 同类问题命中一个典型点即可，不必重复刷评论。
4. 格式类问题如果非常多，可以合并评论。
5. 如果一个“可读性问题”出现在核心状态机、支付、退款、权限判断中，要重新判断是否可能升级为 Major。
