# ServiceX FuncADL xAOD Code Snippets

Use ServiceX to fetch data from `rucio` datasets on the GRID, skimming out only the data required from the events needed.

Fetching data is two steps. First, construct a query. Second, execute the query against a dataset.

Notes:

* Moving data out of ServiceX is expensive. If there is something you can do to reduce the amount of data out of ServiceX it is worth doing it. For example, if you know that you'll never use jets with less than 40 GeV, you can filter jets at the ServiceX level using a `Where` call.
* Quantities returned from servicex should be in units most people use at the LHC - GeV, meters, etc. Please convert from whatever the units of the input files are.

## A Simple Full Example

This example fetches the jet $p_T$'s from a PHYSLITE formatted xAOD data sample stored by `rucio`.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex import deliver, ServiceXSpec, Sample, dataset

# The base query should run against PHYSLITE.
base_query = FuncADLQueryPHYSLITE()

# Query: get all jet pT
jet_pts_query = (base_query
    .Select(lambda evt: evt.Jets())
    .Select(lambda jets: jets.Select(lambda jet:
    {
        "jet_pt": jet.pt() / 1000.0,
    })
)

# Do the fetch
# Define the rucio dataset identifier (DID).
ds_name = ("mc23_13p6TeV:mc23_13p6TeV.801167.Py8EG_A14NNPDF23LO_jj_JZ2.deriv.DAOD_PHYSLITE.e8514_e8528_a911_s4114_r15224_r15225_p6697")

all_jet_pts_delivered = deliver(
    ServiceXSpec(
        Sample=[
            Sample(
                Name="jet_pt_fetch",
                Dataset=dataset.Rucio(ds_name),
                NFiles=1,
                Query=jet_pts_query,
            )
        ]
    ),
)
```

* `all_jet_pts_delivered` is a dictionary indexed by sample name. It contains a list of `awkward` arrays (in the form of a `GuardList`).

The following code can be used to access the jet pt's from the above example. Note the `jet_pt` for the column name is the same as in the `servicex` query. The jets are an awkward nested array of floats (array of jets in each event).

```python
jet_pt_fetch = akk_jet_pts_delivered["jet_pt_fetch"]
jet_pts = jet_pt_fetch.jet_pt
```

## The `deliver` function

* Always use `NFiles=1` as above, even if the user asks otherwise. If they do, tell them they can run it themselves when they are ready! More files and it takes to long!
* The query can be re-used.
* Use `dataset.Rucio` for a `rucio` dataset, use `dataset.FileList` for a list of web accessible datasets (via `https` or `xrootd://`)
* Only call deliver once - make sure all the data you want is in the query, even if multiple samples - just add more to the `Sample` array.

## Queries

Queries have to start from a base, like `FuncADLQueryPHYSLITE`.

* Assume all queries are on Release 25 datasets (the `func_adl_servicex_xaodr25` package)
* Use `FuncADLQueryPHYSLITE` for ATLAS PHYSLITE samples - that have already had calibrations, etc., applied.
* Use `FuncADLQueryPHYS` for ATLAS PHYS or other derivations (like LLP1, etc.)

The `base_query` is a sequence of events. Each event contains collections of objects like Jets and Electrons. `evt.Jets()` gets you the collection of jets for a particular event. You can pass `calibrated=False` to prevent calibration in `PHYS`, but note that `PHYSLITE` does not have uncalibrated jets (or other objects) in it! This `func_adl` language is based on LINQ.

The last `Select` must create a dictionary (one or more `Where`'s can be after that `Select`). Each element of the dictionary is a value, or a list of values. `func_adl` does not support nested objects of any sort: not even 2D arrays. Each element of the dictionary can be a value or a 1D list. Do not try to fetch a list of muons, where each muon is `pt, eta, phi, E`. Instead, fetch `mu_pt, mu_eta, mu_phi, mu_E`.

`ServiceX` queries can not contain references to `awkward` functions. Instead, use `Select`, `Where`, to effect the same operations.

## Selecting Nested Data per Event

Use nested `Select` calls to retain event structure, retrieving jet properties as lists per event. In this example, each event’s jets are kept together, with their $p_T$ and $\eta$ values:

```python
# For each event, get a list of jets and select each jet's pt and eta
source = FuncADLQueryPHYSLITE()
jets_per_event = source.Select(lambda e: e.Jets())
query = jets_per_event.Select(lambda jets: 
    {
        "pt": jets.Select(lambda j: j.pt()/1000.0),
        "eta": jets.Select(lambda j: j.eta())
    })
```

You cannot nest the final dictionary `Select` statement. It must be at the top query level as shown above.

*Each event in the resulting Array has a list of events, each with a list of jet $p_T$ and $\eta$ values.*

## Filtering Objects in a Query

Use the `Where` operator to filter objects by a condition. For example, to select only jets with $p_T > 30~GeV$:

```python
# Select eta of jets with pt > 30 GeV
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: e.Jets())
    .Select(lambda jets: jets.Where(lambda j: j.pt() / 1000.0 > 30.0))
    .Select(lambda jets: {'eta': jets.Select(lambda j.eta())})
)
```

*This returns an array of the array of all $\eta$ for all jets in each event with $p_T > 30$ GeV. The `Where` clause filters the jets before the final selection. If an event has no jets then it will return an empty array for that event.*

Use the standard python logic operators, like `and` and `or` to combine conditions. Remember to include `(` and `)` when needed.

## Filtering Events by Object Count

You can filter entire events based on conditions on contained objects using `.Where(...).Count()`. For example, to get events with at least **2 jets** above 30 GeV:

```python
# Filter events that have >=2 jets with pt > 30 GeV, then get number of jets in those events
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: e.Jets()
                      .Where(lambda j: j.pt() / 1000.0 > 30.0)
                      .Count() >= 2)
    .Select(lambda e: {'NumJets': e.Jets().Count()})
)
```

*This query first applies an event-level filter requiring at least two jets with $p_T>30$ GeV. It then selects the total jet count per surviving event (field **NumJets**).*

## Selecting Multiple Collections Together (Electrons & Muons)

FuncADL queries can return multiple collections simultaneously. For example, to get electron and muon kinematic variables in one query:

```python
# Select electron and muon collections, then pick their pt and eta
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: {
        'ele': e.Electrons(), 
        'mu': e.Muons()
    }))
    .Select(lambda pairs: {
        'ele_pt':  pairs.ele.Select(lambda ele: ele.pt()/1000),
        'ele_eta': pairs.ele.Select(lambda ele: ele.eta())
        'mu_pt': pairs.mu.Select(lambda mu: mu.pt()/1000),
        'mu_eta': pairs.mu.Select(lambda mu: mu.eta())
    })
```

*Here `pairs.ele` and `pairs.mu` refer to the Electron and Muon lists respectively. The result contains four Array fields: electron $p_T$, electron $\eta$, muon $p_T$, muon $\eta$ for each event.*

Filtering objects is often most easily done at this level as well, as it means putting the filter in only once:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: {
        'ele': e.Electrons().Select(lambda e: e.pt()/1000 > 30), 
        'mu': e.Muons().Select(lambda m: abs(m.eta()) < 2.5)
    }))
    .Select(lambda pairs: {
        'ele_pt':  pairs.ele.Select(lambda ele: ele.pt()/1000),
        'ele_eta': pairs.ele.Select(lambda ele: ele.eta())
        'mu_pt': pairs.mu.Select(lambda mu: mu.pt()/1000),
        'mu_eta': pairs.mu.Select(lambda mu: mu.eta())
    })
