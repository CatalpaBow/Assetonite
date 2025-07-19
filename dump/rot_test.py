import quaternion
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Mockオブジェクトの定義（前回のコードから再利用）
class MockPhysics:
    def __init__(self):
        self.steer_angle = 0.5  # 例: ハンドル角度 (右に切る)
        self.wheel_angular_s = [10.0, 10.0, 0.0, 0.0] # 例: 各タイヤの角速度

class MockSM:
    def __init__(self):
        self.Physics = MockPhysics()

sm = MockSM()

def get_local_wheel_rotation_quaternions(sm_physics_steer_angle: float, sm_physics_wheel_angular_s: list,
                                        steer_lock_deg: float = 450.0, steer_ratio: float = 18.0,
                                        delta_time_s: float = 1/60.0) -> list:
    """
    前回のコードから関数を再掲
    """
    wheel_steer_angle_rad = -np.radians(sm_physics_steer_angle * steer_lock_deg) / steer_ratio
    local_wheel_quaternions = []
    roll_axis = np.array([1.0, 0.0, 0.0])
    steer_axis = np.array([0.0, 1.0, 0.0])

    for i, angular_speed in enumerate(sm_physics_wheel_angular_s):
        roll_angle_rad = -angular_speed * delta_time_s
        roll_q = quaternion.from_rotation_vector(roll_axis * roll_angle_rad)
        steer_q = quaternion.one
        if i < 2:
            steer_q = quaternion.from_rotation_vector(steer_axis * wheel_steer_angle_rad)
        
        combined_q = roll_q * steer_q
        local_wheel_quaternions.append(combined_q)
    return local_wheel_quaternions


def plot_rotated_axes(quaternion_list: list, title: str):
    fig = plt.figure(figsize=(12, 6))

    for i, q in enumerate(quaternion_list):
        ax = fig.add_subplot(1, len(quaternion_list), i + 1, projection='3d')
        ax.set_title(f"Wheel {i} Rotated Axes")
        ax.set_xlim([-1, 1]); ax.set_ylim([-1, 1]); ax.set_zlim([-1, 1])
        ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
        ax.set_aspect('equal', adjustable='box')

        # 元の軸（単位ベクトル）
        x_axis_orig = np.array([1, 0, 0])
        y_axis_orig = np.array([0, 1, 0])
        z_axis_orig = np.array([0, 0, 1])

        # numpy-quaternionでベクトルを回転させるための正しい方法
        # ベクトルを純粋なクォータニオンとして表現し、q * vector_q * q.inverse() を計算
        # q.inverse() は q.conjugate() / (q * q.conjugate()) と同じですが、
        # 単位クォータニオンの場合 q.inverse() == q.conjugate() なので、q.conjugate() を使ってもOK
        # あるいは q.rotate(vector) と同じ意味の q.as_quat().rotate_vectors(vector) も使えますが
        # ここでは純粋なクォータニオンとの乗算を示します。

        # ベクトルをクォータニオンに変換 (w=0)
        x_vec_q = quaternion.quaternion(0, x_axis_orig[0], x_axis_orig[1], x_axis_orig[2])
        y_vec_q = quaternion.quaternion(0, y_axis_orig[0], y_axis_orig[1], y_axis_orig[2])
        z_vec_q = quaternion.quaternion(0, z_axis_orig[0], z_axis_orig[1], z_axis_orig[2])

        # 回転の適用
        # q_rotated_vec = q * q_vec * q.inverse() の結果のベクター部分を取り出す
        x_axis_rotated_q = q * x_vec_q * q.inverse()
        y_axis_rotated_q = q * y_vec_q * q.inverse()
        z_axis_rotated_q = q * z_vec_q * q.inverse()

        # 回転後のベクトル成分を取り出す
        x_axis_rotated = x_axis_rotated_q.vec
        y_axis_rotated = y_axis_rotated_q.vec
        z_axis_rotated = z_axis_rotated_q.vec

        # 矢印を描画
        origin = [0, 0, 0]
        ax.quiver(*origin, *x_axis_rotated, color='r', length=0.8, arrow_length_ratio=0.2) # X軸
        ax.quiver(*origin, *y_axis_rotated, color='g', length=0.8, arrow_length_ratio=0.2) # Y軸
        ax.quiver(*origin, *z_axis_rotated, color='b', length=0.8, arrow_length_ratio=0.2) # Z軸

        # 軸ラベルの表示
        ax.text(x_axis_rotated[0]*1.1, x_axis_rotated[1]*1.1, x_axis_rotated[2]*1.1, 'X', color='r')
        ax.text(y_axis_rotated[0]*1.1, y_axis_rotated[1]*1.1, y_axis_rotated[2]*1.1, 'Y', color='g')
        ax.text(z_axis_rotated[0]*1.1, z_axis_rotated[1]*1.1, z_axis_rotated[2]*1.1, 'Z', color='b')

        # グリッド
        ax.grid(True)

    plt.tight_layout()
    plt.suptitle(title)
    plt.show()

if __name__ == "__main__":
    local_wheel_quaternions = get_local_wheel_rotation_quaternions(
        sm.Physics.steer_angle,
        sm.Physics.wheel_angular_s
    )
    plot_rotated_axes(local_wheel_quaternions, "Rotated Local Axes for Each Wheel")