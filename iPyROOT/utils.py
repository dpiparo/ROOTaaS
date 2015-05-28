import os, sys, select, time, tempfile
from IPython import get_ipython
import itertools
from IPython.display import HTML
import IPython.display
import ROOT

# We want iPython to take over the graphics
ROOT.gROOT.SetBatch()

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
        sys.stdout.write(' \b')
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



    def jsDisplay(self):
        # Workaround to have ConvertToJSON work
        pad = ROOT.gROOT.GetListOfCanvases().FindObject(ROOT.gPad.GetName())
        json = ROOT.TBufferJSON.ConvertToJSON(pad, 3)

        # Here we could optimise the string manipulation
        divId = 'root_plot_' + str(int(time.time()))
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

        self.display()

        return 0

    def register(self):
        self.shell.events.register('pre_execute', self.pre_execute)
        self.shell.events.register('post_execute', self.post_execute)

captures = [StreamCapture(sys.stderr),
            StreamCapture(sys.stdout),
            CanvasCapture()]
