.PHONY: up down logs seed migrate createsuperuser build restart clean

# 启动所有服务
up:
	docker-compose up -d
	@echo "✅ 服务已启动"
	@echo "   前端: http://localhost"
	@echo "   后端: http://localhost/api/"
	@echo "   管理: http://localhost/admin/"

# 停止所有服务
down:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f

# 查看后端日志
logs-backend:
	docker-compose logs -f backend

# 查看 Celery 日志
logs-celery:
	docker-compose logs -f celery-worker celery-beat

# 数据库迁移
migrate:
	docker-compose exec backend python manage.py migrate

# 创建超级用户
createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

# 导入价格种子数据
seed:
	docker-compose exec backend python scripts/seed_pricing.py

# 重新构建镜像
build:
	docker-compose build --no-cache

# 重启服务
restart:
	docker-compose restart

# 重建并重启
rebuild: build
	docker-compose up -d

# 清理（删除所有数据！慎用）
clean:
	docker-compose down -v
	@echo "⚠️  所有数据已删除（包括数据库）"

# 开发模式 — 只启动基础设施（MySQL + Redis）
dev-infra:
	docker-compose up -d mysql redis
	@echo "✅ MySQL + Redis 已启动"
	@echo "   后端: cd backend && python manage.py runserver"
	@echo "   前端: cd frontend && npm run dev"

# 进入后端容器
shell:
	docker-compose exec backend python manage.py shell

# 进入 MySQL
mysql:
	docker-compose exec mysql mysql -u llm_cost -pllm_cost123 llm_cost
