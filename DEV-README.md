```
docker run --name cloudbeaver --rm -ti -p 8978:8978 -v /var/cloudbeaver/workspace:/opt/cloudbeaver/workspace -d dbeaver/cloudbeaver:latest
docker run --name mysql --rm -ti -p 3306:3306 -v /var/mysql/workspace:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=xyztxdys -d mysql

service redis-server start
```

```
CREATE TABLE `funboost_consume_results` (
  `_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `function` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `host_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `host_process` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `insert_minutes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `insert_time` datetime DEFAULT NULL,
  `insert_time_str` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `publish_time` float DEFAULT NULL,
  `publish_time_format` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `msg_dict` json DEFAULT NULL,
  `params` json DEFAULT NULL,
  `params_str` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `process_id` bigint DEFAULT NULL,
  `queue_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `result` text COLLATE utf8mb4_unicode_ci,
  `run_times` int DEFAULT NULL,
  `script_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `script_name_long` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `success` tinyint(1) DEFAULT NULL,
  `task_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `thread_id` bigint DEFAULT NULL,
  `time_cost` float DEFAULT NULL,
  `time_end` float DEFAULT NULL,
  `time_start` float DEFAULT NULL,
  `total_thread` int DEFAULT NULL,
  `utime` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exception` mediumtext COLLATE utf8mb4_unicode_ci,
  `rpc_result_expire_seconds` bigint DEFAULT NULL,
  `exception_type` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exception_msg` text COLLATE utf8mb4_unicode_ci,
  `rpc_chain_error_msg_dict` text COLLATE utf8mb4_unicode_ci,
  `run_status` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`_id`),
  KEY `idx_insert_time` (`insert_time`),
  KEY `idx_queue_name_insert_time` (`queue_name`,`insert_time`),
  KEY `idx_params_str` (`params_str`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
```