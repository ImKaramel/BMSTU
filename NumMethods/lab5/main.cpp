#include <iostream>
#include <cmath>
using namespace std;

double eps = 0.001;
double xk, yk;

double f(double x, double y) {
    return x*x + 2*y*y + exp(x + y);
}

pair<double, double> analytical_min() {
    return {-0.292688, -0.14320};
}

double df_dx(double x, double y) {
    return 2*x + exp(x + y);
}

double df_dy(double x, double y) {
    return 4*y + exp(x + y);
}

double d2f_dx2(double x, double y) {
    return 2 + exp(x + y);
}

double d2f_dy2(double x, double y) {
    return 4 + exp(x + y);
}

int main() {
    int k = 0;
    double phi1, phi2, t_star;
    xk = 1.0;
    yk = 1.0;

    do {
        phi1 = - pow(df_dx(xk, yk), 2) - pow(df_dy(xk, yk), 2);

        phi2 = d2f_dx2(xk, yk) * pow(df_dx(xk, yk), 2) + 2 * d2f_dx2(xk, yk) * df_dx(xk, yk) * df_dy(xk, yk) + d2f_dy2(xk, yk) * pow(df_dy(xk, yk), 2);

        t_star = - phi1 / phi2;

        xk = xk - t_star * df_dx(xk, yk);
        yk = yk - t_star * df_dy(xk, yk);

        k++;
    } while (max(df_dx(xk, yk), df_dy(xk, yk)) >= eps);

    cout << "methods min: (" << xk << ", " << yk << ")" << endl;
    cout << "analytical min: (" << analytical_min().first << ", " << analytical_min().second << ")" << endl;
    cout << "difference: (" << fabs(xk - analytical_min().first) << ", " << fabs(yk - analytical_min().second) << ")" << endl;

    return 0;
}
