# Shared presentation: all inferential estimates come from metafor in R.
import html
import math


def mzMpShowFunnel(datasets, options, display, title):
    """Compose public Pj Chart/Html outputs; keep all chart rendering in Pj.

    MetaPj supplies only the Html size control and its normal-flow reservation.
    The chart content is embedded unchanged, without parsing its private DOM.
    Native Svg follows the original Pj path, without an Html zoom wrapper.
    """
    common = dict(name='diag_funnel', title=title, width=display['width'],
                  height=display['height'], result_type=display['result_type'], options=options)
    if display['result_type'] != 'html':
        mzpjShowChart('scatter', datasets, **common)
        return
    import uuid
    items = results['items']
    start = len(items)
    mzpjShowChart('scatter', datasets, **dict(common, name='mzmp_funnel_chart', title='', accordion=False))
    if len(items) != start+1 or items[-1]['type'] != 'Html':
        raise RuntimeError('Pj did not return the expected Html funnel.')
    chart = items.pop()['content']
    # Host UI only: match Pj's thin blue range and orange Z thumb. No vendor
    # stylesheet or renderer is copied into MetaPj.
    css = '''
.mzmp-funnel-size{font:13px/1.5 Arial,sans-serif;color:#475569}
.mzmp-funnel-size .mzmp-size-tools{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:8px 0 12px}
.mzmp-size-tools label{position:relative;width:110px;height:24px;display:flex;align-items:center}
.mzmp-size-tools input{appearance:none;width:110px;height:3px;margin:0;background:#3e6da9;cursor:pointer;border:0;padding:0}
.mzmp-size-tools input::-webkit-slider-thumb{appearance:none;width:16px;height:16px;border-radius:50%;background:#ed784e;border:0}
.mzmp-size-tools input::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:#ed784e;border:0}
.mzmp-size-marker{position:absolute;top:4px;transform:translateX(-50%);font:10px/16px Arial,sans-serif;color:white;pointer-events:none}
.mzmp-size-tools output{min-width:38px;color:#64748b;font-size:12px}
.mzmp-size-tools button{font:inherit;color:#3e6da9;background:white;border:1px solid #b9cce7;border-radius:4px;padding:3px 9px;cursor:pointer}
.mzmp-size-tools button:disabled{opacity:.45;cursor:default}
'''
    identity = 'mzmp_funnel_' + uuid.uuid4().hex
    width = display['width']
    # Chart measures its parent with getBoundingClientRect. Constrain the
    # logical canvas dimensions when the desktop Results page uses CSS zoom.
    css += (f'#{identity} canvas{{max-width:{width}px!important;'
            f'max-height:{display["height"]}px!important}}')
    content = ('<style>' + css + '</style>'
        f'<div id="{identity}" class="mzmp-funnel-size" style="width:{width}px;max-width:none">'
        '<div class="mzmp-size-tools"><label>'
        '<input type="range" min="60" max="140" step="5" value="100" aria-label="Funnel size in percent">'
        '<span class="mzmp-size-marker" aria-hidden="true" style="left:55px">Z</span></label>'
        '<output aria-live="polite">100%</output>'
        '<button type="button" title="Reset funnel size" disabled>Reset</button></div>'
        '<div data-mzmp-frame style="position:relative;overflow:hidden">'
        f'<div data-mzmp-stage style="position:absolute;left:0;top:0;width:{width}px;'
        'display:flow-root;transform-origin:top left">' + chart + '</div></div></div>')
    script = r'''<script>(function(){
const root=document.getElementById('__ID__'),frame=root.querySelector('[data-mzmp-frame]'),
 stage=root.querySelector('[data-mzmp-stage]'),tools=root.querySelector('.mzmp-size-tools'),
 range=tools.querySelector('input'),percent=tools.querySelector('output'),
 marker=tools.querySelector('.mzmp-size-marker'),reset=tools.querySelector('button');
let scheduled=0;
function resize(){
 scheduled=0;if(!root.isConnected||!root.getClientRects().length)return;
 const scale=Number(range.value)/100,width=__WIDTH__*scale;
 root.style.width=width+'px';frame.style.width=width+'px';
 // CSS zoom affects native pointer offsets; CSS transforms already invert
 // their coordinates. Cancel inherited zoom locally and restore its visual
 // size through the transform, without touching the Pj chart or its DOM.
 const uiScale=root.offsetWidth?root.getBoundingClientRect().width/root.offsetWidth:1;
 stage.style.zoom=String(1/uiScale);stage.style.transform='scale('+(uiScale*scale)+')';
 frame.style.height=Math.ceil(stage.offsetHeight*scale)+'px';
 const host=root.closest('.jmv-results-html');if(host){host.style.width=width+'px';host.style.maxWidth='none';}
 percent.textContent=range.value+'%';reset.disabled=scale===1;
 marker.style.left=(8+(Number(range.value)-60)/80*94)+'px';
}
function schedule(){if(!scheduled)scheduled=requestAnimationFrame(resize);}
range.addEventListener('input',resize);
reset.addEventListener('click',()=>{range.value='100';resize();});
const observer=new ResizeObserver(schedule);observer.observe(stage);
const removal=new MutationObserver(()=>{if(!root.isConnected){observer.disconnect();removal.disconnect();cancelAnimationFrame(scheduled);}});
removal.observe(document.body,{childList:true,subtree:true});resize();
})();</script>'''
    content += script.replace('__ID__', identity).replace('__WIDTH__', str(width))
    mzpjShowHtml(content, name='diag_funnel', title=title)


