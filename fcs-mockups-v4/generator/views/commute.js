function renderCommute(state) {
  const schedule = state.builder.generated[state.builder.currentIdx];
  const buildings = schedule ? [...new Set(schedule.sections.map(s => s.location.split(' ')[0]))] : [];
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Commute-Aware Planner</h2>
      ${schedule ? `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3">Buildings visited today</h3>
            <div class="space-y-2">${buildings.map(b => `<div class="flex items-center gap-2"><span class="w-2 h-2 rounded-full bg-blue-500"></span><span class="text-sm font-medium">${b}</span></div>`).join('')}</div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3">Walking Times</h3>
            <div class="space-y-2">${buildings.slice(0,-1).map((b,i) => `<div class="flex justify-between text-sm"><span>${b} → ${buildings[i+1]}</span><span class="font-semibold">${DATA.walkMatrix?.[b]?.[buildings[i+1]] || 5} min</span></div>`).join('')}</div>
          </div>
        </div>
      ` : `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-10 text-center text-slate-500">Generate a schedule to analyze commute.</div>`}
    </div>`;
}
