# jamovi's installed engine receiver accepts at most 4 MiB per response.
# Each Pj call is bounded separately; the consumer must bound their aggregation.
mzMpResultBudget <- function()4*1024^2-128*1024

mzMpGuardResponse <- function(self,private,serial,reserialize) {
    budget<-mzMpResultBudget()
    if(!is.raw(serial)||length(serial)<=budget)return(serial)
    original<-length(serial)
    # Saved pre-fix analyses may contain a heavy inactive forest representation.
    self$results$get(if(self$options$resultType=='svg')'forestHtml'else'forestSvg')$setContent('')
    serial<-reserialize()
    if(is.raw(serial)&&length(serial)<=budget)return(serial)
    explanation<-paste0('The combined Results exceed MetaPj\'s safe transport budget (',
        format(original,big.mark=',',scientific=FALSE),' bytes; jamovi\'s receiver limit is 4 MiB). ',
        'The Python extension output was not applied. Select D3 intervals or Chart.js intervals ',
        'under Graphics engine, then Run the extension again to keep its Plotly graph. ',
        'Multiple inline Plotly graphs can duplicate a large library. Statistical tables remain available.')
    # Also handles saved pre-fix results before .run() gets a chance to execute.
    self$results$extension$clear();self$results$extension$setVisible(FALSE)
    errorContent<-paste0('<p role="alert" style="color:#a54848">',mzMpEscape(explanation),'</p>')
    self$results$extensionStatus$setContent(errorContent)
    state<-self$results$state;if(!is.list(state))state<-list()
    state$extensionRejectedKey<-state$extensionKey
    state$extensionRejectedMessage<-errorContent
    state$extensionKey<-NULL;self$results$setState(state)
    serial<-reserialize()
    if(is.raw(serial)&&length(serial)<=budget)return(serial)
    # A large standard presentation must also fail visibly, never block transport.
    for(name in c('forestHtml','forestSvg')) {
        self$results$get(name)$setContent('');self$results$get(name)$setVisible(FALSE)
    }
    self$results$diagnostics$clear();self$results$diagnostics$setVisible(FALSE)
    state$renderKey<-NULL;self$results$setState(state)
    self$results$status$setContent(paste0('<p>',mzMpEscape(
        'The graphic Results exceed jamovi\'s response-size limit. Reduce figure sizes or use D3/Chart.js intervals. Statistical tables remain available.'),'</p>'))
    serial<-reserialize()
    if(is.raw(serial)&&length(serial)<=budget)return(serial)
    # Cache data and per-study tables may themselves be oversized. Keep pooled
    # summaries, and report the omitted presentation rather than returning stale cells.
    private$.fitCache<-NULL;self$results$setState(list())
    self$results$studies$deleteRows();self$results$studies$setVisible(FALSE)
    self$results$status$setContent('<p>The Results exceed jamovi\'s response-size limit. Per-study output and cached presentation were omitted; pooled model summaries remain available. Reduce the amount of output before running again.</p>')
    serial<-reserialize()
    if(is.raw(serial)&&length(serial)<=budget)return(serial)
    # Last-resort bounded native error (including abnormally large saved code/options).
    error<-jmvcore:::createErrorAnalysis('MetaPj Results exceed jamovi\'s response-size limit. Reduce the amount of output.',
        character(),private$.package,private$.name,private$.datasetId,private$.analysisId,private$.revision)
    error$serialize(createErrorOnFailure=FALSE)
}
