#!/usr/bin/env python

import os
import configuration as conf
import histogramProcessing as hp
import ROOT as r

def fetchHisto(file, dir, histo) :
    f = r.TFile(file)
    hOld = f.Get("%s/%s"%(dir,histo))
    h = hOld.Clone("%s_clone"%hOld.GetName())
    h.SetDirectory(0)
    f.Close()
    return h

def collectHistos(model = None, dir = "/vols/cms02/elaird1/24_sms_isr_from_riccardo", subDir = "") :
    out = {}
    dir = "%s/%s"%(dir, subDir)
    for file in os.listdir(dir) :
        fields = file.split("_")
        if model!=fields[0] : continue
        key = (float(fields[1]), float(fields[2]))
        out[key] = fetchHisto("%s/%s"%(dir,file), "lastPt", "last_pT")
    return out

def model() :
    def isSimplifiedModel(model) : return len(model)==2
    out = conf.switches()["signalModel"]
    assert isSimplifiedModel(out),"%s is not a simplified model"%out
    return out

def example2DHisto(item = "sig10") :
    spec = conf.histoSpecs()[item]
    return hp.loYieldHisto(spec, spec["350Dirs"], lumi = 1.0)

def example1DHisto(collection) :
    return collection[collection.keys()[0]]

def output3DHisto(sms, numCollection = None, denCollection = None) :
    xy = example2DHisto()
    z = example1DHisto(numCollection)
    
    name = "%s_weight"%sms
    out = r.TH3F(name, name,
                 xy.GetNbinsX(), xy.GetXaxis().GetXmin(), xy.GetXaxis().GetXmax(),
                 xy.GetNbinsY(), xy.GetYaxis().GetXmin(), xy.GetYaxis().GetXmax(),
                 z.GetNbinsX(),   z.GetXaxis().GetXmin(),  z.GetXaxis().GetXmax())

    for iBinX in range(1, 1+out.GetNbinsX()) :
        x = out.GetXaxis().GetBinLowEdge(iBinX)
        for iBinY in range(1, 1+out.GetNbinsY()) :
            y = out.GetYaxis().GetBinLowEdge(iBinY)
            fake = False
            if (x,y) not in numCollection : continue
            if (x,y) not in denCollection : continue
            for iBinZ in range(1, 1+out.GetNbinsZ()) :
                num = numCollection[(x,y)].GetBinContent(iBinZ)
                den = denCollection[(x,y)].GetBinContent(iBinZ)
                content = num/den if (den and num) else 1.0
                out.SetBinContent(iBinX, iBinY, iBinZ, content)
    return out
    
sms = model()
histos0 = collectHistos(sms, subDir = "gen0")
histos3 = collectHistos(sms, subDir = "gen3")
print output3DHisto(sms, numCollection = histos3, denCollection = histos0)