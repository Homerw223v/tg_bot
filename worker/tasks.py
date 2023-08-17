"""celery -A worker.celery worker --loglevel=info --concurrency=2  # Запуск  worker
-B # запускает переодичные задачи в определенное время                тоже самое только отдельно   -|                
celery -A worker.celery beat --loglevel=info запускает задачи запланированные в определенное время _|
--purge   # Удалит все задачи при запуске worker
--pool choose between processes or threads. 'solo, prefork, eventlet, gevent. prefork default'
sudo service redis-server restart  # Перезапускает сервер  Redis
sudo service redis-server status  # Проверяет статус Redis
redis-cli"""  # Запускает Redis