def mzpjRenderStandard(context):
    info = context['analysis']
    studies = context['studies']
    models = context['models']
    note = (f"{info['k']} included studies; {info['excluded']} rows excluded. "
            f"Analysis scale: {info['effect_scale']}. Display scale: {info['measure']}. "
            "Study confidence intervals use a normal approximation. Weights sum to 100% within each model.")
    if info.get('input_note'):
        note += ' ' + info['input_note']
    mzpjShowTable([
        {'Study': row['study'], 'Estimate': row['estimate'], 'Lower': row['lower'],
         'Upper': row['upper'], 'FE_weight': row['weight_FE'], 'RE_weight': row['weight_RE']}
        for row in studies], name='studies', title='Study effects', notes=note)
    mzpjShowTable([
        {'Model': row['model'], 'Estimate': row['estimate'], 'SE': row['se'],
         'z': row['statistic'], 'p': row['p'], 'Lower': row['lower'], 'Upper': row['upper'],
         'PI_lower': row['pi_lower'], 'PI_upper': row['pi_upper']}
        for row in models], name='models', title='Model estimates',
        notes=[f"{info['level']}% confidence intervals. SE and z use the analysis scale ({info['effect_scale']}).",
               'FE: common-effect inverse-variance model. RE: REML random-effects model; z inference. Prediction intervals apply only to RE.'] + ([info['input_note']] if info.get('input_note') else []))
    mzpjShowTable([
        {'Model': row['model'], 'tau2': row['tau2'], 'I2': row['I2'], 'H2': row['H2'],
         'Q': row['Q'], 'df': row['Q_df'], 'p': row['Q_p']}
        for row in models], name='heterogeneity', title='Heterogeneity',
        notes='Heterogeneity is calculated by metafor. Tau squared is estimated only for RE; I squared is a percentage.')
    engine = context['presentation']['engine']
    if engine == 'd3':
        # Reuse Pj's interval helper. Ratios use their log analysis scale, explicitly labelled.
        import math
        rows = mzMpPlotRows(context)
        dataset = {'label': [r['label'] for r in rows],
                   'estimate': [math.log(r['estimate']) if info['ratio'] else r['estimate'] for r in rows],
                   'lower': [math.log(r['lower']) if info['ratio'] else r['lower'] for r in rows],
                   'upper': [math.log(r['upper']) if info['ratio'] else r['upper'] for r in rows]}
        mzpjShowIntervals(dataset,'estimate','lower','upper',labels='label',reference=0,
            interval_label=f"{info['level']}% confidence interval",
            name='forest',title='Study and pooled intervals — D3',
            x_label=info['effect_scale'],color='#587295',
            width=context['presentation']['width'],height=context['presentation']['height'],
            result_type=context['presentation']['result_type'])
    elif engine == 'chart':
        mzpjRenderChart(context)
    elif engine == 'plotly':
        mzpjRenderPlotly(context)
    else:
        raise ValueError('Unknown graphics engine.')
    mzMpRenderDiagnostics(context)


def mzMpPlotRows(context):
    rows = []
    weight = 'weight_RE' if any(m['model'] == 'RE' for m in context['models']) else 'weight_FE'
    for index, row in enumerate(context['studies']):
        rows.append(dict(row, label=f"{index + 1}. {row['study']}", weight=row[weight], summary=False))
    for model in context['models']:
        rows.append(dict(model, label=f"{model['model']} pooled ({model['method']})", weight=100, summary=True))
    return rows


