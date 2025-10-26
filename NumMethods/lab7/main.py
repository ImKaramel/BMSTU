import math
import cmath
import matplotlib.pyplot as plt

N = 128
x = [j / N for j in range(N)]
y = [math.sin(2 * math.pi * xj) for xj in x]


def bnf_fft(y):
    r = int(math.log2(N))

    Aq = [[0] * N for _ in range(r + 1)]

    for j in range(N):
        j_bin = bin(j)[2:].zfill(r)
        Aq[0][j] = y[int(j_bin, 2)]

    for m in range(1, r + 1):
        for q in range(N):
            q_bin = bin(q)[2:].zfill(r)
            j_m = int(q_bin[m - 1], 2)

            Aq[m][q] = 0.5 * sum([
                cmath.exp(- 2 * cmath.pi * 1j * j_m * 2 ** (-m) * sum(
                    [int(q_bin[k - 1], 2) * 2 ** (k - 1)
                     for k in range(1, m + 1)])) * Aq[m - 1][q]
                for j_m in range(2 ** (m - 1))
            ])

    return Aq[r]


def main():
    Aq = [1 / N * sum([fj * cmath.exp(- 2 * cmath.pi * 1j * q * xj)
                       for xj, fj in zip(x, y)]) for q in range(N)]

    yf = [sum([Aq[q] * cmath.exp(2 * cmath.pi * 1j * q * xj)
               for q in range(N)]) for xj in x]
    plt.plot(x, [yfj.real for yfj in yf])

    Aq = bnf_fft(y)
    yf = [sum([Aq[q] * cmath.exp(2 * cmath.pi * 1j * q * xj)
               for q in range(N)]) for xj in x]

    plt.plot(x, [yfj.real for yfj in yf])
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
