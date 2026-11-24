# The R host owns statistics, native Results and saved state; Pj owns Python execution.
mzMpNativeTables <- function(self,context) {
    frames<-list(studies=context$studies[c('study','estimate','lower','upper','weight_FE','weight_RE')],
        models=do.call(rbind,lapply(context$models,function(m)as.data.frame(lapply(m[c('model','estimate','se','statistic','p','lower','upper','pi_lower','pi_upper')],function(x)if(is.null(x))NA_real_ else x)))),
        heterogeneity=do.call(rbind,lapply(context$models,function(m)as.data.frame(lapply(m[c('model','tau2','I2','H2','Q','Q_df','Q_p')],function(x)if(is.null(x))NA_real_ else x)))))
    names(frames$studies)<-c('Study','Estimate','Lower','Upper','FE_weight','RE_weight')
    names(frames$models)<-c('Model','Estimate','SE','z','p','Lower','Upper','PI_lower','PI_upper')
    names(frames$heterogeneity)<-c('Model','tau2','I2','H2','Q','df','p')
    for(name in names(frames)) {
        f<-frames[[name]];table<-self$results$get(name);table$deleteRows()
        for(i in seq_len(nrow(f)))table$addRow(rowKey=as.character(i),values=as.list(f[i,,drop=FALSE]))
        table$setNote('r_source',paste0('Calculated by R/metafor. ',context$analysis$level,'% intervals; SE and z use the analysis scale. Prediction intervals apply to RE only. ',context$analysis$input_note),init=FALSE)
        table$setVisible(TRUE)
    }
}

mzMpErrorText <- function(error) {
    detail<-error$details
    if(is.character(detail)&&length(detail)==1L&&nzchar(detail))paste(conditionMessage(error),detail,sep='\n')else conditionMessage(error)
}

mzMpErrorContent <- function(error,filename=NULL) {
    text<-mzMpErrorText(error)
    if(!is.null(filename))text<-paste(filename,text,sep='\n')
    content<-paste0('<pre style="white-space:pre-wrap">',mzMpEscape(text),'</pre>')
    if(inherits(error,'mzPjServiceError')&&is.character(error$help_html)&&length(error$help_html)==1L)
        content<-paste0(content,error$help_html)
    content
}

