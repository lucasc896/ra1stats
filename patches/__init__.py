import sms8

def cmssmCut(iX, x, iY, y, iZ, z) :
    def yMin(x) :
        return 450.0 - (300.0)*(x-500.0)/(1200.0-500.0)

    def yMax(x) :
        return 750.0 - (250.0)*(x-500.0)/(1200.0-500.0)

    if 0.0 <= x <=  500.0 :
        return  500.0 <= y <= 700.0

    if  500.0 <= x <= 1200.0 :
        return yMin(x) <= y <= yMax(x)

    if 1200.0 <= x <= 1500.0:
        return 200.0 <= y <= 450.0

    if 1500.0 <= x:
        return 200.0 <= y <= 400.0

def t2ccCut(iX, x, iY, y, iZ, z) :
    fail = any([x > 270.0, y > x, y < x - 100.0])
    return not fail

def cutFunc() :
    return {"T1":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4),
            "T2":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4 and x<1300.0),
            "T2tt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4 and x<900.0),
            "T2bb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4 and x<1300.0),
            "T2cc":t2ccCut,
            "T2bw":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4),
            "T5zz":lambda iX,x,iY,y,iZ,z:(y<(x-200.1) and iZ==1 and x>399.9),
            "T1bbbb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4),
            "T1tttt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4),
            "T1tttt_ichep":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>287.4),
            "tanBeta10_7":cmssmCut,
            }

def curves() :
    out = {}
    out["tanBeta10_7"] = {
            ("ExpectedUpperLimit",          "default"): [( 120, 594), ( 160, 595), ( 240, 595), ( 320, 590), ( 400, 580), ( 480, 567),
                                                         ( 560, 550), ( 640, 530), ( 720, 500), ( 800, 465), ( 880, 423),
                                                         ( 960, 370), (1040, 342), (1120, 325), (1200, 310), (1280, 300),
                                                         (1360, 295), (1440, 293), (1520, 290), (1600, 287), (1680, 285),
                                                         (1760, 283), (1840, 280), (1920, 275), (2000, 269), (2080, 265),
                                                         (2160, 262), (2240, 260), (2320, 260), (2400, 260), (2480, 260),
                                                         (2560, 260), (2640, 265), (2720, 273), (2800, 282), (2880, 290),
                                                         (2960, 300),],
            ("ExpectedUpperLimit_-1_Sigma", "default"): [( 130, 630), ( 160, 630), ( 240, 635), ( 320, 635), ( 400, 630), ( 480, 620),
                                                         ( 560, 608), ( 640, 590), ( 720, 565), ( 800, 535), ( 880, 500),
                                                         ( 960, 440), (1040, 388), (1120, 365), (1200, 359), (1280, 350),
                                                         (1360, 340), (1440, 330), (1520, 328), (1600, 325), (1680, 322),
                                                         (1760, 321), (1840, 319), (1920, 315), (2000, 310), (2080, 305),
                                                         (2160, 300), (2240, 295), (2320, 292), (2400, 290), (2480, 290),
                                                         (2560, 290), (2640, 294), (2720, 300), (2800, 305), (2880, 310),
                                                         (2960, 315),],
            ("ExpectedUpperLimit_+1_Sigma", "default"): [( 130, 570), ( 160, 570), ( 240, 570), ( 320, 565), ( 400, 550), ( 480, 530),
                                                         ( 560, 505), ( 640, 475), ( 720, 430), ( 800, 390), ( 880, 360),
                                                         ( 960, 336), (1040, 318), (1120, 300), (1200, 280), (1280, 265),
                                                         (1360, 260), (1440, 254), (1520, 250), (1600, 250), (1680, 250),
                                                         (1760, 250), (1840, 250), (1920, 250), (2000, 249), (2080, 247),
                                                         (2160, 244), (2240, 240), (2320, 237), (2400, 235), (2480, 235),
                                                         (2560, 237), (2640, 243), (2720, 253), (2800, 265), (2880, 278),
                                                         (2960, 288),],
            ("UpperLimit",                  "default"): [( 120, 629), ( 160, 630), ( 240, 630), ( 320, 625), ( 400, 610), ( 480, 590),
                                                         ( 560, 570), ( 640, 545), ( 720, 520), ( 800, 490), ( 880, 448),
                                                         ( 960, 392), (1040, 355), (1120, 338), (1200, 328), (1280, 319),
                                                         (1360, 309), (1440, 300), (1520, 295), (1600, 292), (1680, 290),
                                                         (1760, 290), (1840, 289), (1920, 287), (2000, 286), (2080, 283),
                                                         (2160, 280), (2240, 280), (2320, 278), (2400, 275), (2480, 275),
                                                         (2560, 276), (2640, 279), (2720, 281), (2800, 285), (2880, 290),
                                                         (2960, 300),],
            ("UpperLimit",                  "up"     ): [( 120, 629), ( 160, 630), ( 240, 630), ( 320, 630), ( 400, 623), ( 480, 610),
                                                         ( 560, 590), ( 640, 570), ( 720, 545), ( 800, 515), ( 880, 480),
                                                         ( 960, 435), (1040, 395), (1120, 355), (1200, 340), (1280, 330),
                                                         (1360, 320), (1440, 315), (1520, 308), (1600, 306), (1680, 303),
                                                         (1760, 300), (1840, 297), (1920, 295), (2000, 295), (2080, 293),
                                                         (2160, 290), (2240, 289), (2320, 288), (2400, 287), (2480, 286),
                                                         (2560, 287), (2640, 290), (2720, 293), (2800, 298), (2880, 303),
                                                         (2960, 310),],
            ("UpperLimit",                  "down"   ): [( 120, 614), ( 160, 615), ( 240, 615), ( 320, 608), ( 400, 590), ( 480, 570),
                                                         ( 560, 550), ( 640, 525), ( 720, 495), ( 800, 455), ( 880, 415),
                                                         ( 960, 355), (1040, 335), (1120, 320), (1200, 311), (1280, 302),
                                                         (1360, 295), (1440, 287), (1520, 283), (1600, 280), (1680, 280),
                                                         (1760, 279), (1840, 278), (1920, 277), (2000, 274), (2080, 270),
                                                         (2160, 268), (2240, 268), (2320, 267), (2400, 266), (2480, 265),
                                                         (2560, 265), (2640, 265), (2720, 270), (2800, 275), (2880, 283),
                                                         (2960, 292),],
            }
    return out


