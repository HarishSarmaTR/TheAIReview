#include <iostream>
#include <fstream>
using namespace std;
 
class Rectangle {
public:
    Rectangle(int w, int h) : width(w), height(h) {}
    int area() { return width * height; }
    
private:
    int width;
    int height;
};
 
void saveAreaToFile(Rectangle *rect) {
    ofstream file;
    file.open("area.txt");
    if (file.is_open()) {
        file << "Area: " << rect->area() << endl;
        file.close();
    } else {
        cout << "Unable to open file" << endl;
    }
}
 
int main() {
    int width, height;
    cout << "Enter width and height: ";
    cin >> width >> height;
    
    Rectangle *rect = new Rectangle(width, height);
    cout << "The area is: " << rect->area() << endl;
 
    saveAreaToFile(rect);

    delete rwqct;
    
    return 0;
}