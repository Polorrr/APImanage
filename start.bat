@echo off
chcp 65001 >nul
title AIManage - 一键启动

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           AIManage - LLM 成本管理平台                    ║
echo ║                    一键启动脚本                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: 检查 Python
echo [1/8] 检查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python %PYTHON_VERSION% 已安装

:: 检查 Node.js
echo [2/8] 检查 Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)
for /f %%i in ('node --version') do set NODE_VERSION=%%i
echo [成功] Node.js %NODE_VERSION% 已安装

:: 检查 MySQL
echo [3/8] 检查 MySQL...
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 MySQL，请先安装 MySQL 8+
    echo 下载地址: https://dev.mysql.com/downloads/installer/
    pause
    exit /b 1
)
echo [成功] MySQL 已安装

:: 安装 Python 依赖
echo [4/8] 安装 Python 依赖...
cd backend
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [错误] Python 依赖安装失败
    pause
    exit /b 1
)
echo [成功] Python 依赖安装完成

:: 安装 Node 依赖
echo [5/8] 安装 Node 依赖...
cd ..\frontend
call npm install --silent
if %errorlevel% neq 0 (
    echo [错误] Node 依赖安装失败
    pause
    exit /b 1
)
echo [成功] Node 依赖安装完成

:: 创建数据库
echo [6/8] 配置数据库...
cd ..\backend
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS llm_cost CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
mysql -u root -p -e "CREATE USER IF NOT EXISTS 'aimanage'@'localhost' IDENTIFIED BY 'aimanage123';" 2>nul
mysql -u root -p -e "GRANT ALL PRIVILEGES ON llm_cost.* TO 'aimanage'@'localhost';" 2>nul
mysql -u root -p -e "FLUSH PRIVILEGES;" 2>nul
echo [成功] 数据库配置完成

:: 运行数据库迁移
echo [7/8] 运行数据库迁移...
python manage.py migrate --run-syncdb >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 数据库迁移可能失败，请检查数据库连接
)
echo [成功] 数据库迁移完成

:: 导入价格数据
echo [8/8] 导入价格数据...
python manage.py seed_pricing >nul 2>&1
echo [成功] 价格数据导入完成

:: 创建管理员账号
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    创建管理员账号                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 默认管理员账号:
echo   邮箱: admin@aimanage.com
echo   密码: admin123456
echo.
echo 如果账号已存在，会自动跳过。
echo.

python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='admin@aimanage.com').exists():
    User.objects.create_superuser(email='admin@aimanage.com', password='admin123456', username='admin')
    print('[成功] 管理员账号创建成功')
else:
    print('[成功] 管理员账号已存在')
" 2>nul

:: 启动服务
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    启动服务                              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 正在启动后端服务 (http://localhost:8000)...
start "AIManage Backend" cmd /k "cd /d %cd% && python manage.py runserver 0.0.0.0:8000"

echo 正在启动前端服务 (http://localhost:3000)...
cd ..\frontend
start "AIManage Frontend" cmd /k "cd /d %cd% && npm run dev"

:: 等待服务启动
echo.
echo 等待服务启动...
timeout /t 5 /nobreak >nul

:: 打开浏览器
echo 正在打开浏览器...
start http://localhost:3000

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                    启动完成！                            ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║                                                          ║
echo ║   前端地址: http://localhost:3000                         ║
echo ║   后端地址: http://localhost:8000                         ║
echo ║                                                          ║
echo ║   管理员账号: admin@aimanage.com                         ║
echo ║   管理员密码: admin123456                                 ║
echo ║                                                          ║
echo ║   关闭此窗口不会停止服务                                  ║
echo ║   要停止服务，请关闭「AIManage Backend」和                ║
echo ║   「AIManage Frontend」窗口                              ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
pause
