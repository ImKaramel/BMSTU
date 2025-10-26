import math


def newton_method(x0, y0, eps):
    x = x0
    y = y0

    def f1(x, y):
        return math.sin(x + 1) - y - 1.2

    def f2(x, y):
        return -x + math.cos(y) - 2

   
    def df1_dx(x, y):
        return math.cos(x + 1)

    def df1_dy(x, y):
        return -1

    def df2_dx(x, y):
        return -1

    def df2_dy(x, y):
        return -math.sin(y)
    k = 0
    while True:
        f1_val = f1(x, y)
        f2_val = f2(x, y)
        df1_dx_val = df1_dx(x, y)
        df1_dy_val = df1_dy(x, y)
        df2_dx_val = df2_dx(x, y)
        df2_dy_val = df2_dy(x, y)

        det = df1_dx_val * df2_dy_val - df1_dy_val * df2_dx_val
        dx = (-f1_val * df2_dy_val + f2_val * df1_dy_val) / det
        dy = (-f2_val * df1_dx_val + f1_val * df2_dx_val) / det
        k += 1
        x += dx
        y += dy
        if abs(dx) < eps and abs(dy) < eps:
            break
    print(k)

    return x, y


def main():
    x0 = -3
    y0 = -2
    eps = 0.01
    solution = newton_method(x0, y0, eps)
    print("x =", solution[0])
    print("y =", solution[1])


if __name__ == "__main__":
    main()
