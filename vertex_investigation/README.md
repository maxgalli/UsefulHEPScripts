# Vertex Investigation for nanoAODs

This repo contains the script to perform studies on Hgg vertex, in order to understand if it is possible to use vertex 0th instead of the one we choose with a BDT. The reason for this is that vertex 0th is the only one already present in the centrally produced nanoAODs.
Using [this branch](https://github.com/maxgalli/flashgg/tree/Vertex_Investigation) of flashgg we produce two samples of simulated ggH events, one with the currently used vertex and the other with vertex 0th. The scripts in this repo perform studies on these two samples and compare them.
N.B.: at the moment of writing, studies are performed only on ggH samples, but for sure everything will be adapted to produces samples for every production channel.

These are the main studies performed:

- **Reconstruction efficiency**: compute fraction of vertexes are reconstructed closer than 10 mm from the "true" one; this is done as a function of p<sub>t</sub> (```draw_efficiencies_pt.py```) and number of vertexes (```draw_efficiencies_nvtx.py```); resulting plots can be seen [here](https://gallim.web.cern.ch/gallim/plots/Hgg/VertexInvestigation/id_efficiency/);
- Fit $\sigma_M$ in **subdetector categories**, performed in two ways: using **zfit** (```fit_sigma_m.py```, even if goodness of fit is not performed) and using **RooFit** (```fit_sigma_m_roofit.py```); the categories chosen for the fit are (for each gamma pair) EBEB, EBEE, EEEE; main plots available [here];(https://gallim.web.cern.ch/gallim/plots/Hgg/VertexInvestigation/mass_fit_subdetector_categories/mass_fit_roofit/)
- Fit $\sigma_M$ in categories of $\frac{\sigma_{M}}{M}$: categories are designed with an algorithm that minimizes the difference between number of events in each bin; ```fit_sigma_m_smom_cat.py``` performs the fit and dumps a pickle file (```sigma_m_final_plots_specs.pkl```) which then works as an input for ```fit_sigma_m_smom_final_plots.py``` to produce the final plot (see [here](https://gallim.web.cern.ch/gallim/plots/Hgg/VertexInvestigation/m_fit_sigmaMOverM/)).
