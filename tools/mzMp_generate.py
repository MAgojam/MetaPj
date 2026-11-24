"""Genera un solo ingresso con schede e accordion nativi di jamovi."""
from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[1]
name='mzMetaPj'
title='Meta-analysis through Pj'
fields=[('ai','Events — Group 1'),('bi','Non-events — Group 1'),
        ('ci','Events — Group 2'),('di','Non-events — Group 2'),
        ('n1i','N — Group 1'),('m1i','Mean — Group 1'),('sd1i','SD — Group 1'),
        ('n2i','N — Group 2'),('m2i','Mean — Group 2'),('sd2i','SD — Group 2')]
generic_fields=[('yi','Effect size (analysis scale)'),('uncertainty','Sampling variance / standard error'),
                ('ciLower','Input CI — lower limit'),('ciUpper','Input CI — upper limit')]
default_code='''# The context contains metafor results, not the entire jamovi dataset.
def mzRender(context):
    mzpjShowTable(
        [{"Measure": context["analysis"]["measure"],
          "Included studies": context["analysis"]["k"]}],
        name="custom_summary", title="My Python summary")
    mzpjShowText("**Edit this function to add your own results.**", name="custom_note")
'''

def mzWrite(path,data):
    path.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True,width=100),encoding='utf-8')

options=[dict(name='data',type='Data'),
    dict(name='dataType',title='',type='List',options=[dict(name='dichotomous',title='Dichotomous'),dict(name='means',title='Mean differences'),dict(name='generic',title='Generic effect sizes')],default='dichotomous'),
    dict(name='study',title='Study label',type='Variable',default=None,permitted=['factor','id','numeric'],suggested=['nominal','id'])]
options += [dict(name=n,title=t,type='Variable',default=None,permitted=['numeric'],suggested=['continuous']) for n,t in fields+generic_fields]
options += [dict(name='measureDichotomous',title='Effect measure',type='List',options=[dict(name=n,title=t) for n,t in [('RR','Risk ratio'),('OR','Odds ratio'),('RD','Risk difference')]],default='RR'),
    dict(name='measureMeans',title='Effect measure',type='List',options=[dict(name='MD',title='Mean difference'),dict(name='SMD',title="Standardized mean difference (Hedges' g)")],default='MD'),
    dict(name='measureGeneric',title='Effect scale',type='List',options=[dict(name='GEN',title='Generic effect — supplied scale'),dict(name='GEN_LOG',title='Log ratio — display exp(effect)')],default='GEN'),
    dict(name='genericInput',title='Uncertainty input',type='List',options=[dict(name='variance',title='Sampling variance'),dict(name='se',title='Standard error'),dict(name='ci',title='Normal-based confidence interval')],default='variance'),
    dict(name='inputCiLevel',title='Input CI level (%)',type='Number',min=50,max=99.9,default=95),
    dict(name='fe',title='FE — common-effect model',type='Bool',default=True),
    dict(name='re',title='RE — random-effects model (REML)',type='Bool',default=True),
    dict(name='level',title='Confidence level (%)',type='Number',min=50,max=99.9,default=95),
    dict(name='engine',title='Graphics engine',type='List',options=[dict(name=n,title=t) for n,t in [('d3','D3 intervals'),('chart','Chart.js intervals'),('plotly','Plotly forest')]],default='d3'),
    dict(name='showFunnel',title='Funnel plot (descriptive)',type='Bool',default=True),
    dict(name='leaveOneOut',title='Leave-one-out sensitivity',type='Bool',default=False),
    dict(name='python',title='Python interpreter',type='List',options=[dict(name='jamovi',title='jamovi Python'),dict(name='system',title='System Python')],default='jamovi'),
    dict(name='resultType',title='Graphic result',type='List',options=[dict(name='html',title='Interactive HTML'),dict(name='svg',title='Native SVG')],default='html'),
    dict(name='plotWidth',title='Figure width (px)',type='Integer',min=600,max=1600,default=900),
    dict(name='plotHeight',title='Figure height (px)',type='Integer',min=320,max=2000,default=620),
    dict(name='extensionDraft',type='Group',hidden=True,passive=True,elements=[dict(name='draft',type='String',default=default_code),dict(name='filename',type='String',default='my_extension.py')]),
    dict(name='extensionCode',type='String',default='',hidden=True),
    dict(name='extensionRevision',type='Integer',default=0,hidden=True),
    dict(name='extensionScriptName',type='String',default='my_extension.py',hidden=True)]
mzWrite(root/f'jamovi/{name}.a.yaml',dict(name=name,title=title,menuGroup='MetaPj',version='1.1.0',jas='1.2',arbitraryCode=True,options=options))

def mzTarget(n,t):
    return dict(type='TargetLayoutBox',label=t,children=[dict(type='VariablesListBox',name=n,isTarget=True,maxItemCount=1)])

