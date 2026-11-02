#!/usr/bin/env python3
'''FCS Mockups v4 Generator.'''
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.dirname(os.path.abspath(__file__))

PHASES = {
    'A': ['catalog', 'builder', 'saved'],
    'B': ['catalog', 'builder', 'saved', 'instructor', 'compare', 'course', 'willitfill', 'health', 'stress'],
    'C': ['catalog', 'builder', 'saved', 'instructor', 'compare', 'course', 'willitfill', 'health', 'stress',
          'feed', 'review', 'wrapped', 'waitlist', 'monitor', 'protector', 'textbooks', 'commute'],
    'D': ['catalog', 'builder', 'saved', 'instructor', 'compare', 'course', 'willitfill', 'health', 'stress',
          'feed', 'review', 'wrapped', 'waitlist', 'monitor', 'protector', 'textbooks', 'commute',
          'agentchat', 'memory', 'proactive', 'history', 'degree', 'planner', 'substitute', 'chatbot', 'career']
}

VIEW_META = {
    'catalog': {'label': 'Catalog', 'icon': 'academic'},
    'builder': {'label': 'Builder', 'icon': 'calendar'},
    'saved': {'label': 'Saved', 'icon': 'bookmark'},
    'instructor': {'label': 'Instructor', 'icon': 'user'},
    'compare': {'label': 'Compare', 'icon': 'chart'},
    'course': {'label': 'Course', 'icon': 'beaker'},
    'willitfill': {'label': 'Will It Fill', 'icon': 'bolt'},
    'health': {'label': 'Health', 'icon': 'shield'},
    'stress': {'label': 'Stress', 'icon': 'fire'},
    'feed': {'label': 'Feed', 'icon': 'heart'},
    'review': {'label': 'Review', 'icon': 'star'},
    'wrapped': {'label': 'Wrapped', 'icon': 'sparkles'},
    'waitlist': {'label': 'Waitlist', 'icon': 'clock'},
    'monitor': {'label': 'Monitor', 'icon': 'bell'},
    'protector': {'label': 'Protector', 'icon': 'shield'},
    'textbooks': {'label': 'Textbooks', 'icon': 'currency'},
    'commute': {'label': 'Commute', 'icon': 'mapPin'},
    'agentchat': {'label': 'Agent', 'icon': 'chat'},
    'memory': {'label': 'Memory', 'icon': 'cog'},
    'proactive': {'label': 'Hints', 'icon': 'bell'},
    'history': {'label': 'History', 'icon': 'document'},
    'degree': {'label': 'Degree', 'icon': 'academic'},
    'planner': {'label': 'Planner', 'icon': 'calendar'},
    'substitute': {'label': 'Substitute', 'icon': 'search'},
    'chatbot': {'label': 'Chatbot', 'icon': 'chat'},
    'career': {'label': 'Career', 'icon': 'chart'}
}

