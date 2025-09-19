# Loading ServiceX Results into RDF

The `all_jet_pts_delivered` contains a set of files that can be turned into a RDF source. Assume
the ServiceX query result is stored in `all_jet_pts_delivered`, as it in the example above.

```python
import ROOT

# Load the ROOT file and create a DataFrame from the tree
# ServiceX always writes a tree with the name `tree`.
df = ROOT.RDataFrame("tree", all_jet_pts_delivered['jet_pt_fetch'])

# Create a histogram of the 'jet_pt' branch
hist = df.Histo1D(("jet_pt_hist", "Jet pT", 100, 0, 500), "jet_pt")

# Draw the histogram
canvas = ROOT.TCanvas()
hist.Draw()
canvas.SaveAs("jet_pt_hist.png")  # Save to file```
```
