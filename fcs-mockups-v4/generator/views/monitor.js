function renderMonitor(state) {
  const allSections = DATA.courses.flatMap(c => c.sections.map(s => ({...s, courseCode: c.code})));
  const watched = state.monitor.map(id => allSections.find(s => s.id === id)).filter(Boolean);
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Seat Monitor Dashboard</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
        <div class="flex gap-2">
          <select id="watchSelect" class="flex-1 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${allSections.map(s => `<option value="${s.id}">${s.courseCode} ${s.id.split('-').pop()}</option>`).join('')}</select>
          <button onclick="addMonitor(document.getElementById('watchSelect').value)" class="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold">${icon('plus','w-5 h-5')}</button>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        ${watched.length ? watched.map(s => {
           const fill = Math.round((s.seats / s.capacity) * 100);
           return `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
             <div class="flex justify-between items-center"><h3 class="font-bold">${s.courseCode} ${s.id.split('-').pop()}</h3><button onclick="removeMonitor('${s.id}')" class="text-slate-400 hover:text-rose-500">${icon('trash','w-4 h-4')}</button></div>
             <div class="mt-4 flex items-end gap-2 h-24">${[...Array(7)].map((_,i) => `<div class="flex-1 rounded-t-md ${fill>80?'bg-rose-400':fill>50?'bg-amber-400':'bg-emerald-400'}" style="height:${Math.max(10, Math.min(100, 30 + (Math.sin(i+s.id.length)*20+20)))}%"></div>`).join('')}</div>
             <div class="mt-3 flex justify-between items-center"><span class="text-2xl font-bold">${s.seats}</span><span class="text-sm ${fill>80?'text-rose-600':fill>50?'text-amber-600':'text-emerald-600'}">${fill}% full</span></div>
           </div>`;
        }).join('') : '<div class="col-span-full text-center py-10 text-slate-500">No sections monitored.</div>'}
      </div>
    </div>`;
}
