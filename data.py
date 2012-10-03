import math,copy

def scaled(t, factor) :
    return tuple([factor*a if a!=None else None for a in t])

def excl(counts, isExclusive) :
    out = []
    for i,count,isExcl in zip(range(len(counts)), counts, isExclusive) :
        out.append(count if (isExcl or count==None) else (count-counts[i+1]))
    return tuple(out)

def itMult(l1 = [], l2 = []) :
    return tuple([a*b if a!=None else None for a,b in zip(l1,l2)])

def _trigKey(sample = "") :
    d = {"mcTtw":"had", "mcZinv":"had", "mcHad": "had",
         "mcMumu":"mumu", "mcMuon":"muon", "mcPhot":"phot",
         "mcSimple":"simple", # legacy for simple
         "mcZmumu":"mumu" # legacy for orig
         }
    if sample not in d :
        for key,value in d.iteritems() :
            if sample[:len(key)] == key :
                print "WARNING: using %s trigger efficiency for %s" % ( value, sample )
                return value
    return d[sample]


vars = ["mergeBins", "htBinLowerEdges", "htMaxForPlot", "lumi", "htMeans", "systBins",
        "observations", "triggerEfficiencies", "mcStatError", "fixedParameters"]

class data(object) :
    def __init__(self, requireFullImplementation = True, systMode = 1) :
        self.requireFullImplementation = requireFullImplementation
        self.systMode = systMode
        self._fill()
        self._checkVars()
        self._checkLengths()
        self._stashInput()
        self._applyTrigger()
        self._doBinMerge()

    def __str__(self, notes = False) :
        out = ""
        for func in ["observations", "mcExpectations", "mcExtra", "mcStatError"] :
            out += "\n".join(["", func, "-"*20, ""])
            d = getattr(self, func)()
            for key in sorted(d.keys()) :
                out += "%s %s\n"%(key, d[key])
            if notes :
                out += r'''
NOTES
-----

- all numbers are after the trigger, i.e.
-- the observations are integers
-- the appropriate MC samples are scaled down to emulate trigger inefficiency
'''
        return out

    def translationFactor(self, tr = ["gZ", "muW", "mumuZ", "muHad"][0], considerLumi = False, afterTrigger = True) :
        dct = {"gZ":   {"num":"mcPhot", "den":"mcZinv"},
               "muW":  {"num":"mcMuon", "den":"mcTtw" },
               "mumuZ":{"num":"mcMumu", "den":"mcZinv"},
               "muHad":{"num":"mcMuon", "den":"mcHad" },
               }[tr]

        value = self.mcExpectations() if afterTrigger else self._mcExpectationsBeforeTrigger
        error = self.mcStatError()
        lumi = self.lumi()

        num = value[dct["num"]]
        den = value[dct["den"]]
        numErr = error[dct["num"]+"Err"]
        denErr = error[dct["den"]+"Err"]

        out = []
        scale = lumi["mcHad"]/lumi[dct["num"]] if considerLumi else 1.0
        for n,d in zip(num,den) :
            if (n is None or not d) :
                out.append(None)
            else :
                out.append(scale * n/d)

        outErr = []
        for n,d,nE,dE,o in zip(num,den,numErr,denErr,out) :
            if (None in [n,d,nE,dE,o]) or (not n) or (not d) :
                outErr.append(None)
            else :
                outErr.append(o*math.sqrt((nE/n)**2 + (dE/d)**2))
        return out,outErr

    def _fill(self) : raise Exception("NotImplemented", "Implement a member function _fill(self)")

    def _checkVars(self) :
        for item in vars+["mcExpectationsBeforeTrigger", "mcExtraBeforeTrigger"] :
            assert hasattr(self, "_%s"%item),item

    def _checkLengths(self) :
        l = len(self._htBinLowerEdges)
        assert len(self._htMeans)==l
        
        for item in ["observations", "mcExpectationsBeforeTrigger", "mcExtraBeforeTrigger", "mcStatError", "systBins"] :
            for key,value in getattr(self,"_%s"%item).iteritems() :
                assert len(value)==l,"%s: %s"%(item, key)

        for key,value in self._systBins.iteritems() :
            assert min(value)==0, "%s_%s"%(str(key), str(value))
            l = 1+max(value)
            assert key in self._fixedParameters, key
            assert len(self._fixedParameters[key])==l, key

    def _stashInput(self) :
        self._htBinLowerEdgesInput = copy.copy(self._htBinLowerEdges)

    def _applyTrigger(self) :
        for s in ["mcExpectations", "mcExtra"] :
            setattr(self, "_%s"%s, {})
            for sample,t in getattr(self, "_%sBeforeTrigger"%s).iteritems() :
                getattr(self, "_%s"%s)[sample] = itMult(t, self._triggerEfficiencies[_trigKey(sample)])
        
    def _doBinMerge(self) :
        if self._mergeBins is None : return
        assert len(self._mergeBins)==len(self._htBinLowerEdges)
        for a,b in zip(self._mergeBins, sorted(self._mergeBins)) :
            assert a==b,"A non-ascending mergeBins spec is not supported."

        l = sorted(list(set(self._mergeBins)))
        for a,b in zip(l, range(len(l))) :
            assert a==b, "Holes are not allowed."

        #adjust HT means (before the others are adjusted)
        newMeans = [0]*len(l)
        nBulk = [0]*len(l)
        for index,value in enumerate(self._htMeans) :
            newMeans[self._mergeBins[index]] += value*self._observations["nHadBulk"][index]
            nBulk   [self._mergeBins[index]] +=       self._observations["nHadBulk"][index]
        for i in range(len(l)) :
            newMeans[i] /= nBulk[i]
        self._htMeans = newMeans

        #adjust self._htBinLowerEdges
        newBins = []
        for index in range(len(l)) :
            htBinLowerIndex = list(self._mergeBins).index(index)
            newBins.append(self._htBinLowerEdges[htBinLowerIndex])
        self._htBinLowerEdges = tuple(newBins)

        #adjust count dictionaries (review the list)
        for item in ["observations", "mcExpectationsBeforeTrigger", "mcExpectations", "mcExtraBeforeTrigger", "mcExtra"] :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*len(l)
                for index,value in enumerate(t) :
                    d[key][self._mergeBins[index]]+=value
            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(value)

        #adjust errors
        for item in ["mcStatError"] :
            d = {}
            for key,t in getattr(self, "_%s"%item).iteritems() :
                d[key] = [0]*len(l)
                for index,value in enumerate(t) :
                    d[key][self._mergeBins[index]] += value*value
            for key,value in d.iteritems() :
                getattr(self, "_%s"%item)[key] = tuple(map(lambda x:math.sqrt(x), value))

        if self.requireFullImplementation :
            assert False,"Implement trigger efficiency merging."
        else :
            print "WARNING: Trigger efficiency merging is not implemented.  Results are nonsense."
        return

    #define functions called by outside world
    for item in vars+["htBinLowerEdgesInput", "mcExpectations", "mcExtra"] :
        exec('def %s(self) : return self._%s'%(item, item))

    def mergeEfficiency(self, inList) :
        mergeSpec = self.mergeBins()
        if not mergeSpec : return inList
        l = sorted(list(set(mergeSpec)))
        out = [0]*len(l)
        for index,value in enumerate(inList) :
            out[mergeSpec[index]] += value
        return out
