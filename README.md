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

run

```shell
uv run pyxel run game1.py
```

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

## How to build for Steam

```shell
$ uv run pyinstaller --onefile \
--add-data "resources:resources" \
--add-data "stage_map:stage_map" \
menu.py
```
