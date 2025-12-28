set shell := ["powershell.exe", "-c"]


default:
    @just --list

format FILE = ".":
    uv tool run black {{FILE}}

format-check FILE = ".":
    uv tool run black {{FILE}} --diff

dev:
    cd backend; uv run uvicorn main:app --reload --log-level info
