# game

## How to mange project

install package

```shell
uv add ${new_module}
```

update .venv

```
uv sync
```

## How to develop

format

```shell
uv tool run ruff format .
```

install package for development

```shell
uv add --dev ${new_module}
uv sync --no-dev
```

保存先は`uv tool dir`で確認できます

## 怠惰な君へ

uv のインストール

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```
