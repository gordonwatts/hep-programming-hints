# Extracting awkward array data from ServiceX

Use the `to_awk` function on the result of the `deliver` call to convert the dictionary of results into a dictionary of `awkward` arrays.

Continuing the example from the `servicex` section above:

```python
from servicex_analysis_utils import to_awk

all_jets_pts_awk = to_awk(all_jet_pts_delivered)
jet_pts = all_jets_pts_awk["jet_pt_fetch"]
```

And `jet_pts.jet_pt` is a awkward array of jets $p_T$'s. where `jet_pt` comes from the query dictionary.
