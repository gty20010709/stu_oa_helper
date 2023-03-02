# 一、组件说明

## 1. auto_schedule.py

用来调度主程序，本着人道主义精神，兼顾节能的目标，故安排调度计划如下：

| 星期     | 时间段          | 计划       |
| -------- | --------------- | ---------- |
| 周一至五 | 8 - 12; 14 - 18 | 10分钟一次 |
| 周六日   | 8 - 12; 14 - 18 | 20分钟一次 |

## 2. main.py

主程序，抓取OA的首页，将公告条目分离出来，逐条与数据库对比：

- 如果数据库中已有，则啥也不干；
- 如果没有，则用设定好的发件箱发给目标邮箱。同时将条目添加到数据库中，为了保持数据库的高效，每添加一条新的，就删除一条最旧的。

## 3. getConfig.py

用于读取配置文件 config.ini，并把配置提供给主程序

## 4. config.ini

配置文件，用于配置发件箱和收件箱。

# 二、使用说明

**推荐在虚拟环境中运行，此处的示例即是。**

运行前，先在 `config.ini` 中配置收发信箱。

```shell

python -m venv venv

# 激活虚拟环境的命令根据系统选取
source venv/bin/activate # linux
venv\Scripts\activate.bat # Windows CMD
venv\Scripts\Activate.ps1 # Windows PowerShell

pip install -r requirements.txt
playwright install

python auto_schedule.py

```

# 三、鸣谢

- ChatGPT : 帮我写了绝大多数代码。
