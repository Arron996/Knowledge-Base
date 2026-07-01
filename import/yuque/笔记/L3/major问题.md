本文基于《代码评审L3考试赋能》文档与其中截图识别内容整理，目标不是背答案，而是建立 Major 问题的判断框架：看到代码时，能快速判断它是否会引发线上事故、安全风险、资源耗尽或长期不可维护。

## 一、Major 问题的判断标准

Major 不是“代码不优雅”，而是“必须修复，否则有较高概率造成严重后果”的问题。

常见判断标准：

1. 是否可能导致线上故障：OOM、线程耗尽、接口长期阻塞、死锁、连接泄漏、数据库压垮。
2. 是否可能导致安全事故：密码硬编码、敏感信息泄露、权限绕过、SQL 注入、越权访问。
3. 是否可能导致数据错误：重复扣款、重复出票、状态错乱、消息重复消费不幂等、事务不一致。
4. 是否明显破坏可维护性：一个核心方法参数过多、分支过多、职责混乱，后续需求很难安全修改。
5. 是否违反基础工程红线：无界线程池、无超时阻塞、资源未关闭、异常被吞、关键流程无兜底。

考试答题建议：

```
问题是什么：指出具体代码位置和问题类型。
造成什么影响：说明线上风险、故障模式或安全后果。
修复建议：给出可落地的改法，不只说“优化一下”。
```
标准回答模板：

```
MAJOR: 这里存在 XXX 问题。当前实现会在 XXX 场景下导致 XXX 风险，例如 XXX。
建议改为 XXX，并补充 XXX 机制，避免线上出现 XXX。
```
## 二、文档中明确提到的 Major 问题

### 线程池使用问题：禁止直接使用 Executors 创建线程池

文档截图中的问题代码：

```
private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
```
标准评论：

```
MAJOR: 不能直接使用 Executors 创建线程池。Executors 的部分工厂方法默认使用无界队列或不受控的线程创建策略，在高并发或任务堆积时可能导致内存持续上涨、线程资源耗尽，最终引发 OOM 或服务不可用。
建议使用 ThreadPoolExecutor 显式配置 corePoolSize、maximumPoolSize、keepAliveTime、有界队列、ThreadFactory 和 RejectedExecutionHandler，并将线程池统一交由公共组件或配置类管理，避免参数写死和资源生命周期失控。
```
#### 为什么 Executors 危险

记住这句口诀：

```
池子有边界，队列有上限，拒绝有策略，线程有名字，生命周期有归口，任务有超时。
```
`Executors` 的几个常见坑：

|  |  |
| --- | --- |
| 方法 | 隐藏风险 |
| Executors.newFixedThreadPool(n) | 使用无界 LinkedBlockingQueue，任务堆积时可能 OOM |
| Executors.newSingleThreadExecutor() | 也是无界队列，单线程处理慢时任务无限堆积 |
| Executors.newCachedThreadPool() | 最大线程数接近无限，瞬时流量可能创建大量线程 |
| Executors.newScheduledThreadPool(n) | 延迟任务队列可能持续堆积，线程数和队列不可控 |

错误示例：

```
public class ExportService {

    private static final ExecutorService EXECUTOR = Executors.newFixedThreadPool(8);

    public void export(List<Long> orderIds) {
        for (Long orderId : orderIds) {
            EXECUTOR.submit(() -> exportOne(orderId));
        }
    }
}
```
问题分析：

1. `newFixedThreadPool` 背后是无界队列。
2. 如果 `orderIds` 很多，或者 `exportOne` 调下游很慢，任务会持续堆积。
3. 堆积的任务对象、入参、上下文会占用堆内存，最终可能 OOM。
4. 线程池是 `static`，没有统一关闭和监控，不知道什么时候创建、什么时候销毁。
5. 线程没有业务名称，线上看线程 dump 很难定位来源。

正确示例：

