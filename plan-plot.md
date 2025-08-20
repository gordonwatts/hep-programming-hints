# Planning Code For A Plot

The code plan for a plot contains three phases:

1. Get the data from the ATLAS dataset using ServiceX. The data will come back as an awkward array.
2. Manipulate the returned data from ServiceX to build the quantity that needs to be plotted using the `awkward` array collection of packages. You should have the data to be histogrammed as flat awkward arrays.
3. Create and fill and plot the histogram using `hist`.

Details for each phase are listed below.
