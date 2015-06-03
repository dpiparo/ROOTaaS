from IPython.core.extensions import ExtensionManager
from IPython import get_ipython, config
import ROOT
import utils
import cpptransformer
import cppcompleter

# We want iPython to take over the graphics
ROOT.gROOT.SetBatch()

def welcomeMsg():
    print "Welcome to ROOTaas Beta"

def toCpp():
    cpptransformer.load_ipython_extension(get_ipython())
    cppcompleter.load_ipython_extension(get_ipython())
    print "Notebook is in Cpp mode"

def iPythonize():
    utils.setStyle()
    for capture in utils.captures: capture.register()
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.cppmagic")
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.dclmagic")
    ROOT.toCpp = toCpp
    welcomeMsg()


iPythonize()


