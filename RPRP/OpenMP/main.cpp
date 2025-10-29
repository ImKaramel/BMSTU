#include <omp.h>
#include <stdio.h>
#include <iostream>
#include <math.h>
using namespace std;

void printMatrix(double* matrix);
void printVector(double* v);

void fillMatrix(double* matrix);
void fillB(double* matrix);
void fillX(double* matrix);



const long long N = 10000;
const double eps = 0.0000001;
const int NUM_THREADS = 2;



double getScal(double* v1, double* v2) {
    double s = 0;
    int i;
#pragma omp parallel for shared(v1, v2) private(i) reduction (+:s)
    for (int i = 0; i < N; i++) {
        s += (v1[i] * v2[i]);
    }

    return s;
}

void minus2(double* v1, double* v2) {
    int i;
#pragma omp parallel for private(i)
    for (i = 0; i < N; i++) {
        v1[i] -= v2[i];
    }
}

void plus2(double* v1, double* v2) {
    int i;
#pragma omp parallel for private(i)
    for (i = 0; i < N; i++) {
        v1[i] += v2[i];
    }
}
void mult_v_coef(double* v, double s) {
    int i;
#pragma omp parallel for shared(v) private(i)
    for (i = 0; i < N; i++) {
        v[i] *= s;
    }
}

double* mulMatrixByVector(double* matrix, double* x) {

    double* res = new double[N];
    int i = 0;

#pragma omp parallel for shared(matrix, x, res) private(i)
    for (i = 0; i < N; i++) {
        res[i] = 0;
        for (int j = 0; j < N; j++) {
            res[i] += matrix[i * N + j] * x[j];
        }
    }

    return res;
}

void procFunc(double* A, double* B, double* x, double* y) {
    double condition = eps;
    double* rn = new double[N];
    double* zn = new double[N];
    double scalup;
    double scaldown;
    double scalup2;
    double* Az = new double[N];
    double alpha;
    double beta;
    for (int i = 0; i < N; i++) {
        rn[i] = B[i];
    }
    y = mulMatrixByVector(A, x);
    minus2(rn, y);
    for (int i = 0; i < N; i++) {
        zn[i] = rn[i];
    }
    while (true) {
        scalup = getScal(rn, rn);
        Az = mulMatrixByVector(A, zn);
        scaldown = getScal(Az, zn);
        alpha = scalup / scaldown;

        mult_v_coef(zn, alpha);
        plus2(x, zn);
        mult_v_coef(Az, alpha);
        minus2(rn, Az);

        scalup2 = getScal(rn, rn);
        beta = scalup2 / scalup;
        mult_v_coef(zn, beta);

        int i;
#pragma omp parallel shared(rn, zn) private(i)
        {

#pragma omp for
            for (i = 0; i < N; i++) {
                zn[i] += rn[i];
            }
        }

        condition = sqrt(scalup2) / sqrt(getScal(B, B));
        if (condition < eps) {
            break;
        }

    }
}

int main() {

    omp_set_dynamic(0);

    cout << "Matrix dimension N = " << N << endl;

    //устанавливаем количество используемых ядер
    omp_set_num_threads(2);


    double* A = new double[N * N];
    double* B = new double[N];
    double* x = new double[N];
    double* y = new double[N];


    fillX(x);

    fillMatrix(A);
    //printMatrix(A);

    fillB(B);
    //printVector(B);
    fillX(y);

    double start_time = omp_get_wtime();
    procFunc(A, B, x, y);
    double end_time = omp_get_wtime();

    cout << "duration is " << end_time - start_time << " seconds for " << NUM_THREADS << " threads" << endl;

    cout << "Answer: " << x[0];
    for (int i = 1; i < N; i++) {
        cout << ", " << x[i];
    }
    cout << endl;


    delete[] A;
    delete[] B;
    delete[] x;
    delete[] y;

    return 0;
}

void fillMatrix(double* matrix) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (i == j) matrix[i * N + j] = 2.0;
            else matrix[i * N + j] = 1.0;
        }
    }
}

void fillB(double* B) {
    for (int i = 0; i < N; i++) {
        B[i] = N + 1;
    }
}

void fillX(double* x) {
    for (int i = 0; i < N; i++) {
        x[i] = 0;
    }
}


void printMatrix(double* matrix) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            printf("%f ", matrix[i * N + j]);
        }
        printf("\n");
    }
}

void printVector(double* v) {
    cout << v[0];
    for (int i = 1; i < N; i++) {
        cout << ", " << v[i];
    }
    cout << endl;
}