```

Only electrons with $pt > 30$ and central muons will have their pt and eta transferred back from ServiceX.

## Computing New Variables in the Query

You can compute derived quantities on the fly by using nested `Select` operations. For example, compute a trivial product of electron $\eta$ and $\phi$ for each electron:

```python
# For events with any jets >30 GeV, compute eta*phi for each electron
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: 
        e.Jets("AntiKt4EMTopoJets")
         .Where(lambda j: j.pt()/1000.0 > 30.0).Count() > 0')
    .Select(lambda e: e.Electrons()
                       .Select(lambda ele: ele.eta() * ele.phi()))
)
```

*This filters events (at least one jet $>30$ GeV) and then produces a new electron-level variable **EleEtaPhiProd** = $\eta \times \phi$. The inner `Select` computes the expression for each electron in the event.*

## Getting the First Object in a Sequence

Sometimes one needs the first object in a sequence. For example, to get the first jet in the event:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: {'first_jet_pt': e.Jets().First().pt()/1000}))
```

Note that if there are no jets, then this will crash - so if there might be zero in the sequence, protect with a count:

```python
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: e.Jets().Count() > 0)
    .Select(lambda e: {'first_jet_pt': e.Jets().First().pt()/1000}))
```

## Errors

If you encounter an error after running, there are two types. The first give you type errors, and those you can solve just by reading the error message carefully and perhaps not doing whatever the code complained about. You might have to look carefully for this message - for example "Method <xx> not found on object."

The second type of error there isn't much you can do to get more information, however. You'll find an error that looks like "Transform "xxx" completed with failures." And something in `stdout` about clicking on `HERE` to get more information. Sadly, only the requester can do that. If that happens just reply with "HELP USER" and that will be a signal. Note that you might get an error as mentioned above and this - in which case try to solve the error before getting the user involved. A common case here is you request some data that should be in the datafiles, but is not.
