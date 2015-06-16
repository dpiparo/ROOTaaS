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
    # Change highlight mode
    display.display_javascript(utils.jsDefaultHighlight.format(mimeType = utils.cppMIME), raw=True)
    print "Notebook is in Cpp mode"

def iPythonize():
    utils.setStyle()
    for capture in utils.captures: capture.register()
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.cppmagic")
    ExtensionManager(get_ipython()).load_extension("ROOTaaS.iPyROOT.dclmagic")
    # Define highlight mode for %%cpp and %%dcl magics
    display.display_javascript(utils.jsMagicHighlight.format(cppMIME = utils.cppMIME), raw=True)

    ROOT.toCpp = toCpp
    welcomeMsg()


iPythonize()