tabs=[]
for kind,subset,measure in [('dichotomous',fields[:4],'measureDichotomous'),('means',fields[4:],'measureMeans'),('generic',generic_fields,'measureGeneric')]:
    # I target sono figli DIRETTI del supplier: jamovi crea cosi' le frecce native.
    study=mzTarget('study_'+kind,'Study label (optional)')
    study['children'][0]['optionName']='study'
    supplier=dict(type='VariableSupplier',name='supplier_'+kind,persistentItems=False,
        stretchFactor=1,permitted=['numeric','factor','id'],
        children=[study]+[mzTarget(n,t) for n,t in subset])
    controls=[dict(type='ComboBox',name=measure)]
    if kind=='generic':
        controls += [dict(type='ComboBox',name='genericInput')]
        for target in supplier['children']:
            target_name=target['children'][0]['name']
            if target_name=='uncertainty':target['children'][0]['enable']='(!genericInput:ci)'
            elif target_name in ('ciLower','ciUpper'):target['children'][0]['enable']='(genericInput:ci)'
    controls.append(supplier)
    if kind=='generic':
        controls.append(dict(type='TextBox',name='inputCiLevel',format='number',suffix='%',enable='(genericInput:ci)'))
        controls.append(dict(type='Label',label='Use the same analysis scale for effects and CI limits.'))
        controls.append(dict(type='Label',label='For ratios, supply log effects and log CI limits.'))
    tabs.append(dict(type='Content',name=kind,children=controls))
children=[dict(type='ModeSelector',name='dataType',form='tabs',label='',stretchFactor=1,children=tabs),
    dict(type='CollapseBox',label='Models',collapsed=False,children=[
        dict(type='CheckBox',name='fe'),dict(type='CheckBox',name='re'),dict(type='TextBox',name='level',format='number',suffix='%')]),
    dict(type='CollapseBox',label='Presentation',collapsed=False,children=[dict(type='ComboBox',name='engine'),dict(type='ComboBox',name='python'),dict(type='CheckBox',name='showFunnel'),dict(type='CheckBox',name='leaveOneOut'),dict(type='ComboBox',name='resultType'),dict(type='TextBox',name='plotWidth',format='number'),dict(type='TextBox',name='plotHeight',format='number')]),
    dict(type='CollapseBox',label='Python extension (optional)',collapsed=True,children=[dict(type='CustomControl',name='codeArea',stretchFactor=1)])]
mzWrite(root/f'jamovi/{name}.u.yaml',dict(name=name,title=title,jus='3.0',stage=0,compilerMode='tame',
    events=dict(loaded='./mzMp_ui::mzLoaded',update='./mzMp_ui::mzUpdate'),children=children))
tables=[('studies','Study effects',[('Study','text'),('Estimate','number'),('Lower','number'),('Upper','number'),('FE_weight','number'),('RE_weight','number')]),
    ('models','Model estimates',[('Model','text'),('Estimate','number'),('SE','number'),('z','number'),('p','number'),('Lower','number'),('Upper','number'),('PI_lower','number'),('PI_upper','number')]),
    ('heterogeneity','Heterogeneity',[('Model','text'),('tau2','number'),('I2','number'),('H2','number'),('Q','number'),('df','integer'),('p','number')])]
titles={'FE_weight':'FE weight (%)','RE_weight':'RE weight (%)','SE':'SE (analysis scale)','PI_lower':'PI lower','PI_upper':'PI upper','tau2':'Tau²','I2':'I² (%)','H2':'H²'}
items=[dict(name='status',title='Status',type='Html')]
for table,caption,cols in tables:
    columns=[]
    for col,typ in cols:
        column=dict(name=col,title=titles.get(col,col),type=typ)
        if typ=='number':column['format']='pvalue' if col=='p' else 'zto'
        columns.append(column)
    items.append(dict(name=table,title=caption,type='Table',visible=False,clearWith=[],columns=columns))
items += [dict(name='forestHtml',title='Forest plot',type='Html',visible=False),dict(name='forestSvg',title='Forest plot',type='Svg',visible=False),
    dict(name='diagnostics',title='Diagnostics through Pj',type='Group',visible=False,items=[]),
    dict(name='extensionStatus',title='Python extension',type='Html'),dict(name='extension',title='Python extension results',type='Group',visible=False,items=[])]
mzWrite(root/f'jamovi/{name}.r.yaml',dict(name=name,title=title,jrs='1.1',items=items))
(root/f'R/{name}.b.R').write_text('''# One backend: the native tab selects the input contract.
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
''',encoding='utf-8')
mzWrite(root/'jamovi/0000.yaml',dict(name='MetaPj',title='MetaPj - meta-analysis through Pj',version='1.1.0',jms='1.0',usesNative=True,minApp='28.18.0',
    authors=['Maurizio Agosti'],maintainer='Maurizio Agosti <magosti@gmail.com>',
    description='Three native input tabs: dichotomous, mean differences and generic effects; metafor calculations with Python/D3, Chart.js or Plotly through Pj 1.8.0 or newer.',
    analyses=[dict(name=name,ns='MetaPj',title=title,menuGroup='MetaPj',menuTitle=title,arbitraryCode=True,arbitraryCode2=True)],
    datasets=[dict(name='BCG vaccine — dichotomous outcomes',path='MetaPj_BCG.omv',description='Open MetaPj, select the Dichotomous tab and assign tpos, tneg, cpos and cneg.',tags=['Meta-analysis','Dichotomous','Pj']),
              dict(name='Mean differences — Normand 1999',path='MetaPj_MeanDifferences.omv',description='Open MetaPj, select the Mean differences tab and assign n1i, m1i, sd1i, n2i, m2i and sd2i.',tags=['Meta-analysis','Mean differences','Pj']),
              dict(name='Generic effects — BCG precomputed log RR',path='MetaPj_GenericEffects.omv',description='Select Generic effect sizes and Log ratio. Assign study, yi and vi (variance), sei (SE), or ci_lower/ci_upper (95% normal CI). All effects and CI limits are already on the log RR analysis scale.',tags=['Meta-analysis','Generic effects','Pj'])]))
print('MetaPj: full-width native tabs, direct supplier targets, shared study option and native accordions generated.')
