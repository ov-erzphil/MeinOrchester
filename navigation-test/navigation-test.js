/* Isolated navigation test; original calendar and data loading remain untouched. */
(function(){
const css=document.createElement('style');
css.textContent=`
@media(max-width:820px){
 #calendar>.grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:8px}
 #calendar>.grid>.card{min-width:0;padding:9px}
 #calendar #events .event{font-size:12px;overflow-wrap:anywhere;padding:8px 5px}
 #calendar #detail{position:sticky;top:8px;align-self:start;max-height:calc(100dvh - 100px);overflow-y:auto;font-size:12px}
 #calendar #detail h2{font-size:15px;overflow-wrap:anywhere}
}
#detail .mo-nav-actions{display:grid;gap:8px;margin:12px 0}
#detail .mo-nav-actions .btn{display:block;text-align:center;font-size:13px;white-space:normal;overflow-wrap:anywhere}
#detail .mo-go{background:#185b77;color:white;border-color:#185b77}
#detail .mo-return{background:#28734c;color:white;border-color:#28734c}
#detail .mo-return-settings{font-size:12px}
`;
document.head.append(css);
const baseDetail=detail;
detail=function(){
 baseDetail();
 const el=document.getElementById('detail');
 const e=events.find(x=>x.id===selected);
 if(!e||!el)return;
 // Remove only the old outbound navigation, not unrelated maps links.
 el.querySelectorAll('a').forEach(a=>{
   if(/Navigation zum Dienstort|Google Maps/i.test(a.textContent||''))a.closest('p')?.remove();
 });
 const place=String(e.location||'').trim();
 const destination=(localStorage.getItem('mo_return_destination')||'').trim();
 const outward=place?'https://www.google.com/maps/dir/?api=1&destination='+encodeURIComponent(place)+'&travelmode=driving':'';
 const back=place&&destination?'https://www.google.com/maps/dir/?api=1&origin='+encodeURIComponent(place)+'&destination='+encodeURIComponent(destination)+'&travelmode=driving':'';
 const nav=document.createElement('div');nav.className='mo-nav-actions';
 const heading=document.createElement('strong');heading.textContent='Navigation';nav.append(heading);
 function add(label,url,cls){
  const a=document.createElement(url?'a':'button');a.className='btn '+cls;a.textContent=label;
  if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer'}else a.disabled=true;
  nav.append(a);
 }
 add('↗ Navigieren zum Dienstort',outward,'mo-go');
 add('🚗 Verkehrslage Rückfahrt',back,'mo-return');
 if(!place){const msg=document.createElement('small');msg.textContent='Kein Dienstort im Kalendereintrag hinterlegt.';nav.append(msg)}
 const settings=document.createElement('details');settings.className='mo-return-settings';
 const summary=document.createElement('summary');summary.textContent='Rückfahrziel festlegen / ändern';
 const input=document.createElement('input');input.placeholder='Straße, Hausnummer, Ort';input.value=destination;
 const save=document.createElement('button');save.type='button';save.textContent='Speichern';
 save.addEventListener('click',()=>{localStorage.setItem('mo_return_destination',input.value.trim());detail()});
 settings.append(summary,input,save);nav.append(settings);
 const description=Array.from(el.querySelectorAll('h3')).find(h=>/Beschreibung/i.test(h.textContent||''));
 if(description)description.before(nav);else el.append(nav);
};
if(selected)detail();
})();