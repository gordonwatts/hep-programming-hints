# Loading ServiceX Results into RDF

The `all_jet_pts_delivered` is a dictionary indexed by the `Sample` `Name`. Each entry contains a `GuardList`, a `typing.Sequence` of string pathnames for files that can be used on an RDF source, as shown below. If the ServiceX query result is stored in `all_jet_pts_delivered`, as it in the example above, then you can get the first file into RDF as follows:

```python
import ROOT

# Load the ROOT file and create a DataFrame from the tree
# ServiceX always writes a tree with the name `atlas_xaod_tree`.
file_list = all_jet_pts_delivered['jet_pt_fetch']
df = ROOT.RDataFrame("atlas_xaod_tree", file_list)

# Create a histogram of the 'jet_pt' branch
hist = df.Histo1D(("jet_pt_hist", "Jet pT", 100, 0, 500), "jet_pt")

# Draw the histogram
canvas = ROOT.TCanvas()
hist.Draw()
canvas.SaveAs("jet_pt_hist.png")  # Save to file```
```

* If you want to use only the n'th file, replace `file_list` with `file_list[n]`.

## 4-Vectors - DeltaR, Invariant Mass, etc

The Phi wrap-around must be carefully accounted for when calculating Delta R. The easiest is to use the built in functions:

```c++
#include "TVector2.h"

d_phi = TVector2::Phi_mpi_pi(jet1_phi - jet2_phi)
```

If you are want to do any other 4-vector manipulations then it is best to build a 4-vector"

```c++
#include "Math/Vector4D.h""

v1 = ROOT::Math::PtEtaPhiMVector(jet1_pt, jet1_eta, jet1_phi, jet1_m);
v2 = ROOT::Math::PtEtaPhiMVector(jet2_pt, jet2_eta, jet2_phi, jet2_m);

dr = v1.DeltaR(v2);
```

Other 4-vectors constructor's are defined in `Vector4D.h`: `PtEtaPhiMVector`, `PtEtaPhiEVector`, `PtEtaPhiPxPyPzEVector`, `PxPyPzEVector`, `XYZTVector`. Choose whatever makes most sense to solve the problem if you need 4-vectors.