```
@Configuration
public class ExportThreadPoolConfig {

    @Bean(destroyMethod = "shutdown")
    public ThreadPoolExecutor exportExecutor() {
        return new ThreadPoolExecutor(
                8,
                16,
                60L,
                TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(500),
                new ThreadFactoryBuilder().setNameFormat("export-worker-%d").build(),
                new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }
}
```
使用时：

```
@Service
public class ExportService {

    @Resource
    private ThreadPoolExecutor exportExecutor;

    public void export(List<Long> orderIds) {
        for (Long orderId : orderIds) {
            exportExecutor.execute(() -> exportOne(orderId));
        }
    }
}
```
更完整的生产建议：

1. 线程池参数不要散落在业务类里，优先接入公司公共线程池组件或统一配置。
2. 队列必须有上限，防止“慢慢堆死”。
3. 拒绝策略不能默认无感知丢任务，必须符合业务语义。
4. 线程名必须能看出业务来源，方便定位。
5. 核心业务线程池要有监控：活跃线程数、队列长度、拒绝次数、执行耗时。
6. 异步任务如果需要结果，必须设置超时。
7. 不同业务不要混用一个线程池，避免互相拖垮。

#### 怎么在 MR 中快速识别

看到这些关键词要警觉：

```
Executors.newFixedThreadPool
Executors.newCachedThreadPool
Executors.newSingleThreadExecutor
Executors.newScheduledThreadPool
new Thread(...)
CompletableFuture.supplyAsync(...) 未指定 executor
parallelStream()
```
继续追问：

1. 队列是否有界？
2. 拒绝策略是什么？
3. 是否统一管理线程池？
4. 是否配置线程名？
5. 任务堆积时会发生什么？
6. 应用关闭时是否能优雅停止？
7. 异步任务失败和超时如何处理？

#### 让你印象深刻的类比

线程池就像餐厅后厨：

1. `corePoolSize` 是固定厨师数量。
2. `maximumPoolSize` 是最多能临时加多少厨师。
3. `queue` 是等餐队伍。
4. `RejectedExecutionHandler` 是队伍满了以后怎么办。
5. `ThreadFactory` 是每个厨师胸牌写什么名字。

`Executors.newFixedThreadPool` 的问题像是：餐厅只有 8 个厨师，但门口队伍没有长度限制，顾客可以无限排队。人越来越多，最终不是厨师崩，是餐厅被挤爆。

### 异步任务阻塞获取结果时未设置超时时间

文档截图中的问题代码：

```
return zip.blockingGet();
```
类似问题：

```
future.get();
completableFuture.get();
countDownLatch.await();
single.blockingGet();
mono.block();
```
标准评论：

```
MAJOR: 这里异步任务阻塞获取结果时没有设置超时时间。若下游接口慢、线程池任务堆积或异步任务异常未返回，当前线程会无限等待，可能导致请求线程被耗尽，进一步引发接口不可用或级联故障。
建议使用带超时时间的 get/await/blockingGet，并对 TimeoutException 做明确降级、失败返回或中断处理，同时补充日志和监控。
```
错误示例：

```
public OrderDetail queryOrderDetail(Long orderId) throws Exception {
    Future<OrderDetail> future = executor.submit(() -> remoteQuery(orderId));
    return future.get();
}
```
风险：

1. 下游不返回，当前线程永远卡住。
2. Web 容器线程被占满后，新请求无法处理。
3. 如果外层还有重试，会进一步放大流量，造成雪崩。
4. 故障恢复后，旧请求仍可能堆积执行，影响新流量。

正确示例：

```
public OrderDetail queryOrderDetail(Long orderId) {
    Future<OrderDetail> future = executor.submit(() -> remoteQuery(orderId));
    try {
        return future.get(3, TimeUnit.SECONDS);
    } catch (TimeoutException e) {
        future.cancel(true);
        log.warn("query order detail timeout, orderId={}", orderId, e);
        throw new BusinessException("query order detail timeout");
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        log.warn("query order detail interrupted, orderId={}", orderId, e);
        throw new BusinessException("query order detail interrupted");
    } catch (ExecutionException e) {
        log.warn("query order detail failed, orderId={}", orderId, e);
        throw new BusinessException("query order detail failed");
    }
}
```
RxJava 示例：

