import os
import sys
import select
import time
import tempfile
import itertools
from IPython import get_ipython
from IPython.display import HTML
import IPython.display
import ROOT

# We want iPython to take over the graphics
ROOT.gROOT.SetBatch()


cppMIME = 'text/x-c++src'
ipyMIME = 'text/x-ipython'

jsDefaultHighlight = """
// Set default mode for code cells
IPython.CodeCell.options_default.cm_config.mode = '{mimeType}';
// Set CodeMirror's current mode
var cells = IPython.notebook.get_cells();
cells[cells.length-1].code_mirror.setOption('mode', '{mimeType}');
// Set current mode for newly created cell
cells[cells.length-1].cm_config.mode = '{mimeType}';
"""

jsMagicHighlight = "IPython.CodeCell.config_defaults.highlight_modes['magic_{cppMIME}'] = {{'reg':[/^%%cpp|^%%dcl/]}};"


_jsNotDrawableClassesNames = ["TGraph2D"]

_jsROOTSourceDir = "https://root.cern.ch/js/3.4/"
_jsCanvasWidth = 800
_jsCanvasHeight = 600

_jsCode = """
<div id="{jsDivId}"
     style="width: {jsCanvasWidth}px; height: {jsCanvasHeight}px">
</div>

<script>
require(['{jsROOTSourceDir}scripts/JSRootCore.min.js'],
        function() {{
            require(['{jsROOTSourceDir}scripts/d3.v3.min.js'],
                function() {{
                    require(['{jsROOTSourceDir}scripts/JSRootPainter.min.js'],
                        function() {{
define.amd = null;
JSROOT.source_dir = "{jsROOTSourceDir}";
JSROOT.loadScript("{jsROOTSourceDir}style/JSRootPainter.min.css");
var obj = JSROOT.parse('{jsonContent}');
JSROOT.draw("{jsDivId}", obj, "{jsDrawOptions}");
                        }}
                    );
                }}
            );
        }}
);
</script>
"""

class StreamCapture(object):
    def __init__(self, stream, ip=get_ipython()):
        streamsFileNo={sys.stderr:2,sys.stdout:1}
        self.pipe_out = None
        self.pipe_in = None
        self.sysStreamFile = stream
        self.sysStreamFileNo = streamsFileNo[stream]
        self.shell = ip

    def more_data(self):
        r, _, _ = select.select([self.pipe_out], [], [], 0)
        return bool(r)

    def pre_execute(self):
        #self.sysStreamFile.write(' \b')
        self.pipe_out, self.pipe_in = os.pipe()
        os.dup2(self.pipe_in, self.sysStreamFileNo)

    def post_execute(self):
        out = ''
        if self.pipe_out:
            while self.more_data():
                out += os.read(self.pipe_out, 1024)

        self.sysStreamFile.write(out)
        return 0

    def register(self):
        self.shell.events.register('pre_execute', self.pre_execute)
        self.shell.events.register('post_execute', self.post_execute)

class CanvasCapture(object):
    def __init__(self, ip=get_ipython()):
        self.shell = ip
        self.canvas = None
        self.numberOfPrimitives = 0
        self.jsUID = 0

    def hasGPad(self):
        if not sys.modules.has_key("ROOT"): return False
        if not ROOT.gPad: return False
        return True

    def pre_execute(self):
        if not self.hasGPad(): return 0
        gPad = ROOT.gPad
        self.numberOfPrimitives = len(gPad.GetListOfPrimitives())
        self.primitivesNames = map(lambda p: p.GetName(), gPad.GetListOfPrimitives())
        self.canvas = gPad

    def hasDifferentPrimitives(self):
        newPrimitivesNames = map(lambda p: p.GetName(), ROOT.gPad.GetListOfPrimitives())
        return newPrimitivesNames != self.primitivesNames

    def canJsDisplay(self):
        # to be optimised
        primitivesNames = map(lambda prim: prim.Class().GetName() , ROOT.gPad.GetListOfPrimitives())
        for jsNotDrawClassName in _jsNotDrawableClassesNames:
            if jsNotDrawClassName in primitivesNames:
                print >> sys.stderr, "The canvas contains an object which jsROOT cannot currently handle (%s). Falling back to a static png." %jsNotDrawClassName
                return False
        return True

    def getUID(self):
        self.jsUID += 1
        return self.jsUID

    def jsDisplay(self):
        # Workaround to have ConvertToJSON work
        pad = ROOT.gROOT.GetListOfCanvases().FindObject(ROOT.gPad.GetName())
        json = ROOT.TBufferJSON.ConvertToJSON(pad, 3)

        # Here we could optimise the string manipulation
        divId = 'root_plot_' + str(self.getUID())
        thisJsCode = _jsCode.format(jsCanvasWidth = _jsCanvasWidth,
                                    jsCanvasHeight = _jsCanvasHeight,
                                    jsROOTSourceDir = _jsROOTSourceDir,
                                    jsonContent=json.Data(),
                                    jsDrawOptions="",
                                    jsDivId = divId)

        # display is the key point of this hook
        IPython.display.display(HTML(thisJsCode))
        return 0

    def pngDisplay(self):
        ofile = tempfile.NamedTemporaryFile(suffix=".png")
        ROOT.gPad.SaveAs(ofile.name)
        img = IPython.display.Image(filename=ofile.name, format='png', embed=True)
        IPython.display.display(img)
        return 0

    def display(self):
       if self.canJsDisplay():
           self.jsDisplay()
       else:
           self.pngDisplay()


    def post_execute(self):
        if not self.hasGPad(): return 0
        gPad = ROOT.gPad
        isNew = not self.canvas
        if not (isNew or self.hasDifferentPrimitives()): return 0
        gPad.Update()

        parentCanvas = gPad.GetCanvas()
        if (parentCanvas):
           ROOT.gPad=parentCanvas

        self.display()

        ROOT.gPad=gPad

        return 0

    def register(self):
        self.shell.events.register('pre_execute', self.pre_execute)
        self.shell.events.register('post_execute', self.post_execute)

captures = [StreamCapture(sys.stderr),
            StreamCapture(sys.stdout),
            CanvasCapture()]

def processCppCodeImpl(cell):
    return ROOT.gInterpreter.ProcessLine(cell)

def declareCppCodeImpl(cell):
    return ROOT.gInterpreter.Declare(cell)

def processCppCode(cell):
    retval = processCppCodeImpl(cell)
    return retval

def declareCppCode(cell):
    retval = declareCppCodeImpl(cell)
    return retval

def setStyle():
    style=ROOT.gStyle
    style.SetFuncWidth(3)
    style.SetHistLineWidth(3)
    style.SetMarkerStyle(8)
    style.SetMarkerSize(.5)
    style.SetMarkerColor(ROOT.kBlue)
    style.SetPalette(57)
#    style.SetOptStat(0) # Remove statbox