mzMpRun <- function(self,private,kind) {
    status<-function(message)self$results$status$setContent(paste0('<p>',mzMpEscape(message),'</p>'))
    hide<-function()for(name in c('studies','models','heterogeneity','forestHtml','forestSvg','diagnostics','extension'))self$results$get(name)$setVisible(FALSE)
    signature<-NULL
    state<-self$results$state;if(!is.list(state))state<-list()
    if(is.null(private$.fitCache))private$.fitCache<-state$fitCache
    tryCatch({
        inputType<-if(kind=='generic')self$options$genericInput else'variance'
        inputCiLevel<-if(kind=='generic'&&inputType=='ci')self$options$inputCiLevel else 95
        required<-mzMpRequired(kind,inputType)
        mapping<-setNames(lapply(required,function(n)self$options[[if(kind=='generic'&&n%in%c('vi','sei'))'uncertainty'else n]]),required)
        if(any(vapply(mapping,function(x)length(x)!=1L||is.na(x)||!nzchar(x),logical(1)))) {
            hide();status('Select the required study columns. Statistics use R/metafor; Python presentation uses the separately installed Pj module.');return()
        }
        if(length(self$options$study)==1L)mapping$study<-self$options$study
        measure<-switch(kind,dichotomous=self$options$measureDichotomous,means=self$options$measureMeans,generic=self$options$measureGeneric)
        activeData<-self$data[,unique(unlist(mapping,use.names=FALSE)),drop=FALSE]
        signature<-serialize(list(activeData,mapping,kind,measure,self$options$fe,self$options$re,self$options$level,self$options$leaveOneOut,inputType,inputCiLevel),NULL)
        if(is.null(private$.fitCache)||!identical(private$.fitCache$key,signature))
            private$.fitCache<-list(key=signature,context=mzMpFit(activeData,mapping,kind,measure,self$options$fe,self$options$re,self$options$level,leave_one_out=self$options$leaveOneOut,input_type=inputType,input_ci_level=inputCiLevel))
        context<-private$.fitCache$context
        state$fitCache<-private$.fitCache
        mzMpNativeTables(self,context)
        self$results$forestHtml$setVisible(FALSE);self$results$forestSvg$setVisible(FALSE)
        service<-tryCatch(mzMpConnect(),error=identity)
        if(inherits(service,'error')) {
            self$results$extension$setVisible(FALSE);self$results$diagnostics$setVisible(FALSE);self$results$extensionStatus$setContent('')
            status(paste('R/metafor results remain available.',conditionMessage(service)));return()
        }
        context$inputs<-mapping
        context$presentation<-list(show_funnel=self$options$showFunnel,engine=self$options$engine,result_type=self$options$resultType,
            width=self$options$plotWidth,height=self$options$plotHeight)
        # Invalidate pre-fix presentation caches, including saved funnels without size controls.
        renderKey<-serialize(list(cache_schema=3L,context,self$options$python,service$info$module_version,as.character(packageVersion('MetaPj'))),NULL)
        pythonCode<-paste(readLines(system.file('python','mzMp_present.py',package='MetaPj'),encoding='UTF-8',warn=FALSE),collapse='\n')
        code<-pythonCode
        target<-self$results$get(if(self$options$resultType=='svg')'forestSvg'else'forestHtml')
        # Inactive Html/Svg is still serialized by jamovi. Keep only the current
        # representation, otherwise a format switch can duplicate a whole library.
        self$results$get(if(self$options$resultType=='svg')'forestHtml'else'forestSvg')$setContent('')
        if(!identical(state$renderKey,renderKey)||!nzchar(target$content)) {
            response<-service$run(code=mzMpPythonCode(context),service_code=code,data=activeData,python=self$options$python,
                figure_width=self$options$plotWidth,figure_height=self$options$plotHeight,
                timeout=60L,checkpoint=function()private$.checkpoint(flush=FALSE))
            for(name in c('studies','models','heterogeneity')) {
                items<-Filter(function(x)x$name==name&&x$type=='Table',response$items)
                if(length(items)!=1L)stop('Python returned an unexpected table response.',call.=FALSE)
                mzMpFillTable(self$results$get(name),items[[1]])
            }
            plots<-Filter(function(x)x$name=='forest',response$items)
            if(length(plots)!=1L||!plots[[1]]$type %in% c('Html','Svg'))stop('Python returned an unexpected forest response.',call.=FALSE)
            if(!identical(plots[[1]]$type,if(self$options$resultType=='svg')'Svg'else'Html'))stop('Unexpected graphic type.',call.=FALSE)
            target$setContent(plots[[1]]$content)
            extras<-Filter(function(x)startsWith(x$name,'diag_'),response$items)
            elements<-lapply(extras,function(item)mzMpExtensionItem(self$options,item))
            self$results$diagnostics$clear();for(element in elements)self$results$diagnostics$add(element)
            state$renderKey<-renderKey
        }
        target$setVisible(TRUE)
        self$results$diagnostics$setVisible(length(self$results$diagnostics$itemNames)>0L)
        status(paste0('R/metafor ',packageVersion('metafor'),' · ',context$analysis$k,' studies · ',context$analysis$excluded,
            ' excluded rows. Pj ',service$info$module_version,' · API ',service$info$api_version,' · ',
            if(self$options$python=='jamovi')'Embedded Python'else'System Python',' · ',self$options$engine,' / ',self$options$resultType,'.'))
        extension<-self$results$extension
        if(self$options$extensionRevision<1L||!nzchar(trimws(self$options$extensionCode))) {
            extension$setVisible(FALSE);state$extensionKey<-NULL
            state$extensionRejectedKey<-NULL;state$extensionRejectedMessage<-NULL
            self$results$extensionStatus$setContent('<p>Optional: edit mzRender(context), then choose Run Python extension.</p>')
        } else tryCatch({
            extensionKey<-serialize(list(renderKey,signature,self$options$extensionCode,self$options$extensionRevision,self$options$extensionScriptName),NULL)
            if(identical(state$extensionRejectedKey,extensionKey)) {
                extension$setVisible(FALSE)
                self$results$extensionStatus$setContent(state$extensionRejectedMessage)
            } else {
              if(!identical(state$extensionKey,extensionKey)||!length(extension$itemNames)) {
                response<-service$run(code=mzMpPythonCode(context,self$options$extensionCode),service_code=paste(code,mzMpPythonPrelude(context),sep="\n"),
                    data=activeData,python=self$options$python,figure_width=self$options$plotWidth,figure_height=self$options$plotHeight,
                    timeout=60L,checkpoint=function()private$.checkpoint(flush=FALSE))
                elements<-lapply(response$items,function(item)mzMpExtensionItem(self$options,item))
                extension$clear();for(element in elements)extension$add(element)
                state$extensionKey<-extensionKey
                state$extensionRejectedKey<-NULL;state$extensionRejectedMessage<-NULL
              }
              extension$setVisible(TRUE)
              self$results$extensionStatus$setContent('<p>Python extension completed. Active code is saved in this analysis.</p>')
            }
        },error=function(error) {
            if(identical(error$code,'restart'))stop(error)
            extension$clear();extension$setVisible(FALSE);state$extensionKey<-NULL
            self$results$extensionStatus$setContent(mzMpErrorContent(error,self$options$extensionScriptName))
        })
    },error=function(error) {
        if(identical(error$code,'restart'))stop(error)
        if(is.null(private$.fitCache)||!identical(private$.fitCache$key,signature))hide()
        self$results$forestHtml$setVisible(FALSE);self$results$forestSvg$setVisible(FALSE);self$results$diagnostics$setVisible(FALSE);self$results$extension$setVisible(FALSE)
        self$results$extensionStatus$setContent('')
        self$results$status$setContent(mzMpErrorContent(error))
    },finally={self$results$setState(state)})
}

