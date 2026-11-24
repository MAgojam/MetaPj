# Independent statistical core: metafor is a dependency; Metafora is not.
mzMpRequired <- function(kind,input_type='variance') {
    if(kind=='dichotomous')return(c('ai','bi','ci','di'))
    if(kind=='means')return(c('n1i','m1i','sd1i','n2i','m2i','sd2i'))
    if(kind!='generic')stop('Unsupported input family.',call.=FALSE)
    switch(input_type,variance=c('yi','vi'),se=c('yi','sei'),ci=c('yi','ciLower','ciUpper'),
           stop('Unsupported generic uncertainty input.',call.=FALSE))
}

mzMpFit <- function(dataset, mapping, kind, measure, fe=TRUE, re=TRUE, level=95, leave_one_out=FALSE,
                    input_type='variance',input_ci_level=95) {
    if(!fe && !re)stop('Select at least one model: FE or RE.',call.=FALSE)
    allowed <- switch(kind,dichotomous=c('RR','OR','RD'),means=c('MD','SMD'),generic=c('GEN','GEN_LOG'),
                      stop('Unsupported input family.',call.=FALSE))
    if(!measure %in% allowed)stop('Unsupported effect measure.',call.=FALSE)
    if(!is.numeric(level)||length(level)!=1L||!is.finite(level)||level<50||level>99.9)
        stop('Confidence level must be between 50 and 99.9.',call.=FALSE)
    required <- mzMpRequired(kind,input_type)
    if(kind=='generic'&&input_type=='ci'&&(!is.numeric(input_ci_level)||length(input_ci_level)!=1L||
       !is.finite(input_ci_level)||input_ci_level<50||input_ci_level>99.9))
        stop('Input CI level must be between 50 and 99.9.',call.=FALSE)
    if(!all(required %in% names(mapping)))stop('Select all required study columns.',call.=FALSE)
    frame <- as.data.frame(lapply(mapping[required],function(column) {
        if(!column %in% names(dataset))stop('A selected column is no longer available.',call.=FALSE)
        jmvcore::toNumeric(dataset[[column]])
    }))
    n <- nrow(frame)
    complete <- if(n)Reduce(`&`,lapply(frame,is.finite)) else logical()
    labels <- if(!is.null(mapping$study)&&mapping$study %in% names(dataset))
        as.character(dataset[[mapping$study]]) else paste('Study',seq_len(n))
    labels[is.na(labels)|!nzchar(trimws(labels))] <- paste('Study',which(is.na(labels)|!nzchar(trimws(labels))))
    usable <- frame[complete,,drop=FALSE]
    rows <- which(complete)
    input_note <- NULL
    if(kind=='generic') {
        ratio <- measure=='GEN_LOG'
        variance <- if(input_type=='variance')usable$vi else if(input_type=='se') {
            if(any(usable$sei<=0))stop('Standard errors must be positive. Dataset rows: ',paste(rows[usable$sei<=0],collapse=', '),call.=FALSE)
            usable$sei^2
        } else {
            invalid <- usable$ciLower>=usable$ciUpper|usable$yi<usable$ciLower|usable$yi>usable$ciUpper
            if(any(invalid))stop('Input CI limits must be ordered and contain the effect. Dataset rows: ',paste(rows[invalid],collapse=', '),call.=FALSE)
            width <- usable$ciUpper-usable$ciLower
            tolerance <- 0.01*width+64*.Machine$double.eps*pmax(abs(usable$yi),abs(usable$ciLower),abs(usable$ciUpper))
            asymmetric <- abs(usable$yi-(usable$ciLower+width/2))>tolerance
            if(any(!is.finite(width))||any(asymmetric))
                stop('Input CIs must be finite and approximately symmetric on the supplied analysis scale. Supply variance or SE for asymmetric/non-Wald intervals.',call.=FALSE)
            ((width)/(2*qnorm((1+input_ci_level/100)/2)))^2
        }
        if(any(!is.finite(variance)|variance<=0))
            stop('Generic inputs must yield finite, positive sampling variances. Dataset rows: ',paste(rows[!is.finite(variance)|variance<=0],collapse=', '),call.=FALSE)
        effects <- data.frame(yi=usable$yi,vi=variance)
        input_note <- switch(input_type,
            variance='Generic effects: supplied sampling variances used without transformation.',
            se='Generic effects: sampling variance = supplied standard error squared.',
            ci=paste0('Generic effects: sampling variance approximated from ',input_ci_level,'% normal-based Wald CIs on the supplied analysis scale; output CI level is set separately.'))
        if(ratio)input_note <- paste(input_note,'Inputs are log effects/log CI limits; only estimates and interval bounds are exponentiated for display.')
    } else if(kind=='dichotomous') {
        invalid <- if(nrow(usable))apply(usable,1,function(x)any(x<0|x!=floor(x))||x[1]+x[2]<=0||x[3]+x[4]<=0) else logical()
        if(any(invalid))stop(paste('Event/non-event counts must be non-negative integers with positive group totals. Dataset rows:',paste(rows[invalid],collapse=', ')),call.=FALSE)
        ratio <- measure %in% c('RR','OR')
        effects <- do.call(metafor::escalc,c(list(measure=measure,add=if(ratio)0.5 else 0,
            to=if(ratio)'only0' else 'none',drop00=ratio),as.list(usable)))
    } else {
        invalid <- with(usable,n1i<2|n2i<2|n1i!=floor(n1i)|n2i!=floor(n2i)|sd1i<0|sd2i<0)
        if(any(invalid))stop(paste('Sample sizes must be integers of at least 2; SDs must be non-negative. Dataset rows:',paste(rows[invalid],collapse=', ')),call.=FALSE)
        ratio <- FALSE
        effects <- do.call(metafor::escalc,c(list(measure=measure),as.list(usable)))
    }
    keep <- is.finite(effects$yi)&is.finite(effects$vi)&effects$vi>0
    yi <- effects$yi[keep];vi <- effects$vi[keep];rows <- rows[keep]
    if(length(yi)<2L)stop('At least two studies with finite effects and positive sampling variances are required.',call.=FALSE)
    critical <- qnorm(1-(1-level/100)/2)
    display <- function(x)if(ratio)exp(x) else x
    studies <- data.frame(study=labels[rows],source_row=rows,yi=yi,vi=vi,
        estimate=display(yi),lower=display(yi-critical*sqrt(vi)),upper=display(yi+critical*sqrt(vi)),
        weight_FE=NA_real_,weight_RE=NA_real_,stringsAsFactors=FALSE)
    models <- list();fits <- list()
    for(model in c(if(fe)'FE',if(re)'RE')) {
        fit <- metafor::rma(yi=yi,vi=vi,method=if(model=='FE')'FE' else 'REML',test='z',level=level)
        prediction <- predict(fit,level=level)
        studies[[paste0('weight_',model)]] <- as.numeric(weights(fit))
        models[[model]] <- list(model=model,method=if(model=='FE')'FE' else 'REML',
            estimate=display(as.numeric(fit$b)),lower=display(fit$ci.lb),upper=display(fit$ci.ub),
            analysis_estimate=as.numeric(fit$b),se=fit$se,statistic=fit$zval,p=fit$pval,
            tau2=if(model=='RE')fit$tau2 else NULL,I2=fit$I2,H2=fit$H2,Q=fit$QE,
            Q_df=fit$k-fit$p,Q_p=fit$QEp,
            pi_lower=if(model=='RE')display(prediction$pi.lb) else NULL,
            pi_upper=if(model=='RE')display(prediction$pi.ub) else NULL)
        fits[[model]] <- fit
    }
    plot_values <- c(studies$lower,studies$upper,unlist(lapply(models,function(x)c(x$lower,x$upper,x$pi_lower,x$pi_upper))))
    if(any(!is.finite(plot_values))|| (ratio&&any(plot_values<=0)))
        stop('Effect intervals exceed the finite plotting range. Check sparse or extreme study data.',call.=FALSE)
    diagnostics<-list(leave_one_out=list(),notes=list())
    if(leave_one_out) {
        if(length(yi)<3L)diagnostics$notes<-list('Leave-one-out requires at least three included studies.') else {
            for(model in names(fits)) {
                diagnostic<-tryCatch(metafor::leave1out(fits[[model]]),error=identity)
                if(inherits(diagnostic,'error')) {
                    diagnostics$notes<-c(diagnostics$notes,list(paste(model,conditionMessage(diagnostic))));next
                }
                diagnostics$leave_one_out[[length(diagnostics$leave_one_out)+1L]]<-list(model=model,
                    rows=data.frame(omitted=studies$study,source_row=rows,
                        analysis_estimate=diagnostic$estimate,estimate=display(diagnostic$estimate),
                        lower=display(diagnostic$ci.lb),upper=display(diagnostic$ci.ub),
                        se=diagnostic$se,tau2=if(model=='RE')diagnostic$tau2 else rep(NA_real_,length(yi)),I2=diagnostic$I2))
            }
        }
    }
    # Pseudo-CI funnel limits follow metafor's default SE-based construction (addtau2=FALSE).
    reference<-models[[if(re)'RE'else'FE']]
    se<-seq(0,max(sqrt(vi))*1.05,length.out=50)
    diagnostics$funnel<-list(model=reference$model,center=reference$analysis_estimate,
        se=as.list(se),lower=as.list(reference$analysis_estimate-critical*se),
        upper=as.list(reference$analysis_estimate+critical*se))
    display_measure <- if(kind=='generic')if(ratio)'Ratio (exp log effect)'else'Generic effect'else measure
    list(analysis=list(kind=kind,measure=display_measure,ratio=ratio,level=level,k=length(yi),
        total=n,excluded=n-length(yi),effect_scale=if(kind=='generic')if(ratio)'log ratio'else'Supplied effect scale'else if(ratio)paste0('log ',measure)else measure,
        input_type=if(kind=='generic')input_type else'group summaries',
        input_ci_level=if(kind=='generic'&&input_type=='ci')input_ci_level else NULL,input_note=input_note),
        studies=studies,models=unname(models),diagnostics=diagnostics)
}
