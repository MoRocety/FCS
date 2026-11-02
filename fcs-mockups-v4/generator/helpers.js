// Shared runtime helpers embedded in every phase file.
const ICONS = {
  search: 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
  calendar: 'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5',
  bookmark: 'M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0111.186 0z',
  user: 'M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z',
  chart: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z',
  heart: 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
  bolt: 'M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z',
  shield: 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
  academic: 'M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.499 5.221 69.073 69.073 0 00-2.658.814m-15.482 0A50.55 50.55 0 0112 13.489a50.55 50.55 0 0112-2.82',
  beaker: 'M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21a48.25 48.25 0 01-8.135-.687c-1.718-.293-2.3-2.379-1.067-3.61L5 14.5',
  chat: 'M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.449-4.449a.75.75 0 01.53-.217H20a3 3 0 003-3v-7.5a3 3 0 00-3-3H6a3 3 0 00-3 3v9.26z',
  cog: 'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281zM15 12a3 3 0 11-6 0 3 3 0 016 0z',
  plus: 'M12 4.5v15m7.5-7.5h-15',
  trash: 'M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0',
  check: 'M4.5 12.75l6 6 9-13.5',
  chevronLeft: 'M15.75 19.5L8.25 12l7.5-7.5',
  chevronRight: 'M8.25 4.5l7.5 7.5-7.5 7.5',
  star: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
  arrowPath: 'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99',
  mapPin: 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0zM19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z',
  clock: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z',
  bell: 'M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0',
  fire: 'M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z',
  thumbUp: 'M6.633 10.5c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V3a.75.75 0 00-.75-.75A2.25 2.25 0 0013.5 0h-3a2.25 2.25 0 00-2.25 2.25v3c0 .621.504 1.125 1.125 1.125h.003a2.25 2.25 0 011.125 1.79v.006c0 .621-.504 1.125-1.125 1.125H9.75c-.621 0-1.125-.504-1.125-1.125v-1.5A2.25 2.25 0 006.633 10.5z',
  thumbDown: 'M12.367 10.5H9.75c-.621 0-1.125-.504-1.125-1.125V8.25a2.25 2.25 0 012.25-2.25h3a2.25 2.25 0 012.25 2.25v3c0 .621.504 1.125-1.125 1.125h-.003a2.25 2.25 0 01-1.125-1.79v-.006c0-.621.504-1.125 1.125-1.125h3.75a2.25 2.25 0 002.25-2.25V4.5a2.25 2.25 0 00-2.25-2.25h-9A2.25 2.25 0 003 4.5v9a2.25 2.25 0 002.25 2.25h3c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 012.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 00.322-1.672V10.5z',
  information: 'M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zM12 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z',
  moon: 'M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z',
  sun: 'M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z',
  sparkles: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z',
  document: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  currency: 'M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  robot: 'M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
};

function icon(name, cls = 'w-5 h-5') {
  const path = ICONS[name] || '';
  return `<svg class="${cls}" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="${path}"/></svg>`;
}

function toast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed bottom-4 right-4 z-[100] flex flex-col gap-2';
    document.body.appendChild(container);
  }
  const colors = {info: 'bg-slate-800 text-white', success: 'bg-emerald-600 text-white', warning: 'bg-amber-500 text-white', error: 'bg-rose-600 text-white'};
  const el = document.createElement('div');
  el.className = `${colors[type]} px-4 py-3 rounded-xl shadow-lg text-sm font-medium transform transition-all duration-300 translate-y-4 opacity-0`;
  el.innerHTML = `<div class="flex items-center gap-2">${message}</div>`;
  container.appendChild(el);
  requestAnimationFrame(() => el.classList.remove('translate-y-4', 'opacity-0'));
  setTimeout(() => { el.classList.add('translate-y-4', 'opacity-0'); setTimeout(() => el.remove(), 300); }, 3000);
}

