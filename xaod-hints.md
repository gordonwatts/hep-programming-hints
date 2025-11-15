# xAOD Event Data Model Hints

Some hints to help with accessing xAOD objects.

Important note about units:

* All momentum, energy, and mass units are in MeV (e.g. `pt, E, m`). Unless asked otherwise, convert them to GeV by dividing by 1000 as early as possible.
* All distance units are in millimeters. Convert them to meters as early as possible.

## Jets, Muons, Taus, Photons, Electrons

It is possible to access all these objects from the top event level, e.g.,

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        'pt': jets.Select(lambda j: j.pt()/1000.0),
        'eta': jets.Select(lambda j: j.eta()/1000.0),
    })
```

The only odd one are tau's, which use `e.TauJets("AnalysisTauJets")`.

These objects all have `pt, eta, phi` (with methods by those names). To access `px, py, pz` you have to get the 4-vector first:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.Jets()) \
    .Select(lambda jets: {
        'pt': jets.Select(lambda j: j.p4().px()/1000.0),
    })
```

## MissingET

Access:

```python
query = FuncADLQueryPHYS() \
    .Select(lambda e: e.MissingET().First()) \
    .Select(lambda m: {"met": m.met() / 1000.0'})
```

Despite being only a single missing ET for the event, it is stored as a sequence. Thus you must get the first object and then access the `.met()` method from there. Note that the missing ET object has `met`, `mpy`, `mpx`, etc. It adds an `m` in front of everything.

## xAOD Tool Access

Tools are C++ objects used by the framework that is actually extracting the data for servicex. The code is written by the ATLAS experiment. Helper functions, as you'll see below, are created by two methods,

* `make_a_tool` - defines the tool and schedules it to run in the C++ framework during the servicex translation.
* `make_tool_accessor` defines a small light-weight function in C++ that will return a value from the tool.

These are defined in the `xaod_hints` module if you need to define special tools from user instructions. In many cases you find tool helpers. Examples below show you how to use these functions.

```python
```

### BTaggingSelectionTool: getting jet b-tagging results

The `BTaggingSelectionTool` tool to get either a tag weight/discriminant for b-or-charm tagging or to see if a jet is "tagged" for a particular working point (e.g. passed an experiment defined threshold). The working points are provided by the FTAG group in ATLAS.

Working Point Info:

Working points define different b-tagging efficiency and light/charm rejection.

* Working point names: `FixedCutBEff_65`, `FixedCutBEff_70`, `FixedCutBEff_77`, `FixedCutBEff_85`, `FixedCutBEff_90`
* [Further information for user](https://ftag.docs.cern.ch/recommendations/algs/r22-preliminary/#gn2v01-b-tagging)
* By default choose the `FixedCutBEff_77` working point.
* Make sure to let the user know what operating point in your text explanation.

To define the tool you must:

```python
query = FuncADLQueryPHYSLITE()


Make sure the `tool_name` is different if you need to define multiple tools (because user needs more than one operating point)! Name them something reasonable so the code makes sense!

```python
# Specific for the below code
from func_adl_servicex_xaodr25.xAOD.jet_v1 import Jet_v1
from xaod_hints import make_a_tool, make_tool_accessor

# Define the tool
query_base, tag_tool_info = make_a_tool(
    physlite,
    "btag_discriminator",
    "BTaggingSelectionTool",
    include_files=["xAODBTaggingEfficiency/BTaggingSelectionTool.h"],
    init_lines=[
        'ANA_CHECK(asg::setProperty({tool_name}, "OperatingPoint", "FixedCutBEff_77"));',
        "ANA_CHECK({tool_name}->initialize());",
    ],
    link_libraries=["xAODBTaggingEfficiencyLib"]
)

# If you need the tag weight. Tag weights, output of a GNN, are between -10 and 15.
tag_weight = make_tool_accessor(
    tag_tool_info,
    function_name="tag_weight",
    # false in next line for b-tagging weight, true for c-tagging weight
    source_code=["ANA_CHECK({tool_name}->getTaggerWeight(*jet, result, false));"],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="double",
    return_type_python="float",
)

# If you need to know if a jet is tagged or not.
jet_is_tagged = make_tool_accessor(
    tag_tool_info,
    function_name="jet_is_tagged",
    source_code=[
        "result = static_cast<bool>({tool_name}->accept(*jet));"
    ],
    arguments=[("jet", Jet_v1)],
    return_type_cpp="bool",
    return_type_python="bool",
)

Usage of `jet_is_tagged` in `func_adl` is straight forward:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: e.Jets().Select(lambda j: jet_is_tagged(j)))
```

## Event and Sample Weights

Unless otherwise requested by the user, use the following guidelines to determine how to do event weighting:

* **Single MC or Data Dataset**: Apply only the MC event weight.

* **Multiple MC Datasets**: Apply the MC event weight and the cross section scaling. If the cross section values aren't available for any one sample, then don't apply it for any samples (and make sure to tell the user in the notes you are missing that information). The normal way to plot this is with a stacked histogram.

* **MC and Data**: Apply the MC event weights and the cross section, and scale to the integrated luminosity of the data. The normal way to plot this is to use a stacked histogram and the data as a filled black circles.

Always make sure to tell the user what event weights you are applying. If the above guidance tells you to apply event weights but you don't know how, warn the user.

If any calculations are required (e.g. cross section times integrated luminosity, etc), do them in the code so the user can update things as they wish.

It is not uncommon for a user to ask for a MC sample to be scaled by x10 or similar. Make sure to put the scale factor in the legend entry for that sample.

### MC Event Weight

This is encoded on the `EventInfo` object (there is only one), and it is the first `mcEventWeight`:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: e.EventInfo("EventInfo").mcEventWeight(0))
```

