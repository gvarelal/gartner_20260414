# Makefile for Gartner Loan Supervisor ADK Agent

.PHONY: install playground deploy deploy-dry-run info lint

PROJECT ?= $(GOOGLE_CLOUD_PROJECT)
ifeq ($(PROJECT),)
  PROJECT := demo4events10
endif

REGION ?= us-east1

install:
	@echo "======================================================================"
	@echo "Syncing agent dependencies using uv..."
	@echo "======================================================================"
	uv sync

playground:
	@echo "======================================================================"
	@echo "Starting local agent playground..."
	@echo "======================================================================"
	uv run agents-cli playground

deploy:
	@echo "======================================================================"
	@echo "Deploying agent to Vertex AI Agent Runtime..."
	@echo "Project: $(PROJECT)"
	@echo "Region:  $(REGION)"
	@echo "======================================================================"
	uv run agents-cli deploy --project $(PROJECT) --region $(REGION) --no-confirm-project

deploy-dry-run:
	@echo "======================================================================"
	@echo "Dry-run: Deploying agent..."
	@echo "Project: $(PROJECT)"
	@echo "Region:  $(REGION)"
	@echo "======================================================================"
	uv run agents-cli deploy --dry-run --project $(PROJECT) --region $(REGION) --no-confirm-project

info:
	uv run agents-cli info

lint:
	uv run ruff check app/
