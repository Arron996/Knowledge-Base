使用方式：

1. 先不要看答案文件。
2. 每题判断问题级别：Major / Medium / Minor / No Issue。
3. 写出你的 Review 评论，尽量包含：问题是什么、影响是什么、怎么改。
4. 再对照 `code-review-practice-answers.md`。

## 题目 1：线程池

```
public class TicketExportService {

    private static final ExecutorService EXECUTOR = Executors.newFixedThreadPool(10);

    public void export(List<Long> orderIds) {
        for (Long orderId : orderIds) {
            EXECUTOR.submit(() -> exportOne(orderId));
        }
    }
}
```
请判断级别并写 Review 评论。

```
Major：异步线程池使用Exceutor，
Exceutor使用无界队列，任务过多会导致队列超长，最终会导致OOM，
应该改用ThreadPool线程池，并且配置核心、最大线程数，有界等待队列，拒绝策略，将线程池交个配置类和公共资源组件管理，项目中统一管理 复用
```
## 题目 2：异步等待

```
public OrderDetail query(Long orderId) throws Exception {
    Future<OrderDetail> future = executor.submit(() -> supplierClient.query(orderId));
    return future.get();
}
```
请判断级别并写 Review 评论。

```
major： 异步线程get未添加超时时间，下游查询超时或者一直阻塞会导致当前线程阻塞，线程数耗尽，引发一些列事故
未添加超时逻辑会导致线程阻塞
应该添加超时时间 使用future.get(timeout,TimeUnit)并且处理TimeOutException,对超时任务处理返回
```
## 题目 3：多个条件判断

```
if (status == 1 || status == 2 || status == 3 || status == 6) {
    allowRefund(order);
}
```
请判断级别并写 Review 评论。

```
medium： 条件判断复杂,可读性可扩展性较差，新增状态容易漏改
多个条件判断会增加复杂度，难以阅读维护
应该使用集合set的形式判断或者在没姐
```
## 题目 4：敏感日志

```
log.info("create payment request={}", JsonUtils.toJson(paymentRequest));
```
其中 `paymentRequest` 包含手机号、证件号、银行卡后四位、支付 token。

请判断级别并写 Review 评论。

```
major：敏感信息未加密或者未做模糊处理直接打在日志文件中
会导致敏感信息泄露，
应该对关键信息脱敏处理
```
## 题目 5：无用代码

```
public List<FileInfo> getFileList(String batchId) {
    // return oldFileRepository.query(batchId);
    // TODO temporary keep old logic
    return newFileRepository.query(batchId);
}
```
请判断级别并写 Review 评论。

```
medium 无效代码应该移除而不是注释，todo没有标明负责人和解决时间
会导致误解和代码冗余
移除无效底代码，todo信息需要详细
```
## 题目 6：MQ 消费

```
public void consume(RefundMessage message) {
    refundClient.refund(message.getOrderId(), message.getAmount());
    refundRepository.insert(message.getOrderId(), message.getAmount());
}
```
请判断级别并写 Review 评论。

```
major 消费没有做空指针处理 缺少幂等
会导致空指针
空指针判断

```
## 题目 7：格式和 lambda

```
requests.forEach(request -> LogUtil.transactionAndThrow("Job","send",() -> {
CloseableHttpClient httpClient=HttpClientManager.getHttpClient();
String result=httpClient.execute(buildRequest(request),responseHandler);
return result;}));
```
请判断级别并写 Review 评论。

```
medium 使用lambda表达式 格式处理有问题
导致阅读困难，维护困难
使用标准统一换行格式
```
## 题目 8：事务中调用远程服务

```
@Transactional
public void createOrder(CreateOrderRequest request) {
    orderRepository.insert(request);
    supplierClient.createTicket(request);
    orderRepository.updateStatus(request.getOrderId(), "SUCCESS");
}
```
请判断级别并写 Review 评论。

```
major 数据库事务调用远程服务，供应接口慢会占用数据库连接，应该所有事务范围把供应商调用提前单独执行，
导致状态有问题
应该校
```
## 题目 9：组件不统一

```
public void processJob(String jobId) {
    System.out.println("start job " + jobId);
    CLogManager.info("job running, jobId=" + jobId);
    log.info("job success, jobId={}", jobId);
}
```
请判断级别并写 Review 评论。

