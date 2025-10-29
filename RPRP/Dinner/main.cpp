#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>
#include <atomic>
#include <string>
#include <vector>
#include <sstream>
using namespace std;

void states(int n);
ofstream file("philosopher.txt");
mutex printMutex;
atomic<bool> running{true};

class Philosopher {
public:
    string name;
    mutex& Leftfork;
    mutex& Rightfork;

    Philosopher(string xname, mutex& Leftfork, mutex& Rightfork) :
            name(xname), Leftfork(Leftfork), Rightfork(Rightfork) {}

    void run() {
        while (running) {
            this_thread::sleep_for(chrono::milliseconds(rand() % 10 + 1));
            takeForks();
        }
    }

    void takeForks() {

        if (Leftfork.try_lock()) {
            printToFile(name + " БеретЛевуюВилку");
            if (Rightfork.try_lock()) {
                lock_guard<mutex> leftLock(Leftfork, adopt_lock);
                printToFile(name + " БеретПравуюВилку");
                lock_guard<mutex> rightLock(Rightfork, adopt_lock);
                eating();
                printToFile(name + " ПоложилЛевуюВилку");
                printToFile(name + " ПоложилПравуюВилку");
//                Rightfork.unlock();
            } else {
                Leftfork.unlock();
            }
        }
    }


    void printToFile(const string& message) {
        lock_guard<mutex> lock(printMutex);
        file << message << endl;
    }

    void eating() {
        {
            lock_guard<mutex> lock(printMutex);
            file << name << " НачинаетEсть" << endl;
        }
        this_thread::sleep_for(chrono::milliseconds(rand() % 10 + 1));
        {
            lock_guard<mutex> lock(printMutex);
            file << name << " ЗаканчиваетЕсть" << endl;
        }
    }
};

void Philosophers(int numOfPhilosophers) {
    mutex forks[numOfPhilosophers];
    string philosopherNames[] = { "1", "2", "3", "4", "5" };
    vector<Philosopher> philosophersVec;

    for (int i = 0; i < numOfPhilosophers; i++) {
        philosophersVec.emplace_back(Philosopher(philosopherNames[i], forks[i], forks[(i + 1) % numOfPhilosophers]));
    }

    vector<thread> threads;
    for (int i = 0; i < numOfPhilosophers; i++) {
        threads.emplace_back(&Philosopher::run, &philosophersVec[i]);
    }

    this_thread::sleep_for(chrono::seconds(5));
    running = false;

    for (int i = 0; i < numOfPhilosophers; i++) {
        threads[i].join();
    }
}

int main() {
    int numOfPhilosophers;
    cout << "Enter the number of philosophers: ";
    cin >> numOfPhilosophers;
    Philosophers(numOfPhilosophers);

    states(numOfPhilosophers);

    return 0;
}

void states(int n) {
    std::ifstream prv_file("philosopher.txt");
    std::ofstream res_file("states.txt");
//    int n = 5;
    int num_strngs = 0;
    std::string line;
    while (std::getline(prv_file, line)) {
        num_strngs += 1;
    }
    prv_file.clear();  // Переходим в начало файла снова
    prv_file.seekg(0, std::ios::beg);

    int k = 0;
    std::vector<std::vector<std::string>> status(num_strngs, std::vector<std::string>(n, "Размышляет"));
    while (std::getline(prv_file, line)) {
        std::istringstream iss(line);
        int ind;
        std::string state;
        iss >> ind >> state;
        status[k][ind-1] = state;
        if (k > 0) {
            for (int j = 0; j < n; j++) {
                if (j != ind-1) {
                    if (status[k-1][j] == "ПоложилПравуюВилку") {
                        status[k][j] = "Размышляет";
                    } else if (status[k-1][j] == "НачинаетЕсть") {
                        status[k][j] = "ест";
                    } else {
                        status[k][j] = status[k-1][j];
                    }
                }
            }
        }
        k += 1;
    }

    for (int i = 0; i < num_strngs; i++) {
        res_file << i << " момент    ";
        for (int j = 0; j < n; j++) {
            res_file << status[i][j] << "(" << j+1 << ")     ";
        }
        res_file << "\n";
    }
}
