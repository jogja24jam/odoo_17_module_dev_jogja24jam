WEB_DB_NAME = skripsi_odoo_development
DOCKER = docker
DOCKER_COMPOSE = ${DOCKER} compose
CONTAINER_ODOO = odoo
CONTAINER_DB = odoo-postgres

help:
	@echo ""
	@echo "===============   Makefile for Odoo 17 Module Development   ==============="
	@echo "Available commands:"
	@echo "  start				 Start the Odoo and PostgreSQL containers"
	@echo "  stop				 Stop the Odoo and PostgreSQL containers"
	@echo "  restart			 Restart the Odoo and PostgreSQL containers"
	@echo "  console 			 Access the Odoo container shell"
	@echo "  psql				 Access the PostgreSQL database shell"
	@echo "  logs odoo			 View logs of the Odoo container"
	@echo "  logs db			 View logs of the PostgreSQL container"
	@echo "  addon <addon_name>	 	 Restart instance and update specified addon"
	@echo "	 graph			 	 Git Graph"

start:
	$(DOCKER_COMPOSE) up -d

stop:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

console:
	$(DOCKER) exec -it $(CONTAINER_ODOO) odoo shell --db_host=$(CONTAINER_DB) -d $(WEB_DB_NAME) -r $(CONTAINER_ODOO) -w $(CONTAINER_ODOO)

psql:
	$(DOCKER) exec -it $(CONTAINER_DB) psql -U $(CONTAINER_ODOO) -d $(WEB_DB_NAME)

define log_target
	@if [ "$(1)" = "odoo" ]; then \
		$(DOCKER_COMPOSE) logs -f $(CONTAINER_ODOO); \
	elif [ "$(1)" = "db" ]; then \
		$(DOCKER_COMPOSE) logs -f $(CONTAINER_DB); \
	else \
		echo "Invalid logs target. Use 'make logs odoo' or 'make logs db'."; \
	fi
endef

logs:
	$(call log_target,$(word 2,$(MAKECMDGOALS)))

define upgrade_addon
	$(DOCKER) exec -it $(CONTAINER_ODOO) odoo \
		--db_host=$(CONTAINER_DB) \
		-d $(WEB_DB_NAME) \
		-r $(CONTAINER_ODOO) \
		-w $(CONTAINER_ODOO) \
		-u $(1)
endef

addon: restart
	$(call upgrade_addon,$(word 2,$(MAKECMDGOALS)))


#git
graph:
	git log --graph --oneline --all --decorate

.PHONY: start stop restart console psql logs odoo db addon graph
