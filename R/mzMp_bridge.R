# The consumer calls only public Pj exports.
mzMpConnect <- function() {
    if(!'Pj' %in% loadedNamespaces()) {
        libraries <- .libPaths()
        bases <- strsplit(Sys.getenv('JAMOVI_MODULES_PATH'),.Platform$path.sep,fixed=TRUE)[[1]]
        candidates <- unique(c(libraries,file.path(dirname(dirname(libraries)),'Pj','R'),
                               file.path(bases[nzchar(bases)],'Pj','R')))
        candidates <- candidates[file.exists(file.path(candidates,'Pj','DESCRIPTION'))]
        if(!length(candidates))stop('MetaPj requires Pj 1.8.0 or newer. Install Pj, then restart jamovi. Download: https://github.com/MAgojam/Pj/releases',call.=FALSE)
        loadNamespace('Pj',lib.loc=candidates[1])
    }
    exports <- getNamespaceExports('Pj')
    if(!all(c('mzPjServiceInfo','mzPjRunPython') %in% exports))
        stop('The installed Pj has no public service API. Update Pj to 1.8.0 or newer and restart jamovi.',call.=FALSE)
    info <- getExportedValue('Pj','mzPjServiceInfo')()
    if(utils::compareVersion(info$module_version,'1.8.0')<0L||!identical(info$api_version,1L)||!isTRUE(info$capabilities$checkpoint))
        stop('MetaPj requires Pj 1.8.0 or newer with public service API 1 and checkpoint support. Update Pj and restart jamovi.',call.=FALSE)
    list(info=info,run=getExportedValue('Pj','mzPjRunPython'))
}

mzMpEscape <- function(x) {
    x <- gsub('&','&amp;',as.character(x),fixed=TRUE)
    x <- gsub('<','&lt;',x,fixed=TRUE)
    gsub('>','&gt;',x,fixed=TRUE)
}

mzMpPythonPrelude <- function(context) {
    encoded<-base64enc::base64encode(charToRaw(enc2utf8(jsonlite::toJSON(context,
        dataframe='rows',auto_unbox=TRUE,digits=NA,na='null',null='null'))))
    paste0('import base64, json\ncontext = json.loads(base64.b64decode("',encoded,'").decode("utf-8"))\n')
}

mzMpPythonCode <- function(context,extension=NULL) {
    if(is.null(extension))paste0(mzMpPythonPrelude(context),'mzpjRenderStandard(context)')else
        paste0(extension,'\nif not callable(globals().get("mzRender")): raise ValueError("Define a function named mzRender(context).")\nmzRender(context)')
}

# The host declares native columns; Python supplies their values.
mzMpFillTable <- function(table,item) {
    names <- vapply(item$columns,function(column)column$title,character(1))
    table$deleteRows()
    for(i in seq_along(item$rows)) {
        values <- lapply(item$rows[[i]],function(x)if(is.null(x))NA else x)
        table$addRow(rowKey=as.character(i),values=setNames(values,names))
    }
    for(i in seq_along(item$notes))table$setNote(paste0('note',i),item$notes[[i]],init=FALSE)
    table$setVisible(TRUE)
}

# Personal results remain native jamovi elements.
mzMpExtensionItem <- function(options,item) {
    if(!is.null(item$image_request))
        stop('Browser Image capture belongs to the Pj editor. Use result_type="html" or "svg" in MetaPj.',call.=FALSE)
    if(item$type=='Table') {
        # MetaPj's data/script keys own invalidation. Preserve cached cells on UI-only changes.
        element <- jmvcore::Table$new(options,name=item$name,title=item$title,
            clearWith=character(),swapRowsColumns=isTRUE(item$transpose))
        for(column in item$columns)element$addColumn(name=column$name,title=column$title,
            type=column$type,format=column$format,superTitle=column$superTitle,
            combineBelow=isTRUE(column$combineBelow))
        for(i in seq_along(item$rows))element$addRow(rowKey=as.character(i),values=setNames(
            lapply(item$rows[[i]],function(x)if(is.null(x))NA else x),vapply(item$columns,`[[`,character(1),'name')))
        for(i in seq_along(item$notes))element$setNote(paste0('note',i),item$notes[[i]],init=FALSE)
        for(note in item$footnotes)element$addFootnote(col=note$column,rowNo=note$row+1L,note=note$text)
        for(symbol in item$symbols)element$addSymbol(col=symbol$column,rowNo=symbol$row+1L,symbol=symbol$text)
    } else if(item$type %in% c('Html','Svg','Text','Preformatted')) {
        # Preserve the native Svg type emitted by the extension.
        element <- getExportedValue('jmvcore',item$type)$new(options,name=item$name,
            title=if(is.null(item$title))'' else item$title)
        element$setContent(item$content)
        # The service supplies portable inline resources; never resolve paths relative to MetaPj.
        if(length(item$scripts))stop('External script references are not supported in extension results.',call.=FALSE)
    } else stop(paste('Unsupported extension result type:',item$type,'Use Text, Table, Html or Svg.'),call.=FALSE)
    element
}
