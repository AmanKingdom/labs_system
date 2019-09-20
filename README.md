# How to Use?

从0搭建可以参考：https://mp.weixin.qq.com/s/_-7YcSaN7K5_ISw1cjKr4Q

### 1、下载到你的服务器上：

  ```
  git clone https://github.com/AmanKingdom/labs_system.git
  ```

### 2、进入项目目录创建虚拟环境：

  ```
  cd labs_system
  virtualenv --python=/usr/bin/python venv
  ```

### 3、进入虚拟环境：

  ```
  source venv/bin/activate
  ```

### 4、安装依赖：
  
  ```
  pip intall -r requirements.txt
  ```

### 5、数据迁移：

  ```
  python manage.py migrate
  ```
> 这里的数据迁移需要对`labs_system`中的`settings.py`进行一些设置才能适配你的电脑使用，如果是不想用`mysql`则可以直接注释掉`mysql`段落，取消`sqlite3`段落的注释即可

### 6、启用`Django`提供的微型服务器：

  ```
  python manage.py runserver 0.0.0.0:8000
  ```
### 7、浏览器打开：公网`IP`：8000