def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def make_html(phase, views, data_json, helpers_js):
    view_js = '\n'.join(load(os.path.join(GEN, 'views', v + '.js')) for v in views)
    view_map = ',\n    '.join(f"{v}: {{label:'{VIEW_META[v]['label']}', icon:'{VIEW_META[v]['icon']}', render: render{VIEW_META[v]['label'].replace(' ', '')}}}" for v in views)
    # function names are render + label with spaces removed; ensure consistency with view files.
    # Use actual file content function names: renderCatalog, renderBuilder, etc.
    view_map = ',\n    '.join(f"{v}: {{label:'{VIEW_META[v]['label']}', icon:'{VIEW_META[v]['icon']}', render: {view_func_name(v)}}}" for v in views)
    nav_items = ''.join(
        f"<button id='nav-{v}' onclick='setView(\"{v}\")' class='flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition'>"
        f"<span class='nav-icon'>{icon_svg(VIEW_META[v]['icon'])}</span>{VIEW_META[v]['label']}</button>"
        for v in views
    )
    title = f"FCS v4 · Phase {phase}"
    return f'''<!DOCTYPE html>
<html lang='en' class=''>
<head>
<meta charset='UTF-8'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
<title>{title}</title>
<script src='https://cdn.tailwindcss.com'></script>
<script>tailwind.config = {{ darkMode: 'class' }}</script>
<link rel='preconnect' href='https://fonts.googleapis.com'>
<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap' rel='stylesheet'>
<style>
  body {{ font-family: 'Inter', sans-serif; }}
  .animate-fadeIn {{ animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both; }}
  @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(16px) scale(0.97); filter: blur(4px); }} to {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }} }}
  .glass {{ background: rgba(255,255,255,0.72); backdrop-filter: blur(16px) saturate(180%); }}
  .dark .glass {{ background: rgba(15,23,42,0.72); }}
  input[type='range'] {{ accent-color: #2563eb; }}
  ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
  ::-webkit-scrollbar-thumb {{ background: #94a3b8; border-radius: 4px; }}
  .dark ::-webkit-scrollbar-thumb {{ background: #475569; }}

  /* animated aurora background */
  body::before {{
    content: ''; position: fixed; inset: 0; z-index: -1;
    background:
      radial-gradient(circle at 0% 0%, rgba(37,99,235,0.18) 0%, transparent 40%),
      radial-gradient(circle at 100% 0%, rgba(139,92,246,0.18) 0%, transparent 45%),
      radial-gradient(circle at 50% 100%, rgba(16,185,129,0.14) 0%, transparent 45%),
      radial-gradient(circle at 80% 50%, rgba(245,158,11,0.10) 0%, transparent 35%);
    animation: aurora 12s ease-in-out infinite alternate;
    pointer-events: none;
  }}
  .dark body::before {{
    background:
      radial-gradient(circle at 0% 0%, rgba(37,99,235,0.28) 0%, transparent 40%),
      radial-gradient(circle at 100% 0%, rgba(139,92,246,0.28) 0%, transparent 45%),
      radial-gradient(circle at 50% 100%, rgba(16,185,129,0.22) 0%, transparent 45%),
      radial-gradient(circle at 80% 50%, rgba(245,158,11,0.16) 0%, transparent 35%);
  }}
  @keyframes aurora {{ from {{ transform: scale(1) rotate(0deg); }} to {{ transform: scale(1.1) rotate(2deg); }} }}

  /* grain overlay */
  body::after {{
    content: ''; position: fixed; inset: 0; z-index: -1; opacity: 0.06; pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }}

  /* card lift + tinted glow on hover */
  main [class*='rounded-2xl'] {{ transition: transform 0.25s ease, box-shadow 0.25s ease; }}
  main [class*='rounded-2xl']:hover {{ transform: translateY(-3px); box-shadow: 0 18px 38px -12px rgba(37,99,235,0.18); }}
  .dark main [class*='rounded-2xl']:hover {{ box-shadow: 0 18px 38px -12px rgba(37,99,235,0.35); }}

  /* headings with moving gradient */
  main h2 {{
    background: linear-gradient(90deg, #1e293b, #2563eb, #4f46e5, #1e293b);
    background-size: 300% 100%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: textShine 6s linear infinite;
  }}
  .dark main h2 {{ background: linear-gradient(90deg, #f8fafc, #60a5fa, #a78bfa, #f8fafc); background-size: 300% 100%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  @keyframes textShine {{ from {{ background-position: 0% 50%; }} to {{ background-position: 200% 50%; }} }}

  /* nav items glow on hover */
  #main-nav button {{ transition: all 0.2s ease; }}
  #main-nav button:not(.bg-blue-600):hover {{ background: rgba(37,99,235,0.08); color: #2563eb; }}
  .dark #main-nav button:not(.bg-blue-600):hover {{ background: rgba(96,165,250,0.12); color: #93c5fd; }}

  /* logo breathing ring */
  header .w-10.h-10 {{ animation: breathe 3s ease-in-out infinite; }}
  @keyframes breathe {{ 0%,100% {{ box-shadow: 0 0 0 0 rgba(37,99,235,0.35); }} 50% {{ box-shadow: 0 0 0 10px rgba(37,99,235,0); }} }}

  /* button shine sweep */
  button.bg-blue-600 {{ position: relative; overflow: hidden; transition: transform 0.15s; }}
  button.bg-blue-600:active {{ transform: scale(0.96); }}
  button.bg-blue-600::after {{
    content: ''; position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: skewX(-20deg); transition: left 0.6s;
  }}
  button.bg-blue-600:hover::after {{ left: 160%; }}

  /* table rows shimmer on hover */
  tbody tr {{ transition: background 0.15s, transform 0.15s; }}
  tbody tr:hover {{ transform: scale(1.005); }}

  /* focus rings */
  input:focus, select:focus, textarea:focus {{ outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,0.2); }}
</style>
</head>
<body class='bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100 min-h-screen'>
<header class='sticky top-0 z-50 glass border-b border-slate-200 dark:border-slate-700'>
  <div class='max-w-7xl mx-auto px-4 py-3 flex items-center justify-between gap-4'>
    <div class='flex items-center gap-3'>
      <div class='w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-lg'>FCS</div>
      <div>
        <div class='font-bold text-lg leading-tight'>FCS <span class='text-blue-600'>v4</span></div>
        <div class='text-[10px] uppercase tracking-wider text-slate-500'>Phase {phase}</div>
      </div>
    </div>
    <nav id='main-nav' class='flex-1 overflow-x-auto no-scrollbar flex items-center gap-1 px-2'>{nav_items}</nav>
    <div class='flex items-center gap-2'>
      <button onclick='toggleDark()' class='p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition' aria-label='Toggle dark' id='darkBtn'>{icon_svg('moon')}</button>
      <button class='w-9 h-9 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-sm font-bold'>JD</button>
    </div>
  </div>
</header>
<div id='hints' class='max-w-7xl mx-auto px-4 pt-3'></div>
<main id='app' class='max-w-7xl mx-auto px-4 py-6'></main>
<footer class='max-w-7xl mx-auto px-4 pb-8 text-center text-xs text-slate-400'>
  FCS Mockups v4 · Phase {phase} · Self-contained demo · No backend
</footer>
<script>
const DATA = {data_json};
{helpers_js}
{view_js}

const VIEWS = {{
    {view_map}
}};

const DEFAULT_SAVED = [
  {{
    id: 1,
    name: 'Balanced Fall',
    savedAt: 'Jun 14, 2026',
    sections: [
      {{id:'cs101-02', instructor:'dr_ali', days:'TTh', start:10.0, duration:1.5, seats:45, capacity:60, rating:4.2, location:'SCI Lab 3', courseId:'cs101', credits:4}},
      {{id:'math201-01', instructor:'prof_chen', days:'MWF', start:9.0, duration:1.333, seats:30, capacity:80, rating:4.6, location:'MATH Bldg 201', courseId:'math201', credits:4}},
      {{id:'eng102-02', instructor:'prof_kim', days:'TTh', start:13.5, duration:1.5, seats:34, capacity:40, rating:4.5, location:'LIT Hall 11', courseId:'eng102', credits:3}}
    ]
  }}
];

var app = {{
  view: '{views[0]}',
  darkMode: false,
  selectedIds: [],
  catalog: {{search:'', dept:'All', minCredits:0, maxCredits:6, page:1}},
  builder: {{minCredits:12, maxCredits:18, excludedDays:[], generated:[], currentIdx:0}},
  saved: JSON.parse(localStorage.getItem('fcs_saved') || JSON.stringify(DEFAULT_SAVED)),
  activeInstructor: null,
  compare: ['dr_smith','dr_ali'],
  activeCourse: null,
  activeSection: null,
  feedVotes: {{}},
  reviews: [],
  monitor: ['cs101-01','math201-02'],
  protected: [],
  history: [],
  planner: {{1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[]}},
  substitutionQuery: 'humanities elective',
  reviewStars: 0,
  chat: {{open:false, messages:[{{role:'agent', text:'Hi! I am your FCS assistant. Ask me to find courses, build schedules, or check degree progress.'}}], audit:[]}},
  memory: {{major:'Computer Science', year:'Junior', goal:'graduate on time', standing:'Good', preferences:['No 8 AMs','Project-based']}},
  career: 'industry'
}};
if (typeof globalThis !== 'undefined') globalThis.app = app;

function setView(v) {{ app.view = v; render(); }}
function toggleDark() {{ app.darkMode = !app.darkMode; document.documentElement.classList.toggle('dark', app.darkMode); document.getElementById('darkBtn').innerHTML = icon(app.darkMode ? 'sun' : 'moon'); render(); }}

function toggleCourse(id) {{
  const idx = app.selectedIds.indexOf(id);
  if (idx > -1) app.selectedIds.splice(idx, 1);
  else app.selectedIds.push(id);
  render();
}}
function toggleDay(d) {{
  const idx = app.builder.excludedDays.indexOf(d);
  if (idx > -1) app.builder.excludedDays.splice(idx, 1);
  else app.builder.excludedDays.push(d);
  render();
}}
function prevCombo() {{ if (app.builder.currentIdx > 0) {{ app.builder.currentIdx--; render(); }} }}
function nextCombo() {{ if (app.builder.currentIdx < app.builder.generated.length - 1) {{ app.builder.currentIdx++; render(); }} }}
function saveCurrentSchedule() {{
  const s = app.builder.generated[app.builder.currentIdx];
  if (!s) {{ toast('Nothing to save','warning'); return; }}
  app.saved.unshift({{id: Date.now(), name: 'Schedule ' + (app.saved.length + 1), sections: s.sections, savedAt: new Date().toLocaleString()}});
  localStorage.setItem('fcs_saved', JSON.stringify(app.saved));
  toast('Schedule saved','success');
  confetti();
  render();
}}
function loadSaved(i) {{
  const s = app.saved[i];
  app.builder.generated = [{{sections: s.sections, metrics: computeMetrics(s.sections), score: computeMetrics(s.sections).score}}];
  app.builder.currentIdx = 0;
  setView('builder');
}}
function deleteSaved(i) {{ app.saved.splice(i,1); localStorage.setItem('fcs_saved', JSON.stringify(app.saved)); render(); }}
function voteFeed(id, dir) {{ if (app.feedVotes[id] === dir) delete app.feedVotes[id]; else app.feedVotes[id] = dir; render(); }}
function submitReview() {{
  const inst = document.getElementById('revInst').value;
  const course = document.getElementById('revCourse').value;
  const grade = document.getElementById('revGrade').value;
  const text = document.getElementById('revText').value;
  const rating = app.reviewStars || 4;
  app.reviews.unshift({{inst, course, grade, text, rating, anon: document.getElementById('revAnon').checked, author: 'You'}});
  toast('Review submitted','success');
  render();
}}
function addMonitor(id) {{ if (!app.monitor.includes(id)) {{ app.monitor.push(id); render(); }} }}
function removeMonitor(id) {{ app.monitor = app.monitor.filter(x=>x!==id); render(); }}
function toggleProtected(d, h) {{
  const idx = app.protected.findIndex(p => p.day===d && Math.abs(p.start-h)<0.25);
  if (idx > -1) app.protected.splice(idx,1); else app.protected.push({{day:d, start:h, duration:0.5}});
  render();
}}
function addHistory(id, grade) {{ app.history.unshift({{courseId:id, grade}}); render(); }}
function dropPlanner(sem, ev) {{
  const [id, src] = ev.dataTransfer.getData('text').split('|');
  if (src !== 'pool') app.planner[src] = app.planner[src].filter(x=>x!==id);
  if (sem !== 'pool' && !app.planner[sem].includes(id)) app.planner[sem].push(id);
  render();
}}
function gpaPoints(g) {{
  const map = {{'A':4.0,'A-':3.7,'B+':3.3,'B':3.0,'B-':2.7,'C+':2.3,'C':2.0,'D':1.0,'F':0.0}};
  return map[g] || 0;
}}

function render() {{
  const container = document.getElementById('app');
  container.innerHTML = VIEWS[app.view].render(app);
  document.querySelectorAll('#main-nav button').forEach(b => {{
    const active = b.id === 'nav-' + app.view;
    b.className = active
      ? 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition bg-blue-600 text-white shadow-md'
      : 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800';
  }});
  renderHints();
}}

render();
setInterval(() => {{ hintIndex++; renderHints(); }}, 8000);

// respect URL params / hash for demo links
(() => {{
  const raw = location.search || location.hash.replace(/^#/, '?');
  const params = new URLSearchParams(raw);
  if (params.get('dark') === '1' && !app.darkMode) toggleDark();
  const v = params.get('view');
  if (v && VIEWS[v]) {{ app.view = v; }}
  const courses = params.get('courses');
  if (courses) {{ courses.split(',').forEach(id => {{ if (!app.selectedIds.includes(id.trim())) app.selectedIds.push(id.trim()); }}); }}
  render();
  if (params.get('generate') === '1' && app.view === 'builder') generateSchedules();
}})();
</script>
</body>
</html>'''

