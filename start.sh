#!/bin/bash

# AIManage - 一键启动脚本 (Mac/Linux)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_success() { echo -e "${GREEN}[成功]${NC} $1"; }
print_error() { echo -e "${RED}[错误]${NC} $1"; }
print_info() { echo -e "${BLUE}[信息]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[警告]${NC} $1"; }

# 打印横幅
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║           AIManage - LLM 成本管理平台                    ║"
echo "║                    一键启动脚本                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python
print_info "检查 Python..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "未找到 Python，请先安装 Python 3.11+"
        echo "  Mac: brew install python@3.11"
        echo "  Ubuntu: sudo apt-get install python3.11"
        exit 1
    else
        PYTHON=python
    fi
else
    PYTHON=python3
fi
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION 已安装"

# 检查 Node.js
print_info "检查 Node.js..."
if ! command -v node &> /dev/null; then
    print_error "未找到 Node.js，请先安装 Node.js 18+"
    echo "  Mac: brew install node"
    echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION 已安装"

# 检查 MySQL
print_info "检查 MySQL..."
if ! command -v mysql &> /dev/null; then
    print_error "未找到 MySQL，请先安装 MySQL 8+"
    echo "  Mac: brew install mysql"
    echo "  Ubuntu: sudo apt-get install mysql-server"
    exit 1
fi
print_success "MySQL 已安装"

# 安装 Python 依赖
print_info "安装 Python 依赖..."
cd backend
if [ -f "requirements.txt" ]; then
    $PYTHON -m pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        print_error "Python 依赖安装失败"
        exit 1
    fi
    print_success "Python 依赖安装完成"
else
    print_warning "未找到 requirements.txt，跳过"
fi

# 安装 Node 依赖
print_info "安装 Node 依赖..."
cd ../frontend
if [ -f "package.json" ]; then
    npm install --silent
    if [ $? -ne 0 ]; then
        print_error "Node 依赖安装失败"
        exit 1
    fi
    print_success "Node 依赖安装完成"
else
    print_warning "未找到 package.json，跳过"
fi

# 创建数据库
print_info "配置数据库..."
cd ../backend

# 尝试创建数据库和用户
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS llm_cost CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'aimanage'@'localhost' IDENTIFIED BY 'aimanage123';
GRANT ALL PRIVILEGES ON llm_cost.* TO 'aimanage'@'localhost';
FLUSH PRIVILEGES;
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "数据库配置完成"
else
    print_warning "数据库配置可能失败，请检查 MySQL 连接"
fi

# 运行数据库迁移
print_info "运行数据库迁移..."
$PYTHON manage.py migrate --run-syncdb > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "数据库迁移完成"
else
    print_warning "数据库迁移可能失败，请检查数据库连接"
fi

# 导入价格数据
print_info "导入价格数据..."
$PYTHON manage.py seed_pricing > /dev/null 2>&1
print_success "价格数据导入完成"

# 创建管理员账号
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    创建管理员账号                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "默认管理员账号:"
echo "  邮箱: admin@aimanage.com"
echo "  密码: admin123456"
echo ""
echo "如果账号已存在，会自动跳过。"
echo ""

$PYTHON manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='admin@aimanage.com').exists():
    User.objects.create_superuser(email='admin@aimanage.com', password='admin123456', username='admin')
    print('[成功] 管理员账号创建成功')
else:
    print('[成功] 管理员账号已存在')
" 2>/dev/null

# 启动服务
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    启动服务                              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 启动后端
print_info "启动后端服务 (http://localhost:8000)..."
cd "$SCRIPT_DIR/backend"
$PYTHON manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# 启动前端
print_info "启动前端服务 (http://localhost:3000)..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

# 等待服务启动
print_info "等待服务启动..."
sleep 5

# 打开浏览器
print_info "正在打开浏览器..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:3000
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    启动完成！                            ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                          ║"
echo "║   前端地址: http://localhost:3000                         ║"
echo "║   后端地址: http://localhost:8000                         ║"
echo "║                                                          ║"
echo "║   管理员账号: admin@aimanage.com                         ║"
echo "║   管理员密码: admin123456                                 ║"
echo "║                                                          ║"
echo "║   按 Ctrl+C 停止所有服务                                 ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 捕获 Ctrl+C
trap 'echo ""; print_info "正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; print_success "服务已停止"; exit 0' INT

# 等待子进程
wait
