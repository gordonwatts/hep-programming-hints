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
