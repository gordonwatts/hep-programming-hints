# The Histogram phase

For each histogram that needs to be made, list title, x, y, axis titles, number of bins, and high and low limits. List one per histogram.

Notes:

* Where possible, repeat a name that was used to refer to the histogramming data in a previous step.
* Do not hesitate to use latex symbols in the title and axes. Looks more professional!
* For labels, use latex and not unicode characters when math or other symbols are required.
* When using math symbols make sure to include `$` - e.g. `$p_T$`!
* Plot titles should be:
  * Short (`Jet $p_T$`, or `Top Mass`). Try to keep it to less than 6 words so it will fit on top of the plot.
  * Capitalize the title as you would normally capitalize text that is a title. Same with axis labels.
* Pick binning as best you can.
* Histogram `limits`:
  * The is ATLAS data, so any energy units (mass, momentum, energy, etc.) should be in GeV.
  * Make sure you use units for the `limits` of the histogram. Make sure units are consistent with other places used in the plan.

== Start Example Response ==

## Phase Histogram

* Histogram of dijet pt dijet_pT
  * Title: "$p_T$ of the Dijet System"
  * y-axis label: "Event Count"
  * x-axis label: "dijet $p_T$ [GeV]"
  * bins: 50
  * limits: 0-200 GeV

== End Example Response ==
