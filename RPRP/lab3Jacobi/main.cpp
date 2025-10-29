#include <iostream>
#include <cmath>
#include <omp.h>

//DCMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES="/usr/local/opt/libomp/include";
//DOpenMP_CXX_FLAGS="-I/usr/local/opt/libomp/include"

using namespace std;
void read_matrix(float **A, float *B, int row);
void write_matrix(float **A, float *B, int row);


float form_jacobi_parallel(float **alf, float *x, float *x1, float *bet, int n,
                           int core) {
    int i, j;
    float s, max;
#pragma omp parallel for private(i, j, s)
    for (i = 0; i < n; i++) {
        s = 0;
        for (j = 0; j < n; j++) {
            s += alf[i][j] * x[j];
        }
        s += bet[i];
        if (i == 0) {
            max = fabs(x[i] - s);
        } else if (fabs(x[i] - s) > max) {
            max = fabs(x[i] - s);
        }
        x1[i] = s;
    }
    return max;
}

int jacobi_parallel(float **a, float *b, float *x, int n, float eps, int core) {

    float **f, *h, **alf, *bet, *x1, *xx, max;
    int i, j, kvo;
    f = new float *[n];
    for (i = 0; i < n; i++)
        f[i] = new float[n];
    h = new float[n];
    alf = new float *[n];
    for (i = 0; i < n; i++)
        alf[i] = new float[n];
    bet = new float[n];
    x1 = new float[n];
    xx = new float[n];
#pragma omp parallel for
    for (i = 0; i < n; i++) {
#pragma omp parallel for
        for (j = 0; j < n; j++)
            if (i == j)
                alf[i][j] = 0;
            else
                alf[i][j] = -a[i][j] / a[i][i];
        bet[i] = b[i] / a[i][i];
    }
    for (i = 0; i < n; i++)
        x1[i] = bet[i];
    kvo = 0;
    max = 5 * eps;
    while (max > eps) {
        for (i = 0; i < n; i++)
            x[i] = x1[i];
        max = form_jacobi_parallel(alf, x, x1, bet, n, core);
        kvo++;
    }
    delete[] f;
    delete[] h;
    delete[] alf;
    delete[] bet;
    delete[] x1;
    delete[] xx;
    return kvo;
}

int main() {

    omp_set_dynamic(0);

    int   i, N,core;
    float **a;
    float *b;
    float *x;
    float ep;
    ep = 1e-6;
    cout << "Matrix dimension N = ";
    cin >> N;
//    N = 10;
    cout << "Core Number = ";
//    core = 2;
    cin >> core;

    omp_set_num_threads(core);

    a = new float *[N];
    for (i = 0; i < N; i++)
        a[i] = new float[N];
    b = new float[N];
    x = new float[N];
    read_matrix(a, b, N);

    auto t1 = omp_get_wtime();

    jacobi_parallel(a, b, x, N, ep, core);

    cout << "\n Вектор X" << endl;
    for (int k = 0; k < N; k++){
        cout << (x[k]) << " ";
    }


    cout << endl;
    auto t2 = omp_get_wtime();

    cout << "время для N = " << N << ":" << endl;
    cout << t2 - t1 << ' ';
    cout.flush();
    delete[] a;
    delete[] b;
    delete[] x;

    cout << endl;

    return 0;
}

void read_matrix(float **A, float *B, int row) {
    printf("\n");
    int i, j;
    for (i = 0; i < row; i++) {
        B[i] = row + row - 1;
        for (j = 0; j < row; j++) {
            if (j == i) {
                A[i][j] = row;
            }

            else A[i][j] = 1;
        }
    }
    write_matrix(A, B, row);
}

void write_matrix(float **A, float *B, int row) {
    int i, j;
    for (i = 0; i < row; i++) {
        for (j = 0; j < row; j++) {
            printf("%f ", A[i][j]);
        }
        printf("%f ", B[i]);
        printf("\n");
    }
}
