/* No credentials or write tokens in this client. Google verifies publication. */
(function(){
 const account='ov.erzphil@gmail.com';
 const source=new URL('./eilmeldung.json',location.href);
 function calendarUrl(){const url=new URL('https://calendar.google.com/calendar/u/0/r');url.searchParams.set('authuser',account);return url.href;}
 function utc(date){return date.toISOString().replace(/[-:]/g,'').replace(/\.\d{3}Z$/,'Z');}
 function template(title,message,expiry){
  const now=new Date(),end=new Date(expiry);
  if(!title.trim()||title.length>180||message.length>5000||!Number.isFinite(end.getTime())||end<=now||end-now>7*86400000)throw Error('Bitte Überschrift und ein Ablaufdatum innerhalb der nächsten sieben Tage eingeben.');
  const url=new URL('https://calendar.google.com/calendar/r/eventedit');
  url.searchParams.set('action','TEMPLATE');url.searchParams.set('authuser',account);
  url.searchParams.set('text','[EILMELDUNG] '+title.trim());url.searchParams.set('details',message.trim());
  url.searchParams.set('dates',utc(now)+'/'+utc(end));url.searchParams.set('ctz','Europe/Berlin');
  return url.href;
 }
 function localTime(date){return new Date(date.getTime()-date.getTimezoneOffset()*60000).toISOString().slice(0,16);}
 async function show(){
  let panel=document.getElementById('mo-alert-editor');
  if(panel){panel.querySelector('input').focus();return;}
  panel=document.createElement('section');panel.id='mo-alert-editor';panel.setAttribute('aria-label','Eilmeldungen');
  panel.style.cssText='position:fixed;inset:0;z-index:2147483100;overflow:auto;background:#f8fafc;color:#17324a;padding:20px;box-sizing:border-box;font:16px system-ui';
  panel.innerHTML='<div style="max-width:680px;margin:auto"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><h2>Eilmeldung</h2><button id="mo-alert-close" type="button">Schließen</button></div><p id="mo-alert-current" role="status">Meldungsstatus wird geladen …</p><button id="mo-alert-create" type="button" style="padding:13px;background:#b91c1c;color:white;border:0;border-radius:7px;font:700 17px system-ui">Eilmeldung erstellen</button><form id="mo-alert-form" hidden style="margin-top:18px"><label style="display:block;margin:12px 0">Überschrift<input id="mo-alert-title" required maxlength="180" placeholder="Zum Beispiel: Vorstellung entfällt" style="display:block;width:100%;padding:12px;box-sizing:border-box;font:inherit"></label><label style="display:block;margin:12px 0">Nachricht<textarea id="mo-alert-message" required maxlength="5000" rows="7" placeholder="Datum, Uhrzeit, betroffener Dienst und weitere Hinweise" style="display:block;width:100%;padding:12px;box-sizing:border-box;font:inherit"></textarea></label><label style="display:block;margin:12px 0">Anzeigen bis<input id="mo-alert-expiry" type="datetime-local" required style="display:block;padding:10px;font:inherit"></label><p>Veröffentlichung durch die drei Berechtigten: Bei Google mit <strong>ov.erzphil@gmail.com</strong> anmelden und den vorbereiteten Eintrag in diesem Kalender <strong>speichern</strong>. Erst dadurch wird die Meldung veröffentlicht. Das Google-Passwort ausschließlich bei Google eingeben.</p><button type="submit" style="padding:13px;background:#b91c1c;color:white;border:0;border-radius:7px;font:700 16px system-ui">Bei Google bestätigen und speichern</button><p id="mo-alert-result" role="status"></p></form><hr style="margin-top:24px"><p>Die Übernahme in die App erfolgt nach dem automatischen Abgleich. Dieser ist alle fünf Minuten vorgesehen; Google und die Veröffentlichung können zusätzliche Verzögerungen verursachen.</p><p><a id="mo-alert-calendar" target="_blank" rel="noopener noreferrer">Eilmeldung im Google-Kalender ändern oder zurücknehmen</a></p><p style="font-size:14px">Zum Zurücknehmen den Eintrag mit „[EILMELDUNG]“ im gemeinsamen Kalender löschen. Nach dem Abgleich verschwindet die Meldung. Zum festgelegten Ablaufzeitpunkt endet die Anzeige automatisch.</p></div>';
  document.body.append(panel);panel.querySelector('#mo-alert-close').onclick=()=>panel.remove();
  panel.querySelector('#mo-alert-calendar').href=calendarUrl();
  panel.querySelector('#mo-alert-expiry').value=localTime(new Date(Date.now()+24*3600000));
  panel.querySelector('#mo-alert-create').onclick=()=>{panel.querySelector('#mo-alert-form').hidden=false;panel.querySelector('#mo-alert-title').focus();};
  panel.querySelector('#mo-alert-form').onsubmit=event=>{
   event.preventDefault();const status=panel.querySelector('#mo-alert-result');
   try{
    const url=template(panel.querySelector('#mo-alert-title').value,panel.querySelector('#mo-alert-message').value,panel.querySelector('#mo-alert-expiry').value);
    const opened=window.open(url,'_blank','noopener,noreferrer');
    status.replaceChildren();status.append(document.createTextNode('Bei Google das Konto und den Kalender kontrollieren und auf „Speichern“ klicken. '));
    const link=document.createElement('a');link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='Vorbereitete Meldung bei Google öffnen';status.append(link);
   }catch(error){status.textContent=error.message;}
  };
  try{
   const response=await fetch(source.href+'?t='+Date.now(),{cache:'no-store'});if(!response.ok)throw Error();const data=await response.json();
   panel.querySelector('#mo-alert-current').textContent=data.active===true&&(!data.expiresAt||Date.parse(data.expiresAt)>Date.now())?'Aktive Eilmeldung: '+data.title:'Derzeit ist keine Eilmeldung aktiv.';
  }catch(error){panel.querySelector('#mo-alert-current').textContent='Der aktuelle Meldungsstatus konnte nicht geladen werden.';}
 }
 function bind(doc){
  if(!doc||doc.documentElement.dataset.moAlertsBound)return;doc.documentElement.dataset.moAlertsBound='1';
  doc.addEventListener('click',event=>{
   const target=event.target.closest?.('button,a,[role="tab"],[role="button"]');if(!target)return;
   const label=(target.textContent||target.getAttribute('aria-label')||'').trim();
   if(/^(Eilmeldung|Aktuell|Aktuelles|Eilmitteilungen|Eilmeldungen)$/.test(label)){event.preventDefault();event.stopImmediatePropagation();show();}
  },true);
 }
 bind(document);
 const frame=document.getElementById('app');
 function bindFrame(){try{bind(frame.contentDocument);}catch(error){}}
 if(frame){frame.addEventListener('load',bindFrame);bindFrame();}
 window.moOpenAlertEditor=show;
})();
