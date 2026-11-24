# Run from the MetaPj project after closing jamovi.
# Optional: options(jamovi_home="PATH/TO/JAMOVI") before sourcing this file.
if(!requireNamespace('jmvtools',quietly=TRUE))stop('Install jmvtools before compiling MetaPj.')
status<-jmvtools::install()
if(!is.null(status)&&status!=0L)stop('MetaPj build/install failed: ',status)
