import sys
import multiprocessing
import numpy as np
import time

def mat_mult(matIn1, matIn2):

    n, m = matIn1.shape
    _, r = matIn2.shape

    matOut = np.zeros((n, r), dtype=int)
    for i in range(n):
        for j in range(r):
            for k in range(m):
                matOut[i][j] = matOut[i][j] + matIn1[i][k] * matIn2[k][j]

    return matOut


def mat_mult_parallel(matIn1, matIn2, sharedMemArr, lastI):


    n, m = matIn1.shape
    _, r = matIn2.shape
    # print((n,m,r))
    for i in range(n):
        # print(i,j,k)
        for j in range(r):
            sumMat = 0
            for k in range(m):
                sumMat = sumMat + int(matIn1[i][k] * matIn2[k][j])

            # print(lastI)
            sharedMemArr[lastI * r + i * r + j] = sumMat

def from1D_to_2D_arr(arr1D, desired_shape):

    m, n = desired_shape
    ind = 0
    # print(m,n)
    arr2D = np.zeros((m, n), dtype=int)

    for i in range(m):
        for j in range(n):
            arr2D[i][j] = arr1D[ind]
            ind = ind + 1
    return arr2D


def runSequentialMatMul(matIn1, matIn2):
    timeStart = time.time()
    matOut = mat_mult(matIn1, mat_trp(matIn2))
    timeEnd = time.time()

    timeForExecSeq = (timeEnd - timeStart) * 1000
    print("Time taken for sequential multiplication:", timeForExecSeq, "ms")
    return timeForExecSeq, matOut


def print_message_about_default(numProcessors, lowerLimit, upperLimit, n, m):
    print("Values in arguments: ")
    print("numProcessors = %d" % numProcessors)
    print("lowerLimit = %d, upperLimit = %d" % (lowerLimit, upperLimit))
    print("n = %d, m = %d" % (n, m))

def get_division(tot_rows, numProcessors):

    division = []
    resLast, res = 0, 0
    division.append(res)

    while numProcessors != 0:
        if tot_rows >= numProcessors:
            resLast = resLast + res
            res = tot_rows // numProcessors

            division.append(resLast + res)
            tot_rows = tot_rows - res
            numProcessors = numProcessors - 1

        else:
            division = np.linspace(0, tot_rows, num=tot_rows, dtype=int)
            break

    return division

def mat_trp(matIn):
    n,m = matIn.shape
    matOut = np.zeros((m,n),dtype=int)

    for i in range(n):
        for j in range(m):
            matOut[j][i] = matIn[i][j]

    return matOut

def runParallelMatMul(matIn1, matIn2, sharedMemArr, numProcessors):

    procArr = []
    tot_rows, _ = matIn1.shape
    division = get_division(tot_rows, numProcessors)
    timeStart = time.time()

    for i in range(len(division) - 1):
        matIn1_slice = matIn1[division[i]: division[i + 1], :]
        matIn2_trp = mat_trp(matIn2)

        p = multiprocessing.Process(target=mat_mult_parallel,
                                    args=(matIn1_slice, matIn2_trp, sharedMemArr, division[i]))
        procArr.append(p)

    if len(division) == 1:
        sharedMemArr = mat_mult(matIn1, mat_trp(matIn2))

    for p in procArr:
        p.start()

    for p in procArr:
        p.join()

    timeEnd = time.time()

    timeForExecPar = (timeEnd - timeStart) * 1000

    n = int(len(sharedMemArr) ** 0.5)
    desired_shape = (n, n)

    matOut = from1D_to_2D_arr(sharedMemArr, desired_shape)

    print("Time taken for parallel multiplication:", timeForExecPar, "ms")

    return timeForExecPar, matOut


def main(argv):
    # numProcessors = multiprocessing.cpu_count()
    # numProcessors, lowerLimit, upperLimit, n, m = get_args(argv)
    numProcessors = int(sys.argv[1])
    lowerLimit = int(sys.argv[2])
    upperLimit = int(sys.argv[3])
    n = int(sys.argv[4])
    m = n
    print_message_about_default(numProcessors, lowerLimit, upperLimit, n, m)

    matIn1 = np.random.randint(low=lowerLimit, high=upperLimit, size=(n, m))
    matIn2 = np.random.randint(low=lowerLimit, high=upperLimit, size=(n, m))

    print("First Matrix \n", matIn1)
    print("Second Matrix \n", matIn2)

    timeForExecSeq, matOutSeq = runSequentialMatMul(matIn1, matIn2)
    sharedMemArr = multiprocessing.Array('i', n * n)
    timeForExecPar, matOutPar = runParallelMatMul(matIn1, matIn2, sharedMemArr, numProcessors)

    print("\n" , "Serial Multiplication: ")
    # print(matOutSeq)
    print("\n" , "Parallel Multiplication: ")
    # print(matOutPar)
    print("\n", "Hence, with {0} cores, parallel algorithm runs faster  {1}".format(numProcessors, float(
        timeForExecSeq - timeForExecPar)))

if __name__ == "__main__":
    argv = sys.argv[1:]
    main(argv)