function modal(title, content) {
  const id = 'fcs-modal-' + Math.random().toString(36).slice(2);
  const wrapper = document.createElement('div');
  wrapper.innerHTML = `
    <div id="${id}" class="fixed inset-0 z-[90] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm" onclick="if(event.target===this){closeModal('${id}')}">
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-auto border border-slate-200 dark:border-slate-700">
        <div class="sticky top-0 bg-white/90 dark:bg-slate-800/90 backdrop-blur px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <h3 class="text-lg font-semibold">${title}</h3>
          <button onclick="closeModal('${id}')" class="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">${icon('plus', 'w-5 h-5 rotate-45')}</button>
        </div>
        <div class="p-6">${content}</div>
      </div>
    </div>`;
  document.body.appendChild(wrapper.firstElementChild);
}
function closeModal(id) { const el = document.getElementById(id); if (el) el.remove(); }

function barChart(data, labels, opts = {}) {
  const width = opts.width || 300;
  const height = opts.height || 120;
  const max = Math.max(...data, 1);
  const barW = (width / data.length) * 0.6;
  const gap = (width / data.length) * 0.4;
  const colors = opts.colors || Array(data.length).fill('#2563eb');
  const bars = data.map((d, i) => {
    const h = (d / max) * (height - 24);
    const x = i * (barW + gap) + gap / 2;
    const y = height - h - 20;
    return `<rect x="${x}" y="${y}" width="${barW}" height="${h}" rx="4" fill="${colors[i]}" opacity="0.9"/><text x="${x + barW / 2}" y="${height - 4}" text-anchor="middle" font-size="10" fill="currentColor" class="text-slate-500">${labels[i]}</text>`;
  }).join('');
  return `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">${bars}</svg>`;
}

function gauge(value, label, opts = {}) {
  const r = opts.r || 40;
  const c = 2 * Math.PI * r;
  const offset = c - (value / 100) * c;
  const color = value >= 75 ? '#10b981' : value >= 50 ? '#f59e0b' : '#ef4444';
  return `
    <div class="relative inline-flex flex-col items-center justify-center">
      <svg width="${r * 2 + 16}" height="${r * 2 + 16}" viewBox="0 0 ${r * 2 + 16} ${r * 2 + 16}">
        <circle cx="${r + 8}" cy="${r + 8}" r="${r}" stroke="currentColor" stroke-width="8" fill="none" class="text-slate-200 dark:text-slate-700"/>
        <circle cx="${r + 8}" cy="${r + 8}" r="${r}" stroke="${color}" stroke-width="8" fill="none" stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${offset}" transform="rotate(-90 ${r + 8} ${r + 8})"/>
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-xl font-bold">${value}</span>
        <span class="text-[10px] uppercase tracking-wide text-slate-500">${label}</span>
      </div>
    </div>`;
}

function formatTime(h) {
  const hour = Math.floor(h);
  const min = Math.round((h - hour) * 60);
  const ampm = hour < 12 ? 'AM' : 'PM';
  const disp = hour % 12 || 12;
  return `${disp}:${min.toString().padStart(2, '0')} ${ampm}`;
}

function parseDays(str) { return str.replace('Th', 'R').split(''); }
function dayName(d) { return {M: 'Mon', T: 'Tue', W: 'Wed', R: 'Thu', F: 'Fri'}[d]; }
function dayNameShort(d) { return d === 'R' ? 'Th' : d; }

function courseById(id) { return DATA.courses.find(c => c.id === id); }
function instructorById(id) { return DATA.instructors.find(i => i.id === id); }
function sectionById(id) {
  for (const c of DATA.courses) {
    const s = c.sections.find(x => x.id === id);
    if (s) return {...s, courseId: c.id, courseCode: c.code, credits: c.credits};
  }
  return null;
}
function instructorName(id) { const i = instructorById(id); return i ? i.name.split(' ').pop() : id; }
function courseCode(id) { const c = courseById(id); return c ? c.code : id; }
function sectionCode(secId) { const s = sectionById(secId); return s ? `${s.courseCode} ${secId.split('-').pop()}` : secId; }

