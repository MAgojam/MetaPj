// One script per analysis. Loading/editing changes a passive draft until Run.
'use strict';
module.exports = {
    mzLoaded: function(ui) {
        const area=ui.codeArea.el;
        const info=document.createElement('p');
        info.style.cssText='color:#657b9b;font-size:12px;margin:0 0 8px';
        info.setAttribute('aria-live','polite');area.appendChild(info);
        const editor=document.createElement('textarea');editor.rows=12;editor.spellcheck=false;
        editor.setAttribute('aria-label','Python function mzRender(context)');
        editor.style.cssText='display:block;box-sizing:border-box;width:100%;min-width:280px;max-width:100%;resize:vertical;font:13px/1.45 monospace;padding:10px;border:1px solid #a9bdd9;border-radius:6px;background:white;color:#22334b';
        const initial=ui.extensionDraft.value()||{};editor.value=initial.draft||'';
        let filename=initial.filename||'my_extension.py';area.appendChild(editor);
        const row=document.createElement('div');row.style.cssText='display:flex;align-items:flex-start;gap:12px;margin-top:10px;flex-wrap:wrap';area.appendChild(row);
        const frame=title=>{
            const group=document.createElement('fieldset');
            group.style.cssText='display:flex;align-items:center;gap:8px;min-width:0;margin:0;padding:6px 8px 8px;border:1px solid #c1d1e5;border-radius:7px;background:transparent';
            const legend=document.createElement('legend');legend.textContent=title;
            legend.style.cssText='margin-left:0;padding:0 5px;font-size:11px;font-weight:500;line-height:1.2;color:#64748b;background:transparent';
            group.appendChild(legend);row.appendChild(group);return group;
        };
        const scriptFrame=frame('Script'),pythonFrame=frame('Python');
        const error=document.createElement('p');error.setAttribute('role','alert');
        error.style.cssText='font-size:12px;color:#a54848;white-space:pre-wrap';area.appendChild(error);
        const button=(text,callback,parent,label)=>{
            const el=document.createElement('button');el.type='button';el.textContent=text;
            el.title=label;el.setAttribute('aria-label',label);
            el.style.cssText='box-sizing:border-box;min-width:56px;flex-shrink:0;border:1px solid #b8cbe1;border-radius:5px;background:#f7faff;color:#3e6da9;padding:7px 12px;font:inherit;cursor:pointer';
            el.addEventListener('click',callback);parent.appendChild(el);return el;
        };
        const refresh=()=>{
            const active=ui.extensionCode.value()||'';
            const applied=active===editor.value&&ui.extensionScriptName.value()===filename;
            info.textContent=filename+' · '+(!active?'Draft; extension disabled':applied?'Applied script':'Draft changes; previous script remains active');
        };
        const draft=()=>{ui.extensionDraft.setValue({draft:editor.value,filename});error.textContent='';refresh();};
        editor.addEventListener('input',draft);
        const picker=document.createElement('input');picker.type='file';picker.accept='.py,text/x-python';picker.multiple=false;picker.hidden=true;area.appendChild(picker);
        button('Load',()=>{picker.value='';picker.click();},scriptFrame,'Load script…');
        let loadSequence=0;
        picker.addEventListener('change',async()=>{
            const file=picker.files[0];if(!file)return;const sequence=++loadSequence;
            try {
                if(!/\.py$/i.test(file.name))throw Error('Choose one Python .py file.');
                if(file.size>256*1024)throw Error('Choose a script no larger than 256 KiB.');
                const bytes=await file.arrayBuffer();
                const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes).replace(/^\uFEFF/,'');
                if(sequence!==loadSequence)return;
                if(text.includes('\0'))throw Error('The selected file contains null bytes. Choose a UTF-8 Python script.');
                editor.value=text;filename=file.name;draft();
            }catch(e){if(sequence===loadSequence)error.textContent=e.message||'The script could not be loaded.';}
        });
        button('Save',()=>{
            const blob=new Blob([editor.value],{type:'text/x-python;charset=utf-8'});
            const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=filename;
            area.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
        },scriptFrame,'Save script…');
        const apply=code=>{
            const options=ui.view.model.options;options.beginEdit();
            try{ui.extensionCode.setValue(code);ui.extensionScriptName.setValue(filename);ui.extensionRevision.setValue((ui.extensionRevision.value()||0)+1);}
            finally{options.endEdit();}
            error.textContent='';refresh();
        };
        button('Run',()=>apply(editor.value),pythonFrame,'Run Python extension');
        button('Disable',()=>apply(''),pythonFrame,'Disable extension');
        const note=document.createElement('p');
        note.textContent='Load replaces this draft only. Run sends one script to Pj and applies mzRender(context). Disabling retains the draft. Applied code runs again when its context changes; it has the permissions of the selected Python interpreter.';
        note.style.cssText='font-size:12px;color:#657b9b;max-width:620px';area.appendChild(note);
        this.editor=editor;
        this.syncDraft=()=>{if(document.activeElement!==editor){const value=ui.extensionDraft.value()||{};editor.value=value.draft||'';filename=value.filename||'my_extension.py';}refresh();};
        refresh();
    },
    mzUpdate: function(){this.syncDraft?.();}
};
