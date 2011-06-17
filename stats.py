#!/usr/bin/env python
import os,cPickle,utils
import configuration as conf
import histogramProcessing as hp
############################################
def opts() :
    from optparse import OptionParser
    parser = OptionParser("usage: %prog [options]")
    parser.add_option("--batch",      dest = "batch",      default = None,  metavar = "N", help = "split into N jobs and submit to batch queue (N<=0 means max splitting)")
    parser.add_option("--local",      dest = "local",      default = None,  metavar = "N", help = "loop over events locally using N cores (N>0)")
    parser.add_option("--merge",      dest = "merge",      default = False, action  = "store_true", help = "profile merge job output")
    parser.add_option("--efficiency", dest = "efficiency", default = False, action  = "store_true", help = "make efficiency plots")
    parser.add_option("--validation", dest = "validation", default = False, action  = "store_true", help = "make validation plots")
    parser.add_option("--output",     dest = "output",     default = False, action  = "store_true", help = "write stdout&stderr to disk rather than to /dev/null")
    options,args = parser.parse_args()
    assert options.local==None or int(options.local)>0,"N must be greater than 0"
    for pair in [("local", "batch"), ("merge", "batch"), ("local", "efficiency"), ("batch", "efficiency")] :
        assert (not getattr(options, pair[0])) or (not getattr(options, pair[1])),"Choose only one of (%s, %s)"%pair
    return options
############################################
def jobCmds(nSlices = None) :
    def logFileName(iSlice) :
        return "%s_%d.log"%(conf.stringsNoArgs()["logStem"], iSlice)

    pwd = os.environ["PWD"]

    if nSlices<=0 : nSlices = len(hp.points())
    out = []

    strings = conf.stringsNoArgs()
    switches = conf.switches()
    for iSlice in range(nSlices) :
        args = [ "%d %d %d"%point for point in hp.points()[iSlice::nSlices] ]
        s  = "%s/job.sh"%pwd                             #0
        s += " %s"%pwd                                   #1
        s += " %s"%switches["envScript"]                 #2
        s += " %s"%("/dev/null" if not options.output else "%s/%s"%(pwd, logFileName(iSlice))) #3
        s += " %s"%(" ".join(args))                      #4
        out.append(s)

    return out
############################################
def batch(nSlices) :
    subCmds = ["%s %s"%(conf.switches()["subCmd"], jobCmd) for jobCmd in jobCmds(nSlices)]
    utils.operateOnListUsingQueue(4, utils.qWorker(os.system, star = False), subCmds)
############################################
def local(nWorkers) :
    utils.operateOnListUsingQueue(nWorkers, utils.qWorker(os.system, star = False), jobCmds())
############################################
def mkdirs() :
    s = conf.stringsNoArgs()
    utils.mkdir(s["logDir"])
    utils.mkdir(s["outputDir"])
############################################
def mergeRootFiles(nSlices) :
    def cleanUp(stderr, files) :
        if stderr :
            print "hadd had this stderr: %s"%stderr
            return
        else :
            for fileName in files :
                os.remove(fileName)

    def prunedList(l) :
        out = []
        for fileName in l :
            if os.path.exists(fileName) :
                out.append(fileName)
            else :
                print "Skipping %s"%fileName
        return out

    def go(outFile, inList) :
        inList2 = prunedList(inList)
        hAdd = utils.getCommandOutput("hadd -f %s %s"%(outFile, " ".join(prunedList(inList2))))
        cleanUp(hAdd["stderr"], inList2)
        return outFile if inList2 else None
        
    def mergeOneType(attr) :
        inList = [conf.strings(*point)["%sFileName"%attr] for point in hp.points()]
        outFile = "%s.root"%conf.stringsNoArgs()["%sStem"%attr]

        outFiles = []
        for iSlice in range(nSlices) :
            tmpFile = outFile.replace(".root","_%d.root"%iSlice)
            addedFile = go(tmpFile, inList[iSlice::nSlices])
            if addedFile : outFiles.append(addedFile)
        go(outFile, outFiles)

    mergeOneType("plot")
    if conf.switches()["writeWorkspaceFile"] :
        mergeOneType("workspace")
############################################
hp.checkHistoBinning()
mkdirs()

options = opts()
if options.batch : batch(int(options.batch))
if options.local : local(int(options.local))
if options.merge : hp.mergePickledFiles()
    
if options.merge or options.validation :
    hp.makeValidationPlots()
if options.efficiency :
    hp.makeEfficiencyPlots()
    hp.makeEfficiencyUncertaintyPlots()
    hp.makeTopologyXsLimitPlots()

if not any([getattr(options,item) for item in ["batch", "local", "merge", "validation", "efficiency"]]) :
    print "nPoints = %s"%len(hp.points())
