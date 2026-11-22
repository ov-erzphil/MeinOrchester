(() => {
  const calendar = document.getElementById('calendar');
  if (!calendar || document.getElementById('mo-planning')) return;

  const berlin = {timeZone: 'Europe/Berlin'};
  const dates = new Intl.DateTimeFormat('sv-SE', berlin);
  const times = new Intl.DateTimeFormat('de-DE', {...berlin, hour: '2-digit', minute: '2-digit'});
  const heading = new Intl.DateTimeFormat('de-DE', {month: 'long', year: 'numeric'});
  const dayLabel = new Intl.DateTimeFormat('de-DE', {weekday: 'long', day: 'numeric', month: 'long'});
  const today = () => dates.format(new Date());
  const localDate = key => new Date(key + 'T12:00:00');
  const keyOf = day => [
    day.getFullYear(), String(day.getMonth() + 1).padStart(2, '0'), String(day.getDate()).padStart(2, '0')
  ].join('-');
  const eventDay = event => {
    if (!/T.*(?:Z|[+-]\d\d:\d\d)$/.test(event.start)) return event.start.slice(0, 10);
    const instant = new Date(event.start);
    return Number.isFinite(+instant) ? dates.format(instant) : '';
  };
  const eventTime = event => event.start.length === 10 ? 'Ganztägig' :
    /(?:Z|[+-]\d\d:\d\d)$/.test(event.start) ? times.format(new Date(event.start)) + ' Uhr' :
    event.start.slice(11, 16) + ' Uhr';
  const activeDuty = event => event.start && event.status !== 'CANCELLED' &&
    !/^(frei|dienstfrei|freier tag)(\b|\s|$)/i.test(event.title.trim());
  const node = (tag, text) => {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    return el;
  };
  const button = (label, action) => {
    const el = node('button', label);
    el.type = 'button';
    el.onclick = action;
    return el;
  };

  const style = node('style');
  style.textContent = `
    #mo-planning h2{margin:0 0 .5rem;font-size:1.22rem}
    #mo-planning p{margin:.45rem 0 .75rem}
    #calendar > [hidden],#mo-planning [hidden]{display:none!important}
    #mo-planning .mo-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:4px;margin:.75rem 0}
    #mo-planning .mo-year{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:8px;margin:.75rem 0}
    #mo-planning .mo-weekday{text-align:center;font-size:.8rem}
    #mo-planning .mo-day-button{min-width:0;min-height:44px;padding:4px;text-align:center;font-size:.85rem;border-radius:6px}
    #mo-planning .mo-busy{background:#e1edf2;font-weight:700}
    #mo-planning .mo-weekend:not(.mo-busy){background:#f2f5f6}
    #mo-planning [aria-current="date"]{outline:2px solid #185b77;outline-offset:-2px}
    #mo-planning [aria-pressed="true"]{box-shadow:inset 0 0 0 2px #185b77}
    #mo-planning .mo-day-button small{display:block;font-size:.68rem}
    @media(max-width:450px){#mo-planning .mo-year{grid-template-columns:1fr}}
    #mo-planning details{margin-top:.75rem}
    #mo-planning details label{display:inline-block;margin:.5rem .65rem 0 0}
    #mo-planning details input{display:block;width:8rem;margin:4px 0}
    #mo-planning .mo-period{margin-top:.7rem}
    #mo-planning .mo-date-results button{display:block;text-align:left;width:100%;margin:5px 0}
  `;
  document.head.append(style);
  const panel = node('div');
  panel.id = 'mo-planning';
  panel.innerHTML = `
    <div class="card">
      <h2>Mein nächster Dienst</h2>
      <div class="mo-next"></div>
      <details hidden><summary>Abfahrt einstellen</summary>
        <label>Fahrzeit in Minuten<input class="mo-travel" type="number" min="0" max="1440" step="1"></label>
        <label>Puffer in Minuten<input class="mo-buffer" type="number" min="0" max="1440" step="1" value="15"></label>
      </details>
    </div>
    <div class="card">
      <h2>Planung</h2>
      <div class="actions mo-views"></div>
      <div class="row mo-period" hidden></div>
      <div class="mo-overview" hidden></div>
    </div>`;
  calendar.prepend(panel);

  const next = panel.querySelector('.mo-next');
  const settings = panel.querySelector('details');
  const travel = panel.querySelector('.mo-travel');
  const buffer = panel.querySelector('.mo-buffer');
  const period = panel.querySelector('.mo-period');
  const overview = panel.querySelector('.mo-overview');
  const filters = panel.nextElementSibling;
  const list = filters.nextElementSibling;
  const toggleViews = panel.querySelector('.mo-views');
  const travelKey = 'mo_duty_travel_minutes';
  const bufferKey = 'mo_duty_buffer_minutes';
  travel.value = localStorage.getItem(travelKey) ?? '';
  buffer.value = localStorage.getItem(bufferKey) ?? '15';
  for (const [input, key] of [[travel, travelKey], [buffer, bufferKey]]) {
    input.addEventListener('input', () => {
      if (input.validity.valid) localStorage.setItem(key, input.value);
      updateNext();
    });
  }

  let mode = 'Dienste';
  let focusDay = today();
  let grouped = new Map();

  function showDuty(event) {
    const day = eventDay(event);
    document.getElementById('query').value = '';
    document.getElementById('history').checked = day < today();
    document.getElementById('from').value = event.start.slice(0, 10);
    document.getElementById('to').value = event.start.slice(0, 10);
    selected = event.id;
    switchView('Dienste');
    render();
    document.getElementById('detail').scrollIntoView({block: 'nearest'});
  }

  function updateNext() {
    const now = Date.now();
    const berlinNow = times.format(now);
    const event = [...grouped.entries()]
      .filter(([day]) => day >= today())
      .sort(([a], [b]) => a.localeCompare(b))
      .flatMap(([, dayEvents]) => dayEvents)
      .find(item => eventDay(item) > today() || eventTime(item) === 'Ganztägig' ||
        eventTime(item).slice(0, 5) >= berlinNow);
    next.replaceChildren();
    settings.hidden = !event || event.start.length === 10;
    if (!event) {
      next.append(node('p', 'Im Kalender steht derzeit kein kommender Dienst.'));
      return;
    }
    next.append(node('strong', event.title || 'Dienst'));
    next.append(node('p', dayLabel.format(localDate(eventDay(event))) + ' · ' + eventTime(event) +
      ' · ' + (event.location || 'Ort nicht angegeben')));
    if (!settings.hidden && travel.value !== '' && travel.validity.valid && buffer.validity.valid) {
      const minutes = travel.valueAsNumber + Number(buffer.value);
      const [hour, minute] = eventTime(event).slice(0, 5).split(':').map(Number);
      const departure = localDate(eventDay(event));
      departure.setHours(hour, minute - minutes, 0, 0);
      next.append(node('p', 'Geplante Abfahrt ' + (keyOf(departure) !== eventDay(event) ?
        dayLabel.format(departure) + ', ' : '') +
        departure.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'}) + ' Uhr'));
    }
    const actions = node('div');
    actions.className = 'actions';
    if (event.location.trim()) {
      const maps = node('a', 'Navigieren');
      maps.className = 'btn primary';
      const url = new URL('https://www.google.com/maps/dir/');
      url.searchParams.set('api', '1');
      url.searchParams.set('destination', event.location);
      const home = (localStorage.getItem('mo_home_address') || localStorage.getItem('mo_return_destination') || '').trim();
      if (home) url.searchParams.set('origin', home);
      url.searchParams.set('travelmode', 'driving');
      maps.href = url.href;
      maps.target = '_blank';
      maps.rel = 'noopener noreferrer';
      actions.append(maps);
    }
    actions.append(button('Tagesplan', () => window.parent.startDayplan()),
      button('Dienstdetails', () => showDuty(event)));
    next.append(actions);
  }

  function switchView(view) {
    mode = view;
    for (const el of toggleViews.children) el.setAttribute('aria-pressed', el.textContent === mode);
    filters.hidden = list.hidden = mode !== 'Dienste';
    period.hidden = overview.hidden = mode === 'Dienste';
    drawOverview();
  }

  function movePeriod(step) {
    const current = localDate(focusDay);
    focusDay = keyOf(new Date(current.getFullYear() + (mode === 'Jahr' ? step : 0),
      current.getMonth() + (mode === 'Monat' ? step : 0), 1));
    drawOverview();
  }

  function drawOverview() {
    if (mode === 'Dienste') return;
    const current = localDate(focusDay);
    const year = current.getFullYear();
    const month = current.getMonth();
    period.replaceChildren(button('‹', () => movePeriod(-1)),
      node('strong', mode === 'Monat' ? heading.format(current) : String(year)),
      button('›', () => movePeriod(1)), button('Heute', () => {
        focusDay = today();
        drawOverview();
      }));
    period.firstChild.setAttribute('aria-label', 'Vorheriger Zeitraum');
    period.children[2].setAttribute('aria-label', 'Nächster Zeitraum');
    overview.replaceChildren();
    const grid = node('div');
    if (mode === 'Jahr') {
      grid.className = 'mo-year';
      for (let index = 0; index < 12; index++) {
        const first = new Date(year, index, 1);
        const last = new Date(year, index + 1, 0).getDate();
        const monthCard = node('div');
        monthCard.append(button(heading.format(first), () => {
          focusDay = keyOf(first);
          switchView('Monat');
        }));
        const weeks = node('div');
        weeks.className = 'mo-grid';
        for (let day = 1; day <= last;) {
          const date = new Date(year, index, day);
          const length = Math.min(7 - (date.getDay() + 6) % 7, last - day + 1);
          const days = Array.from({length}, (_, offset) => keyOf(new Date(year, index, day + offset)));
          const count = days.filter(key => grouped.has(key)).length;
          const week = button(String(day), () => {
            focusDay = days.find(key => grouped.has(key)) || days[0];
            switchView('Monat');
          });
          week.className = 'mo-day-button' + (count ? ' mo-busy' : '');
          week.setAttribute('aria-label', dayLabel.format(date) + ', ' + count + ' Tage mit Dienst');
          weeks.append(week);
          day += length;
        }
        monthCard.append(weeks);
        grid.append(monthCard);
      }
      overview.append(grid, node('p', 'Blau markierte Wochenabschnitte enthalten Dienste. Helle Abschnitte haben keine Kalendereinträge.'));
      return;
    }
    grid.className = 'mo-grid';
    for (const day of ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']) {
      const label = node('span', day);
      label.className = 'mo-weekday';
      grid.append(label);
    }
    const first = new Date(year, month, 1);
    for (let j = 0; j < (first.getDay() + 6) % 7; j++) grid.append(node('span'));
    const last = new Date(year, month + 1, 0).getDate();
    for (let day = 1; day <= last; day++) {
      const date = new Date(year, month, day);
      const key = keyOf(date);
      const count = grouped.get(key)?.length ?? 0;
      const cell = button(String(day), () => {
        focusDay = key;
        drawOverview();
        overview.querySelector('[aria-pressed="true"]')?.focus();
      });
      cell.className = 'mo-day-button' + (count ? ' mo-busy' : '') +
        ([0, 6].includes(date.getDay()) ? ' mo-weekend' : '');
      if (count) cell.append(node('small', count + '×'));
      cell.setAttribute('aria-label', dayLabel.format(date) + ', ' + count + ' Dienste');
      cell.setAttribute('aria-pressed', key === focusDay);
      if (key === today()) cell.setAttribute('aria-current', 'date');
      grid.append(cell);
    }
    const results = node('div');
    results.className = 'mo-date-results';
    results.append(node('strong', dayLabel.format(current)));
    for (const event of grouped.get(focusDay) ?? []) {
      results.append(button(eventTime(event) + ' · ' + event.title, () => showDuty(event)));
    }
    if (!grouped.has(focusDay)) results.append(node('p', 'Keine Dienste eingetragen.'));
    overview.append(grid, results);
  }

  for (const view of ['Dienste', 'Monat', 'Jahr']) {
    toggleViews.append(button(view, () => switchView(view)));
  }

  function updateCalendar() {
    grouped = new Map();
    for (const event of events.filter(activeDuty).sort((a, b) => eventTime(a).localeCompare(eventTime(b)))) {
      const key = eventDay(event);
      if (!key) continue;
      if (!grouped.has(key)) grouped.set(key, []);
      grouped.get(key).push(event);
    }
    for (const duties of grouped.values()) duties.sort((a, b) => eventTime(a).localeCompare(eventTime(b)));
    updateNext();
    drawOverview();
  }

  const renderCalendar = render;
  render = function () {
    renderCalendar();
    updateCalendar();
  };
  switchView(mode);
  updateCalendar();
  setInterval(updateNext, 60_000);
})();
