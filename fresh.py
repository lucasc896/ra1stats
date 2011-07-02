import math,array,copy
import plotting,utils
import ROOT as r

def modelConfiguration(w, smOnly) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(pdf(w))
    if not smOnly :
        modelConfig.SetParametersOfInterest(w.set("poi"))
        modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def q0q1(inputData, factor, A_ewk_ini) :
    def thing(i) :
        return (o["nHad"][i] - o["nHadBulk"][i]*A_ewk_ini*factor)
    o = inputData.observations()
    return thing(0)/thing(1)

def initialkQcd(inputData, factor, A_ewk_ini) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()    
    out = q0q1(inputData, factor, A_ewk_ini)
    out *= obs["nHadBulk"][1]/float(obs["nHadBulk"][0])
    out = math.log(out)
    out /= (htMeans[1] - htMeans[0])
    return out

def initialAQcd(inputData, factor, A_ewk_ini, kQcd) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()
    out = math.exp(kQcd)
    out *= (obs["nHad"][0]/float(obs["nHadBulk"][0]) - A_ewk_ini*factor)
    return out
                     
def initialkQcdControl(inputData, label) :
    obs = inputData.observations()
    out = float(obs["nHadControl%s"%label][0]*obs["nHadBulk"][1])/float(obs["nHadControl%s"%label][1]*obs["nHadBulk"][0])
    out = math.log(out)
    htMeans = inputData.htMeans()    
    out /= (htMeans[1] - htMeans[0])
    return out

def initialAQcdControl(inputData, label) :
    obs = inputData.observations()
    htMeans = inputData.htMeans()
    out = math.exp( initialkQcdControl(inputData, label)*htMeans[0] )
    out *= (obs["nHadControl%s"%label][0]/float(obs["nHadBulk"][0]))
    return out
                     
