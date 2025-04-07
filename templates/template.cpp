# define DEBUG


#include <bits/stdc++.h>
using namespace std;

int main() {
#ifdef DEBUG

std::string input = R"(


)";
    std::istringstream in(input);
    std::cin.rdbuf(in.rdbuf());

    auto start = std::chrono::high_resolution_clock::now();
#endif

    // code here
    const string ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const string abc = "abcdefghijklmnopqrstuvwxyz";

    int n;
    std::cin >> n;

    int a, b;
    std::cin >> a >> b;

    std::string s;
    std::cin >> s;



#ifdef DEBUG
    auto stop = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = stop - start;

    std::cout << "time: " << elapsed.count() << " sec" << std::endl;
#endif

    return 0;
}