
'use strict';
async function loadJSON(p){const r=await fetch(p);if(!r.ok)throw new Error(p);return r.json();}
let INDEX=null;
async function init(){
  try{INDEX=await loadJSON('search_index.json');}catch(e){
    document.getElementById('buildmeta').textContent='search_index.json missing — run build_atlas.py';
    return;}
  const cov=await loadJSON('coverage_summary.json');
  document.getElementById('buildmeta').textContent =
    INDEX.length + ' taxa indexed · ' + cov.total_pages_written + ' pages';
  document.getElementById('q').addEventListener('input',doSearch);
  document.getElementById('f_genus').addEventListener('input',doSearch);
}
function doSearch(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  const g=document.getElementById('f_genus').value.trim().toLowerCase();
  const out=document.getElementById('results'); out.innerHTML='';
  if(q.length<2 && !g) return;
  let n=0;
  for(const row of INDEX){
    const hay=(row.n+' '+(row.s||[]).join(' ')+' '+row.f).toLowerCase();
    if(q && !hay.includes(q)) continue;
    if(g && !(row.f||'').toLowerCase().startsWith(g)) continue;
    const li=document.createElement('li');
    const a=document.createElement('a'); a.textContent=row.n;
    a.href='#'+row.u; a.onclick=ev=>{ev.preventDefault();showPage(row.u);return false;};
    li.appendChild(a); out.appendChild(li);
    if(++n>=200){const li2=document.createElement('li');li2.textContent='… more — refine query';out.appendChild(li2);break;}
  }
}
async function showPage(slug){
  const p=await loadJSON('pages/'+slug+'.json');
  const root=document.getElementById('page'); root.innerHTML='';
  const h2=document.createElement('h2'); h2.textContent=p.display_name; root.appendChild(h2);
  const meta=document.createElement('p'); meta.className='meta';
  meta.innerHTML='Accepted key: <code>'+p.accepted_taxon_key+'</code> · rank: '+
    (p.rank||'unknown')+' · genus (inferred): '+(p.genus_inferred||'—');
  root.appendChild(meta);
  const syn=document.createElement('p'); syn.className='syn';
  syn.textContent='Synonyms: '+((p.synonyms&&p.synonyms.length)?p.synonyms.join('; '):'(none ingested)');
  root.appendChild(syn);
  const prov=document.createElement('p'); prov.className='prov';
  const ids=p.external_ids||{};
  prov.innerHTML='Provenance: ' + Object.entries(ids).filter(([,v])=>v)
      .map(([k,v])=>'<span class="badge">'+k+':'+v+'</span>').join(' ');
  root.appendChild(prov);
  for(let t=1;t<=6;t++){
    const sec=p.tracks[t]; if(!sec)continue;
    const div=document.createElement('section'); div.className='track band-'+sec.state;
    const h=document.createElement('h3');
    h.innerHTML='Track '+t+' — '+sec.title+
      ' <span class="bandtag">'+sec.state.toUpperCase()+'</span>';
    div.appendChild(h);
    if(sec.state==='data-limited'){
      const p1=document.createElement('p'); p1.className='reason';
      p1.textContent=sec.data_limited_reason; div.appendChild(p1);
    } else {
      for(const klass of ['observed','enriched','predicted']){
        for(const e of sec[klass]||[]){
          const row=document.createElement('div'); row.className='row '+klass;
          row.innerHTML='<span class="band '+klass+'">'+klass.toUpperCase()+'</span> '+
            '<code>'+e.edge_type+'</code> — src <code>'+(e.source_group||'?')+
            '</code> — license: '+(e.license||'?').slice(0,60)+
            (e.pending_crosswalk?' <em>(pending_crosswalk)</em>':'')+
            ' — confidence '+(e.confidence!=null?e.confidence:'—');
          div.appendChild(row);
        }
      }
    }
    if(sec.instrument_pending){
      const ip=document.createElement('p'); ip.className='ipending';
      ip.innerHTML='<strong>Instrument M3.T'+t+': pending</strong> — expected files '+
        '<code>'+sec.instrument_expected_files.join(', ')+'</code> from <em>'+
        sec.instrument_sibling_clone+'</em>. '+(sec.instrument_contract_reason||'Not yet emitted at Atlas build time.');
      div.appendChild(ip);
    }
    root.appendChild(div);
  }
  // Counter-claim button
  const cc=document.createElement('section'); cc.className='counterclaim';
  cc.innerHTML='<h3>File a counter-claim</h3>'+
    '<p>Counter-claims are append-only and require a target edge_id. The form '+
    'below builds a JSON payload; save it as a line to <code>counter_claims.jsonl</code> '+
    'or pipe through <code>tools/file_counter_claim.py</code> to also emit a '+
    'promise-ledger event.</p>'+
    '<label>Target edge_id <input id="cc_edge" size="60"></label><br>'+
    '<label>Reviewer id (orcid:… or email:…) <input id="cc_who" size="40"></label><br>'+
    '<label>Comment <textarea id="cc_cmt" rows="3" cols="60"></textarea></label><br>'+
    '<button id="cc_go">Build JSON</button>'+
    '<pre id="cc_out"></pre>';
  root.appendChild(cc);
  document.getElementById('cc_go').onclick=()=>{
    const payload={
      schema:'phytograph.counter_claim.v1',
      accepted_taxon_key:p.accepted_taxon_key,
      target_edge_id:document.getElementById('cc_edge').value.trim(),
      target_kind:'evidence_row_or_prediction',
      reviewer_id:document.getElementById('cc_who').value.trim(),
      comment:document.getElementById('cc_cmt').value.trim(),
      iso_timestamp:new Date().toISOString(),
    };
    document.getElementById('cc_out').textContent=JSON.stringify(payload,null,2);
  };
}
init();
