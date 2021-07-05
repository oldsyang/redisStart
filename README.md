将工作中使用过的Redis技巧分享出来

造数据的地方，没有考虑性能，因为是批量模拟数据

- app/api/modesl/model里的类方法均是造数据使用的

- 配置信息可以看deploy下的README.MD和supervisor.conf

- 接口查询，使用app/api/views/index.py,直接访问localhost:8081/yang/v1/docs