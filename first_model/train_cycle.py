# パッケージのインポート
from dual_network import dual_network
from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# デュアルネットワークの作成
dual_network()

# for i in range(10):
#     print('Train',i,'====================')
# セルフプレイ部
self_play()

# ネットワーク訓練部
train_network()

# パラメータ更新部
evaluate_network()

# # ベストプレイヤーの評価
# if update_best_player:
#     evaluate_best_player()