def hadTerms(w, inputData, REwk, RQcd, nFZinv, smOnly, hadControlSamples = []) :
    o = inputData.observations()
    htMeans = inputData.htMeans()
    terms = []

    A_ewk_ini = 1.3e-5
    if REwk :
        wimport(w, r.RooRealVar("A_ewk", "A_ewk", A_ewk_ini, 0.0, 1.0))
        wimport(w, r.RooRealVar("k_ewk", "k_ewk", 1.0e-6,    0.0, 1.0))
    if REwk=="Constant" :
        w.var("k_ewk").setVal(0.0)
        w.var("k_ewk").setConstant()

    wimport(w, r.RooRealVar("A_qcd", "A_qcd", 1.5e-5, 0.0, 100.0))
    wimport(w, r.RooRealVar("k_qcd", "k_qcd", 1.0e-5, 0.0,   1.0))
    if RQcd=="Zero" :
        w.var("A_qcd").setVal(0.0)
        w.var("A_qcd").setConstant()
        w.var("k_qcd").setVal(0.0)
        w.var("k_qcd").setConstant()
    else :
        factor = 0.7
        if not hadControlSamples :
            w.var("k_qcd").setVal(initialkQcd(inputData, factor, A_ewk_ini))
        else :
            w.var("k_qcd").setVal(initialkQcdControl(inputData, "_"+hadControlSamples[0]))
        w.var("A_qcd").setVal(initialAQcd(inputData, factor, A_ewk_ini, w.var("k_qcd").getVal()))

    for i,htMeanValue,nBulkValue in zip(range(len(htMeans)), htMeans, o["nHadBulk"]) :
        for item in ["htMean", "nBulk"] :
            wimport(w, r.RooRealVar("%s%d"%(item, i), "%s%d"%(item, i), eval("%sValue"%item)))

    iLast = len(htMeans)-1
    for i,nHadValue in zip(range(len(htMeans)), o["nHad"]) :
        wimport(w, r.RooFormulaVar("qcd%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A_qcd"), w.var("k_qcd"), w.var("htMean%d"%i))))
        if REwk :
            wimport(w, r.RooFormulaVar("ewk%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A_ewk"), w.var("k_ewk"), w.var("htMean%d"%i))))
            ewk = w.function("ewk%d"%i)
        else :
            wimport(w, r.RooRealVar("ewk%d"%i, "ewk%d"%i, 0.5*max(1, nHadValue), 0.0, 10.0*max(1, nHadValue)))
            ewk = w.var("ewk%d"%i)

        if nFZinv=="All" :
            wimport(w, r.RooRealVar("fZinv%d"%i, "fZinv%d"%i, 0.5, 0.2, 0.8))
        elif nFZinv=="One" :
            if not i :
                wimport(w, r.RooRealVar("fZinv%d"%i, "fZinv%d"%i, 0.5, 0.0, 1.0))
            else :
                wimport(w, r.RooFormulaVar("fZinv%d"%i, "(@0)", r.RooArgList(w.var("fZinv0"))))
        elif nFZinv=="Two" :
            if not i :
                wimport(w, r.RooRealVar("fZinv%d"%i, "fZinv%d"%i, 0.5, 0.0, 1.0)); firstFZinv = w.var("fZinv0")
                wimport(w, r.RooRealVar("fZinv%d"%iLast, "fZinv%d"%iLast, 0.5, 0.0, 1.0)); lastFZinv = w.var("fZinv%d"%iLast)
            elif i!=iLast :
                argList = r.RooArgList(firstFZinv, lastFZinv, w.var("htMean%d"%i), w.var("htMean0"), w.var("htMean%d"%iLast))
                wimport(w, r.RooFormulaVar("fZinv%d"%i, "(@0)+((@2)-(@3))*((@1)-(@0))/((@4)-(@3))", argList))

        fZinv = w.var("fZinv%d"%i) if w.var("fZinv%d"%i) else w.function("fZinv%d"%i)
        wimport(w, r.RooFormulaVar("zInv%d"%i, "(@0)*(@1)",       r.RooArgList(ewk, fZinv)))
        wimport(w, r.RooFormulaVar("ttw%d"%i,  "(@0)*(1.0-(@1))", r.RooArgList(ewk, fZinv)))

        wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)", r.RooArgList(ewk, w.function("qcd%d"%i))))
        wimport(w, r.RooRealVar("nHad%d"%i, "nHad%d"%i, nHadValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadB%d"%i)))
        else :
            wimport(w, r.RooProduct("hadS%d"%i, "hadS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("signalEffHad%d"%i))))
            wimport(w, r.RooAddition("hadExp%d"%i, "hadExp%d"%i, r.RooArgSet(w.function("hadB%d"%i), w.function("hadS%d"%i))))
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadExp%d"%i)))
        terms.append("hadPois%d"%i)
    
    if not smOnly :
        terms.append("signalGaus") #defined in signalVariables()
    w.factory("PROD::hadTerms(%s)"%",".join(terms))

def hadControlTerms(w, inputData, REwk, RQcd, smOnly, label = "") :
    def s(i = None) : return ("_%s%s"%(label, "_%d"%i if i!=None else ""))
    o = inputData.observations()
    htMeans = inputData.htMeans()
    terms = []

    assert (REwk and RQcd=="FallingExp")
    wimport(w, r.RooRealVar("A_qcdControl%s"%s(), "A_qcdControl%s"%s(), initialAQcdControl(inputData, s()), 0.0, 100.0))
    wimport(w, r.RooRealVar("A_ewkControl%s"%s(), "A_ewkControl%s"%s(), 10.0e-6, 0.0, 1.0))
    wimport(w, r.RooRealVar("k_ewkControl%s"%s(), "k_ewkControl%s"%s(), 0.0, 0.0, 1.0))
    w.var("k_ewkControl%s"%s()).setVal(0.0)
    w.var("k_ewkControl%s"%s()).setConstant()

    for i,htMeanValue,nBulkValue,nControlValue in zip(range(len(htMeans)), htMeans, o["nHadBulk"], o["nHadControl%s"%s()]) :
        wimport(w, r.RooFormulaVar("qcdControl%s"%s(i), "(@0)*(@1)*exp(-(@2)*(@3))",
                                   r.RooArgList(w.var("nBulk%d"%i), w.var("A_qcdControl%s"%s()), w.var("k_qcd"),        w.var("htMean%d"%i))))
        wimport(w, r.RooFormulaVar("ewkControl%s"%s(i), "(@0)*(@1)*exp(-(@2)*(@3))",
                                   r.RooArgList(w.var("nBulk%d"%i), w.var("A_ewkControl%s"%s()), w.var("k_ewkControl%s"%s()), w.var("htMean%d"%i))))
        wimport(w, r.RooFormulaVar("hadControlB%s"%s(i), "(@0)+(@1)", r.RooArgList(w.function("ewkControl%s"%s(i)), w.function("qcdControl%s"%s(i)))))
        wimport(w, r.RooRealVar("nHadControl%s"%s(i), "nHadControl%s"%s(i), nControlValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadControlPois%s"%s(i), "hadControlPois%s"%s(i), w.var("nHadControl%s"%s(i)), w.function("hadControlB%s"%s(i))))
        else :
            wimport(w, r.RooPoisson("hadControlPois%s"%s(i), "hadControlPois%s"%s(i), w.var("nHadControl%s"%s(i)), w.function("hadControlB%s"%s(i))))            
        terms.append("hadControlPois%s"%s(i))
    
    w.factory("PROD::hadControlTerms%s(%s)"%(s(), ",".join(terms)))

def mumuTerms(w, inputData) :
    terms = []
    wimport(w, r.RooRealVar("rhoMumuZ", "rhoMumuZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("oneMumu", "oneMumu", 1.0))
    wimport(w, r.RooRealVar("sigmaMumuZ", "sigmaMumuZ", inputData.fixedParameters()["sigmaMumuZ"]))
    wimport(w, r.RooGaussian("mumuGaus", "mumuGaus", w.var("oneMumu"), w.var("rhoMumuZ"), w.var("sigmaMumuZ")))
    terms.append("mumuGaus")

    rFinal = None
    for i,nMumuValue,purity,mcZmumuValue,mcZinvValue,stopHere in zip(range(len(inputData.observations()["nMumu"])),
                                                                     inputData.observations()["nMumu"],
                                                                     inputData.purities()["mumu"],
                                                                     inputData.mcExpectations()["mcZmumu"],
                                                                     inputData.mcExpectations()["mcZinv"],
                                                                     inputData.constantMcRatioAfterHere(),
                                                                     ) :
        if nMumuValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcZmumu"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        wimport(w, r.RooRealVar("nMumu%d"%i, "nMumu%d"%i, nMumuValue))
        wimport(w, r.RooRealVar("rMumu%d"%i, "rMumu%d"%i, (mcZumuValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("mumuExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMumuZ"), w.var("rMumu%d"%i), w.function("zInv%d"%i))))
        wimport(w, r.RooPoisson("mumuPois%d"%i, "mumuPois%d"%i, w.var("nMumu%d"%i), w.function("mumuExp%d"%i)))
        terms.append("mumuPois%d"%i)
    
    w.factory("PROD::mumuTerms(%s)"%",".join(terms))

def photTerms(w, inputData) :
    terms = []
    wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("onePhot", "onePhot", 1.0))
    wimport(w, r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", inputData.fixedParameters()["sigmaPhotZ"]))
    wimport(w, r.RooGaussian("photGaus", "photGaus", w.var("onePhot"), w.var("rhoPhotZ"), w.var("sigmaPhotZ")))
    terms.append("photGaus")

    rFinal = None
    for i,nPhotValue,purity,mcGjetValue,mcZinvValue,stopHere in zip(range(len(inputData.observations()["nPhot"])),
                                                                    inputData.observations()["nPhot"],
                                                                    inputData.purities()["phot"],
                                                                    inputData.mcExpectations()["mcGjets"],
                                                                    inputData.mcExpectations()["mcZinv"],
                                                                    inputData.constantMcRatioAfterHere(),
                                                                    ) :
        if nPhotValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcGjets"][i:])/sum(inputData.mcExpectations()["mcZinv"][i:])
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, (mcGjetValue/mcZinvValue if not rFinal else rFinal)/purity))
        wimport(w, r.RooFormulaVar("photExp%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoPhotZ"), w.var("rPhot%d"%i), w.function("zInv%d"%i))))
        wimport(w, r.RooPoisson("photPois%d"%i, "photPois%d"%i, w.var("nPhot%d"%i), w.function("photExp%d"%i)))
        terms.append("photPois%d"%i)
    
    w.factory("PROD::photTerms(%s)"%",".join(terms))

def muonTerms(w, inputData, smOnly) :
    terms = []
    wimport(w, r.RooRealVar("rhoMuonW", "rhoMuonW", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("oneMuon", "oneMuon", 1.0))
    wimport(w, r.RooRealVar("sigmaMuonW", "sigmaMuonW", inputData.fixedParameters()["sigmaMuonW"]))
    wimport(w, r.RooGaussian("muonGaus", "muonGaus", w.var("oneMuon"), w.var("rhoMuonW"), w.var("sigmaMuonW")))
    terms.append("muonGaus")

    rFinal = None
    for i,nMuonValue,mcMuonValue,mcTtwValue,stopHere in zip(range(len(inputData.observations()["nMuon"])),
                                                            inputData.observations()["nMuon"],
                                                            inputData.mcExpectations()["mcMuon"],
                                                            inputData.mcExpectations()["mcTtw"],
                                                            inputData.constantMcRatioAfterHere(),
                                                            ) :
        if nMuonValue<0 : continue
        if stopHere : rFinal = sum(inputData.mcExpectations()["mcMuon"][i:])/sum(inputData.mcExpectations()["mcTtw"][i:])
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue if not rFinal else rFinal))
        wimport(w, r.RooFormulaVar("muonB%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.function("ttw%d"%i))))

        if smOnly :
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonB%d"%i)))
        else :
            wimport(w, r.RooProduct("muonS%d"%i, "muonS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("muonLumi"), w.var("signalEffMuon%d"%i))))
            wimport(w, r.RooAddition("muonExp%d"%i, "muonExp%d"%i, r.RooArgSet(w.function("muonB%d"%i), w.function("muonS%d"%i))))
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def signalVariables(w, inputData, signalDict) :
    wimport(w, r.RooRealVar("hadLumi", "hadLumi", inputData.lumi()["had"]))
    wimport(w, r.RooRealVar("muonLumi", "muonLumi", inputData.lumi()["muon"]))
    wimport(w, r.RooRealVar("xs", "xs", signalDict["xs"]))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 2.0))

    wimport(w, r.RooRealVar("oneRhoSignal", "oneRhoSignal", 1.0))
    wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("deltaSignal", "deltaSignal", 2.0*inputData.fixedParameters()["sigmaLumi"]))
    wimport(w, r.RooGaussian("signalGaus", "signalGaus", w.var("oneRhoSignal"), w.var("rhoSignal"), w.var("deltaSignal")))

    for key,value in signalDict.iteritems() :
        if key=="xs" : continue
        for iBin,eff in enumerate(value) :
            name = "signal%s%d"%(key.replace("eff","Eff"), iBin)
            wimport(w, r.RooRealVar(name, name, eff))

def multi(w, variables, inputData) :
    out = []
    bins = range(len(inputData.observations()["nHad"]))
    for item in variables :
        for i in bins :
            if item.count("_") < 2 : name = "%s%d"%(item,i)
            else : name = "%s_%d"%(item,i)
            if not w.var(name) : continue
            out.append(name)
    return out

def setupLikelihood(w, inputData, REwk, RQcd, nFZinv, signalDict, includeHadTerms = True, hadControlSamples = [],
                    includeMuonTerms = True, includePhotTerms = True, includeMumuTerms = False) :
    terms = []
    obs = []
    nuis = []
    multiBinObs = []
    multiBinNuis = []

    if signalDict :
        signalVariables(w, inputData, signalDict)

    smOnly = not signalDict
    nuis += ["A_qcd","k_qcd"]
    if REwk : nuis += ["A_ewk","k_ewk"]

    hadTerms(w, inputData, REwk, RQcd, nFZinv, smOnly, hadControlSamples)
    photTerms(w, inputData)
    muonTerms(w, inputData, smOnly)
    mumuTerms(w, inputData)

    if includeHadTerms :
        terms.append("hadTerms")
        multiBinObs.append("nHad")

    for item in hadControlSamples :
        hadControlTerms(w, inputData, REwk, RQcd, smOnly, item)
        terms.append("hadControlTerms_%s"%item)
        multiBinObs.append("nHadControl_%s"%item)

    if includePhotTerms :
        terms.append("photTerms")
        obs.append("onePhot")
        multiBinObs.append("nPhot")
        nuis.append("rhoPhotZ")
        
    if includeMuonTerms :
        terms.append("muonTerms")
        obs.append("oneMuon")
        multiBinObs.append("nMuon")
        nuis.append("rhoMuonW")
        
    if includeMumuTerms :
        terms.append("mumuTerms")
        obs.append("oneMumu")
        multiBinObs.append("nMumu")
        nuis.append("rhoMumuZ")
        
    multiBinNuis += ["fZinv"]

    w.factory("PROD::model(%s)"%",".join(terms))

    if not smOnly :
        obs.append("oneRhoSignal")
        nuis.append("rhoSignal")
        w.defineSet("poi", "f")

    obs += multi(w, multiBinObs, inputData)
    nuis += multi(w, multiBinNuis, inputData)
    w.defineSet("obs", ",".join(obs))
    w.defineSet("nuis", ",".join(nuis))

def dataset(obsSet) :
    out = r.RooDataSet("dataName","dataTitle", obsSet)
    #out.reset() #needed?
    out.add(obsSet)
    #out.Print("v")
    return out

def plInterval(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly
    out = {}
    calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()
    out["upperLimit"] = lInt.UpperLimit(wspace.var("f"))
    out["lowerLimit"] = lInt.LowerLimit(wspace.var("f"))

    if makePlots :
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        psFile = "intervalPlot_%s_%g.ps"%(note, 100*cl)
        plot = r.RooStats.LikelihoodIntervalPlot(lInt)
        plot.Draw(); print
        canvas.Print(psFile)
        utils.ps2pdf(psFile)

    utils.delete(lInt)
    return out

def fcExcl(dataset, modelconfig, wspace, note, smOnly, cl = None, makePlots = True) :
    assert not smOnly

    f = r.RooRealVar("f", "f", 1.0)
    poiValues = r.RooDataSet("poiValues", "poiValues", r.RooArgSet(f))
    r.SetOwnership(poiValues, False) #so that ~FeldmanCousins() can delete it
    points = [1.0]
    for point in [0.0] + points :
        f.setVal(point)
        poiValues.add(r.RooArgSet(f))
        
    out = {}
    calc = r.RooStats.FeldmanCousins(dataset, modelconfig)
    calc.SetPOIPointsToTest(poiValues)
    calc.FluctuateNumDataEntries(False)
    calc.UseAdaptiveSampling(True)
    #calc.AdditionalNToysFactor(4)
    #calc.SetNBins(40)
    #calc.GetTestStatSampler().SetProofConfig(r.RooStats.ProofConfig(wspace, 1, "workers=4", False))
    
    calc.SetConfidenceLevel(cl)
    lInt = calc.GetInterval()

    out["upperLimit"] = lInt.UpperLimit(wspace.var("f"))
    return out

def cls(dataset, modelconfig, wspace, smOnly, method, nToys, makePlots) :
    assert not smOnly

    out = {}

    if method=="CLs" :
        calc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)

        wspace.var("f").setVal(0.0)
        wspace.var("f").setConstant()
        calc.SetNullParameters(r.RooArgSet(wspace.var("f")))
        out["CLb"] = 1.0 - calc.GetHypoTest().NullPValue()

        wspace.var("f").setVal(1.0)
        wspace.var("f").setConstant()
        calc.SetNullParameters(r.RooArgSet(wspace.var("f")))
        out["CLs+b"] = calc.GetHypoTest().NullPValue()

    if method=="CLsViaToys" :
        wspace.var("f").setVal(0.0)
        wspace.var("f").setConstant()
        out["CLb"] = 1.0 - pValue(wspace, dataset, nToys = nToys, note = "", plots = makePlots)

        wspace.var("f").setVal(1.0)
        wspace.var("f").setConstant()
        out["CLs+b"] = pValue(wspace, dataset, nToys = nToys, note = "", plots = makePlots)
        
    out["CLs"] = out["CLs+b"]/out["CLb"] if out["CLb"] else 9.9
    return out

def profilePlots(dataset, modelconfig, note, smOnly) :
    assert not smOnly

    canvas = r.TCanvas()
    canvas.SetTickx()
    canvas.SetTicky()
    psFile = "profilePlots_%s.ps"%note
    canvas.Print(psFile+"[")

    plots = r.RooStats.ProfileInspector().GetListOfProfilePlots(dataset, modelconfig); print
    for i in range(plots.GetSize()) :
        plots.At(i).Draw("al")
        canvas.Print(psFile)
    canvas.Print(psFile+"]")
    utils.ps2pdf(psFile)

def pseudoData(wspace, nToys) :
    out = []
    #make pseudo experiments with current parameter values
    dataset = pdf(wspace).generate(obs(wspace), nToys)
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        data = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.add(argSet)
        out.append(data)
    return out

def limits(wspace, snapName, modelConfig, smOnly, cl, datasets, makePlots = False) :
    out = []
    for i,dataset in enumerate(datasets) :
        wspace.loadSnapshot(snapName)
        #dataset.Print("v")
        interval = plInterval(dataset, modelConfig, wspace, note = "", smOnly = smOnly, cl = cl, makePlots = makePlots)
        out.append(interval["upperLimit"])
    return sorted(out)

def quantiles(limits, plusMinus, makePlots = False) :
    def histoFromList(l, name, title, bins, cutZero = False) :
        h = r.TH1D(name, title, *bins)
        for item in l :
            if cutZero and (not item) : continue
            h.Fill(item)
        return h
    
    def probList(plusMinus) :
        def lo(nSigma) : return ( 1.0-r.TMath.Erf(nSigma/math.sqrt(2.0)) )/2.0
        def hi(nSigma) : return 1.0-lo(nSigma)
        out = []
        out.append( (0.5, "Median") )
        for key,n in plusMinus.iteritems() :
            out.append( (lo(n), "MedianMinus%s"%key) )
            out.append( (hi(n), "MedianPlus%s"%key)  )
        return sorted(out)

    def oneElement(i, l) :
        return map(lambda x:x[i], l)
    
    pl = probList(plusMinus)
    probs = oneElement(0, pl)
    names = oneElement(1, pl)
    
    probSum = array.array('d', probs)
    q = array.array('d', [0.0]*len(probSum))

    h = histoFromList(limits, name = "upperLimit", title = ";upper limit on XS factor;toys / bin", bins = (50, 1, -1), cutZero = True) #enable auto-range
    h.GetQuantiles(len(probSum), q, probSum)
    return dict(zip(names, q)),h
    
def expectedLimit(dataset, modelConfig, wspace, smOnly, cl, nToys, plusMinus, note = "", makePlots = False) :
    assert not smOnly
    
    #fit to SM-only
    wspace.var("f").setVal(0.0)
    wspace.var("f").setConstant(True)
    results = utils.rooFitResults(pdf(wspace), dataset)

    #generate toys
    toys = pseudoData(wspace, nToys)

    #restore signal model
    wspace.var("f").setVal(1.0)
    wspace.var("f").setConstant(False)

    #save snapshot
    snapName = "snap"
    wspace.saveSnapshot(snapName, wspace.allVars())

    #fit toys
    l = limits(wspace, snapName, modelConfig, smOnly, cl, toys)
    q,hist = quantiles(l, plusMinus, makePlots)
    nSuccesses = hist.GetEntries()

    obsLimit = limits(wspace, snapName, modelConfig, smOnly, cl, [dataset])[0]

    if makePlots : plotting.expectedLimitPlots(quantiles = q, hist = hist, obsLimit = obsLimit, note = note)
    return q,nSuccesses

def pValue(wspace, data, nToys = 100, note = "", plots = True) :
    def lMax(results) :
        #return math.exp(-results.minNll())
        return -results.minNll()
    
    def indexFraction(item, l) :
        totalList = sorted(l+[item])
        assert totalList.count(item)==1
        return totalList.index(item)/(0.0+len(totalList))
        
    results = utils.rooFitResults(pdf(wspace), data) #fit to data
    wspace.saveSnapshot("snap", wspace.allVars())    
    lMaxData = lMax(results)
    
    graph = r.TGraph()
    lMaxs = []
    for i,dataSet in enumerate(pseudoData(wspace, nToys)) :
        wspace.loadSnapshot("snap")
        #dataSet.Print("v")
        results = utils.rooFitResults(pdf(wspace), dataSet)
        lMaxs.append(lMax(results))
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
        utils.delete(results)
    
    out = indexFraction(lMaxData, lMaxs)
    if plots : plotting.pValuePlots(pValue = out, lMaxData = lMaxData, lMaxs = lMaxs, graph = graph, note = note)
    return out

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def pdf(w) :
    return w.pdf("model")

def obs(w) :
    return w.set("obs")

def note(REwk = None, RQcd = None, nFZinv = None, hadTerms = None, hadControlSamples = [], muonTerms = None, photTerms = None, mumuTerms = None) :
    out = ""
    if REwk : out += "REwk%s_"%REwk
    out += "RQcd%s"%RQcd
    out += "_fZinv%s"%nFZinv
    if hadTerms :        out += "_had"
    for item in hadControlSamples : out += "_hadControl_%s"%item
    if muonTerms :       out += "_muon"
    if photTerms :       out += "_phot"
    if mumuTerms :       out += "_mumu"
    return out

class foo(object) :
    def __init__(self, inputData = None, REwk = None, RQcd = None, nFZinv = None, signal = {}, signalExampleToStack = ("", {}), trace = False,
                 hadTerms = True, hadControlSamples = [], muonTerms = True, photTerms = True, mumuTerms = False) :
        for item in ["inputData", "REwk", "RQcd", "nFZinv", "signal", "signalExampleToStack",
                     "hadTerms", "hadControlSamples", "muonTerms", "photTerms", "mumuTerms"] :
            setattr(self, item, eval(item))

        self.checkInputs()
        r.gROOT.SetBatch(True)
        r.RooRandom.randomGenerator().SetSeed(1)

        self.wspace = r.RooWorkspace("Workspace")
        setupLikelihood(self.wspace, self.inputData, self.REwk, self.RQcd, self.nFZinv, self.signal,
                        includeHadTerms = self.hadTerms, hadControlSamples = self.hadControlSamples,
                        includeMuonTerms = self.muonTerms, includePhotTerms = self.photTerms, includeMumuTerms = self.mumuTerms)
        self.data = dataset(obs(self.wspace))
        self.modelConfig = modelConfiguration(self.wspace, self.smOnly())

        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def checkInputs(self) :
        assert self.REwk in ["", "FallingExp", "Constant"]
        assert self.RQcd in ["FallingExp", "Zero"]
        assert self.nFZinv in ["One", "Two", "All"]
        bins = self.inputData.htBinLowerEdges()
        for d in [self.signal, self.signalExampleToStack[1]] :
            for key,value in d.iteritems() :
                if key=="xs" : continue
                assert key in ["effHad", "effMuon"]
                assert len(value)==len(bins)
            
    def smOnly(self) :
        return not self.signal

    def note(self) :
        d = {}
        for item in ["REwk", "RQcd", "nFZinv", "hadTerms", "hadControlSamples", "muonTerms", "photTerms", "mumuTerms"] :
            d[item] = getattr(self, item)
        return note(**d)
    
    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        utils.rooFitResults(pdf(self.wspace), self.data).Print("v")
        #wspace.Print("v")

    def interval(self, cl = 0.95, method = "profileLikelihood", makePlots = False) :
        if method=="profileLikelihood" :
            return plInterval(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)
        elif method=="feldmanCousins" :
            return fcExcl(self.data, self.modelConfig, self.wspace, self.note(), self.smOnly(), cl = cl, makePlots = makePlots)

    def cls(self, method = "CLs", nToys = 300, makePlots = False) :
        return cls(self.data, self.modelConfig, self.wspace, self.smOnly(), method = method, nToys = nToys, makePlots = makePlots)

    def profile(self) :
        profilePlots(self.data, self.modelConfig, self.note(), self.smOnly())

    def pValue(self, nToys = 200) :
        pValue(self.wspace, self.data, nToys = nToys, note = self.note())

    def expectedLimit(self, cl = 0.95, nToys = 200, plusMinus = {}, makePlots = False) :
        return expectedLimit(self.data, self.modelConfig, self.wspace, smOnly = self.smOnly(), cl = cl, nToys = nToys,
                             plusMinus = plusMinus, note = self.note(), makePlots = makePlots)

    def bestFit(self, printPages = False) :
        plotting.validationPlots(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data),
                                 self.inputData, self.REwk, self.RQcd, self.hadControlSamples, self.smOnly(), self.note(), self.signalExampleToStack, printPages = printPages)
