#pragma once
#include <cstdarg>
namespace Eloquent {
    namespace ML {
        namespace Port {
            class RandomForest {
                public:
                    /**
                    * Predict class for features vector
                    */
                    int predict(float *x) {
                        uint8_t votes[5] = { 0 };
                        // tree #1
                        if (x[2] <= 98.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 593.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 389.3999938964844) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[0] <= 215.6999969482422) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #2
                        if (x[1] <= 111.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 85.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 975.4499816894531) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[0] <= 234.5) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #3
                        if (x[0] <= 27.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 583.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 147.54999542236328) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 591.9500122070312) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #4
                        if (x[0] <= 27.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 85.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 152.3000030517578) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 540.5500030517578) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #5
                        if (x[2] <= 103.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 229.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 395.8999938964844) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1253.5499877929688) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #6
                        if (x[0] <= 26.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 584.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 1287.75) {
                                    if (x[4] <= 988.4999694824219) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #7
                        if (x[2] <= 104.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 595.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 233.8000030517578) {
                                    if (x[4] <= 943.8500061035156) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #8
                        if (x[0] <= 28.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 234.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 932.6499938964844) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1288.7000122070312) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #9
                        if (x[2] <= 103.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 217.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 399.75) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1268.7999877929688) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #10
                        if (x[1] <= 110.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 243.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 582.7999877929688) {
                                    if (x[2] <= 360.9499969482422) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #11
                        if (x[1] <= 111.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 577.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 388.5) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[0] <= 228.0999984741211) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #12
                        if (x[2] <= 98.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 83.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 575.0499877929688) {
                                    if (x[2] <= 387.8500061035156) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #13
                        if (x[2] <= 103.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 212.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 144.3000030517578) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 571.7000122070312) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #14
                        if (x[0] <= 25.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 85.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 387.1999969482422) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 586.3999938964844) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #15
                        if (x[1] <= 107.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 621.5499877929688) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 547.0500030517578) {
                                    if (x[3] <= 7.450000047683716) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[2] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #16
                        if (x[4] <= 306.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 237.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 927.5999755859375) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[1] <= 588.1499938964844) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #17
                        if (x[1] <= 106.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 591.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 398.6999969482422) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1299.5999755859375) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #18
                        if (x[4] <= 317.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 596.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 395.6999969482422) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 577.6000061035156) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #19
                        if (x[4] <= 322.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 238.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 228.9499969482422) {
                                    if (x[2] <= 396.9499969482422) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #20
                        if (x[4] <= 328.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 235.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 1273.7999877929688) {
                                    if (x[0] <= 160.64999389648438) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // return argmax of votes
                        uint8_t classIdx = 0;
                        float maxVotes = votes[0];

                        for (uint8_t i = 1; i < 5; i++) {
                            if (votes[i] > maxVotes) {
                                classIdx = i;
                                maxVotes = votes[i];
                            }
                        }

                        return classIdx;
                    }

                    /**
                    * Predict readable class name
                    */
                    const char* predictLabel(float *x) {
                        return idxToLabel(predict(x));
                    }

                    /**
                    * Convert class idx to readable name
                    */
                    const char* idxToLabel(uint8_t classIdx) {
                        switch (classIdx) {
                            case 0:
                            return "Sangat Rendah";
                            case 1:
                            return "Rendah";
                            case 2:
                            return "Sedang";
                            case 3:
                            return "Tinggi";
                            case 4:
                            return "Sangat Tinggi";
                            default:
                            return "Houston we have a problem";
                        }
                    }

                protected:
                };
            }
        }
    }