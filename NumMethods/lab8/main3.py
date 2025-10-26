import numpy as np
import matplotlib.pyplot as plt


def f(x, y, z):
    return z, 2 * z - y + 3 * np.exp(x)


def solve_shooting_method(a, b, h, alpha, beta):
    n = int((b - a) / h) + 1
    x = np.linspace(a, b, n)
    y = np.zeros(n)
    z = np.zeros(n)
    y[0] = alpha
    z[0] = beta

    for i in range(1, n):
        k1, l1 = f(x[i - 1], y[i - 1], z[i - 1])
        k2, l2 = f(x[i - 1] + h / 2, y[i - 1] + h / 2 * k1, z[i - 1] + h / 2 * l1)
        k3, l3 = f(x[i - 1] + h / 2, y[i - 1] + h / 2 * k2, z[i - 1] + h / 2 * l2)
        k4, l4 = f(x[i - 1] + h, y[i - 1] + h * k3, z[i - 1] + h * l3)
        y[i] = y[i - 1] + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        z[i] = z[i - 1] + h / 6 * (l1 + 2 * l2 + 2 * l3 + l4)

    return x, y


alpha = 2
beta = 3

x, y = solve_shooting_method(0, 1, 0.05, alpha, beta)
print("x =", x)
print("y =", y)

plt.plot(x, y)
plt.xlabel('x')
plt.ylabel('y')
plt.title('shooting method y\'\' - 2y\' + y = 3*exp(x)')
plt.grid(True)
plt.show()