def mzpjRenderChart(context):
    rows = mzMpPlotRows(context)
    # Standard numeric coordinates through the public helper; no custom plugin.
    intervals = []
    for i, row in enumerate(rows):
        color = ('#a57c59' if row.get('model') == 'RE' else '#54786d') if row['summary'] else '#587295'
        intervals.append({'label': row['label'], 'data': [
            {'x': value, 'y': i + 1} for value in (row['lower'], row['estimate'], row['upper'])],
            'showLine': True, 'borderColor': color, 'borderWidth': 1.5,
            'pointRadius': [2, 7 if row['summary'] else 3 + .11 * row['weight'], 2],
            'pointStyle': 'rectRot' if row['summary'] else 'rect', 'backgroundColor': color})
        if row['summary'] and row['model'] == 'RE' and row['pi_lower'] is not None:
            intervals.append({'label': 'RE prediction interval', 'data': [
                {'x': value, 'y': i + 1} for value in (row['pi_lower'], row['pi_upper'])],
                'showLine': True, 'borderColor': '#a57c59', 'borderDash': [4, 3],
                'borderWidth': 1, 'pointRadius': 2})
    reference = 1 if context['analysis']['ratio'] else 0
    intervals.append({'label': 'Null effect', 'data': [
        {'x': reference, 'y': .5}, {'x': reference, 'y': len(rows) + .5}],
        'showLine': True, 'borderColor': '#9aa8ba', 'borderDash': [5, 4], 'borderWidth': 1, 'pointRadius': 0})
    mzpjShowChart('scatter', intervals, name='forest',
        title='Effect intervals — Chart.js', width=context['presentation']['width'], height=context['presentation']['height'],
        options={'scales': {
            'x': {'type': 'logarithmic' if context['analysis']['ratio'] else 'linear',
                  'title': {'display': True, 'text': context['analysis']['measure']}},
            'y': {'type': 'linear', 'reverse': True, 'min': .5, 'max': len(rows) + .5,
                  'ticks': {'stepSize': 1}, 'title': {'display': True, 'text': 'Study / pooled row'}}},
            'plugins': {'legend': {'display': False}}}, accordion=False,
        floating_legend={'title': 'Studies and models', 'collapsed': True,
                         'text': 'Rows follow the study table; pooled models are last. Click a series to change its visibility.'},
        result_type=context['presentation']['result_type'])


def mzpjRenderPlotly(context):
    # Ordinary dictionaries use Pj's vendored Plotly.js; no Python plotly package.
    rows = mzMpPlotRows(context)
    traces = []
    for index, row in enumerate(rows):
        color = ('#a57c59' if row.get('model') == 'RE' else '#54786d') if row['summary'] else '#587295'
        text = (f"{html.escape(row['label'])}<br>Effect: {row['estimate']:.4g}"
                f" [{row['lower']:.4g}, {row['upper']:.4g}]<br>Weight: {row['weight']:.1f}%")
        if row['summary']:
            traces.append(dict(type='scatter', x=[row['lower'],row['estimate'],row['upper'],row['estimate'],row['lower']],
                y=[index,index-.2,index,index+.2,index], mode='lines',fill='toself',
                line=dict(color=color),fillcolor=color,text=[text]*5,hoverinfo='text',showlegend=False))
        else:
            traces.append(dict(type='scatter',x=[row['estimate']],y=[index],mode='markers',
                marker=dict(size=5+3*math.sqrt(row['weight']),color=color,symbol='square'),
                error_x=dict(type='data',symmetric=False,array=[row['upper']-row['estimate']],
                    arrayminus=[row['estimate']-row['lower']],color=color),
                text=[text],hoverinfo='text',showlegend=False))
        if row['summary'] and row['model']=='RE' and row['pi_lower'] is not None:
            traces.append(dict(type='scatter',x=[row['pi_lower'],row['pi_upper']],y=[index,index],
                mode='lines+markers',line=dict(color=color,dash='dash'),
                marker=dict(symbol='line-ns',size=11,line=dict(width=2,color=color)),
                name='Prediction interval',hovertemplate='Prediction interval endpoint: %{x:.4g}<extra></extra>'))
    reference = 1 if context['analysis']['ratio'] else 0
    figure = dict(data=traces,layout=dict(template='plotly_white',
        font=dict(family='Arial, sans-serif',size=13,color='#334155'),
        legend=dict(orientation='h',x=.5,xanchor='center',y=1.04,yanchor='bottom'),
        margin=dict(l=200,r=35,t=65,b=65),
        shapes=[dict(type='line',xref='x',yref='paper',x0=reference,x1=reference,y0=0,y1=1,line=dict(color='#98a7b9',dash='dash'))],
        xaxis=dict(title=dict(text=context['analysis']['measure']),type='log' if context['analysis']['ratio'] else 'linear'),
        yaxis=dict(tickmode='array',tickvals=list(range(len(rows))),
            ticktext=[html.escape(r['label']) for r in rows],autorange='reversed')))
    if context['analysis']['ratio']:
        limits = [r[key] for r in rows for key in ('lower','upper')]
        ticks = [m*10.0**power for power in range(math.floor(math.log10(min(limits))), math.ceil(math.log10(max(limits)))+1) for m in (1,2,5)]
        ticks = [x for x in ticks if min(limits)*.9 <= x <= max(limits)*1.1]
        figure['layout']['xaxis'].update(tickmode='array',tickvals=ticks,ticktext=[f'{x:.4g}' for x in ticks])
    mzpjShowPlotly(figure,name='forest',title='Forest plot — Plotly',
        width=context['presentation']['width'],height=context['presentation']['height'],
        result_type=context['presentation']['result_type'],config={'displayModeBar':False})


