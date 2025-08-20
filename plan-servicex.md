# The ServiceX Phase

In this phase the data is fetched from the ATLAS xAOD data file and returned. Additionally, initial, loose cuts are applied if possible to reduce the amount of data required to extract.

The xAOD is arranged in collections (jets, tracks, muons, electrons, photons, vertices, etc.). In this phase you must identify all the collections, and the specific data from each collection, required.

While servicex is capable of complex operations, we want to keep this simple (as long as we can reduce the amount of data we need to pull).

Here is an example output:

== Start Example Response ==

## Phase ServiceX

* Jet Collection
  * What: pt, eta, phi
  * Filter: Jets can be filtered to be 15 GeV or better, and with eta < 1.5
* Electron Collection
  * What: pt, eta, phi
  * Filter: None

== End Example Response ==
