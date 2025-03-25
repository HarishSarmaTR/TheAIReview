#include <iostream>
#include <vector>
#include <stdexcept>

// Base class
class Shape {
public:
    virtual double area() const = 0; // Pure virtual function
    virtual ~Shape() {}
};

// Derived class for Circle
class Circle : public Shape {
private:
    double radius;

public:
    Circle(double r) : radius(r) {}

    double area() const override {
        return 3.14159 * radius * radius;
    }
};

// Derived class for Rectangle
class Rectangle : public Shape {
private:
    double width, height;

public:
    Rectangle(double w, double h) : width(w), height(h) {}

    double area() const override {
        return width * height;
    }
};

// Function to calculate the total area of all shapes
double totalArea(const std::vector<Shape*>& shapes) {
    double total = 0.0;
    for (const Shape* shape : shapes) {
        total += shape->area();
    }
    return total;
}

int main() {
    try {
        std::vector<Shape*> shapes;
        shapes.push_back(new Circle(5));
        shapes.push_back(new Rectangle(4, 6));

        double area = totalArea(shapes);
        std::cout << "Total area: " << area << std::endl;

        for (Shape* shape : shapes) {
            delete shape; // Clean up
        }
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }

    return 0;
}
