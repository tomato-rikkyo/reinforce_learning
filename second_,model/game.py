# パッケージのインポート
import random
import math

# ゲーム状態
class State:
    # 初期化
    def __init__(self, pieces=None, enemy_pieces=None):
        # プレイヤーの石（Noneじゃなければ、そのまま、Noneなら[0]の配列(15*15)で初期化）
        self.pieces = pieces if pieces != None else [0] * 225
        # 相手プレイヤーの石
        self.enemy_pieces = enemy_pieces if enemy_pieces != None else [0] * 225

    # 石の数の取得
    def piece_count(self, pieces):
        count = 0
        for i in pieces:
            if i == 1:
                count +=  1
        return count

    # 負けかどうか判定
    def is_lose(self):
        # 5目並んでいるかどうかを判定
        def is_comp(x, y, dx, dy):
            for _ in range(5):
                # その場所が盤面外じゃないかどうか、その場所に相手の石がないかどうかをチェック
                if self.enemy_pieces[x+y*15] == 0:
                    return False
                x, y = x+dx, y+dy
            return True
        # 縦判定
        for r in range(11):
            for c in range(15):
                if is_comp(c, r, 0, 1):
                    return True
        # 横判定
        for r in range(15):
            for c in range(11):
                if is_comp(c, r, 1, 0):
                    return True
        # 斜め（右下）
        for r in range(11):
            for c in range(11):
                if is_comp(c, r, 1, 1):
                    return True
        # 斜め（左下）
        for r in range(11):
            for c in range(4, 15):
                if is_comp(c, r, -1, 1):
                    return True
        return False

    # 引き分けかどうか
    def is_draw(self):
        return self.piece_count(self.pieces) + self.piece_count(self.enemy_pieces) == 225

    # ゲーム終了かどうか
    def is_done(self):
        return self.is_lose() or self.is_draw()

    # 次の状態の取得
    def next(self, action):
        pieces = self.pieces.copy()
        pieces[action] = 1
        return State(self.enemy_pieces, pieces)

    # 合法手のリストの取得
    def legal_actions(self):
        actions = []
        for i in range(225):
            # 自分と相手の石の両方が置かれていない場所が石をおける場所
            if self.pieces[i] == 0 and self.enemy_pieces[i] == 0:
                actions.append(i)
        return actions

    # 先手かどうか（置いてある石の数が同数なら先手）
    def is_first_player(self):
        return self.piece_count(self.pieces) == self.piece_count(self.enemy_pieces)

    # 文字列表示
    def __str__(self):
        ox = ('o', 'x') if self.is_first_player() else ('x', 'o')
        str = ''
        for i in range(225):
            if self.pieces[i] == 1:
                str += ox[0]
            elif self.enemy_pieces[i] == 1:
                str += ox[1]
            else:
                str += '-'
            if i % 15 == 14:
                str += '\n'
        return str