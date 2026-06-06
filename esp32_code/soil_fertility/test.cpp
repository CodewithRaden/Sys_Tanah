#include <iostream>
#include "rf_model.h"

int main() {
    Eloquent::ML::Port::RandomForest clf;
    float features[5] = {15.0, 82.0, 74.0, 6.3, 259.0}; // N, P, K, pH, EC
    int pred = clf.predict(features);
    std::cout << "Prediction Index: " << pred << std::endl;
    std::cout << "Prediction Label: " << clf.idxToLabel(pred) << std::endl;
    return 0;
}