function hasConflict(sections) {
  const slots = [];
  sections.forEach(s => parseDays(s.days).forEach(d => slots.push({d, start: s.start, end: s.start + s.duration})));
  for (let i = 0; i < slots.length; i++) {
    for (let j = i + 1; j < slots.length; j++) {
      if (slots[i].d === slots[j].d && slots[i].start < slots[j].end && slots[j].start < slots[i].end) return true;
    }
  }
  return false;
}

function computeMetrics(sections) {
  const credits = sections.reduce((a, s) => a + (sectionById(s.id)?.credits || 0), 0);
  const starts = sections.map(s => s.start);
  const avgStart = starts.length ? formatTime(starts.reduce((a, b) => a + b, 0) / starts.length) : '—';
  const spread = starts.length ? Math.max(...starts) - Math.min(...starts) : 0;
  const compactness = Math.max(0, Math.min(100, Math.round(100 - spread * 8)));
  const rating = sections.length ? (sections.reduce((a, s) => a + s.rating, 0) / sections.length).toFixed(1) : '—';
  const score = Math.round((compactness + (parseFloat(rating) * 20) + Math.min(100, credits / 18 * 100)) / 3);
  return {credits, avgStart, compactness, rating, score};
}

function cartesian(arrays) {
  if (!arrays.length) return [[]];
  return arrays.reduce((acc, arr) => acc.flatMap(a => arr.map(b => [...a, b])), [[]]);
}

function generateSchedules() {
  const selected = DATA.courses.filter(c => app.selectedIds.includes(c.id));
  const excluded = new Set(app.builder.excludedDays);
  const pool = selected.map(c => {
    let secs = c.sections.filter(s => !parseDays(s.days).some(d => excluded.has(d)));
    if (!secs.length) secs = c.sections;
    return secs.map(s => ({...s, courseId: c.id, credits: c.credits}));
  });
  let combos = cartesian(pool).filter(sections => !hasConflict(sections)).slice(0, 12);
  app.builder.generated = combos.map((sections, i) => {
    const metrics = computeMetrics(sections);
    const score = Math.max(0, Math.min(100, metrics.score - i * 2));
    return {sections, metrics, score};
  }).sort((a, b) => b.score - a.score);
  app.builder.currentIdx = 0;
  toast('Generated ' + app.builder.generated.length + ' schedules', 'success');
  render();
}

function renderTimetable(sections, opts = {}) {
  const days = ['M', 'T', 'W', 'R', 'F'];
  const startHour = 8, endHour = 18;
  const rows = (endHour - startHour) * 2;
  const header = `<div class="grid grid-cols-6 gap-px mb-1" style="grid-column:1/-1"><div class="text-xs text-slate-400 text-center py-1">Time</div>${days.map(d => `<div class="text-xs font-semibold text-center py-1">${dayName(d)}</div>`).join('')}</div>`;
  let grid = '';
  for (let h = startHour; h < endHour; h += 0.5) {
    const row = Math.round((h - startHour) * 2) + 2;
    grid += `<div class="grid grid-cols-6 gap-px" style="grid-row:${row};grid-column:1/-1"><div class="text-[10px] text-slate-400 text-right pr-2 py-1 border-t border-slate-100 dark:border-slate-800">${formatTime(h)}</div>${days.map(() => `<div class="border-t border-slate-100 dark:border-slate-800"></div>`).join('')}</div>`;
  }
  const palette = ['bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500', 'bg-violet-500', 'bg-cyan-500', 'bg-fuchsia-500', 'bg-lime-500'];
  const colorMap = {};
  DATA.courses.forEach((c, idx) => colorMap[c.id] = palette[idx % palette.length]);
  const blocks = sections.map(s => {
    const sec = sectionById(s.id) || s;
    const course = courseById(sec.courseId) || {};
    return parseDays(sec.days).map(d => {
      const col = days.indexOf(d) + 2;
      const startRow = Math.round((sec.start - startHour) * 2) + 2;
      const endRow = startRow + Math.round(sec.duration * 2);
      return `<div class="rounded-lg p-1.5 text-[10px] text-white shadow-md overflow-hidden ${colorMap[sec.courseId] || 'bg-slate-500'}" style="grid-column:${col};grid-row:${startRow}/${endRow}">
        <div class="font-bold truncate">${course.code || ''}</div>
        <div class="truncate opacity-90">${formatTime(sec.start)}-${formatTime(sec.start + sec.duration)}</div>
        <div class="truncate opacity-80">${sec.location || ''}</div>
      </div>`;
    }).join('');
  }).join('');
  return `<div class="relative rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden bg-white dark:bg-slate-800" style="height:${opts.height || '320px'}">
    <div class="absolute inset-0 p-2 grid" style="grid-template-rows:auto repeat(${rows}, 1fr);grid-template-columns:3.5rem repeat(5,1fr);gap:2px">${header}${grid}${blocks}</div>
  </div>`;
}

