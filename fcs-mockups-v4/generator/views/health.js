function renderHealth(state) {
  const schedule = state.builder.generated[state.builder.currentIdx];
  const components = schedule ? [
    {name:'No time conflicts', score: 100, weight: 25},
    {name:'Compact commute', score: schedule.metrics.compactness, weight: 15},
    {name:'Workload balance', score: Math.max(0, Math.round(100 - schedule.sections.length * 8)), weight: 20},
    {name:'Instructor quality', score: Math.round(schedule.sections.reduce((a, s) => a + s.rating, 0) / schedule.sections.length * 20), weight: 20},
    {name:'Seat urgency', score: Math.round(schedule.sections.reduce((a, s) => a + (s.seats / s.capacity * 100), 0) / schedule.sections.length), weight: 20},
  ] : [];
  const total = components.length ? Math.round(components.reduce((a, c) => a + c.score * (c.weight / 100), 0)) : 0;
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Schedule Health Score</h2>
      ${schedule ? `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div class="md:col-span-1 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 flex flex-col items-center justify-center">
            ${gauge(total, 'Health', {r:56})}
            <div class="mt-3 text-sm font-medium ${total>=80?'text-emerald-600':total>=60?'text-amber-600':'text-rose-600'}">${total>=80?'Excellent':total>=60?'Good':'Needs work'}</div>
          </div>
          <div class="md:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-4">Score Breakdown</h3>
            <div class="space-y-4">${components.map(c => `<div><div class="flex justify-between text-sm mb-1"><span>${c.name}</span><span class="font-semibold">${c.score}/100</span></div><div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2.5"><div class="h-2.5 rounded-full ${c.score>=80?'bg-emerald-500':c.score>=60?'bg-amber-500':'bg-rose-500'}" style="width:${c.score}%"></div></div><div class="text-xs text-slate-400 mt-1">Weight ${c.weight}%</div></div>`).join('')}</div>
          </div>
        </div>
      ` : `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-10 text-center text-slate-500">Generate a schedule in the Builder to see health analysis.</div>`}
    </div>`;
}
