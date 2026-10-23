/* Test branch only: visual/navigation extension; does not change calendar data. */
(function(){
 const style=document.createElement('style');
 style.textContent=`
 @media(max-width:820px){#calendar .grid{grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px}#calendar .grid>.card{min-width:0;padding:9px}#calendar .event{font-size:12px;overflow-wrap:anywhere}#calendar #detail{position:sticky;top:8px;align-self:start;max-height:calc(100dvh - 100px);overflow-y:auto;font-size:12px}#calendar #detail h2{font-size:16px;overflow-wrap:anywhere}}
 #detail .mo-nav-actions{display:grid;gap:8px;margin:12px 0}#detail .mo-nav-actions .btn{display:block;text-align:center;font-size:13px;white-space:normal;overflow-wrap:anywhere}#detail .mo-go{background:#185b77;color:white;border-color:#185b77}#detail .mo-return{background:#28734c;color:white;border-color:#28734c}#detail .mo-return-settings{font-size:12px}
 `;
 document.head.append(style);
 const originalDetail=detail;
 detail=function(){
   originalDetail();
   const el=document.getElementById('detail');
   const e=events.find(x=>x.id===selected);
   if(!e||!el)return;
   el.querySelectorAll('a[href*="google.com/maps/dir/"]').forEach(a=>a.closest('p')?.remove());
   const place=(e.location||'').trim();
   const dest=(localStorage.getItem('mo_return_destination')||'').trim();
   const outbound=place?'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(place)+'&travelmode=driving':'';
   const inbound=place&&dest?'https://www.google.com/maps/dir/?api=1&origin='+encodeURIComponent(place)+'&destination='+encodeURIComponent(dest)+'&travelmode=driving':'';
   const box=document.createElement('div');box.className='mo-nav-actions';
   const heading=document.createElement('strong');heading.textContent='Navigation';box.append(heading);
   const link=(label,url,cls)=>{const a=document.createElement(url?'a':'button');a.className='btn '+cls;a.textContent=label;if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer'}else{a.disabled=true}box.append(a)};
   link('↗ Navigieren zum Dienstort',outbound,'mo-go');
   link('🚗 Verkehrslage Rückfahrt',inbound,'mo-return');
   if(!place){const note=document.createElement('small');note.textContent='Für diesen Dienst ist kein Ort hinterlegt.';box.append(note)}
   const details=document.createElement('details');details.className='mo-return-settings';details.innerHTML='<summary>Rückfahrziel festlegen / ändern</summary><label>Adresse für Rückfahrt</label>';
   const input=document.createElement('input');input.value=dest;input.placeholder='Straße, Hausnummer, Ort';
   const save=document.createElement('button');save.type='button';save.textContent='Speichern';save.onclick=()=>{localStorage.setItem('mo_return_destination',input.value.trim());detail()};
   details.append(input,save);box.append(details);
   const desc=Array.from(el.querySelectorAll('h3')).find(x=>x.textContent.includes('Beschreibung'));
   if(desc)desc.before(box);else el.append(box);
 };
 if(selected)detail();
})();
