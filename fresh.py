#!/usr/bin/env python

import math,plotting,utils
import ROOT as r

def modelConfiguration(w, smOnly) :
    modelConfig = r.RooStats.ModelConfig("modelConfig", w)
    modelConfig.SetPdf(pdf(w))
    if not smOnly :
        modelConfig.SetParametersOfInterest(w.set("poi"))
        modelConfig.SetNuisanceParameters(w.set("nuis"))
    return modelConfig

def initialA(inputData, i = 0) :
    o = inputData.observations()
    return (0.0+o["nHad"][i])*math.exp(initialk(inputData)*o["htMean"][i])/o["nBulk"][i]

def initialk(inputData) :
    o = inputData.observations()
    lengthMatch = len(set(map(lambda x:len(o[x]),["nHad", "nBulk", "htMean"])))==1
    assert lengthMatch and (len(o["nHad"])>1)

    rAlphaT = [(o["nHad"][i]+0.0)/o["nBulk"][i] for i in range(2)]
    return math.log(rAlphaT[1]/rAlphaT[0])/(o["htMean"][0]-o["htMean"][1])

def hadTerms(w, inputData, REwk, RQcd, smOnly) :
    o = inputData.observations()

    terms = []

    A_ini = initialA(inputData)
    k_ini = initialk(inputData)
    wimport(w, r.RooRealVar("A_qcd", "A_qcd", A_ini/10.0, 0.0, 30.0*A_ini))
    wimport(w, r.RooRealVar("k_qcd", "k_qcd", k_ini,      0.0, 30.0*k_ini))

    if REwk :
        wimport(w, r.RooRealVar("A_ewk", "A_ewk", A_ini, 0.0, 30.0*A_ini))
        wimport(w, r.RooRealVar("k_ewk", "k_ewk", k_ini, 0.0, 30.0*k_ini))

    if RQcd=="Zero" :
        w.var("A_qcd").setVal(0.0)
        w.var("A_qcd").setConstant()
        w.var("k_qcd").setVal(0.0)
        w.var("k_qcd").setConstant()

    if REwk=="Constant" :
        w.var("k_ewk").setVal(0.0)
        w.var("k_ewk").setConstant()

    for i,htMeanValue,nBulkValue,nHadValue in zip(range(len(o["htMean"])), o["htMean"], o["nBulk"], o["nHad"]) :
        for item in ["htMean", "nBulk"] :
            wimport(w, r.RooRealVar("%s%d"%(item, i), "%s%d"%(item, i), eval("%sValue"%item)))

        wimport(w, r.RooFormulaVar("qcd%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A_qcd"), w.var("k_qcd"), w.var("htMean%d"%i))))
        if REwk :
            wimport(w, r.RooFormulaVar("ewk%d"%i, "(@0)*(@1)*exp(-(@2)*(@3))", r.RooArgList(w.var("nBulk%d"%i), w.var("A_ewk"), w.var("k_ewk"), w.var("htMean%d"%i))))
            ewk = w.function("ewk%d"%i)
        else :
            wimport(w, r.RooRealVar("ewk%d"%i, "ewk%d"%i, 0.5*max(1, nHadValue), 0.0, 10.0*max(1, nHadValue)))
            ewk = w.var("ewk%d"%i)
        wimport(w, r.RooRealVar("fZinv%d"%i, "fZinv%d"%i, 0.5, 0.0, 1.0))

        wimport(w, r.RooFormulaVar("zInv%d"%i, "(@0)*(@1)",       r.RooArgList(ewk, w.var("fZinv%d"%i))))
        wimport(w, r.RooFormulaVar("ttw%d"%i,  "(@0)*(1.0-(@1))", r.RooArgList(ewk, w.var("fZinv%d"%i))))

        wimport(w, r.RooFormulaVar("hadB%d"%i, "(@0)+(@1)", r.RooArgList(ewk, w.function("qcd%d"%i))))
        wimport(w, r.RooRealVar("nHad%d"%i, "nHad%d"%i, nHadValue))
        if smOnly :
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadB%d"%i)))
        else :
            wimport(w, r.RooProduct("hadS%d"%i, "hadS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("hadLumi"), w.var("hadSignalEff%d"%i))))
            wimport(w, r.RooAddition("hadExp%d"%i, "hadExp%d"%i, r.RooArgSet(w.function("hadB%d"%i), w.function("hadS%d"%i))))
            wimport(w, r.RooPoisson("hadPois%d"%i, "hadPois%d"%i, w.var("nHad%d"%i), w.function("hadExp%d"%i)))
        terms.append("hadPois%d"%i)
    
    if not smOnly :
        terms.append("signalGaus") #defined in signalVariables()
    w.factory("PROD::hadTerms(%s)"%",".join(terms))

def photTerms(w, inputData) :
    terms = []
    #wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 2.0))
    wimport(w, r.RooRealVar("rhoPhotZ", "rhoPhotZ", 1.0, 1.0e-3, 3.0))
    wimport(w, r.RooRealVar("onePhot", "onePhot", 1.0))
    wimport(w, r.RooRealVar("sigmaPhotZ", "sigmaPhotZ", inputData.fixedParameters()["sigmaPhotZ"]))
    wimport(w, r.RooGaussian("photGaus", "photGaus", w.var("onePhot"), w.var("rhoPhotZ"), w.var("sigmaPhotZ")))
    terms.append("photGaus")

    for i,nPhotValue,mcPhotValue,mcZinvValue in zip(range(len(inputData.observations()["nPhot"])),
                                                    inputData.observations()["nPhot"],
                                                    inputData.mcExpectations()["mcPhot"],
                                                    inputData.mcExpectations()["mcZinv"]) :
        if nPhotValue<0 : continue
        wimport(w, r.RooRealVar("nPhot%d"%i, "nPhot%d"%i, nPhotValue))
        wimport(w, r.RooRealVar("rPhot%d"%i, "rPhot%d"%i, mcPhotValue/mcZinvValue))
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

    for i,nMuonValue,mcMuonValue,mcTtwValue in zip(range(len(inputData.observations()["nMuon"])),
                                                   inputData.observations()["nMuon"],
                                                   inputData.mcExpectations()["mcMuon"],
                                                   inputData.mcExpectations()["mcTtw"]) :
        if nMuonValue<0 : continue
        wimport(w, r.RooRealVar("nMuon%d"%i, "nMuon%d"%i, nMuonValue))
        wimport(w, r.RooRealVar("rMuon%d"%i, "rMuon%d"%i, mcMuonValue/mcTtwValue))
        wimport(w, r.RooFormulaVar("muonB%d"%i, "(@0)*(@1)*(@2)", r.RooArgList(w.var("rhoMuonW"), w.var("rMuon%d"%i), w.function("ttw%d"%i))))

        if smOnly :
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonB%d"%i)))
        else :
            wimport(w, r.RooProduct("muonS%d"%i, "muonS%d"%i, r.RooArgSet(w.var("f"), w.var("rhoSignal"), w.var("xs"), w.var("muonLumi"), w.var("muonSignalEff%d"%i))))
            wimport(w, r.RooAddition("muonExp%d"%i, "muonExp%d"%i, r.RooArgSet(w.function("muonB%d"%i), w.function("muonS%d"%i))))
            wimport(w, r.RooPoisson("muonPois%d"%i, "muonPois%d"%i, w.var("nMuon%d"%i), w.function("muonExp%d"%i)))
        
        terms.append("muonPois%d"%i)
    
    w.factory("PROD::muonTerms(%s)"%",".join(terms))

def signalVariables(w, inputData, signalXs, signalEff) :
    wimport(w, r.RooRealVar("hadLumi", "hadLumi", inputData.lumi()["had"]))
    wimport(w, r.RooRealVar("muonLumi", "muonLumi", inputData.lumi()["muon"]))
    wimport(w, r.RooRealVar("xs", "xs", signalXs))
    wimport(w, r.RooRealVar("f", "f", 1.0, 0.0, 5.0))

    wimport(w, r.RooRealVar("oneRhoSignal", "oneRhoSignal", 1.0))
    wimport(w, r.RooRealVar("rhoSignal", "rhoSignal", 1.0, 0.0, 2.0))
    wimport(w, r.RooRealVar("deltaSignal", "deltaSignal", 2.0*inputData.fixedParameters()["sigmaLumi"]))
    wimport(w, r.RooGaussian("signalGaus", "signalGaus", w.var("oneRhoSignal"), w.var("rhoSignal"), w.var("deltaSignal")))

    for box,effs in signalEff.iteritems() :
        for iBin,eff in enumerate(effs) :
            name = "%sSignalEff%d"%(box, iBin)
            wimport(w, r.RooRealVar(name, name, eff))

def multi(w, variables, inputData) :
    out = []
    bins = range(len(inputData.observations()["nHad"]))
    for item in variables :
        for i in bins :
            name = "%s%d"%(item,i)
            if not w.var(name) : continue
            out.append(name)
    return out

def setupLikelihood(w, inputData, REwk, RQcd, signalXs, signalEff) :
    terms = []
    obs = []
    nuis = []
    multiBinObs = []
    multiBinNuis = []

    if signalXs :
        signalVariables(w, inputData, signalXs, signalEff)

    smOnly = not signalXs
    hadTerms(w, inputData, REwk, RQcd, smOnly)
    terms.append("hadTerms")
    multiBinObs.append("nHad")
    nuis += ["A_qcd","k_qcd"]
    if REwk : nuis += ["A_ewk","k_ewk"]

    photTerms(w, inputData)
    muonTerms(w, inputData, smOnly)
    terms += ["photTerms", "muonTerms"]
    obs += ["onePhot", "oneMuon"]
    multiBinObs += ["nPhot", "nMuon"]
    nuis += ["rhoPhotZ", "rhoMuonW"]
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

def interval(dataset, modelconfig, wspace, note, smOnly, makePlot = True) :
    assert not smOnly

    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetConfidenceLevel(0.95)
    plInt = plc.GetInterval()
    ul = plInt.UpperLimit(wspace.var("f"))

    if makePlot :
        canvas = r.TCanvas()
        canvas.SetTickx()
        canvas.SetTicky()
        psFile = "intervalPlot_%s.ps"%note
        plot = r.RooStats.LikelihoodIntervalPlot(plInt)
        plot.Draw(); print
        canvas.Print(psFile)
        utils.ps2pdf(psFile)

    return ul

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

def pValue(wspace, data, nToys = 100, note = "", plots = True) :
    def lMax(results) :
        return math.exp(-results.minNll())
    
    def indexFraction(item, l) :
        totalList = sorted(l+[item])
        assert totalList.count(item)==1
        return totalList.index(item)/(0.0+len(totalList))
        
    results = utils.rooFitResults(pdf(wspace), data) #fit to data
    #wspace.saveSnapshot("snap", wspace.allVars(), False)
    #results.Print()
    lMaxData = lMax(results)
    dataset = pdf(wspace).generate(wspace.set("obs"), nToys) #make pseudo experiments with final parameter values

    graph = r.TGraph()
    lMaxs = []
    for i in range(int(dataset.sumEntries())) :
        argSet = dataset.get(i)
        pseudoData = r.RooDataSet("pseudoData%d"%i, "title", argSet)
        data.reset()
        data.add(argSet)
        #data.Print("v")
        #wspace.loadSnapshot("snap")
        #wspace.var("A").setVal(initialA())
        #wspace.var("k").setVal(initialk())
        results = utils.rooFitResults(pdf(wspace), data)
        lMaxs.append(lMax(results))
        graph.SetPoint(i, i, indexFraction(lMaxData, lMaxs))
        #utils.delete(results)
    
    out = indexFraction(lMaxData, lMaxs)
    if plots : plotting.pValuePlots(pValue = out, lMaxData = lMaxData, lMaxs = lMaxs, graph = graph, note = note)
    return out

def pValueOld(dataset, modelconfig) :
    plc = r.RooStats.ProfileLikelihoodCalculator(dataset, modelconfig)
    plc.SetNullParameters(modelconfig.GetParametersOfInterest())
    htr = plc.GetHypoTest()
    print "p-value = %g +/- %g"%(htr.NullPValue(), htr.NullPValueError())
    print "significance = %g"%htr.Significance()

def wimport(w, item) :
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.WARNING) #suppress info messages
    getattr(w, "import")(item)
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.DEBUG) #re-enable all messages

