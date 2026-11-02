function renderStress(state) {
  const schedule = state.builder.generated[state.builder.currentIdx];
  const flags = [];
  if (schedule) {
    const days = new Set(schedule.sections.flatMap(s => parseDays(s.days)));
    if (days.size === 5) flags.push({level:'warn', title:'No free weekday', desc:'Back-to-back classes every day can lead to burnout.'});
    if (schedule.sections.some(s => s.start < 8.5)) flags.push({level:'warn', title:'Early mornings', desc:'Classes before 8:30 AM hurt sleep consistency.'});
    const totalHours = schedule.sections.reduce((a, s) => a + s.duration * parseDays(s.days).length, 0);
    if (totalHours > 20) flags.push({level:'bad', title:'Heavy load', desc:`${Math.round(totalHours)} hours of class per week plus study time.`});
    if (schedule.sections.length > 5) flags.push({level:'warn', title:'Context switching', desc:'Many distinct courses fragment focus.'});
    if (!flags.length) flags.push({level:'good', title:'Low stress', desc:'Schedule has breathing room and balanced timing.'});
  }
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Schedule Stress Test</h2>
      ${schedule ? `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          ${flags.map(f => `<div class="flex gap-4 p-5 rounded-2xl border ${f.level==='good'?'border-emerald-200 bg-emerald-50/50 dark:bg-emerald-900/10':f.level==='warn'?'border-amber-200 bg-amber-50/50 dark:bg-amber-900/10':'border-rose-200 bg-rose-50/50 dark:bg-rose-900/10'}">
            <div class="mt-1">${icon(f.level==='good'?'check':f.level==='warn'?'information':'fire','w-6 h-6')}</div>
            <div><h3 class="font-semibold ${f.level==='good'?'text-emerald-700 dark:text-emerald-300':f.level==='warn'?'text-amber-700 dark:text-amber-300':'text-rose-700 dark:text-rose-300'}">${f.title}</h3><p class="text-sm text-slate-600 dark:text-slate-300 mt-1">${f.desc}</p></div>
          </div>`).join('')}
        </div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-4">Weekly Energy Forecast</h3>
          <div class="flex items-end gap-2 h-40">${['M','T','W','R','F'].map(d => {
             const hours = schedule.sections.filter(s => parseDays(s.days).includes(d)).reduce((a, s) => a + s.duration, 0);
             return `<div class="flex-1 flex flex-col items-center gap-2"><div class="w-full rounded-t-xl ${hours>5?'bg-rose-400':hours>3?'bg-amber-400':'bg-emerald-400'} transition-all" style="height:${Math.min(100, hours * 16)}%"></div><span class="text-xs text-slate-500">${d}</span><span class="text-xs font-semibold">${Math.round(hours)}h</span></div>`;
          }).join('')}</div>
        </div>
      ` : `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-10 text-center text-slate-500">Generate a schedule first.</div>`}
    </div>`;
}
