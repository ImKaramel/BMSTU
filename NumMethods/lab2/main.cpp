#include <iostream>
#include <cmath>
#include <iomanip>

double myFunction(double x) {
    return exp(sqrt(x));
}

double method_of_trapezoid(double a = 0, double b = 4, int n = 2) {
    double h = (b - a) / n;
    double series_of_sum = 0;

    for (int i = 0; i < n - 1; i++) {
        double x = a + (i + 1) * h;
        series_of_sum +=  myFunction(x);
    }

    return h * ( myFunction(a) +  myFunction(b) / 2 + series_of_sum);
}


double method_of_simpson(double a = 0, double b = 4, int n = 2) {
    double h = (b - a) / n;
    double series_of_sum = 0;

    for (int i = 0; i < n; i++) {
        double x1 = a + (i + 0.5) * h;
        double x2 = a + (i + 1) * h;

        series_of_sum += 4 * myFunction(x1);
        if (i < n - 1) {
            series_of_sum += 2 *  myFunction(x2);
        }
    }

    return h / 3 * ( myFunction(a) +  myFunction(b) + series_of_sum);
}

double method_of_rectangles(double a = 0, double b = 4, int n = 2) {
    double h = (b - a) / n;
    double result = 0;

    for (int i = 0; i < n; i++) {
        double x = a + (i + 0.5) * h;
        result += h *  myFunction(x);
    }

    return result;
}

double get_richardson(double i_n, double i_n2, int k) {
    return (i_n - i_n2) / (2 * k - 1);
}


int main() {
    double eps =  1e-3;
    std::cout << std::setw(20) << "Метод трапеций  " << std::setw(20) << "Метод прямоугольников" << std::setw(30) << "Метод Симпсона" << std::endl;

    std::vector<double> N;
    std::vector<double> Result;
    std::vector<double> Richardson;

    int count = 0;

    for (int j = 0; j < 3; j++) {
        int n = 1;
        double richardson = INFINITY;
        int iteration = 0;
        double i_n = 0, i_n2 = 0;

        while (std::abs(richardson) >= eps) {
            n *= 2;
            i_n2 = i_n;
            if (count == 1) {
                i_n = method_of_simpson(0, 4, 4);
                richardson = get_richardson(i_n, i_n2, 4);
            } else if (count == 0) {
                i_n = method_of_trapezoid(0, 4, 2);
                richardson = get_richardson(i_n, i_n2, 2);
            } else {
                i_n = method_of_rectangles(0, 4, 2);
                richardson = get_richardson(i_n, i_n2, 2);
            }
            iteration++;
        }
        count++;
        N.push_back(iteration);
        Result.push_back(i_n);
        Richardson.push_back(i_n + richardson);
    }
    std::cout << std::setw(2) << std::fixed << std::setprecision(3) << "N)" << std::setw(9) << N[0] << std::setw(15) << N[1] << std::setw(25) << N[2]<< std::setw(30)  << std::endl;
    std::cout << std::setw(2) << std::fixed << std::setprecision(3) << "Res)" <<  std::setw(7) << Result[0] << std::setw(15) << Result[1] << std::setw(25) << Result[2]<< std::setw(30)  << std::endl;
    std::cout << std::setw(2) << std::fixed << std::setprecision(3) << "Rich)" <<  std::setw(6) << Richardson[0] << std::setw(15) << Richardson[1] << std::setw(25) << Richardson[2]<< std::setw(30)  << std::endl;


    return 0;
}