# Reconstruct dynamic schemas before standard native state loading.
mzMpRestoreExtension <- function(self,private) {
    jmvcore:::initProtoBuf()
    path <- private$.statePathSource()
    if(!file.exists(path))return()
    connection <- file(path,open='rb',raw=TRUE)
    on.exit(close(connection),add=TRUE)
    pb <- jmvcore:::RProtoBuf_read(jamovi.coms.AnalysisResponse,connection)
    # Dynamic table row keys must exist before fromProtoBuf.
    for(item in pb$results$group$elements)if(item$has('table')) {
        target <- self$results$get(item$name)
        if(!is.null(target)) {
            target$deleteRows()
            for(rowName in item$table$rowNames)target$addRow(rowKey=jsonlite::fromJSON(rowName))
        }
    }
    for(group in pb$results$group$elements)if(group$name %in% c('extension','diagnostics')&&group$has('group')) {
        for(item in group$group$elements) {
            if(item$has('table')) {
                element <- jmvcore::Table$new(self$options,name=item$name,title=item$title,
                    clearWith=character(),swapRowsColumns=item$table$swapRowsColumns)
                for(column in item$table$columns)element$addColumn(name=column$name,title=column$title,
                    type=column$type,format=column$format,superTitle=if(nzchar(column$superTitle))column$superTitle else NULL,
                    combineBelow=column$combineBelow)
                for(rowName in item$table$rowNames)element$addRow(rowKey=jsonlite::fromJSON(rowName))
            } else {
                type <- if(item$has('svg'))'Svg' else if(item$has('html'))'Html' else
                    if(item$has('text'))'Text' else if(item$has('preformatted'))'Preformatted' else NULL
                if(is.null(type))next
                element <- getExportedValue('jmvcore',type)$new(self$options,name=item$name,title=item$title)
            }
            self$results$get(group$name)$add(element)
        }
    }
}
