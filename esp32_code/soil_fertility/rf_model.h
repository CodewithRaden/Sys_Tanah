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
                        if (x[1] <= 111.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 220.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 958.2499694824219) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[1] <= 598.0) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #2
                        if (x[2] <= 103.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 576.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 552.6999969482422) {
                                    if (x[1] <= 382.04998779296875) {
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

                        // tree #3
                        if (x[4] <= 316.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 231.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 916.6000061035156) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 580.3999938964844) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #4
                        if (x[1] <= 105.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 81.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 145.25) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[0] <= 232.5) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #5
                        if (x[2] <= 104.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 84.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 147.8000030517578) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1271.7000122070312) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #6
                        if (x[0] <= 26.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 235.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 562.1000061035156) {
                                    if (x[2] <= 390.5500030517578) {
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
                        if (x[4] <= 307.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 244.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 393.1000061035156) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[1] <= 570.3999938964844) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #8
                        if (x[1] <= 107.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 75.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 567.2999877929688) {
                                    if (x[0] <= 152.5) {
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

                        // tree #9
                        if (x[1] <= 111.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 631.1499938964844) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 558.4499969482422) {
                                    if (x[1] <= 420.40000915527344) {
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

                        // tree #10
                        if (x[1] <= 112.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 85.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 593.0) {
                                    if (x[2] <= 363.34999084472656) {
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
                        if (x[2] <= 97.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 242.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 230.3000030517578) {
                                    if (x[4] <= 925.9500122070312) {
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

                        // tree #12
                        if (x[1] <= 105.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 260.3999938964844) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 577.0) {
                                    if (x[1] <= 375.6499938964844) {
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
                        if (x[0] <= 27.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 519.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 144.8499984741211) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[4] <= 1268.0499877929688) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #14
                        if (x[4] <= 317.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 84.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 226.4000015258789) {
                                    if (x[2] <= 379.8500061035156) {
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

                        // tree #15
                        if (x[0] <= 25.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 594.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 148.6999969482422) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[0] <= 232.8000030517578) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #16
                        if (x[4] <= 310.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 84.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 233.0) {
                                    if (x[1] <= 393.8999938964844) {
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

                        // tree #17
                        if (x[2] <= 103.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 241.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 933.2999877929688) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 555.3000030517578) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #18
                        if (x[0] <= 27.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 547.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 146.60000610351562) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[2] <= 558.1999969482422) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #19
                        if (x[0] <= 28.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 245.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 1301.7999877929688) {
                                    if (x[1] <= 393.09999084472656) {
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
                        if (x[2] <= 99.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 156.3000030517578) {
                                if (x[4] <= 549.5) {
                                    votes[1] += 1;
                                }

                                else {
                                    votes[2] += 1;
                                }
                            }

                            else {
                                if (x[2] <= 574.1499938964844) {
                                    votes[3] += 1;
                                }

                                else {
                                    votes[4] += 1;
                                }
                            }
                        }

                        // tree #21
                        if (x[2] <= 102.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 74.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[0] <= 161.04999542236328) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[1] <= 577.0) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #22
                        if (x[2] <= 105.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[0] <= 81.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 570.2999877929688) {
                                    if (x[4] <= 946.6999816894531) {
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

                        // tree #23
                        if (x[1] <= 110.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 238.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 560.3500061035156) {
                                    if (x[1] <= 406.9499969482422) {
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

                        // tree #24
                        if (x[0] <= 22.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 242.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 580.3999938964844) {
                                    if (x[4] <= 904.1999816894531) {
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

                        // tree #25
                        if (x[2] <= 103.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 238.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[1] <= 576.7000122070312) {
                                    if (x[1] <= 360.3999938964844) {
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

                        // tree #26
                        if (x[0] <= 26.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 595.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 1284.7999877929688) {
                                    if (x[2] <= 404.8000030517578) {
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

                        // tree #27
                        if (x[0] <= 26.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 228.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[2] <= 572.1000061035156) {
                                    if (x[1] <= 403.5500030517578) {
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

                        // tree #28
                        if (x[0] <= 26.0) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[2] <= 206.5) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 900.3999938964844) {
                                    votes[2] += 1;
                                }

                                else {
                                    if (x[1] <= 577.25) {
                                        votes[3] += 1;
                                    }

                                    else {
                                        votes[4] += 1;
                                    }
                                }
                            }
                        }

                        // tree #29
                        if (x[4] <= 319.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[1] <= 573.4500122070312) {
                                if (x[4] <= 547.5) {
                                    votes[1] += 1;
                                }

                                else {
                                    if (x[2] <= 389.1999969482422) {
                                        votes[2] += 1;
                                    }

                                    else {
                                        votes[3] += 1;
                                    }
                                }
                            }

                            else {
                                votes[4] += 1;
                            }
                        }

                        // tree #30
                        if (x[4] <= 307.5) {
                            votes[0] += 1;
                        }

                        else {
                            if (x[4] <= 549.0) {
                                votes[1] += 1;
                            }

                            else {
                                if (x[4] <= 1318.7999877929688) {
                                    if (x[0] <= 150.60000610351562) {
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