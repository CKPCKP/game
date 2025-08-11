import pyxel

class InputManager:
    """
    キー設定をまとめて管理し、
    アクション名でボタン状態を取得できるクラス
    """
    def __init__(self, key_map=None):
        # デフォルトのキー割り当て
        default_map =  {
            "left":    [pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT],
            "right":   [pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT],
            "up":      [pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP],
            "down":    [pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN],
            "jump":    [pyxel.KEY_SPACE, pyxel.GAMEPAD1_BUTTON_A],
            "shoot":   [pyxel.KEY_Z, pyxel.GAMEPAD1_BUTTON_X],
            "transform": [pyxel.KEY_X, pyxel.GAMEPAD1_BUTTON_Y],
            "confirm": [pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A],
            "pause":   [pyxel.KEY_P, pyxel.GAMEPAD1_BUTTON_START],
            "restart": [pyxel.KEY_R, pyxel.GAMEPAD1_BUTTON_RIGHTSTICK],
            "delete": [pyxel.KEY_C, pyxel.GAMEPAD1_BUTTON_GUIDE]
        }
       # デフォルト＋外部上書きを統合
        combined = {**default_map, **(key_map or {})}
        # 各アクションのキーをリスト化して統一
        self.key_map = {
           action: list(keys) if isinstance(keys, (list, tuple, set)) else [keys]
           for action, keys in combined.items()
        }

    def set_key(self, action: str, key: int):
        """特定アクションのキーを変更する"""
        if action not in self.key_map:
            raise KeyError(f"Unknown action: {action}")
        # 単一キーまたはリストで設定可能
        if isinstance(key, (list, tuple, set)):
            self.key_map[action] = list(key)
        else:
            self.key_map[action] = [key]

    def btn(self, action: str) -> bool:
        """
        押しっぱなし判定
        例: input_mgr.btn("left")
        """
        keys = self.key_map.get(action)
        if keys is None:
            raise KeyError(f"Unknown action: {action}")
        return any(pyxel.btn(k) for k in keys)

    def btnp(self, action: str) -> bool:
        """
        押した瞬間判定
        例: input_mgr.btnp("jump")
        """
        keys = self.key_map.get(action)
        if keys is None:
            raise KeyError(f"Unknown action: {action}")
        return any(pyxel.btnp(k) for k in keys)

    def get_horizontal(self) -> int:
        """
        横方向の入力量を -1, 0, +1 で返す
        左: -1, 右: +1
        """
        dx = 0
        if self.btn("left"):
            dx -= 1
        if self.btn("right"):
            dx += 1
        return dx

    def get_vertical(self) -> int:
        """
        縦方向の入力量を -1, 0, +1 で返す
        上: -1, 下: +1
        """
        dy = 0
        if self.btn("up"):
            dy -= 1
        if self.btn("down"):
            dy += 1
        return dy