```
List<RoomAllDataEntity> result = zip
        .timeout(3, TimeUnit.SECONDS)
        .blockingGet();
```
CompletableFuture 示例：

```
OrderDetail detail = CompletableFuture
        .supplyAsync(() -> remoteQuery(orderId), executor)
        .orTimeout(3, TimeUnit.SECONDS)
        .exceptionally(ex -> {
            log.warn("query order detail failed, orderId={}", orderId, ex);
            return OrderDetail.empty(orderId);
        })
        .join();
```
识别口诀：

```
凡是等待，都要问多久；凡是异步，都要问失败怎么办。
```
### 敏感信息硬编码或配置明文存储

文档截图中的问题：

```
String password = QConfigHelper.getValue(JP_HOMESTAY_PASSWORD, A_YX_63_7_N_U);
```
评论指出：用户名、密码需要 KMS 化管理。

标准评论：

```
MAJOR: 这里存在敏感信息硬编码/明文配置问题。用户名、密码、Token、密钥等敏感信息不能直接写在代码或普通配置中，否则代码仓库、日志、配置平台或构建产物泄露时会直接造成安全风险。
建议统一接入 KMS/密钥管理服务，通过受控权限动态获取密钥，并避免在日志、异常、监控中输出敏感值。
```
错误示例：

```
public SftpClient createClient() {
    String username = "order_admin";
    String password = "P@ssw0rd123";
    return SftpClient.connect(host, username, password);
}
```
普通配置也可能不合规：

```
String password = config.get("sftp.password", "defaultPassword");
```
为什么危险：

1. 代码仓库有多人可见，密码传播范围不可控。
2. 历史 commit 很难彻底清除密钥。
3. 构建包、日志、异常栈、配置快照都可能泄露。
4. 密钥轮换困难，离职、供应商变更时风险更大。

正确示例：

```
public SftpClient createClient() {
    String username = kmsClient.getSecret("sftp.username");
    String password = kmsClient.getSecret("sftp.password");
    return SftpClient.connect(host, username, password);
}
```
更好的实践：

1. 密码、Token、私钥、AK/SK 全部走 KMS 或公司统一密钥平台。
2. 配置里只保存密钥引用，不保存密钥值。
3. 日志打印时脱敏。
4. 密钥支持定期轮换。
5. 默认值里不能放真实密钥。

MR 中看到这些要警觉：

```
password
secret
token
privateKey
accessKey
appSecret
Authorization
Bearer
Basic
AK/SK
```
标准回答增强版：

```
MAJOR: 这里把敏感凭证直接放在代码/普通配置中，属于安全红线问题。一旦代码仓库、配置平台或日志被非授权人员访问，凭证会直接泄露，可能导致下游系统被非法访问。
建议改为 KMS 化管理，只在运行时按权限读取密钥引用；同时检查日志、异常和监控中是否输出该敏感值，并补充密钥轮换方案。
```
### 核心方法参数过多、分支过多，需要重构设计

文档截图中的问题代码：

```
public void handle(String source,
                   String operationType,
                   String count,
                   String delete,
                   String deduplicate,
                   Map<String, String> param) throws Exception {
    if ("T".equals(param.get("retry"))) {
        retry(param, count);
    } else if ("T".equals(delete)) {
        deleteDataFromDB(param, count);
    } else {
        switch (operationType) {
            // ...
        }
    }
}
```
标准评论：

