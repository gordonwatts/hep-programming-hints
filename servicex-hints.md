# ServiceX FuncADL xAOD Code Snippets

Use ServiceX to fetch data from `rucio` datasets on the GRID, skimming out only the data required from the events needed.

Fetching data is two steps. First, construct a query. Second, execute the query against a dataset.

Important Note: Moving data out of ServiceX and into awkward arrays is expensive. If there is something you can do to reduce the amount of data out of ServiceX it is worth doing it. For example, if you know that you'll never use jets with less than 40 GeV, you can filter jets at the ServiceX level.

## A Simple Full Example

This example fetches the jet $p_T$'s from a PHYSLITE formatted xAOD data sample stored by `rucio`.

```python
from func_adl_servicex_xaodr25 import FuncADLQueryPHYSLITE
from servicex_analysis_utils import to_awk
from servicex import deliver, ServiceXSpec, Sample, dataset

# The base query should run against PHYSLITE.
base_query = FuncADLQueryPHYSLITE()

# Query: get all jet pT
jet_pts_query = (base_query
    .SelectMany(lambda evt: evt.Jets())
    .Select(lambda jet: {
        "jet_pt": jet.pt() / 1000.0,
    })
)

# Do the fetch
# Define the dataset
ds_name = ("mc23_13p6TeV:mc23_13p6TeV.801167.Py8EG_A14NNPDF23LO_jj_JZ2.deriv.DAOD_PHYSLITE.e8514_e8528_a911_s4114_r15224_r15225_p6697")

all_jet_pts = to_awk(
    deliver(
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
)
```

`all_jet_pts` is a dictionary indexed by the `Sample` `Name`. And `all_jet_pts["jet_pt_fetch"].jet_pt` is a awkward array of jets $p_T$'s.

## The `deliver` function

* Leave `NFiles` out to run on the full dataset, but start with 1 for testing. Only change it to something else if there is a good reason (and please explain that reason in your response to the user).
* The query can be re-used.
* Use `dataset.Rucio` for a `rucio` dataset, use `dataset.FileList` for a list of web accessible datasets (via `https` or `xrootd://`)

## Queries

Queries have to start from a base, like `FuncADLQueryPHYSLITE`.

* Assume all queries are on Release 25 datasets (the `func_adl_servicex_xaodr25` package)
* Use `FuncADLQueryPHYSLITE` for ATLAS PHYSLITE samples - that have already had calibrations, etc., applied.
* Use `FuncADLQueryPHYS` for ATLAS PHYS or other derivations (like LLP1, etc.)

The `base_query` is a sequence of events. Each event contains collections of objects like Jets and Electrons. `evt.Jets()` gets you the collection of jets for a particular event. You can pass `calibrated=False` to prevent calibration in `PHYS`, but note that `PHYSLITE` does not have uncalibrated jets (or other objects) in it!

It is best practice to always end the query with a `Select` call that puts the data in a dictionary, as the dictionary keys become column labels.

## Selecting a Flat Variable (Jet $p_T$)

Use `SelectMany` to flatten jets across all events, then `Select` to get each jet’s transverse momentum. This yields a flat list of jet $p_T$ values (in GeV) from all events.

```python
query = FuncADLQueryPHYS() \
    .SelectMany(lambda e: e.Jets("AntiKt4EMTopoJets")) \
    .Select(lambda j: {"pt": j.pt() / 1000.0'})
```

Notes:

- If you have flattened a variable like this, you'll get an unnested array.

*(The above returns an Awkward Array of jet $p_T$ values under the key `pt`.)*

## Selecting Nested Data per Event (Jets per Event)

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

You cannot nest the selection: the following will not work:

```python
# Example of what not to do
source = FuncADLQueryPHYSLITE()
jets_per_event = source.Select(lambda e: e.Jets())
query = jets_per_event.Select(lambda jets: jets.Select(lambda j:
    {
        "pt": j.pt()/1000.0,  # WILL NOT WORK
        "eta": j: j.eta(),  # WILL NOT WORK
    }))
```


*Each event in the resulting Awkward Array has a list of events, each with a list of jet $p_T$ and $\eta$ values.*

## Filtering Objects in a Query (Jet Cuts)

Use the `Where` operator to filter objects by a condition. For example, to select only jets with $p_T > 30~GeV$:

```python
# Select eta of jets with pt > 30 GeV
query = (FuncADLQueryPHYSLITE()
    .SelectMany(lambda e: e.Jets())
    .Where(lambda j: j.pt() / 1000.0 > 30.0)
    .Select(lambda j: {'pt': j.eta()})
)
```

*This returns the $\eta$ of all jets with $p_T > 30$ GeV. The `Where` clause filters the jets before the final selection.*

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
query = (FuncADLQueryPHYSLITE() \
    .Select(lambda e: (e.Electrons("Electrons"), e.Muons("Muons")))
    .Select(lambda pairs: {
        'ele_pt':  pairs[0].Select(lambda ele: ele.pt()),
        'ele_eta': pairs[0].Select(lambda ele: ele.eta())
        'mu_pt': pairs[1].Select(lambda mu: mu.pt()),
        'mu_eta': pairs[1].Select(lambda mu: mu.eta())
    })
)
```

*Here `pairs[0]` and `pairs[1]` refer to the Electron and Muon lists respectively. The result contains four Awkward Array fields: electron $p_T$, electron $\eta$, muon $p_T$, muon $\eta$ for each event.*

## Computing New Variables in the Query

You can compute derived quantities on the fly by using nested `Select` operations. For example, compute a trivial product of electron $\eta$ and $\phi$ for each electron:

```python
# For events with any jets >30 GeV, compute eta*phi for each electron
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: 
        e.Jets("AntiKt4EMTopoJets")
         .Where(lambda j: j.pt()/1000.0 > 30.0).Count() > 0')
    .Select(lambda e: e.Electrons("Electrons")
                       .Select(lambda ele: ele.eta() * ele.phi()))
)
```

*This filters events (at least one jet $>30$ GeV) and then produces a new electron-level variable **EleEtaPhiProd** = $\eta \times \phi$. The inner `Select` computes the expression for each electron in the event.*

## Getting the First Object in a Sequence

Sometimes one needs the first object in a sequence. For example, to get the first jet in the event:

```python
query = (FuncADLQueryPHYSLITE()
    .Select(lambda e: {'first_jet_pt': e.Jets().First().pt()}))
```

Note that if there are no jets, then this will crash - so if there might be zero in the sequence, protect with a count:

```python
query = (FuncADLQueryPHYSLITE()
    .Where(lambda e: e.Jets().Count() > 0)
    .Select(lambda e: {'first_jet_pt': e.Jets().First().pt()}))
```
