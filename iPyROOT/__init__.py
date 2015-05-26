import tempfile
import IPython.core.magic as ipym
from IPython.core import display
from IPython.display import Javascript
import ROOT

# We want iPython to take over the graphics
ROOT.gROOT.SetBatch()

# Useful parameters

# We need an automatic mechanism: ldd, rootmaps whatever
__classesToiPythonize = [ROOT.TH1,
ROOT.TH2,
ROOT.TH3,
ROOT.TH1C,
ROOT.TH1D,
ROOT.TH1F,
ROOT.TH1I,
ROOT.TH1K,
ROOT.TH1S,
ROOT.TH2C,
ROOT.TH2D,
ROOT.TH2F,
ROOT.TH2I,
ROOT.TH2S,
ROOT.TH3C,
ROOT.TH3D,
ROOT.TH3F,
ROOT.TH3I,
ROOT.TH3S,
ROOT.TH2Poly,
ROOT.TGraphTime,
ROOT.TGraphErrors,
ROOT.TGraphSmooth,
ROOT.TGraph2DErrors,
ROOT.TGraphDelaunay,
ROOT.TGraphBentErrors,
ROOT.TGraphAsymmErrors,
ROOT.TGraph,
ROOT.TGraph2D,
ROOT.TGraphPolar,
ROOT.TGraphPolargram,
ROOT.TGraphQQ,
ROOT.TLine,
ROOT.TLink,
ROOT.TLatex,
ROOT.TLegend,
ROOT.TCanvas]

__jsROOTSourceDir = "https://root.cern.ch/js/3.4/"
__jsCanvasWidth = 800
__jsCanvasHeight = 600

__jsCode = """
// Create DIV
var timestamp = Math.floor(new Date().getTime() / 1000);
var divName = 'object_draw_' + timestamp;
var plotDiv = document.createElement('div');
plotDiv.id = divName;
plotDiv.style.width = "{jsCanvasWidth}px"
plotDiv.style.height = "{jsCanvasHeight}px";
element[0].appendChild(plotDiv);

// Draw object
require(['{jsROOTSourceDir}scripts/JSRootCore.min.js'],
        function() {{{{
            require(['{jsROOTSourceDir}scripts/d3.v3.min.js'],
                function() {{{{
                    require(['{jsROOTSourceDir}scripts/JSRootPainter.min.js'],
                        function() {{{{
define.amd = null;
JSROOT.source_dir = "{jsROOTSourceDir}";
var obj = JSROOT.parse('{{jsonContent}}');
JSROOT.draw(divName, obj, "{{jsDrawOptions}}");
                        }}}}
                    );
                }}}}
            );
        }}}}
);
"""

def iPythonize():
    """
    Add an implementation of the Draw() function which involves javascript
    and the json representation of the object.
    """

    # Keep the Draw method of C++ aside
    for ROOTClass in __classesToiPythonize:
       ROOTClass.CppDraw = ROOTClass.Draw

    # Format string with all parameters but the json and draw options
    preFormattedJSCode = __jsCode.format(jsCanvasWidth = __jsCanvasWidth,
                                         jsCanvasHeight = __jsCanvasHeight,
                                         jsROOTSourceDir = __jsROOTSourceDir)

    # This is the draw function we'll invoke instead of the C++ one
    def PyDraw(self, drawOptions=""):

       # Draw "in ROOT" before going to the pythonisation
       try:
         self.CppDraw(drawOptions)
       except:
         self.CppDraw()

       json = ROOT.TBufferJSON.ConvertToJSON(self, 3)
       thisJsCode = preFormattedJSCode.format(jsonContent=json.Data(),
                                              jsDrawOptions=drawOptions)

       return Javascript(thisJsCode)

    # Now pythonise the Draw method
    for ROOTClass in __classesToiPythonize:
       ROOTClass.Draw = PyDraw

iPythonize()

