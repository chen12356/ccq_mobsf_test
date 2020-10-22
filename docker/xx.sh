#!/bin/bash
if docker logs db | grep "InitComplete">/dev/null
then
	#启动 Mobsf 容器
docker run -d \
       --name=mobsf \
       -v $REMOTE_DIR:/root/Mobile-Security-Framework-MobSF \
       --network=mobsf-net \
       --ip=172.18.0.10 \
       -p 8000:8000 \
       --restart=always \
       mobsf:latest

else
	echo "数据库初始化失败,手动建数据库,单独启动 MobSF 容器即可"
fi