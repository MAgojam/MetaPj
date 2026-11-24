# Run from the MetaPj source directory; adapt this connector into your own module.
# Pj must be installed separately. No Pj internal function or private file is used.
source(file.path('R','mzMp_bridge.R'))
service<-mzMpConnect()
response<-service$run(
    code=paste(
        'mzpjShowTable([{"Rows":len(data["x"])}],name="summary")',
        'mzpjShowScatter(data,"x","y",name="graphic",result_type="html")',sep='\n'),
    data=data.frame(x=1:5,y=c(2,4,3,6,7)),python='jamovi',timeout=30L)
# In an R6 analysis, also pass checkpoint=function()private$.checkpoint(flush=FALSE).
# Your module owns the native containers and validates/maps their expected types.
stopifnot(inherits(response,'mzPjServiceResult'))
lapply(response$items,function(item)list(name=item$name,type=item$type))
