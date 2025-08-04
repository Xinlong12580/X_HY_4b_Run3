# Fitting with shape templates

* The files are located on EOS under `/store/user/xinlong/XHY4bRun3_2022_selection_1p1/Templates__2022__*`
* However, I will group them by process and store them locally under `rootfiles/`.
    * In the final fits, you should keep them on EOS but also group by process so that you reduce the number of histograms needed. This will greatly reduce the amount of computation needed. 
    * I get the files locally and group them using `python get_all.py`

# 1) Create workspace 
`python XYH.py --sig $sig --tf $tf --make --makeCard`

where:
* `$sig` = `3000-300` (by default)
* `$tf` = TF paramererization (0x0 by default)

# 2) Run fit
`python XYH.py --sig $sig --tf $tf --fit`

(to-do, add minimization options e.g. strategy, tolerance, rMin/Max, etc)

# 3) plot results
