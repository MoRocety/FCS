function renderWillItFill(state) {
  const sections = DATA.courses.flatMap(c => c.sections.map(s => ({...s, courseCode: c.code, courseTitle: c.title})));
  const activeId = state.activeSection || sections[0].id;
  const sec = sections.find(s => s.id === activeId);
  const velocity = [Math.max(0, sec.seats - 5), Math.max(0, sec.seats - 2), sec.seats, Math.min(sec.capacity, sec.seats + 4), Math.min(sec.capacity, sec.seats + 7)];
  const fillChance = Math.round((sec.seats / sec.capacity) * 100);
  const trend = velocity[velocity.length - 1] > velocity[0] ? 'up' : 'down';
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Will It Fill?</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
        <label class="text-sm font-medium">Select a section</label>
        <select onchange="app.activeSection=this.value; render();" class="mt-2 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">
          ${sections.map(s => `<option value="${s.id}" ${s.id===activeId?'selected':''}>${s.courseCode} ${s.id.split('-').pop()} · ${formatTime(s.start)} ${s.days}</option>`).join('')}
        </select>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="md:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-3">Seat Velocity (last 5 checks)</h3>
          ${barChart(velocity, ['-48h','-24h','Now','+24h','+48h'], {colors: velocity.map(v => v >= sec.capacity ? '#ef4444' : '#2563eb')})}
        </div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 flex flex-col items-center justify-center text-center">
          ${gauge(fillChance, 'Fill Chance', {r:44})}
          <div class="mt-3 text-sm text-slate-500">Trend: <span class="font-semibold ${trend==='up'?'text-rose-600':'text-emerald-600'}">${trend==='up'?'Rising ↗':'Steady ↘'}</span></div>
          <div class="mt-2 text-xs text-slate-400">Confidence interval: ±${Math.round(100 - fillChance / 2)}%</div>
        </div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
        <h3 class="font-semibold mb-3">Historical Fill Data</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="font-bold">72h</div><div class="text-xs text-slate-500">avg fill time</div></div>
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="font-bold">${sec.capacity}</div><div class="text-xs text-slate-500">capacity</div></div>
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="font-bold">${sec.seats}</div><div class="text-xs text-slate-500">open seats</div></div>
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="font-bold">${Math.max(0, sec.capacity - sec.seats)}</div><div class="text-xs text-slate-500">filled</div></div>
        </div>
      </div>
    </div>`;
}