```
MAJOR: 该方法入参过多且分支复杂，多个业务动作被塞进同一个 handle 方法中，职责不清晰，可读性和可维护性较差。后续新增操作类型时容易继续堆叠 if-else/switch，修改一个分支可能影响其他流程。
建议封装请求对象表达业务语义，并按 operationType/retry/delete 等维度拆分为独立策略或处理器，通过策略模式进行路由，降低主流程复杂度。
```
为什么这是 Major：

不是所有“方法长”都是 Major。它成为 Major 的条件通常是：

1. 它在核心链路上。
2. 它包含多个业务动作。
3. 参数是弱语义字符串、布尔开关、Map。
4. 分支之间互相影响，新增需求会继续堆 if-else。
5. 出错后影响范围大，测试覆盖困难。

错误示例：

```
public void process(String type, String retry, String force, Map<String, String> params) {
    if ("Y".equals(retry)) {
        retry(params);
    } else if ("Y".equals(force)) {
        forceProcess(params);
    } else if ("CREATE".equals(type)) {
        create(params);
    } else if ("CANCEL".equals(type)) {
        cancel(params);
    } else if ("REFUND".equals(type)) {
        refund(params);
    }
}
```
正确方向一：封装参数对象

```
public class OperationCommand {

    private String operationType;
    private boolean retry;
    private boolean force;
    private Map<String, String> params;

    public boolean needRetry() {
        return retry;
    }
}
```
正确方向二：策略模式

```
public interface OperationHandler {

    boolean support(OperationCommand command);

    void handle(OperationCommand command);
}
```

```
@Service
public class RetryOperationHandler implements OperationHandler {

    @Override
    public boolean support(OperationCommand command) {
        return command.needRetry();
    }

    @Override
    public void handle(OperationCommand command) {
        // retry logic
    }
}
```

```
@Service
public class OperationDispatcher {

    @Resource
    private List<OperationHandler> handlers;

    public void dispatch(OperationCommand command) {
        OperationHandler handler = handlers.stream()
                .filter(item -> item.support(command))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("unsupported operation"));
        handler.handle(command);
    }
}
```
识别方法：

1. 方法参数超过 5 个，尤其是多个 `String`、`Boolean`、`Map`。
2. 方法名很泛：`handle`、`process`、`execute`、`doAction`。
3. `if-else` 和 `switch` 同时出现。
4. 业务标识靠字符串判断：`"T"`、`"Y"`、`"1"`、`"CREATE"`。
5. 一个方法里既做校验、查询、计算、落库、发消息、重试、删除。

## 三、可扩展的常见 Major 问题清单

下面这些不一定都在原文中出现，但在 L3 Code Review 和真实生产评审中很常见。

### 资源未关闭：连接、流、游标、锁没有释放

错误示例：

```
InputStream inputStream = fileClient.download(fileId);
String content = IOUtils.toString(inputStream, StandardCharsets.UTF_8);
return content;
```
问题：

1. `InputStream` 未关闭，可能导致文件句柄或连接泄漏。
2. 高并发下连接池耗尽，后续请求全部失败。

标准评论：

```
MAJOR: 这里获取 IO 资源后没有关闭，异常场景下会导致连接/文件句柄泄漏。高并发或长期运行后可能耗尽系统资源，导致接口不可用。
建议使用 try-with-resources 或 finally 保证资源关闭，并确认底层客户端连接能正确归还连接池。
```
正确示例：

```
try (InputStream inputStream = fileClient.download(fileId)) {
    return IOUtils.toString(inputStream, StandardCharsets.UTF_8);
}
```
### 分布式锁未在 finally 中释放

错误示例：

```
lock.lock(orderId);
process(orderId);
lock.unlock(orderId);
```
风险：`process` 抛异常后锁不释放，后续同订单永远无法处理。

标准评论：

```
MAJOR: 分布式锁释放没有放在 finally 中，业务处理抛异常时锁无法释放，可能导致订单长期阻塞或后续任务无法执行。
建议加锁成功后使用 try-finally 释放锁，并设置合理的锁超时时间和唯一 owner token，避免误删其他线程持有的锁。
```
正确示例：

