all: test docker-deploy

test:
	@echo "Start tests"
	@python manage.py test --settings pur_beurre_web.settings.test
	@echo "Tests finished"

docker-deploy:
	@echo "Start docker deployment"
	@chmod +x docker_deploy.sh
	@./docker_deploy.sh
	@echo "Deployment made !"