#include <iomanip>
#include <iostream>
#include <cmath>
#include <vector>

using namespace std;
vector<double> solution( vector<vector<double>>&a,  vector<double> &b);


double myFunction(double x) {
    return exp(sqrt(x));
}
std::vector<std::vector<double>> createTridiagonalMatrix(std::vector<double> diag_a, std::vector<double> diag_b,
                                                         std::vector<double> diag_c, int n)
{
    vector<vector<double>> matrix(n,  vector<double>(n, 0.0));

    // Заполнение главной диагонали
    for (int i = 0; i < n; i++) {
        matrix[i][i] = diag_a[i];
    }

    // Заполнение диагонали ниже главной
    for (int i = 1; i < n; i++) {
        matrix[i][i - 1] = diag_b[i - 1];
    }

    // Заполнение диагонали выше главной
    for (int i = 0; i < n - 1; i++) {
        matrix[i][i + 1] = diag_c[i];
    }

    return matrix;
}


int main() {

    double a = 0;
    double b = 4;
    double step = (b - a) / 32.0; // шаг
    double start = 0.0;
    int n; // количество значений

    std::cout << "Enter size of matrix \n";
    cin >> n;

    std::vector<double> koef_a;
    std::vector<double> koef_b(n + 1, 0);
    std::vector<double> koef_c(n + 1, 0);
    std::vector<double> koef_d(n + 1, 0); //коэф д
    std::vector<double> S(n + 1, 0); //сам сплайн
    std::vector<double> delta(n + 1, 0); //погрешность

    vector<double> arrX;

    int num = 0;

    for (double x = start; x <= b; x += step) {
        if (num == n) {
            break;
        }
        double result = myFunction(x);
        cout << result << endl;
        arrX.push_back(x);
        koef_a.push_back(result);
        num++;
    }

    for (size_t i = 0; i < arrX.size(); i++) {
        cout << "f(" << arrX[i] << ") = " << koef_a[i] << endl;
    }

    std::vector<double> diag_a(n - 1, 1.0);
    std::vector<double> diag_b(n, 4);
    std::vector<double> diag_c(n - 1, 1.0);
    std::vector<double> free_d(n, 0.0);

    for (int i = 0; i < n-1; i++) {
        diag_a[i] = 4.0;
    }
    for (int i=0; i< n - 2; i++) {
        diag_b[i] = 1.0;
        diag_c[i] = 1.0;
    }

    vector<vector<double>> result = createTridiagonalMatrix(diag_b, diag_a, diag_c, n);
    vector<double> ek = solution(result, free_d);

    for (int i = 1; i < n-1 ; i++) {
        koef_c[i] = ek[i];
    }
    koef_c[n-1] = 0;
    koef_c[0] = 0;

    for(int i = 0; i < n - 1; i++){
        koef_b[i] = (koef_a[i + 1] - koef_a[i]) / step - (step / 3) * (koef_c[i + 1] + 2 * koef_c[i]);
        koef_d[i] = (koef_c[i + 1] - koef_c[i]) / (3 * step);
    }

    koef_b[n - 1] = ((koef_a[n] - koef_a[n - 1]) / step) * (2.0 / 3) * step * koef_c[n - 1];
    koef_d[n - 1] = (-1) * koef_c[n] / (3 * step);


    for(int i = 0; i < n + 1; i++) {
        S[i] = koef_a[i] + koef_b[i] * step + koef_c[i] * step * step + koef_d[i] * step * step * step;
    }

    for(int i = 0; i < n + 1; i++){
        delta[i] = abs(koef_a[i] - S[i]);
    }

    std::cout << std::setw(10) << "X" << std::setw(15) << "Y" << std::setw(15) << "S" << std::setw(20) << "|S(x) - Y(x)|" << std::endl;
    for(int i = 0; i < n + 1; i++){
        std::cout << std::setw(10) << std::fixed << std::setprecision(3) << step * i << std::setw(15) << koef_a[i] << std::setw(15) << S[i] << std::setw(20) << delta[i] << std::endl;
    }
    return 0;
}

vector<double> solution( vector<vector<double>>&a,  vector<double> &b) {

    size_t n = a.size();
    vector<double> x(n, 0);

//   Прямой ход
    vector<double> v(n, 0);
    vector<double> u(n, 0);

    v[0] = a[0][1] / (-a[0][0]);
    u[0] = (-b[0]) / (-a[0][0]);

    for (size_t i = 1; i < n - 1; ++i) {
        v[i] = a[i][i + 1] / (-a[i][i] - a[i][i - 1] * v[i - 1]);
        u[i] = (a[i][i - 1] * u[i - 1] - b[i]) / (-a[i][i] - a[i][i - 1] * v[i - 1]);
    }

    v[n - 1] = 0;
    u[n - 1] = (a[n - 1][n - 2] * u[n - 2] - b[n - 1]) / (-a[n - 1][n - 1] - a[n - 1][n - 2] * v[n - 2]);

//  Обратный ход
    x[n - 1] = u[n - 1];
    for (int i = n - 1; i > 0; --i) {
        x[i - 1] = v[i - 1] * x[i] + u[i - 1];
    }

    return x;
}

void printX(string string, std::string namevec, vector<double>& a) {
    if (a.size() == 1 && (typeid(a[0]) == typeid(int) || typeid(a[0]) == typeid(float))) {
        cout << a[0] << endl;
    } else {
        cout << string << endl;
        for (size_t k = 0; k < a.size(); ++k) {
            cout << namevec << "[" << k << "] = " << fixed << a[k] << endl;
        }
    }
}