```
boolean locked = lock.tryLock(orderId, 30, TimeUnit.SECONDS);
if (!locked) {
    throw new BusinessException("lock failed");
}
try {
    process(orderId);
} finally {
    lock.unlock(orderId);
}
```
### MQ 消费、支付、出票、退款等核心流程缺少幂等

错误示例：

```
public void consume(RefundMessage message) {
    refundClient.refund(message.getOrderId(), message.getAmount());
    refundRepository.saveRefundRecord(message);
}
```
风险：

1. MQ 至少一次投递，消息可能重复。
2. 消费失败重试可能重复退款。
3. 先调用外部退款，后保存记录失败，会出现状态不一致。

标准评论：

```
MAJOR: 该 MQ 消费逻辑缺少幂等控制。消息重复投递、消费超时重试或服务重启时可能重复执行退款/出票等核心动作，造成资金或订单状态错误。
建议基于业务唯一键建立幂等记录或状态机校验，核心动作执行前先判断是否已处理，并保证外部调用和本地状态更新的一致性。
```
正确方向：

```
public void consume(RefundMessage message) {
    String idempotentKey = message.getRefundId();
    if (refundRepository.existsSuccess(idempotentKey)) {
        return;
    }
    refundRepository.createProcessing(idempotentKey);
    try {
        refundClient.refund(message.getOrderId(), message.getAmount());
        refundRepository.markSuccess(idempotentKey);
    } catch (Exception e) {
        refundRepository.markFailed(idempotentKey);
        throw e;
    }
}
```
### 事务边界错误：本地事务和远程调用混在一起

错误示例：

```
@Transactional
public void createOrder(CreateOrderRequest request) {
    orderRepository.save(order);
    supplierClient.createTicket(order);
    orderRepository.updateStatus(order.getId(), "SUCCESS");
}
```
风险：

1. 远程调用很慢，会长时间占用数据库事务和连接。
2. 远程调用成功后本地事务回滚，外部已出票但本地无记录。
3. 本地成功后外部失败，状态可能不一致。

标准评论：

```
MAJOR: 这里在数据库事务中执行远程调用，事务边界过大。下游接口慢或超时时会长时间占用数据库连接，远程调用成功但本地事务回滚时还可能导致本地与外部系统状态不一致。
建议缩小本地事务范围，使用状态机/本地消息表/最终一致性方案编排远程调用，并补充失败补偿和重试机制。
```
正确方向：

```
@Transactional
public void createOrder(CreateOrderRequest request) {
    orderRepository.save(order);
    localMessageRepository.save(new CreateTicketMessage(order.getId()));
}
```
由异步任务或消息消费执行远程调用，并根据结果推进状态机。

### 异常被吞或只打印日志，导致调用方误判成功

错误示例：

```
public void cancelOrder(Long orderId) {
    try {
        supplierClient.cancel(orderId);
    } catch (Exception e) {
        log.error("cancel order failed, orderId={}", orderId, e);
    }
}
```
风险：

1. 下游取消失败，但上游认为成功。
2. 状态推进错误，造成订单状态和供应商状态不一致。
3. 没有重试或补偿，问题被隐藏。

标准评论：

```
MAJOR: 这里捕获异常后只打印日志，没有向上抛出、返回失败结果或触发补偿。调用方会误认为取消成功，可能导致本地订单状态与下游状态不一致。
建议根据业务语义明确失败处理策略：向上抛出异常、返回失败码、记录补偿任务或进入可重试状态，不能静默吞掉核心链路异常。
```
正确示例：

```
public void cancelOrder(Long orderId) {
    try {
        supplierClient.cancel(orderId);
    } catch (Exception e) {
        log.warn("cancel order failed, orderId={}", orderId, e);
        compensationRepository.saveCancelRetryTask(orderId);
        throw new BusinessException("cancel order failed");
    }
}
```
### 缺少接口超时、重试、限流、熔断，可能造成级联故障