### Data

When including data we need to calculate the luminosity of the data we are including and rescale any MC to that. The proper way is not current available in this system. For now, scale the luminosity for a particular run by the number of events you are looking at (you'll have to count the number of events).

The dataset will contain a tag detailing which run you are looking at. We are using an estimate of the number of events - 10^9 per year.

Dataset | Number of Events | Total Luminosity |
| --- | --- | --- |
data24_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
data22_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
data23_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
data24_13p6TeV | 200000000000000 | 52.4 femto-barns^-1 |
data25_13p6TeV | 150000000000000 | 39.3 femto-barns^-1 |

### Cross-section Scaling and MC

Each event in a sample is scaled by a constant scale factor:

$ sf = $ L * \sigma / N_S $

* $L$ - the target integrated luminosity for the plot. Use 1 femto-barn-1 by default.
* $\sigma$ the cross section of the sample - see below. Doublecheck the units of these numbers! See below for information.
* $N_S$ sum of all the per-event weights (the `mcEventWeight(0)` above). This must be taken as the sum over all events in the file - before *any* cuts. Gather the `mcEventWeight(0)` for all events in the file.

The cross-section table is below, organized by run number and name. Every ATLAS sample is unique by run number, which is in the name of the dataset. For example, "mc23_13p6TeV:mc23_13p6TeV.801167.Py8EG_A14NNPDF23LO_jj_JZ2.deriv.DAOD_PHYSLITE.e8514_e8528_a911_s4114_r15224_r15225_p6697" is an MC dataset with run number 801167 and name Py8EG_A14NNPDF23LO_jj_JZ2 (or JZ2). Data leads with "data..." in the name.

Run Number | Name | Cross Section
--- | --- | ---
801167/364702 | Py8EG_A14NNPDF23LO_jj_JZ2 | 2582600000.0 pico-barn
801168/364703 | Py8EG_A14NNPDF23LO_jj_JZ3 | 28528000.0 pico-barn
513109/700325 | MGPy8EG_Zmumu_FxFx3jHT2bias_SW_CFilterBVeto | 2.39 nano-barn
601237/410471 | PhPy8EG_A14_ttbar_hdamp258p75_allhad | 812 pico-barn
701005/700588 | Sh_2214_lllvjj | 53.1 femto-barn

Make sure to do all calculations in the code; don't do the math in your head. The user may well want to take the code and change some of the parameters.

### Event Scaling and Information on the Plot

When applying this scaling, detail what you are doing in some detail in the notes. On the plot, only put the integrated luminosity you rescaled the MC to (`L=xx $fb^-1$`). Do not mention what scaling was applied, etc., on the plot itself. We want as little possible to detract from the display of the data. If you aren't doing the luminosity rescaling, don't put anything on the plot.
