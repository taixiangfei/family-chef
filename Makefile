.DEFAULT_GOAL := help

.PHONY: help install install-front install-admin install-server \
	dev-h5 dev-weixin dev-admin dev-server migrate test lint check \
	build build-h5 build-weixin build-admin import-recipes

help:
	@printf '%s\n' \
		'Family Chef commands:' \
		'  make install         Install all project dependencies' \
		'  make dev-h5          Start the uni-app H5 frontend' \
		'  make dev-weixin      Start the WeChat Mini Program build' \
		'  make dev-admin       Start the management console' \
		'  make dev-server      Start the Django API' \
		'  make migrate         Apply Django database migrations' \
		'  make test            Run backend tests' \
		'  make lint            Run backend lint checks' \
		'  make check           Run all backend checks' \
		'  make build           Build H5, Mini Program and admin' \
		'  make import-recipes  Rebuild cookbook data from local sources'

install: install-front install-admin install-server

install-front:
	npm --prefix front install

install-admin:
	npm --prefix admin install

install-server:
	cd server && uv sync

dev-h5:
	npm --prefix front run dev:h5

dev-weixin:
	npm --prefix front run dev:mp-weixin

dev-admin:
	npm --prefix admin run dev -- --host 127.0.0.1

dev-server:
	cd server && uv run python manage.py runserver 127.0.0.1:8000

migrate:
	cd server && uv run python manage.py migrate

test:
	cd server && uv run pytest

lint:
	cd server && uv run ruff check .

check:
	cd server && uv run python manage.py check
	cd server && uv run python manage.py makemigrations --check
	cd server && uv run pytest
	cd server && uv run ruff check .

build: build-h5 build-weixin build-admin

build-h5:
	npm --prefix front run build:h5

build-weixin:
	npm --prefix front run build:mp-weixin

build-admin:
	npm --prefix admin run build

import-recipes:
	npm --prefix front run import:recipes
