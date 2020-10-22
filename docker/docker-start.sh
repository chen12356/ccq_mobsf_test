#!/bin/bash
#项目绝对路径
REMOTE_DIR=$(dirname $(pwd))

#安装docker
function docker_install()
{
	echo "=====检查docker是否安装====="
	docker -v
	if [ $? -eq  0 ]; then
		echo "=====检测到docker已经安装==="
	else 
		echo "=====开始apt安装docker======"
        apt-get update -y
		apt-get install docker-io -y
		echo "======docker 安装完成======="
	fi
	echo "========启动docker=========="
	service docker start
	echo "=======docker启动完成======="
}

#检查镜像函数
function docker_pull_images()
{
    # 获取当前拥有的所有镜像
    existImages=(`docker images |awk '{print $1":"$2}' ""`) # 获取当前所有镜像
    # 获取镜像个数
    existImagesNum=${#existImages[@]}
	# 需要拉取的镜像
	declare -A needImages
	needImages=(
		[ubuntu:18.04]="ubuntu:18.04"
		[redis:latest]="redis:latest"
		[mysql:5.7.29]="mysql:5.7.29"
		[db:latest]="$(pwd)/db"
		[rds:latest]="$(pwd)/rds"
		[mobsf:latest]="$REMOTE_DIR"
	)
	needImagesNum=${#needImages[@]}
	# 查看镜像是否存在
	for image in ${!needImages[@]}; do
        isExist=0
        for (( j = 0; j < existImagesNum; j++ )); do
        	if [[ ${image}  =  ${existImages[$j]} ]] ;  then
        		isExist=1
        		break
        	fi
        done
        if [[ $isExist -eq 1 ]]; then
        	echo "======${image} 镜像存在"
        else
        	echo "=====${image} 镜像不存在"
      		# 拉取不存在的镜像
        	docker pull ${image}
		if [[ $? -eq 1 ]];then
			echo "=====拉取镜像失败,通过Dockerfile重新构建镜像:${image}===="
		docker build -t ${image} ${needImages[${image}]}

		fi
        fi
    done
}
docker_install
docker_pull_images


#创建容器网络和存储卷
docker network create --subnet=172.18.0.0/16 mobsf-net
docker volume create mobsf-rds
docker volume create mobsf-db

#启动 Redis 容器
docker run -d  \
       --name=rds \
       -v mobsf-rds:/data \
       --network=mobsf-net \
       --ip=172.18.0.20 \
       --restart=always \
       rds:latest

#启动 MySQL 容器
docker run -d \
       --name=db \
       -v mobsf-db:/var/lib/mysql \
       --network=mobsf-net \
       --ip=172.18.0.30 \
       -e MYSQL_ROOT_PASSWORD=123456 \
       --restart=always \
       db:latest
sleep 7
if docker logs db | grep "InitComplete">/dev/null
then
	#启动 Mobsf 容器
echo "数据库初始化完成..."
docker run -d \
       --name=mobsf \
       -v $REMOTE_DIR:/root/Mobile-Security-Framework-MobSF \
       --network=mobsf-net \
       --ip=172.18.0.10 \
       -p 8000:8000 \
       --restart=always \
       mobsf:latest
else
	echo "数据库初始化失败,手动建数据库,启动 MobSF 容器即可"
fi



