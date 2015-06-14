from IPython import get_ipython, config
from IPython.core import display
from IPython.core.extensions import ExtensionManager
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
    display.display_javascript("IPython.CodeCell.config_defaults.highlight_modes['magic_text/x-c++src'] = {'reg':[/^%%cpp|^%%dcl/]};", raw=True)
    ROOT.toCpp = toCpp
    welcomeMsg()


iPythonize()


