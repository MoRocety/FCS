function renderSaved(state) {
  return `
    <div class="space-y-6 animate-fadeIn">
      <div class="flex items-center justify-between"><h2 class="text-2xl font-bold tracking-tight">Saved Schedules</h2><span class="text-sm text-slate-500">${state.saved.length} saved</span></div>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        ${state.saved.length ? state.saved.map((s,i) => {
           const m = computeMetrics(s.sections);
           return `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 hover:shadow-md transition group">
             <div class="flex items-start justify-between"><div><h3 class="font-bold text-lg">${s.name}</h3><p class="text-xs text-slate-500">${s.savedAt}</p></div><div class="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600">${icon('bookmark','w-5 h-5')}</div></div>
             <div class="mt-4 flex flex-wrap gap-2">${s.sections.map(sec => `<span class="px-2 py-1 rounded-md text-xs font-medium bg-slate-100 dark:bg-slate-700">${sectionCode(sec.id)}</span>`).join('')}</div>
             <div class="mt-4 grid grid-cols-3 gap-2 text-center">
               <div class="rounded-lg bg-slate-50 dark:bg-slate-900 p-2"><div class="text-xs text-slate-500">Credits</div><div class="font-bold">${m.credits}</div></div>
               <div class="rounded-lg bg-slate-50 dark:bg-slate-900 p-2"><div class="text-xs text-slate-500">Start</div><div class="font-bold">${m.avgStart}</div></div>
               <div class="rounded-lg bg-slate-50 dark:bg-slate-900 p-2"><div class="text-xs text-slate-500">Score</div><div class="font-bold ${m.score>=80?'text-emerald-600':m.score>=60?'text-amber-600':'text-rose-600'}">${m.score || '—'}</div></div>
             </div>
             <div class="mt-4 flex gap-2"><button onclick="loadSaved(${i})" class="flex-1 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold">Load</button><button onclick="deleteSaved(${i})" class="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-900/20">${icon('trash','w-4 h-4')}</button></div>
           </div>`;
        }).join('') : `<div class="col-span-full text-center py-16 bg-white dark:bg-slate-800 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700"><p class="text-slate-500">No saved schedules yet.</p></div>`}
      </div>
    </div>`;
}
