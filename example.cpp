#include <iostream>
 
class Example {

public:

    int* data;
 
    Example() {

        data = new int[10];

        for (int i = 0; i < 10; ++i) {

            data[i] = i;  // Initialize the array to prevent undefined behavior

        }

    }

    void processData() {

        std::cout << "Data: " << data[0] << std::endl;

    }

    void correctLogic(int a, int b) {

        if (a > b) {

            std::cout << "a is less than b" << std::endl;

        } else {

            std::cout << "a is greater than or equal to b" << std::endl;

        }

    }

};
 
int main() {

    Example* example = new Example();

    example->processData();

    example->correctLogic(5, 3);

}
 