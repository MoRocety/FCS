function renderProactive(state) {
  const hints = [
    {type:'urgent', text:'Registration opens in 3 days. Finalize backup schedules.'},
    {type:'info', text:'CHEM201-A added 12 seats.'},
    {type:'tip', text:'You prefer project-based courses — 3 matching electives found.'},
    {type:'warn', text:'Your planned load (19 cr) exceeds your stated cap (18 cr).'}
  ];
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Proactive Suggestions</h2>
      <div class="grid gap-4">
        ${hints.map(h => `<div class="flex items-start gap-4 p-5 rounded-2xl border ${h.type==='urgent'?'border-rose-200 bg-rose-50 dark:bg-rose-900/10':h.type==='warn'?'border-amber-200 bg-amber-50 dark:bg-amber-900/10':h.type==='tip'?'border-emerald-200 bg-emerald-50 dark:bg-emerald-900/10':'border-blue-200 bg-blue-50 dark:bg-blue-900/10'}">
          <div class="mt-0.5">${icon(h.type==='urgent'?'fire':h.type==='warn'?'information':h.type==='tip'?'sparkles':'bell','w-6 h-6')}</div>
          <div><p class="font-medium text-slate-900 dark:text-white">${h.text}</p><p class="text-sm text-slate-500 mt-1">${h.type==='urgent'?'Action recommended':'Contextual hint'}</p></div>
        </div>`).join('')}
      </div>
    </div>`;
}
