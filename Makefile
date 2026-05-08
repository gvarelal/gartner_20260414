# Unified Makefile for Gartner Loan Processing ADK Agents

.PHONY: install playground deploy info lint

PROJECT ?= $(GOOGLE_CLOUD_PROJECT)
ifeq ($(PROJECT),)
  PROJECT := demo4events10
endif

REGION ?= us-east1

install:
	@echo "======================================================================"
	@echo "Syncing workspace dependencies using uv..."
	@echo "======================================================================"
	uv sync

playground:
	@echo "======================================================================"
	@echo "Starting local agent playground..."
	@echo "======================================================================"
	agents-cli playground

deploy:
	@echo "======================================================================"
	@echo "Deploying agent to Vertex AI Agent Runtime (Reasoning Engine)..."
	@echo "Project: $(PROJECT)"
	@echo "Region:  $(REGION)"
	@echo "======================================================================"
	agents-cli deploy --project $(PROJECT) --region $(REGION) --no-confirm-project

deploy-dry-run:
	@echo "======================================================================"
	@echo "Dry-run: Deploying agent..."
	@echo "Project: $(PROJECT)"
	@echo "Region:  $(REGION)"
	@echo "======================================================================"
	agents-cli deploy --dry-run --project $(PROJECT) --region $(REGION) --no-confirm-project

info:
	agents-cli info

lint:
	uv run ruff check agent/