const HINTS = [
  {icon:'bolt', text:'Press / to search, G to generate schedules.'},
  {icon:'bell', text:'Registration opens in 3 days — finalize backups.'},
  {icon:'sparkles', text:'3 project-based electives match your profile.'},
  {icon:'fire', text:'Hot seat alert: CS301-A only 10 seats left.'}
];
let hintIndex = 0;

function renderHints() {
  const el = document.getElementById('hints');
  if (!el) return;
  const hint = HINTS[hintIndex % HINTS.length];
  el.innerHTML = `
    <div class="flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-100 dark:border-blue-900/30 text-sm text-blue-800 dark:text-blue-200 animate-fadeIn">
      ${icon(hint.icon, 'w-4 h-4')}
      <span class="flex-1">${hint.text}</span>
      <button onclick="hintIndex++; renderHints();" class="text-blue-400 hover:text-blue-600">${icon('chevronRight', 'w-4 h-4')}</button>
      <button onclick="document.getElementById('hints').style.display='none'" class="text-blue-400 hover:text-blue-600">${icon('plus', 'w-4 h-4 rotate-45')}</button>
    </div>`;
}

function confetti() {
  for (let i = 0; i < 40; i++) {
    const el = document.createElement('div');
    el.style.position = 'fixed'; el.style.left = '50%'; el.style.top = '40%';
    el.style.width = '8px'; el.style.height = '8px'; el.style.borderRadius = '50%';
    el.style.background = ['#2563eb','#10b981','#f59e0b','#ef4444','#8b5cf6'][Math.floor(Math.random() * 5)];
    el.style.zIndex = 9999; el.style.pointerEvents = 'none';
    const angle = Math.random() * Math.PI * 2;
    const dist = 60 + Math.random() * 120;
    el.style.transition = 'transform 0.8s ease-out, opacity 0.8s ease-out';
    document.body.appendChild(el);
    requestAnimationFrame(() => { el.style.transform = `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px) scale(0)`; el.style.opacity = 0; });
    setTimeout(() => el.remove(), 850);
  }
}

function sendAgent(text) {
  if (!text || !text.trim()) return;
  app.chat.messages.push({role:'user', text});
  app.chat.audit.push({tool:'search_courses', args:text, result:'Found relevant matches'});
  render();
  setTimeout(() => {
    app.chat.messages.push({role:'agent', text: 'I found some options. You can refine by time, instructor, or difficulty.'});
    render();
  }, 600);
}

function setReviewStar(n) {
  app.reviewStars = n;
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById('rs'+i);
    if (el) el.className = i <= n ? 'text-amber-400' : 'text-slate-300';
  }
}

document.addEventListener('keydown', e => {
  if (e.key === '/' && app.view === 'catalog') { e.preventDefault(); const el = document.querySelector('#app input[type=text]'); if (el) el.focus(); }
  if ((e.key === 'g' || e.key === 'G') && app.view === 'builder') { e.preventDefault(); generateSchedules(); }
  if (e.key >= '1' && e.key <= '9') {
    const keys = Object.keys(VIEWS);
    const idx = parseInt(e.key, 10) - 1;
    if (keys[idx] && !['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) { setView(keys[idx]); }
  }
});
