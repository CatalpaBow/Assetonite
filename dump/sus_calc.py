import numpy as np

# 上端・下端の座標
top = np.array([0.2005, 0.41825, -0.043160])
bottom = np.array([0.11121, -0.11753, 0.01839])

# ベクトルと長さ
damper_vec = top - bottom
damper_length = np.linalg.norm(damper_vec)

# 正規化（軸方向の単位ベクトル）
damper_dir = damper_vec / damper_length

# 垂直（Y方向）成分
vertical_component = abs(damper_dir[1])

print("ダンパー軸方向ベクトル:", damper_vec)
print("ダンパー長:", damper_length)
print("Y方向の動きの割合:", vertical_component)
