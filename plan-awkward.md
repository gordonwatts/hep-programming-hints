# The `awkward` phase

In this phase the data should be taken from the previous phase, filtered, and combined as necessary to generate an awkward array that is ready to be histogrammed or plotted.

This phase has several sub-steps:

1. Build 3-vectors (for spacial filtering or calculations) or 4-vectors (for invariant mass or similar calculations).
2. Filter the previous built objects as necessary
3. Build more complex objects (like an invariant mass, etc.).
4. Repeat steps 2 and 3 as needed until the values for the final arrays are prepared.

The result should be an awkward array.

Each step should be specified in a short english sentence, do not resort to actual `awkward` calls. However, each step should be able to be accomplished with an `awkward` primitive.

Notes:

* Don't re-apply filters that you've already specified in a previous phase. Look at the solution to understand what should be done.
* Assume all input data is in units like GeV and meters - no need to convert.
* Give complex objects a name when they are built, and refer to them later on

== Start Example Response ==

## Phase Awkward

1. Build objects
    * Build 4-vector for jets from pt, eta, and phi
    * BUild 3-vector for electrons from pt, eta, and phi
2. Filter
    * jets must have a pt > 40 GeV
3. Build Objects
    * Build all 2-jet combinations (dijet1)
4. Filter
    * Require the 2-jet combinations (dijet1) to have an invariant mass between 80 and 100.
5. Build Objects
    * Build all electron-dijet1 combinations (edijet1)
6. Filter
    * Remove all edijet1 combinations that are DeltaR < 0.4 from the electrons
7. Build Objects
    * Save the dijet1 pT for those that survive the edijet1 combination for making a histogram (dijet_pT)
== End Example Response ==
