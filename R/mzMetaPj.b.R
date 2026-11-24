# One backend: the native tab selects the input contract.
mzMetaPjClass <- R6::R6Class('mzMetaPjClass',inherit=mzMetaPjBase,
    public=list(serialize=function(final=FALSE,createErrorOnFailure=TRUE,includeState=TRUE) {
        serializeNative<-function()super$serialize(final=final,createErrorOnFailure=createErrorOnFailure,includeState=includeState)
        mzMpGuardResponse(self,private,serializeNative(),serializeNative)
    },.load=function(vChanges=character()) {
        mzMpRestoreExtension(self,private)
        super$.load(vChanges)
    }),
    private=list(.fitCache=NULL,.renderCache=NULL,.extensionCache=NULL,
        .run=function()mzMpRun(self,private,self$options$dataType)))
