from IPython.core.extensions import ExtensionManager
from IPython import get_ipython
import ROOT
import utils


# We want iPython to take over the graphics
ROOT.gROOT.SetBatch()

def setStyle():
    style=ROOT.gStyle
    style.SetFuncWidth(3)
    style.SetHistLineWidth(3)
    style.SetMarkerStyle(8)
    style.SetMarkerSize(.5)
    style.SetMarkerColor(ROOT.kBlue)
    style.SetOptStat(0)

def iPythonize():
    setStyle()
    for capture in utils.captures: capture.register()
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.cppmagic")

iPythonize()


