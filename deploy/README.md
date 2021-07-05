Redis使用主从集群+哨兵集群模式部署

使用docker方式，在一台机器上完成上述模拟


# 配置文件

Master

```bash
bind 0.0.0.0
port 6379
daemonize yes
requirepass 123456

```

Slave-node1

```bash
port 6479  
daemonize yes
slaveof 127.0.0.1 6379
masterauth 123456
```


Slave-node2

```bash
port 6579  
daemonize yes
slaveof 127.0.0.1 6379
masterauth 123456
```

使用相同方式，复制三台为哨兵（也是单个的Redis实例）

sentinel1

```bash
port 26379  
dir ./26379
logfile "26379.log"

sentinel monitor master 127.0.0.1   6379  2 
sentinel auth-pass mymaster 123456
//让哨兵在后台运行
daemonize yes
```

sentinel2

```bash
port 26380  
dir ./26380
logfile "26380.log"

sentinel monitor master 127.0.0.1   6379  2 
sentinel auth-pass mymaster 123456
//让哨兵在后台运行
daemonize yes
```

sentinel3

```bash
port 26381  
dir ./26381
logfile "26381.log"

sentinel monitor master 127.0.0.1  6379  2 

sentinel auth-pass mymaster 123456
//让哨兵在后台运行
daemonize yes
```

# 手动启动

```bash
./redis-server ./redis.conf
./redis-server ./redis-node1.conf
./redis-server ./redis-node2.conf

./redis-server ./sentinel1.conf --sentinel
./redis-server ./sentinel2.conf --sentinel
./redis-server ./sentinel3.conf --sentinel

# 或者是 
redis-sentinel ./sentinel1.conf
redis-sentinel ./sentinel2.conf
redis-sentinel ./sentinel3.conf
```

# supervisor启动

详情见supervisor.conf
