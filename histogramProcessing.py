#!/usr/bin/env python
import collections
import configuration as conf
import ROOT as r

def checkHistoBinning() :
    def axisStuff(axis) :
        return (axis.GetXmin(), axis.GetXmax(), axis.GetNbins())

    def properties(handles) :
        out = collections.defaultdict(list)
        for handle in handles :
            f = r.TFile(handle[0])
            h = f.Get("%s/%s"%(handle[1], handle[2]))
            out["x"].append(axisStuff(h.GetXaxis()))
            out["y"].append(axisStuff(h.GetYaxis()))
            f.Close()
        return out
    
    def handles() :
        s = conf.stringsNoArgs()
        return [
            (s["signalFile"],        s["signalDir2"],      s["signalLoYield"]),
            (s["sys05File"],         s["signalDir2"],      s["signalLoYield"]),
            (s["sys2File"],          s["signalDir2"],      s["signalLoYield"]),
            (s["muonControlFile"],   s["muonControlDir2"], s["muonControlLoYield"]),
            ]

    for axis,values in properties(handles()).iteritems() :
        assert len(set(values))==1,"The %s binnings do not match: %s"%(axis, str(values))
    
def fullPoints() :
    #return 
    f = r.TFile(conf.mSuGra_FileMuonControl())
    h = f.Get("%s/%s"%(conf.mSuGra_DirMuonControl(), conf.mSuGra_HistMuonControl()))
    out = []

    for iBinX in range(1, 1+h.GetNbinsX()) :
        for iBinY in range(1, 1+h.GetNbinsY()) :
            for iBinZ in range(1, 1+h.GetNbinsZ()) :
                content = h.GetBinContent(iBinX, iBinY, iBinZ)
                if content==0.0 : continue
                out.append( (iBinX, iBinY, iBinZ) )

    f.Close()
    return out

def cachedPoints() :
    if conf.switches()["testPointsOnly"] :
        return [(10, 10, 1), (10, 20, 1), (20, 10, 1), (20, 20, 1)]
    else :
        return fullPoints()

def points() :
    return _points

_points = cachedPoints()
