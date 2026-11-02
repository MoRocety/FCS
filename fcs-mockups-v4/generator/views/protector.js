function renderProtector(state) {
  const days = ['M','T','W','R','F'];
  const slots = [];
  for (let h = 8; h < 18; h += 0.5) slots.push(h);
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Time Protector</h2>
      <p class="text-slate-500 text-sm">Click cells to block personal time. Conflicts with generated schedules are flagged.</p>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 overflow-x-auto">
        <div class="min-w-[600px]">
          <div class="grid grid-cols-6 gap-1 mb-1"><div class="text-xs text-slate-400 text-center">Time</div>${days.map(d => `<div class="text-xs font-semibold text-center py-1">${dayName(d)}</div>`).join('')}</div>
          ${slots.map(h => `<div class="grid grid-cols-6 gap-1"><div class="text-xs text-slate-400 text-right pr-2 py-2">${formatTime(h)}</div>${days.map(d => {
             const prot = state.protected.find(p => p.day === d && Math.abs(p.start - h) < 0.25);
             const conflict = state.builder.generated[state.builder.currentIdx]?.sections.some(s => parseDays(s.days).includes(d) && s.start <= h && s.start + s.duration > h);
             return `<button onclick="toggleProtected('${d}',${h})" class="h-8 rounded-md text-xs transition ${prot?'bg-rose-400 text-white':'bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-700'} ${conflict && !prot?'ring-1 ring-amber-400':''}">${prot?'Busy':''}</button>`;
          }).join('')}</div>`).join('')}
        </div>
      </div>
    </div>`;
}