```
medium 使用日志组件输出不统一
导致维护困难，排查问题困难
应该换成统一的标准日志输出方式
```
## 题目 10：资源关闭

```
public String download(String fileId) throws IOException {
    InputStream inputStream = fileClient.download(fileId);
    return IOUtils.toString(inputStream, StandardCharsets.UTF_8);
}
```
请判断级别并写 Review 评论。

```
major 读取文件没有关闭流
导致内存泄露
应该使用完毕最终需要关闭文件流  try-with-resources

```
## 题目 11：魔法值

```
if ("T".equals(order.getRetryFlag())) {
    retry(order);
}
```
请判断级别并写 Review 评论。

```
medium 使用了魔法值
明确声明一下常量

```
## 题目 12：权限校验

```
public OrderDetail queryOrder(Long orderId) {
    return orderRepository.queryById(orderId);
}
```
该接口面向用户端，用户传入订单号查询详情。

请判断级别并写 Review 评论。

```
major，未处理权限校验
导致数据泄露风险
添加数据权限校验
```
## 题目 13：异常处理

```
public void cancelOrder(Long orderId) {
    try {
        supplierClient.cancel(orderId);
    } catch (Exception e) {
        log.error("cancel supplier order failed, orderId={}", orderId, e);
    }
    orderRepository.updateStatus(orderId, "CANCELLED");
}
```
请判断级别并写 Review 评论。

```
major 更新状态取消异常仍会更新状态此处代码逻辑有误
应该update放在try里面
```
## 题目 14：命名

```
public void handle(String type, String f, Map<String, Object> map) {
    if ("1".equals(type) && "Y".equals(f)) {
        doSomething(map);
    }
}
```
请判断级别并写 Review 评论。

```
medium 使用了魔法值，函数参数命名模糊不准确
导致阅读性下降
应该声明提取一下常量，函数参数命名准确而不是宽泛
```
## 题目 15：全量查询

```
public void syncAllOrders() {
    List<Order> orders = orderRepository.queryAll();
    for (Order order : orders) {
        sync(order);
    }
}
```
订单表是核心大表，历史数据千万级。

请判断级别并写 Review 评论。

```
major 大表使用全量查询
导致严重性能问题
禁止全量查询，改用带索引的条件查询
```
## 题目 16：注释与代码不一致

```
// 查询已支付订单
List<Order> orders = orderRepository.queryByStatus(OrderStatus.CANCELLED);
```
请判断级别并写 Review 评论。

```
minor 注释代码不一致
导致误解
修改注释
```
## 题目 17：CompletableFuture 默认线程池

```
CompletableFuture<OrderDetail> future = CompletableFuture.supplyAsync(() -> {
    return supplierClient.queryOrder(orderId);
});
return future.join();
```
请判断级别并写 Review 评论。

```
major，使用了默认线程池，没有复用线程池
导致额外性能开销，维护管理困难
使用统一bean管理的复用线程池
join没有设置超时并使用 orTimeout/completeOnTimeout 等方式设置超时和失败处理。
```
## 题目 18：重复代码

```
if (order.getPassenger() != null && order.getPassenger().getName() != null) {
    passengerName = order.getPassenger().getName();
}

if (refund.getPassenger() != null && refund.getPassenger().getName() != null) {
    refundPassengerName = refund.getPassenger().getName();
}
```
请判断级别并写 Review 评论。

```
medium 重复代码
代码改动会导致遗漏引发问题
代码复用提取调用
```
## 题目 19：分布式锁

```
lock.lock(orderId);
processRefund(orderId);
lock.unlock(orderId);
```
请判断级别并写 Review 评论。

```
major 没有异常处理，
会导致异常没有释放锁的情况
try catch finally释放锁
```
## 题目 20：大方法

```
public void handle(String source, String operationType, String count,
                   String delete, String deduplicate, Map<String, String> param) {
    if ("T".equals(param.get("retry"))) {
        retry(param, count);
    } else if ("T".equals(delete)) {
        deleteData(param, count);
    } else {
        switch (operationType) {
            case "CREATE":
                create(param);
                break;
            case "UPDATE":
                update(param);
                break;
            case "REFUND":
                refund(param);
                break;
            default:
                throw new IllegalArgumentException("unsupported operation");
        }
    }
}
```
请判断级别并写 Review 评论。

```
medium 方法巨大 可阅读性差，参数多 cas讹夺 方法参数名称简单
维护困难
减少参数

```
