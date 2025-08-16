import re
import pyxel
import os
from flag_block import FlagBlock
from opening import Opening
from player import Player
from laser import Laser
from stage import Stage
from save_manager import load_slot
from config import (
    FPS,
    GRID_SIZE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRAVITY,
    JUMP_STRENGTH,
    PLAYER_SPEED,
    LASER_SPEED,
    LASER_LIFETIME,
    LASER_LENGTH,
    MAX_GRAVITY,
)
from save_manager import list_slots, load_slot, save_slot

DEATH_ANIMATION_FRAMES = FPS // 2
DEATH_SHAKE_AMPLITUDE = 2


class Game:
    ICON_MAP = {
        "<keyboard>": (2, 0, 128, 16, 16),
        "<gamepad>": (2, 16, 128, 16, 16),
    }
    def __init__(self, input_mgr, slot_index=None, slot_data=None):
        # window の初期化(pyxel.init)は menu.py で行われる
        pyxel.load("resources/pyxel_resource.pyxres")
        # ... 既存の player, stages, timers 初期化 ...
        self.input = input_mgr
        self.player = Player(self.input, GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE * 2)
        self.current_stage_index_x = 0
        self.current_stage_index_y = 10
        self.stages = self.load_stages("stage_map")
        self.paused = False
        self.menu_index = 0
        self.death_timer = 0
        self.current_slot = slot_index
        self.opening = None
        self.popup_active = False
        self.popup_timer = 0
        self.font = pyxel.Font("resources/umplus_j10r.bdf")
        self.gate_toggle = False
        self.end_flag = False
        if slot_data is None:
            self.start_popup_timer = FPS // 2
            self.start_popup_shown = False
        else:
            # ロード時はスキップ
            self.start_popup_timer = None
            self.start_popup_shown = True

        # menu.py から渡されたセーブスロット情報で新規 or ロード
        self.current_slot = slot_index
        if slot_data is None:
            self.new_game(self.current_slot)
        else:
            self._load_save_data(slot_data)
        pyxel.playm(2, loop = True)

    def load_stages(self, directory):
        stages = {}
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r") as file:
                    x, y = filename.removesuffix(".txt").split("-")
                    stages[(int(x), int(y))] = Stage(
                        file.read().splitlines(), int(x), int(y)
                    )
        return stages

    def update(self):
        if self.opening and self.opening.active:
            self.opening.update()
            return
        # 新規ゲーム開始時のみ 0.5秒後にジャンプチュートリアルを表示
        if self.start_popup_timer is not None and not self.start_popup_shown:
            self.start_popup_timer -= 1
            if self.start_popup_timer <= 0:
                self.popup_active = "jump"
                self.popup_text = "<keyboard> [SPACE] / <gamepad> (A)"
                self.popup_timer = 0
                self.start_popup_shown = True
                return
        if self.death_timer > 0:
            self.update_death_animation()
        else:
            if self.input.btnp("pause"):
                self.paused = not self.paused
            if self.paused:
                if self.update_pause_menu():
                    return True
            else:
                self.update_game()

    def update_game(self):
        if self.popup_active:
            if self.popup_timer >= 15 and \
                (
                    self.input.btnp("jump") or 
                    self.input.btnp("shoot") or 
                    self.input.btnp("transform") or 
                    self.input.btnp("confirm")
                ):
                self.popup_active = False
                self.player.animating = True
                self.popup_timer = 0
            else:
                self.popup_timer = min(self.popup_timer+1, 15)
            return

        if self.input.btnp("restart"):
            self.player.alive = False
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]

        if sum(b.absorbed for b in current_stage.collidables if isinstance(b, FlagBlock)): 
            self.gate_toggle ^= True
        
        current_stage.update(self.gate_toggle)

        if any(p.anim_timer > 0 for p in current_stage.potions):
        # Player.update などスキップして描画だけ
            return
        
        for p in current_stage.potions:
            if p.collected and p.anim_timer == 0 and not getattr(p, "popup_shown", False):
                pyxel.play(3, 57, resume=True)
                self.popup_active = p.type
                self.popup_timer = 0
                if p.type == "can_be_laser":
                    self.popup_text = "<keyboard> [X] / <gamepad> (Y)"
                else:
                    self.popup_text = "<keyboard> [Z] / <gamepad> (X)"
                p.popup_shown = True
                return

        # レーザー更新 & DeathBlock 衝突を検知
        for laser in self.player.lasers:
            laser.update(current_stage.collidables)
            if laser.hit_death and laser.state != "laser":
                self.player.alive = False
                break
        self.player.update(
            PLAYER_SPEED, JUMP_STRENGTH, GRAVITY, MAX_GRAVITY, current_stage.collidables
        )
        self.player.check_get_coin(current_stage.coins)
        self.player.check_get_potion(current_stage.potions)

        if (
            self.player.can_be_laser == "OK"
            and not self.player.laser
            and self.input.btnp("transform")
        ):
            self.player.be_laser(
                lambda x, y, direction, state: Laser(
                    x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED, state
                )
            )

        if (self.player.can_shoot_laser and self.input.btnp("shoot")):
            self.player.shoot_laser(
                lambda x, y, direction: Laser(
                    x, y, direction, LASER_LIFETIME, LASER_LENGTH, LASER_SPEED
                )
            )

        stage_changed = False
        # プレイヤーが画面の右端に到達したら次のステージに切り替え
        if (self.player.laser and self.player.laser.x > SCREEN_WIDTH) or (
            not self.player.laser and self.player.x > SCREEN_WIDTH - GRID_SIZE
        ):
            stage_changed = True
            self.current_stage_index_x = (self.current_stage_index_x + 1) % len(
                self.stages
            )
            self.player.x -= SCREEN_WIDTH - GRID_SIZE
            if self.player.laser:
                self.player.laser.change_stage("RIGHT")

        elif (self.player.laser and self.player.laser.x < 0) or (
            not self.player.laser and self.player.x < 0
        ):
            stage_changed = True
            self.current_stage_index_x = (self.current_stage_index_x - 1) % len(
                self.stages
            )
            self.player.x += SCREEN_WIDTH - GRID_SIZE
            if self.player.laser:
                self.player.laser.change_stage("LEFT")

        if (self.player.laser and self.player.laser.y > SCREEN_HEIGHT) or (
            not self.player.laser and self.player.y > SCREEN_HEIGHT - GRID_SIZE
        ):
            stage_changed = True
            self.current_stage_index_y = (self.current_stage_index_y + 1) % len(
                self.stages
            )
            self.player.y -= SCREEN_HEIGHT - GRID_SIZE
            if self.player.laser:
                self.player.laser.change_stage("DOWN")

        elif (self.player.laser and self.player.laser.y < 0) or (
            not self.player.laser and self.player.y < 0
        ):
            stage_changed = True
            self.current_stage_index_y = (self.current_stage_index_y - 1) % len(
                self.stages
            )
            self.player.y += SCREEN_HEIGHT - GRID_SIZE
            if self.player.laser:
                self.player.laser.change_stage("UP")

        if stage_changed:
            self.player.erase_inactive_laser(all=True)
            current_stage = self.stages[
                (self.current_stage_index_y, self.current_stage_index_x)
            ]
            current_stage.update(self.gate_toggle)

        # 死亡を検知してデスアニメーションを開始
        if not self.player.alive and self.death_timer == 0:
            pyxel.play(3, 60, loop=False, resume=True)
            self.death_timer = DEATH_ANIMATION_FRAMES

        # セーブポイントに触れたときだけ保存
        if self.current_slot is not None and getattr(self.player, "just_saved", False):
            self.save_to_disk()
            self.player.just_saved = False
            if (self.current_stage_index_y, self.current_stage_index_x) == (9, 31) and self.end_flag == False:
                self.popup_active = "demo_end"
                self.popup_text = "Demo is over.<br>Thank you for playing!!"
                self.popup_timer = 0
                self.end_flag = True

    def update_pause_menu(self):
        if self.input.btnp("up"):
            self.menu_index = (self.menu_index - 1) % 4
        if self.input.btnp("down"):
            self.menu_index = (self.menu_index + 1) % 4
        if self.input.btnp("confirm"):
            if self.menu_index == 0:  # Continue
                self.paused = False
            elif self.menu_index == 1:  # Options
                # オプション画面の処理を追加
                pass
            elif self.menu_index == 2:  # Title
                return True
            elif self.menu_index == 3:  # Quit
                pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        if self.opening and self.opening.active:
            self.opening.draw()
            return
        
        if self.popup_active:
            # ポップアップ中はプレイヤーアニメーションを停止
            self.player.animating = False
            self.draw_popup(self.popup_active)
            return

        if self.paused:
            self.draw_pause_menu()
        elif self.death_timer > DEATH_ANIMATION_FRAMES // 2:
            self.draw_death_animation()
        elif self.death_timer > 0:
            self.draw_death_animation(shake=0)
        else:
            self.draw_game()
    
    def draw_popup(self, type):
        # メッセージ
        if type == "jump":
            self.draw_game()
            w, h = 110, 72
            x = (SCREEN_WIDTH - w) // 2
            y = (SCREEN_HEIGHT - h) // 2
            # 背景（黒）
            pyxel.rect(x, y, w, h, 0)
            # 枠線（白）
            pyxel.rectb(x, y, w, h, 7)
            self.write_text("CENTER", self.popup_text, y + 8)
            pyxel.blt(
                x + 48,
                y + 24,
                0,
                48,
                32,
                GRID_SIZE,
                GRID_SIZE
            )
            pyxel.line(x + 53, y + 62, x + 53, y + 47, 7)
            pyxel.line(x + 59, y + 62, x + 59, y + 47, 7)
        if type == "can_shoot_laser":
            self.draw_game(player="smile")
            w, h = 96, 72
            x = (SCREEN_WIDTH - w) // 2
            y = (SCREEN_HEIGHT - h) // 2
            # 背景（黒）
            pyxel.rect(x, y, w, h, 0)
            # 枠線（白）
            pyxel.rectb(x, y, w, h, 7)
            self.write_text("CENTER", self.popup_text, y + 8)
            pyxel.blt(
                x + 48,
                y + 48,
                0,
                0,
                0,
                GRID_SIZE,
                GRID_SIZE
            )

            pyxel.line(x + 35, y + 35, x + 48, y + 48, 8)
        elif type == "can_be_laser":
            self.draw_game(player="smile")
            w, h = 96, 55
            x = (SCREEN_WIDTH - w) // 2
            y = (SCREEN_HEIGHT - h) // 2
            # 背景（黒）
            pyxel.rect(x, y, w, h, 0)
            # 枠線（白）
            pyxel.rectb(x, y, w, h, 7)
            self.write_text("CENTER", self.popup_text, y + 8)
            pyxel.blt(
                x + 16,
                y + 32,
                0,
                16,
                0,
                GRID_SIZE,
                GRID_SIZE
            )
            pyxel.blt(
                x + 40,
                y + 32,
                1,
                0,
                112,
                GRID_SIZE,
                GRID_SIZE
            )

            pyxel.line(x + 65, y + 47, x + 80, y + 32, 7)
        elif type == "demo_end":
            self.draw_game(player="smile")
            w, h = 200, 40
            x = (SCREEN_WIDTH - w) // 2
            y = (SCREEN_HEIGHT - h) // 2
            # 背景（黒）
            pyxel.rect(x, y, w, h, 0)
            # 枠線（白）
            pyxel.rectb(x, y, w, h, 7)
            # 中央揃えで英語テキストを表示
            self.write_text("CENTER", self.popup_text, y + 8)



    def new_game(self, slot_index):
        # 全ステージをリセットして Player を初期化
        self.current_stage_index_x = 0
        self.current_stage_index_y = 10
        for st in self.stages.values():
            st.reset()
        self.player = Player(self.input, GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE * 2)
        # プレイヤー初期位置を save_point に登録
        self.player.save_point = (0, 0, self.player.x, self.player.y)
        # 空データで即セーブ
        self.save_to_disk()
        self.opening = Opening(self.input)

    def _load_save_data(self, data):
        sp = data["save_point"]
        # セーブポイント＆ステージ復元
        self.current_stage_index_y, self.current_stage_index_x = sp["stage"]
        px, py = sp["pos"]
        px, py = sp["pos"]
        # セーブポイント座標をplayer.save_pointに登録
        self.player.save_point = (
            self.current_stage_index_x,
            self.current_stage_index_y,
            px,
            py,
        )
        # プレイヤーの画面上の位置を復元
        self.player.x = px
        self.player.y = py
        self.player.can_shoot_laser = data.get("player_can_shoot_laser")
        self.player.can_be_laser = "OK" if data.get("player_can_be_laser") else False
        # コイン復元
        for key, flags in data["collected_coins"].items():
            sy, sx = map(int, key.split("-"))
            stage = self.stages[(sy, sx)]
            for coin, collected in zip(stage.coins, flags):
                coin.collected = collected
                if collected:
                    self.player.collected_coins[coin] = "fixed"
            # ポーション復元
        for key, flags in data.get("collected_potions", {}).items():
            sy, sx = map(int, key.split("-"))
            stage = self.stages[(sy, sx)]
            for potion, collected in zip(stage.potions, flags):
                potion.collected = collected
                if collected:
                    # すでに取得済みとしてポップアップを抑制
                    potion.popup_shown = True
        self.gate_toggle = data.get("gate_toggle")

    def save_to_disk(self):
        data = {
            "save_point": {
                "stage": [self.current_stage_index_y, self.current_stage_index_x],
                "pos": [self.player.save_point[2], self.player.save_point[3]],
            },
            "player_can_shoot_laser": self.player.can_shoot_laser,
            "player_can_be_laser": self.player.can_be_laser,
            "collected_coins": {
                f"{y}-{x}": [coin.collected for coin in stage.coins]
                for (y, x), stage in self.stages.items()
            },
            "collected_potions": {
                f"{y}-{x}": [bool(p.collected) for p in stage.potions]
                for (y, x), stage in self.stages.items()
            },
            "gate_toggle": self.gate_toggle,
        }
        save_slot(self.current_slot, data)

    def draw_game(self, player=None):
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]
        current_stage.draw()
        if player == "smile":
            self.player.draw(look="smile")
        else:
            self.player.draw()

    def draw_pause_menu(self):
        self.write_text("CENTER", "PAUSE MENU", 120)
        options = ["Continue", "Options", "Back to Title", "Quit"]
        for i, option in enumerate(options):
            color = 7 if i != self.menu_index else 6
            self.write_text("CENTER", option, 160 + i * 15, color)

    def update_death_animation(self):
        # デスアニメーション処理（カウントダウンし、終了時にリスポーン）
        self.death_timer -= 1
        if self.death_timer == 0:
            slot_data = load_slot(self.current_slot)
            self._load_save_data(slot_data)
            self.player.revive()

    def draw_death_animation(self, shake=DEATH_SHAKE_AMPLITUDE):
        dx = pyxel.rndi(-shake, shake)
        dy = pyxel.rndi(-shake, shake)
        # オフセット付きでステージ＆プレイヤーを描画
        self.draw_game_with_offset(dx, dy)

    # オフセット付き描画用メソッド
    def draw_game_with_offset(self, offset_x, offset_y):
        current_stage = self.stages[
            (self.current_stage_index_y, self.current_stage_index_x)
        ]
        current_stage.draw(offset_x, offset_y)
        self.player.draw(offset_x, offset_y)
    
    def write_text(self, align: str, text: str, y: int = 10, col: int = 7, bg: int = 2):
        """指定した整列方法でテキストを描画する

        align: "LEFT", "CENTER", "RIGHT"
        text: 描画する文字列
        y: 縦位置（省略時は10）
        col: 色（省略時は7=白）
        """

        # タグ (<keyboard>, <gamepad> ...) を考慮した幅を計算
        # マークアップ (<keyboard>, <gamepad>, […], (…) ) を考慮した分割と幅計算
        FONT_HEIGHT = 10  # BDF フォントの高さ(px)。必要に応じて調整してください
        # ICON_MAP のキー、\[...\]、\(...\) をまとめてキャプチャ
        if "<br>" in text:
            lines = text.split("<br>")
            for i, line in enumerate(lines):
                # y オフセットを行数分だけずらして再帰呼び出し
                self.write_text(align, line, y + i * FONT_HEIGHT, col, bg)
            return
        pattern = r'(' + '|'.join(map(re.escape, self.ICON_MAP.keys())) + r'|\[.*?\]|\(.*?\))'
        tokens = re.split(pattern, text)

        widths = []
        for token in tokens:
            if token in self.ICON_MAP:
                # アイコン幅
                widths.append(self.ICON_MAP[token][3])
            elif token.startswith('[') and token.endswith(']'):
                # 四角ボックス：文字幅
                inner = token[1:-1]
                widths.append(self.font.text_width(inner))
            elif token.startswith('(') and token.endswith(')'):
                # 円枠：文字幅と高さの大きい方で直径を決定
                inner = token[1:-1]
                tw = self.font.text_width(inner)
                r = max(tw, FONT_HEIGHT) // 2
                widths.append(r * 2)
            else:
                # 通常テキスト
                widths.append(self.font.text_width(token))

        text_width = sum(widths)

        if align == "LEFT":
            x = 0
        elif align == "CENTER":
            x = (SCREEN_WIDTH - text_width) // 2
        elif align == "RIGHT":
            x = SCREEN_WIDTH - text_width
        else:
            raise ValueError("align は 'LEFT', 'CENTER', 'RIGHT' のいずれかで指定してください")

        # テキスト＆アイコンを順に描画
        # トークン順に描画
        for token, w in zip(tokens, widths):
            if token in self.ICON_MAP:
                img, u, v, pw, ph = self.ICON_MAP[token]
                pyxel.blt(x, y, img, u, v, pw, ph)
            elif token.startswith('[') and token.endswith(']'):
                # 四角枠
                inner = token[1:-1]
                pyxel.rect(x-1, y, w + 2, FONT_HEIGHT + 2, bg)
                pyxel.text(x, y, inner, col, self.font)
            elif token.startswith('(') and token.endswith(')'):
                # 円枠
                inner = token[1:-1]
                tw = self.font.text_width(inner)
                r = max(tw, FONT_HEIGHT) // 2
                cx = x + r
                cy = y + FONT_HEIGHT // 2
                pyxel.circ(cx - 1, cy, r, bg)
                # 中心揃えでテキスト
                tx = x + (r * 2 - tw) // 2
                pyxel.text(tx, y, inner, col, self.font)
            else:
                # 通常テキスト
                pyxel.text(x, y, token, col, self.font)

            x += w