错误示例：

```
TicketResponse response = httpClient.post(url, request);
```
如果看不到超时配置、重试策略、异常处理，要继续追。

标准评论：

```
MAJOR: 这里调用外部服务没有看到明确的连接超时、读取超时和失败处理策略。下游慢响应或不可用时，当前服务线程会持续阻塞，可能造成线程池耗尽并引发级联故障。
建议统一使用带超时、熔断、限流和重试控制的 HTTP/RPC 客户端；重试必须限制次数并结合幂等，避免故障时放大流量。
```
正确方向：

```
HttpRequestConfig config = HttpRequestConfig.builder()
        .connectTimeoutMillis(1000)
        .readTimeoutMillis(3000)
        .retryTimes(1)
        .build();
```
注意：重试不是越多越好。没有幂等的写操作不要随便自动重试。

### 大数据量一次性加载到内存，可能 OOM

错误示例：

```
List<Order> orders = orderRepository.queryAll();
for (Order order : orders) {
    process(order);
}
```
标准评论：

```
MAJOR: 这里一次性加载全量数据到内存，数据量增长后可能导致内存占用过高甚至 OOM，同时长时间处理会影响数据库和应用稳定性。
建议改为分页查询、游标流式处理或批任务分片处理，并限制单批数据量，补充执行进度和失败重试能力。
```
正确示例：

```
long lastId = 0L;
while (true) {
    List<Order> orders = orderRepository.queryByLastId(lastId, 500);
    if (orders.isEmpty()) {
        break;
    }
    for (Order order : orders) {
        process(order);
        lastId = order.getId();
    }
}
```
### SQL 或查询条件缺失，可能全表扫描或误更新

错误示例：

```
update order_detail set status = 'CANCELLED';
```
或：

```
List<Order> orders = orderRepository.queryByStatus(status);
```
但 `status` 为空时查询全表。

标准评论：

```
MAJOR: 这里更新/查询缺少关键条件或未校验入参为空，可能导致全表扫描、误更新或数据库压力突增。核心订单表一旦误更新会造成严重数据事故。
建议对关键查询参数做强校验，更新语句必须带业务主键/分片键/租户条件，并对影响行数做校验和监控。
```
正确方向：

```
if (CollectionUtils.isEmpty(orderIds)) {
    throw new IllegalArgumentException("orderIds is empty");
}
int affected = orderRepository.updateStatus(orderIds, targetStatus);
if (affected != orderIds.size()) {
    log.warn("update order status affected row mismatch, expected={}, actual={}", orderIds.size(), affected);
}
```
### 权限校验缺失或越权访问

错误示例：

```
public OrderDetail queryOrder(Long orderId) {
    return orderRepository.queryById(orderId);
}
```
风险：只要知道 `orderId`，就能查别人订单。

标准评论：

```
MAJOR: 查询订单详情时只根据 orderId 查询，没有校验当前用户/租户/渠道是否有权限访问该订单，存在越权访问风险。
建议在查询条件中加入用户身份、租户、渠道或权限范围校验，并对无权限访问返回明确错误，避免敏感订单信息泄露。
```
正确示例：

```
public OrderDetail queryOrder(Long orderId, Long userId) {
    Order order = orderRepository.queryByIdAndUserId(orderId, userId);
    if (order == null) {
        throw new BusinessException("order not found");
    }
    return convert(order);
}
```
### 日志泄露敏感信息

错误示例：

```
log.info("create payment request={}", JsonUtil.toJson(paymentRequest));
```
如果 `paymentRequest` 里包含证件号、手机号、银行卡、Token，就是风险。

标准评论：

```
MAJOR: 这里直接打印完整请求对象，可能包含手机号、证件号、支付信息、Token 等敏感字段，日志平台可见范围较广，存在敏感信息泄露风险。
建议只打印必要的业务定位字段，并对手机号、证件号、Token 等字段做脱敏或完全不输出。
```
正确示例：

