# The ServiceX Phase

In this phase the data is fetched from the ATLAS xAOD data file and returned. Additionally, initial, loose cuts are applied if possible to reduce the amount of data required to extract.

The xAOD is arranged in collections (jets, tracks, muons, electrons, photons, vertices, etc.). In this phase you must identify all the collections, and the specific data from each collection, required.

Notes:

* Servicex is capable of complex operations, don't do anything beyond filtering
* Units: At the end of this step everything should be in units of GeV for energy, momentum, etc., and distance measurements should be in meters.
* Don't worry about exact ServiceX data times (containers, etc.). Just mention the general items. A data expert will go over this and is responsible for mapping to explicit containers and branches, etc., in the data file.

Here is an example output:

== Start Example Response ==

## Phase ServiceX

* Dataset(s)
  * <dataset-1>
* Jet Collection
  * What: pt, eta, phi
  * Filter: Jets can be filtered to be 15 GeV or better, and with eta < 1.5
* Electron Collection
  * What: pt, eta, phi
  * Filter: None

== End Example Response ==