def mzMpRenderDiagnostics(context):
    info = context['analysis']
    display = context['presentation']
    diagnostics = context.get('diagnostics', {})
    if display.get('show_funnel'):
        f = diagnostics['funnel']
        datasets = [dict(label=r['study'],data=[dict(x=r['yi'],y=math.sqrt(r['vi']))],
            backgroundColor='#587295',borderColor='#587295',pointRadius=4,showLine=False)
            for r in context['studies']]
        for key in ('lower','upper'):
            datasets.append(dict(label=f"{info['level']}% pseudo-CI ({key})",
                data=[dict(x=x,y=y) for x,y in zip(f[key],f['se'])],
                showLine=True,pointRadius=0,borderColor='#9aabbe',borderDash=[4,3],borderWidth=1.3))
        datasets.append(dict(label=f['model']+' pooled reference',
            data=[dict(x=f['center'],y=0),dict(x=f['center'],y=max(f['se']))],
            showLine=True,pointRadius=0,borderColor='#54786d',borderDash=[5,3],borderWidth=1.5))
        mzMpShowFunnel(datasets,
            options=dict(scales=dict(
                x=dict(type='linear',title=dict(display=True,text=info['effect_scale'])),
                y=dict(type='linear',reverse=True,min=0,title=dict(display=True,text='Standard error'))),
                plugins=dict(legend=dict(display=False))), display=display,
            title='Funnel plot — '+f['model']+' reference')
        mzpjShowText(f"**Descriptive funnel.** {info['level']}% pseudo-confidence limits around the {f['model']} pooled analysis-scale effect, "
            'without adding heterogeneity. These are not prediction limits. Asymmetry alone does not establish publication bias; no asymmetry test is run.',
            name='diag_funnel_note')
    for diagnostic in diagnostics.get('leave_one_out', []):
        rows = diagnostic['rows']
        model = diagnostic['model']
        mzpjShowTable(rows,name='diag_loo_table_'+model,title='Leave-one-out — '+model,
            notes='R/metafor refits the same model omitting each included study in turn. SE and tau2 use the analysis scale; estimate and CI use the display scale.')
        values = dict(label=[r['omitted'] for r in rows],
            estimate=[r['analysis_estimate'] for r in rows],
            lower=[math.log(r['lower']) if info['ratio'] else r['lower'] for r in rows],
            upper=[math.log(r['upper']) if info['ratio'] else r['upper'] for r in rows])
        reference = next(m['analysis_estimate'] for m in context['models'] if m['model']==model)
        mzpjShowIntervals(values,'estimate','lower','upper',labels='label',reference=reference,
            name='diag_loo_'+model,title='Leave-one-out estimates — '+model,
            x_label=info['effect_scale'],interval_label=f"{info['level']}% confidence interval",
            width=display['width'],height=display['height'],result_type=display['result_type'],color='#54786d')
    for index,note in enumerate(diagnostics.get('notes', [])):
        mzpjShowText(note,name='diag_note_'+str(index))
