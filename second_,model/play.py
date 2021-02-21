from game import State
# from pv_mcts import pv_mcts_action
# from tensorflow.keras.models import load_model
from pathlib import Path
from threading import Thread
import tkinter as tk
import numpy as np
import torch
from network import Policy_Net

# 対戦相手のAIのモデル格納先を指定し、モデルをロード
model_path = "./model/model_cpu.pth"
model = Policy_Net()
model.load_state_dict(torch.load(model_path))

def predict(model, state):
    # 推論のための入力データのシェイプの変換
    x = np.array([state.pieces, state.enemy_pieces]).astype(np.float32)
    x = torch.from_numpy(x.reshape(1,2,15,15)).clone()
    policies = torch.nn.functional.softmax(model(x), dim=1).detach().numpy().copy()

    # 方策の取得
    policies = policies.squeeze()[list(state.legal_actions())] # 合法手のみ
    policies /= sum(policies) if sum(policies) else 1 # 合計1の確率分布に変換

    return policies

class GameUI(tk.Frame):
    # コンストラクタ
    def __init__(self, master=None, model=None):
        # Frameクラスを継承し、Frameクラスの初期処理を実行
        tk.Frame.__init__(self, master)
        self.master.title("グラフィックの描画")

        # 状態クラスからインスタンスを設定
        self.state = State()

        # AIの行動関数（方策）を指定
        self.next_action = predict(model, self.state)

        # 盤面の大きさを設定
        self.c = tk.Canvas(self, width=675, height=675, highlightthickness=0)

        # 左クリック操作を指定
        self.c.bind("<Button-1>", self.turn_of_human)

        # 描画
        self.c.pack()
        self.on_draw()

    def turn_of_human(self, event):
        # 終局時には描画のみした上でNoneを返す処理
        if self.state.is_done():
            self.state = State()
            self.on_draw()
            return
        
        # 先手じゃない場合はNoneを返す処理
        if not self.state.is_first_player():
            return

        # クリック位置を取得
        x = int(event.x/45)
        y = int(event.y/45)
        # 画面外ならNoneを返す処理
        # print(x, y)
        if x < 0 or 15 < x or y < 0 or 15 < y:
            return
        
        # クリックした位置に基づき行動（どこに打ったか）を取得
        action = x + y * 15
        print(action)

        # 選択した行動がルールに則ったものかチェック
        if not (action in self.state.legal_actions()):
            return
        
        # ある行動を取った後の状態を取得し、元の状態を更新・描画
        self.state = self.state.next(action)
        self.on_draw()

        # 描画処理を待つため1ミリ秒待機した後に後手に順番を移動
        self.master.after(1, self.turn_of_ai)
    
    def turn_of_ai(self):
        # 終局チェック
        if self.state.is_done():
            return
        
        # 状態に応じて次の行動を取得
        policies = predict(model, self.state)
        action = np.random.choice(self.state.legal_actions(), p=policies)
        print(action)
        # 行動に応じて次の状態を取得し、元の状態を更新・描画
        self.state = self.state.next(action)
        self.on_draw()

    def draw_piece(self, index, first_player):
        x = (index%15)*45+10
        y = int(index/15)*45+10
        if first_player:
            self.c.create_oval(x, y, x+25, y+25, width=0.0, fill="#333333")
        else:
            self.c.create_oval(x, y, x+25, y+25, width=0.0, fill="#FFFFFF")

    def on_draw(self):
        # 盤面の描画初期化
        self.c.delete("all")

        # 盤面の格子を描画
        self.c.create_rectangle(0,0,675,675,width=0.0,fill="#DEB887")
        for r in range(15):
            self.c.create_line(0,r*45,720,r*45, width=1.0, fill="#333333")
        for c in range(15):
            self.c.create_line(c*45, 0, c*45, 720, width=1.0, fill="#333333")
        self.c.create_text(337.5,337.5,text="真ん中", font="courier 10", anchor=tk.CENTER)

        # 現在の状況から石の配置を描画
        for i in range(225):
            if self.state.pieces[i] == 1:
                # print(self.state.pieces)
                self.draw_piece(i, self.state.is_first_player())
            if self.state.enemy_pieces[i] == 1:
                self.draw_piece(i, not self.state.is_first_player())

f = GameUI(model=model)
f.pack()
f.mainloop()