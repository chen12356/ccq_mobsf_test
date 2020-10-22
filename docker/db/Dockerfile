FROM mysql:5.7.29

#设置免密登录
ENV MYSQL_ALLOW_EMPTY_PASSWORD yes

VOLUME /var/lib/mysql
#将所需文件放到容器中
COPY setup.sh setup.sh
COPY init.sql init.sql

#设置容器启动时执行的命令
CMD bash setup.sh
