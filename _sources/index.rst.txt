.. icecube_tools documentation master file, created by
   sphinx-quickstart on Wed Dec 29 10:33:57 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to icecube_tools's documentation!
=========================================

The ``icecube_tools`` package is designed to make it easier to interact with the publicly available information provided by the `IceCube Neutrino Observatory <https://icecube.wisc.edu>`_ in Python. You can use it to download datasets as well as load detector information like effective areas, energy resolution and angular resolution in a unified format. This information can then be brought together with simple astrophysical source models to run simulations of neutrino detections, or even to evaluate the likelihood and reproduce the results of the standard IceCube point source searches. 

You can find more information on how to make use of ``icecube_tools`` in the example notebooks listed below. The source code for these notebooks can be found in markdown format `here <https://github.com/cescalara/icecube_tools/docs/markdown>`_ in the GitHub repository. These markdown files can then be converted to ``ipynb`` format by using ``jupytext``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   notebooks/public_data_access.ipynb
   notebooks/detector_model.ipynb
   notebooks/source_model.ipynb
   notebooks/simulation.ipynb
   notebooks/point_source_likelihood.ipynb
   notebooks/point_source_analysis.ipynb
   notebooks/events.ipynb
   api/api