def pdf(w) :
    return w.pdf("model")

class foo(object) :
    def __init__(self, inputData = None, REwk = None, RQcd = None, signalXs = None, signalEff = {}, trace = False) :
        self.checkInputs(REwk, RQcd, signalEff)
        for item in ["inputData", "REwk", "RQcd", "signalXs", "signalEff"] :
            setattr(self, item, eval(item))

        r.gROOT.SetBatch(True)
        r.RooRandom.randomGenerator().SetSeed(1)

        self.note = plotting.note(REwk, RQcd)
        self.wspace = r.RooWorkspace("Workspace")
        setupLikelihood(self.wspace, inputData, REwk, RQcd, signalXs, signalEff)
        self.data = dataset(self.wspace.set("obs"))
        self.modelConfig = modelConfiguration(self.wspace, self.smOnly())

        if trace :
            #lots of info for debugging (from http://root.cern.ch/root/html/tutorials/roofit/rf506_msgservice.C.html)
            #r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing), r.RooFit.ClassName("RooGaussian"))
            r.RooMsgService.instance().addStream(r.RooFit.DEBUG, r.RooFit.Topic(r.RooFit.Tracing))

    def checkInputs(self, REwk, RQcd, signalEff) :
        assert REwk in ["", "FallingExp", "Constant"]
        assert RQcd in ["FallingExp", "Zero"]
        for key in signalEff.keys() :
            assert key in ["had", "muon"]
            
    def smOnly(self) :
        return not self.signalXs
            
    def debug(self) :
        self.wspace.Print("v")
        plotting.writeGraphVizTree(self.wspace)
        #pars = utils.rooFitResults(pdf(wspace), data).floatParsFinal(); pars.Print("v")
        utils.rooFitResults(pdf(self.wspace), self.data).Print("v")
        #wspace.Print("v")

    def upperLimit(self, makePlot = False) :
        return interval(self.data, self.modelConfig, self.wspace, self.note, self.smOnly(), makePlot = makePlot)

    def profile(self) :
        profilePlots(self.data, self.modelConfig, self.note, self.smOnly())

    def pValue(self, nToys = 200) :
        pValue(self.wspace, self.data, nToys = nToys, note = self.note)

    def bestFit(self) :
        plotting.validationPlots(self.wspace, utils.rooFitResults(pdf(self.wspace), self.data), self.inputData, self.REwk, self.RQcd, self.smOnly())
