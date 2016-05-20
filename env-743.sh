if [[ "$HOSTNAME" == *hep.ph.ic.ac.uk ]]; then
    . /vols/cms/grid/setup.sh
    LOC=/cvmfs/cms.cern.ch/

elif [[ "$HOSTNAME" == *.fnal.gov ]]; then
    echo "FIX ME"
else
    LOC=/afs/cern.ch/cms
fi

cd ${LOC}/slc6_amd64_gcc472/cms/cmssw/CMSSW_6_2_10/src && eval `scramv1 runtime -sh` && cd - > /dev/null