def icon_svg(name):
    # minimal inline icon map for nav; full map lives in helpers.js runtime
    paths = {
        'academic': 'M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.499 5.221 69.073 69.073 0 00-2.658.814m-15.482 0A50.55 50.55 0 0112 13.489a50.55 50.55 0 0112-2.82',
        'calendar': 'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5',
        'bookmark': 'M17.593 3.322c1.1.128 1.907 1.077 1.907 2.185V21L12 17.25 4.5 21V5.507c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 0111.186 0z',
        'user': 'M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z',
        'chart': 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z',
        'beaker': 'M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21a48.25 48.25 0 01-8.135-.687c-1.718-.293-2.3-2.379-1.067-3.61L5 14.5',
        'bolt': 'M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z',
        'shield': 'M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z',
        'fire': 'M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z',
        'heart': 'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z',
        'star': 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
        'clock': 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z',
        'bell': 'M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0',
        'mapPin': 'M15 10.5a3 3 0 11-6 0 3 3 0 016 0zM19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z',
        'chat': 'M2.25 12.76c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.449-4.449a.75.75 0 01.53-.217H20a3 3 0 003-3v-7.5a3 3 0 00-3-3H6a3 3 0 00-3 3v9.26z',
        'cog': 'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281zM15 12a3 3 0 11-6 0 3 3 0 016 0z',
        'document': 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
        'currency': 'M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
        'search': 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
        'sparkles': 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z',
        'moon': 'M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z',
        'sun': 'M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z'
    }
    p = paths.get(name, '')
    return f"<svg class='w-5 h-5' fill='none' viewBox='0 0 24 24' stroke-width='1.5' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' d='{p}'/></svg>"

def view_func_name(v):
    # view files define functions like renderCatalog, renderBuilder, renderWillItFill, renderChatbot
    specials = {'willitfill': 'renderWillItFill', 'chatbot': 'renderChatbot', 'agentchat': 'renderAgentChat'}
    if v in specials:
        return specials[v]
    return 'render' + v[0].upper() + v[1:]

def main():
    data_json = load(os.path.join(GEN, 'data.json'))
    helpers_js = load(os.path.join(GEN, 'helpers.js'))
    for phase, views in PHASES.items():
        out_dir = os.path.join(ROOT, f'phase{phase}')
        os.makedirs(out_dir, exist_ok=True)
        html = make_html(phase, views, data_json, helpers_js)
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'Generated phase{phase}/index.html')

if __name__ == '__main__':
    main()