```
log.info("create payment request, orderId={}, userId={}",
        request.getOrderId(), request.getUserId());
```
### 静态可变共享状态导致并发问题

错误示例：

```
private static BatchResultListener currentBatch;

public void start(BatchResultListener listener) {
    currentBatch = listener;
}
```
风险：

1. 多个请求互相覆盖。
2. 并发读写不可见。
3. 上一次任务的状态污染下一次任务。

标准评论：

```
MAJOR: 这里使用 static 可变字段保存业务状态，多请求或多任务并发执行时会互相覆盖，导致结果串单、状态污染或线程安全问题。
建议避免使用全局可变状态，将状态放入请求上下文、任务对象或持久化存储中；如确需共享，需要明确并发控制和生命周期管理。
```
### 缓存更新与数据库不一致

错误示例：

```
cache.put(orderId, newStatus);
orderRepository.updateStatus(orderId, newStatus);
```
如果 DB 更新失败，缓存已经变了。

标准评论：

```
MAJOR: 这里缓存和数据库更新顺序存在一致性风险。缓存先更新而数据库更新失败时，读请求会看到不存在或错误的状态，可能影响订单主流程判断。
建议以数据库为准，更新数据库成功后删除缓存或通过可靠消息异步刷新缓存，并设置合理过期时间，避免缓存长期脏读。
```
## 四、Code Review 时的 Major 搜索清单

拿到 MR 后，可以先扫这些关键词和模式。

### 并发与线程

```
Executors
new Thread
Thread.sleep
synchronized
parallelStream
CompletableFuture
Future.get
CountDownLatch.await
blockingGet
block()
static mutable field
```
重点问：

1. 线程池是否有界？
2. 等待是否有超时？
3. 并发写共享变量是否安全？
4. 任务失败是否可感知？

### 外部调用

```
httpClient
rpcClient
supplierClient
paymentClient
retry
timeout
fallback
```
重点问：

1. 是否设置连接超时和读取超时？
2. 是否有失败处理？
3. 写操作重试是否幂等？
4. 下游慢是否会拖垮本服务？

### 安全

```
password
secret
token
privateKey
accessKey
authorization
phone
idCard
passport
```
重点问：

1. 密钥是否 KMS 化？
2. 日志是否脱敏？
3. 接口是否做权限校验？
4. 是否有越权访问可能？

### 数据一致性

```
@Transactional
sendMessage
remote call
updateStatus
refund
pay
ticket
consume
```
重点问：

1. 本地事务和远程调用是否混用？
2. MQ 消费是否幂等？
3. 状态机是否允许非法跳转？
4. 失败后是否有补偿？

### 数据库与资源

```
queryAll
select *
update
delete
InputStream
OutputStream
Connection
lock
tryLock
```
重点问：

1. 是否可能全表扫描？
2. 是否可能误更新？
3. 资源是否关闭？
4. 锁是否 finally 释放？

## 五、Major 标准回答库

### 线程池

```
MAJOR: 这里直接使用 Executors 创建线程池，线程池队列/线程数/拒绝策略不可控，任务堆积时可能导致 OOM 或线程资源耗尽。建议使用 ThreadPoolExecutor 显式配置核心线程数、最大线程数、有界队列、线程命名和拒绝策略，并将线程池生命周期统一收口到配置类或公共组件中。
```
### 无超时阻塞

```
MAJOR: 这里调用 future.get/blockingGet/await 时没有设置超时时间。异步任务异常、下游慢响应或线程池堆积时，当前请求线程会无限等待，可能导致请求线程耗尽和级联故障。建议使用带超时时间的等待方式，并对 TimeoutException 做取消、降级、失败返回或补偿处理。
```
### 密钥硬编码

