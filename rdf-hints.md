# ROOT's RDataFrame

Use the PyROOT interface to build RDataFrame (RDF) pipelines. Complex manipulations may require C++ code injection as arguments to RDF pipeline primitives.

Try not to code everything in C++, rather code in steps, defining variables with `Declare` that get combined or cut on. Some complex variables may need to be defined by C++, of course.

* Use `<source>.Define` function to define new variables in the RDF
* Use `<source>.Filter` function to filter
* Use `<source>.Histo1D` and `2D` and `3D` functions to define histograms.

Also, you can use in other places

* Use `.Count` function to count (say, number of jets)
* Use `Max`, `Mean`, and `Min` functions as needed.

When you do have to declare C++ functions (with `ROOT.gInterpreter.Declare`) try to make sure they functions follow good engineering principles - so, for example, no duplicated code.

## Define

* `<source>.Define("new_leaf_name", "old_leaf1 + old_leaf2*2.0")` - C++ JIT expression (preferred way - efficient).
* `<source>.Define("new_leaf_name", f"old_leaf*{scale_factor}")` - Inject a value calculated in python into the calculation

## Weights

Lets say you have a per-event weight called `weight` stored in the tree. You want to use it to weight your histogram:

```python
hist_def = ("met_hist", "Missing ET (weighted);MET [GeV];Events", 100, 0.0, 1000.0)
hist = <source>.Histo1D(hist_def, "met", "weight")
```

## Other Notes

* When creating the canvas for the plot, `canvas = ROOT.TCanvas("plot-name")`, it is ok to add a name if you want, but do not add any other arguments (for example, the size). Only default sizes should be used for the canvas.

## 4-Vectors - DeltaR, Invariant Mass, etc

The Phi wrap-around must be carefully accounted for when calculating Delta R. The easiest is to use the built in functions:

```c++
#include "TVector2.h"

d_phi = TVector2::Phi_mpi_pi(jet1_phi - jet2_phi)
```

If you are want to do any other 4-vector manipulations then it is best to build a 4-vector"

```c++
#include "Math/Vector4D.h""
#include "Math/VectorUtil.h"

v1 = ROOT::Math::PtEtaPhiMVector(jet1_pt, jet1_eta, jet1_phi, jet1_m);
v2 = ROOT::Math::PtEtaPhiMVector(jet2_pt, jet2_eta, jet2_phi, jet2_m);

dr = ROOT::Math::VectorUtil::DeltaR(v1, v2);
```

And in RDataFrame you could do:

```cpp
auto df2 = df
  .Define("jet1_p4", "ROOT::Math::PtEtaPhiMVector(jet1_pt, jet1_eta, jet1_phi, jet1_m)")
  .Define("jet2_p4", "ROOT::Math::PtEtaPhiMVector(jet2_pt, jet2_eta, jet2_phi, jet2_m)")
  .Define("deltaR_j1j2", "ROOT::Math::VectorUtil::DeltaR(jet1_p4, jet2_p4)");
```

Other 4-vectors constructor's are defined in `Vector4D.h`: `PtEtaPhiMVector`, `PtEtaPhiEVector`, `PtEtaPhiPxPyPzEVector`, `PxPyPzEVector`, `XYZTVector`. Choose whatever makes most sense to solve the problem if you need 4-vectors.

You can add the vectors together, and use `M()` as the invarrient mass: `(v1+v2).M()`

## `RVec` and defines

RDF works by passing, as arrays, everything from a single event. When processing with C++, you need to use `RVec` for those arrays (not `vector`!!).

If you put this inside a `Declare` statement as a string, it will be JIT compiled by ROOT.

```cpp
# include "ROOT/RVec.hxx"

template<typename TF>
double compute_sum(const ROOT::VecOps::RVec<TF> &a)
{
  double sum = 0;
  for (auto pt : a) {
    sum += pt;
  }
  return sum
}
```

And then this will work correctly:

```python
rdf2 = rdf.Define("sum", "compute_sum(ele_pt)")
```

## The `Take` method, and AsNumpy

Use `Take` to materialize data into a C++ `vector` or `RVec`. Use `AsNumpy` to materialize a numpy array.

Take in python:

```python
pts = df.Take["float"]("pt")
```

 or in C++

```cpp
auto pts = df.Take<float>("pt")
```

And `AsNumpy`:

```python
arrays = df.AsNumpy(columns=['pt', 'eta'])
```

Which will return a dictionary with `pt` and `eta`, and the value `arrays['pt']` will be a numpy array.