def overwriteOutput() :
    out = {}
    out.update({"T1": [(35, 25, 1, "ew"),
                       (41, 10, 1, "ew"),
                       (41,  9, 1, "ew"),
                       (41,  8, 1, "ew"),
                       (41,  7, 1, "ew"),
                       (41,  6, 1, "ew"),
                       (41,  5, 1, "ew"),
                       (41,  4, 1, "ew"),
                       (41,  3, 1, "ew"),
                       (41,  2, 1, "ew"),
                       (41,  1, 1, "ew"),
                       (69,  2, 1, "ew"),
                       ],
                "T2": [(38, 22, 1), (44, 29, 1),],
                "T2bb": [(33,  5, 1, "ns"),
                         (34,  5, 1, "ns"),
                         (34,  8, 1, "ns"),
                         (35, 10, 1, "ns"),
                       ],
                "T1bbbb": [(14,  6, 1, "ew"),
                           (40, 22, 1, "ew"),
                           (40, 23, 1, "ew"),
                           (40, 24, 1, "ew"),
                           (40, 25, 1, "ew"),
                           (40, 26, 1, "ew"),
                           (40, 27, 1, "ew"),
                           (40, 28, 1, "ew"),
                           (40, 29, 1, "ew"),
                           (40, 30, 1, "ew"),
                           (40, 31, 1, "ew"),
                           (40, 32, 1, "ew"),

                           (41,  1, 1, "ew"),
                           (41,  2, 1, "ew"),
                           (41,  3, 1, "ew"),
                           (41,  4, 1, "ew"),
                           (41,  5, 1, "ew"),
                           (41,  6, 1, "ew"),
                           (41,  7, 1, "ew"),
                           (41,  8, 1, "ew"),
                           (41,  9, 1, "ew"),
                           (41, 10, 1, "ew"),
                           (41, 11, 1, "ew"),
                           (41, 12, 1, "ew"),
                           (41, 13, 1, "ew"),
                           (41, 14, 1, "ew"),
                           (41, 15, 1, "ew"),
                           (41, 16, 1, "ew"),

                           (69, 39, 1, "ew"),
                           (69, 40, 1, "ew"),
                           (69, 41, 1, "ew"),
                           (69, 42, 1, "ew"),
                           (69, 43, 1, "ew"),
                           (69, 44, 1, "ew"),
                           (69, 45, 1, "ew"),
                           (69, 46, 1, "ew"),
                           (69, 47, 1, "ew"),
                           (69, 48, 1, "ew"),
                           (69, 49, 1, "ew"),
                           (69, 50, 1, "ew"),
                           (69, 51, 1, "ew"),
                           (69, 52, 1, "ew"),
                           (69, 53, 1, "ew"),
                           (69, 54, 1, "ew"),
                           (69, 55, 1, "ew"),
                           (69, 56, 1, "ew"),
                           (69, 57, 1, "ew"),
                           (69, 58, 1, "ew"),
                           ],
                "T1tttt":[(56, 8, 1),(76, 9, 1)],
                "T2tt": [(80,  3, 1, "ew"),
                         (80,  4, 1, "ew"),
                         (80, 13, 1, "ew"),
                         (80, 14, 1, "ew"),
                         (80, 15, 1, "ew"),
                         (80, 16, 1, "ew"),
                         (80, 17, 1, "ew"),
                         (80, 18, 1, "ew"),
                         (80, 19, 1, "ew"),
                         (80, 20, 1, "ew"),
                         ],
                })
    return out


def compat(funcName="", model=""):
    if model in ["T1", "T2", "T2bb", "T2tt", "T1bbbb", "T1tttt", "T1tttt_ichep"]:
        funcName = funcName.replace("m1", "-1").replace("p1", "+1")
        return {"replace": sms8.graphReplacePoints()[funcName].get(model, {}),
                "blackList": sms8.graphBlackLists()[funcName].get(model, []),
                }
    else:
        try:
            exec("import %s as module" % model.replace(".", "p"))
            return getattr(module, funcName)()
        except ImportError:
            return {"replace": {},
                    "blackList": [],
                    }


def ExpectedUpperLimit_m1_Sigma(model=""):
    return compat(funcName="ExpectedUpperLimit_m1_Sigma", model=model)


def ExpectedUpperLimit_p1_Sigma(model=""):
    return compat(funcName="ExpectedUpperLimit_p1_Sigma", model=model)


def ExpectedUpperLimit(model=""):
    return compat(funcName="ExpectedUpperLimit", model=model)


def UpperLimit(model=""):
    return compat(funcName="UpperLimit", model=model)


def UpperLimit_p1_Sigma(model=""):
    return compat(funcName="UpperLimit_p1_Sigma", model=model)


def UpperLimit_m1_Sigma(model=""):
    return compat(funcName="UpperLimit_m1_Sigma", model=model)
