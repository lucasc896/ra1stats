import likelihood


class l2010(likelihood.spec):
    def _fill(self):
        self._name = self.__class__.__name__[1:]
        self._constrainQcdSlope = True
        self._qcdParameterIsYield = True
        self._initialValuesFromMuonSample = False
        self._initialFZinvFromMc = False
        self._REwk = ""
        self._RQcd = "FallingExp"
        self._nFZinv = "Two"
        self._legendTitle = "CMS (re-analyzed), L = 35 pb^{-1}, #sqrt{s} = 7 TeV"
        from inputData.dataMisc import orig as module

        self.add([likelihood.selection(name="55",
                                       boxes={"had":True, "muon":True, "phot":False}.keys(),
                                       data = module.data_2010(),
                                       ),
                  ])
