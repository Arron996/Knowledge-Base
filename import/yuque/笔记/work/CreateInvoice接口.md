#### createInvoice 接口

* renfe 同步返回票台结果 ： 成功（urlList）/失败
+ mq `train.global.rail.gds.booking.system.order.invoice.result`
+ body `OrderInvoiceResult``fileUrlList`发票链接
* iryos 发票结果由供应抛Q给email
* 退改会给发票状态置为失败
* 老票台退改抛消息，新票台处理，抛给订单消息
* renfe `"vatNumber": "74358844M"` 在renfe注册过税务信息

```
{
  "currency": "GBP",
  "uid": "_TRXX1hym6vvt2erl",
  "locale": "en_GB",
  "udl": "GB_90009",
  "clientMetaInfo": {
    "devOs": "ios",
    "appVersion": "82350000",
    "clientId": "50861104410000203992",
    "deviceId": "61A19350-A50B-48EC-A1DD-CAF0849F2DAD_iOS"
  },
  "channelMetaInfo": {
    "channel": "trainpal",
    "timestamp": 1733811475390
  },
  "orderId": 1134766010930620,
  "orderItemId": 70011065791,
  "invoiceProfile": {
    "address": {
      "country": "Italia",
      "province": "Torino",
      "city": "Torino",
      "address": "Awwwwwwww",
      "countryCode": "IT",
      "provinceCode": "TO",
      "houseNumbering": "012345",
      "postalCode": "10121",
      "streetType": "BORGO"
    },
    "personType": 1,
    "firstName": "Rocco",
    "lastName": "Hi",
    "fiscalCode": "PZZMTI02S28A662R",
    "certifiedMail": "Jinlinli@trip.com",
    "recipientCode": "",
    "vatNumber": "74358844M"
  }
}
```
supplier ='iryos' and invoice\_status in(-1,0) and order\_status = 600

```
{
  "currency": "GBP",
  "uid": "",
  "locale": "en_GB",
  "clientMetaInfo": {
    "devOs": "ios",
    "appVersion": "82350000",
    "clientId": "50861033291260519181",
    "deviceId": "A1456750-33E0-4FB4-96CE-959F8F682DB9_iOS"
  },
  "channelMetaInfo": {
    "channel": "trainpal",
    "timestamp": 1733730173210
  },
  "orderId": 1134766010919436,
  "orderItemId": 70011054646,
  "invoiceProfile": {
    "address": {
      "country": "Italia",
      "province": "Torino",
      "city": "Torino",
      "address": "Awwwwwwww",
      "countryCode": "IT",
      "provinceCode": "TO",
      "houseNumbering": "012345",
      "postalCode": "10121",
      "streetType": "BORGO"
    },
    "personType": 1,
    "firstName": "Rocco",
    "lastName": "Hi",
    "fiscalCode": "PZZMTI02S28A662R",
    "certifiedMail": "Jinlinli@trip.com",
    "recipientCode": ""
  }
}
```
