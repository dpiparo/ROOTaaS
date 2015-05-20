import ROOT
from IPython.display import Javascript

clToiPythonize=[ROOT.TH1F]

def iPythonize(ROOTClasses):
    """
    Add an implementation of the Draw() function which involves javascript
    and the json representation of the object.
    """
    def Draw(self):
       json = ROOT.TBufferJSON.ConvertToJSON(self, 3)
       return Javascript("""
// Create DIV
var timestamp = Math.floor(new Date().getTime() / 1000);
var divName = 'object_draw_' + timestamp;
var plotDiv = document.createElement('div');
plotDiv.id = divName;
plotDiv.style.width = "800px"
plotDiv.style.height = "600px";
element[0].appendChild(plotDiv);

// Draw object
require(['https://root.cern.ch/js/3.4/scripts/JSRootCore.min.js'],
        function() {
            require(['https://root.cern.ch/js/3.4/scripts/d3.v3.min.js'],
                function() {
                    require(['https://root.cern.ch/js/3.4/scripts/JSRootPainter.min.js'],
                        function() {
define.amd = null;
JSROOT.source_dir = "https://root.cern.ch/js/3.4/";
var obj = JSROOT.parse('""" + json.Data() + """');
JSROOT.draw(divName, obj, "colz");
                        }
                    );
                }
            );
        }
);
""")

    for ROOTClass in ROOTClasses:
       # for debugging purposes
       ROOTClass.__repr__ = lambda obj: "Hello."
       ROOTClass.Draw = Draw 


iPythonize(clToiPythonize)

