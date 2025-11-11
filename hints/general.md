# Generating HEP Plots Using ServiceX
You will be asked to write python code that will access ATLAS data, extract some items, and then make one or more plots.

If the user's prompt doesn't fit that request, please complain. Generate code using ServiceX to fetch the data, Awkward array to manipulate the data that comes back (with vector for doing any physics calculations like invariant mass), and Hist to generate and plot the histogram. Write the histogram/plots to png files. If hints contain instructions to tell the user some bit of information, make sure to do that. If you are manipulating from ServiceX, use only Awkward array - do not use python lists, etc. Just give the user the code, do not try to create a pull request in any repo.

## Runtime Environment
I want you to create a python virtual environment and install the following python libraries. Use this environment for running the generated script

  - servicex
  - func-adl-servicex-xaodr25
  - hist
  - awkward
  - vector
  - matplotlib
  - servicex_analysis_utils
  - jinja2
  - numpy
  - uproot
  - dask
  - dask-awkward
