import math
import matplotlib
# seaborn
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    n = 8
    x = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    y = [0.96, 2.07, 1.96, 2.62, 3.75, 4.12, 3.98, 3.63, 4.70]
    x_a = (x[0] + x[n]) / 2
    print("x_a: ", x_a)
    x_g = math.sqrt(x[0] * x[n])
    print("x_g: ", x_g)
    x_h = 2 / ((1 / x[0]) + (1 / x[n]))
    print("x_h: ", x_h)
    y_a = (y[0] + y[n]) / 2
    y_g = math.sqrt(y[0] * y[n])
    y_h = 2 / ((1 / y[0]) + (1 / y[n]))
    z_x_a = 2.16
    z_x_g = 1.91
    z_x_h = 1.537

    delt1 = abs(z_x_a - y_a)
    delt2 = abs(z_x_g - y_g)
    delt3 = abs(z_x_a - y_g)
    delt4 = abs(z_x_g - y_a)
    delt5 = abs(z_x_h - y_a)
    delt6 = abs(z_x_a - y_h)
    delt7 = abs(z_x_h - y_h)
    delt8 = abs(z_x_h - y_g)
    delt9 = abs(z_x_g - y_h)
    del_array = [delt1, delt2, delt3, delt4, delt5, delt6, delt7, delt8, delt9]
    min_del = 1000
    min_ind = 0
    for i in range(0, 9):
        # print("delta", i+1, " ", del_array[i])
        if del_array[i] < min_del:
            min_ind = i + 1
            min_del = del_array[i]

    print("min delta", min_ind, min_del)
    x_log = [math.log(i) for i in x]
    sum_lnx = sum(x_log)
    x_log_2 = [(math.log(i)) ** 2 for i in x]
    sum_lnx_2 = sum(x_log_2)

    sum_lnx_y = 0
    for i in range(len(x)):
        sum_lnx_y += math.log(x[i]) * y[i]

    sum_y_i = sum(y)
    m = 9
    a = (m * sum_lnx_y - sum_lnx * sum_y_i) / (m * sum_lnx_2 - sum_lnx ** 2)
    b = sum_y_i / m - (a * (sum_lnx)) / m

    print("a: " + str(a))
    print("b: " + str(b))
    print("z(x) = ", str(a) + "*ln(x) + " + str(b))

    plt.plot(x, y, color='green', marker='o', markersize=5)
    x = np.linspace(1, 5, 1000)
    f1 = np.log(x) * a + b
    plt.plot(x, f1)
    plt.show()