```
MAJOR: 这里存在敏感信息硬编码/明文配置问题。密码、Token、AK/SK 等凭证直接出现在代码或普通配置中，一旦代码仓库、配置平台或日志泄露，会造成安全事故。建议接入 KMS/密钥管理服务，只保存密钥引用，并避免日志输出敏感值。
```
### 核心方法复杂度过高

```
MAJOR: 该核心方法参数过多、分支过多，多个业务动作混在同一个方法中，职责不清晰，后续新增逻辑容易继续堆叠 if-else/switch，修改风险较高。建议封装业务请求对象，并通过策略模式/处理器拆分不同操作类型，降低主流程复杂度。
```
### 幂等缺失

```
MAJOR: 该核心动作缺少幂等控制。MQ 重复投递、接口重试或服务重启后可能重复执行退款/出票/支付等动作，导致资金或订单状态错误。建议基于业务唯一键建立幂等记录，执行前判断处理状态，并保证重复请求返回一致结果。
```
### 事务与远程调用混用

```
MAJOR: 这里在数据库事务中执行远程调用，事务边界过大。下游慢响应会长时间占用数据库连接，远程调用成功但本地事务回滚时还会造成跨系统状态不一致。建议缩小本地事务范围，通过本地消息表、状态机或补偿任务实现最终一致性。
```
### 异常吞掉

```
MAJOR: 这里捕获异常后只打印日志，没有向上抛出、返回失败或触发补偿，会导致调用方误认为处理成功，进而推进错误状态。建议根据业务语义明确失败处理方式，核心链路不能静默吞异常。
```
### 资源泄漏

```
MAJOR: 这里获取 IO/连接/锁等资源后没有保证释放，异常场景下可能导致连接、文件句柄或锁泄漏，长期运行会造成资源耗尽。建议使用 try-with-resources 或 try-finally 保证资源释放，并补充异常场景测试。
```
### 权限校验缺失

```
MAJOR: 这里只根据业务 ID 查询/操作数据，没有校验当前用户、租户或渠道权限，存在越权访问风险。建议在查询和操作条件中加入权限范围校验，并对无权限场景返回明确错误。
```
### 敏感日志

```
MAJOR: 这里直接打印完整请求/响应对象，可能包含手机号、证件号、支付信息或 Token 等敏感字段。日志平台可见范围较广，存在信息泄露风险。建议只打印必要定位字段，并对敏感字段脱敏或禁止输出。
```
## 六、考试时怎么提高 Major 命中率

建议按这个顺序看 MR：

1. 先看新增入口：Controller、RPC、MQ Consumer、Job、定时任务。
2. 再看核心业务动作：支付、出票、退款、取消、改签、库存、状态更新。
3. 搜索高危关键词：`Executors`、`get()`、`blockingGet`、`password`、`@Transactional`、`sendMessage`、`queryAll`。
4. 对每个异步和远程调用问：有没有超时？失败怎么办？能否重复执行？
5. 对每个状态变更问：是否幂等？是否事务一致？是否有补偿？
6. 对每个大方法问：它是不是在用分支硬撑多个业务？

考试评论不要只写：

```
线程池有问题。
```
要写成：

```
MAJOR: 这里直接使用 Executors.newFixedThreadPool 创建线程池，底层使用无界队列。任务处理慢或流量突增时，请求会无限堆积在队列中，可能导致内存持续上涨甚至 OOM。
建议使用 ThreadPoolExecutor 显式配置有界队列、拒绝策略、线程命名和监控，并将线程池统一交由配置类或公共线程池组件管理。
```
## 七、一句话记忆

```
线程池怕无界，异步怕无超时，密钥怕明文，核心流程怕不幂等，事务怕套远程，异常怕吞掉，资源怕不关，权限怕不校验，大方法怕全都管。
```
这句话可以作为 Major 扫描口诀。看到其中任何一类，不要只停留在“代码风格不好”，要继续写出它的线上后果和修复建议。

