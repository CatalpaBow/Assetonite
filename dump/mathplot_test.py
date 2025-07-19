import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'Yu Gothic'
def main():
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]
    plt.plot(x, y)           # 折れ線グラフ
    plt.title("サンプル折れ線グラフ")
    plt.xlabel("X軸")
    plt.ylabel("Y軸")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()