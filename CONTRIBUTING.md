# Contributing

Gracias por contribuir al proyecto-semilla.

## Table of Contents
1. [Flujo recomendado](#flujo-recomendado)
2. [Estándares](#estándares)

## Flujo recomendado

1. Crea una rama desde `main`.
2. Instala herramientas:
   - `pip install -r requirements/dev.txt`
   - `pre-commit install`
3. Antes de abrir PR:
   - `make fmt`
   - `make lint`
   - `make typecheck`
   - `make test`

## Estándares

- Python 3.12+, Django 5+.
- Lógica de negocio en servicios, no en views.
- Modularidad estricta: evitar acoplamientos directos entre apps.

