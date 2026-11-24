# Optional source-maintainer tool; takes the MetaPj root as its only argument.
# Requires metadat, metafor and jmvReadWrite in the maintainer's R libraries.
args<-commandArgs(TRUE);root<-normalizePath(args[1],winslash='/')
data('dat.bcg',package='metadat')
effects<-metafor::escalc(measure='RR',ai=dat.bcg$tpos,bi=dat.bcg$tneg,
                       ci=dat.bcg$cpos,di=dat.bcg$cneg,add=.5,to='only0',drop00=TRUE)
dataset<-data.frame(study=paste(dat.bcg$author,dat.bcg$year),yi=effects$yi,vi=effects$vi,
                    sei=sqrt(effects$vi),ci_lower=effects$yi-qnorm(.975)*sqrt(effects$vi),
                    ci_upper=effects$yi+qnorm(.975)*sqrt(effects$vi))
attr(dataset$study,'jmv-id')<-TRUE
file<-file.path(root,'data','MetaPj_GenericEffects.omv')
jmvReadWrite::write_omv(dataset,file)
restored<-jmvReadWrite::read_omv(file)
stopifnot(nrow(restored)==nrow(dataset),all(names(dataset)%in%names(restored)))
for(name in names(dataset)[-1])stopifnot(isTRUE(all.equal(restored[[name]],dataset[[name]],check.attributes=FALSE,tolerance=1e-12)))
cat('Generic BCG log-RR, variance, SE, 95% log-scale CI Data Library example verified\n')
