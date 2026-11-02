function renderWaitlist(state) {
  const sections = DATA.courses.flatMap(c => c.sections.map(s => ({...s, courseCode: c.code}))).slice(0, 5);
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Waitlist Strategy</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        ${sections.map(s => {
           const fill = Math.round((s.seats / s.capacity) * 100);
           const odds = fill < 20 ? 'High' : fill < 60 ? 'Medium' : 'Low';
           const safe = DATA.courses.find(c => c.id !== s.id.split('-')[0])?.code || 'TBD';
           return `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
             <div class="flex justify-between items-start"><div><h3 class="font-bold">${s.courseCode} ${s.id.split('-').pop()}</h3><p class="text-xs text-slate-500">${formatTime(s.start)} ${s.days}</p></div><span class="px-2 py-1 rounded-full text-xs font-bold ${odds==='High'?'bg-emerald-100 text-emerald-700':odds==='Medium'?'bg-amber-100 text-amber-700':'bg-rose-100 text-rose-700'}">${odds} odds</span></div>
             <div class="mt-3"><div class="flex justify-between text-xs text-slate-500 mb-1"><span>Capacity</span><span>${s.seats}/${s.capacity}</span></div><div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2"><div class="bg-blue-500 h-2 rounded-full" style="width:${fill}%"></div></div></div>
             <div class="mt-4 flex items-center justify-between">
               <div class="text-sm text-slate-500">Safe alt: <span class="font-semibold text-slate-700 dark:text-slate-300">${safe}</span></div>
               <label class="inline-flex items-center gap-2 text-sm"><input type="checkbox" onchange="toast(this.checked?'Auto-swap enabled':'Auto-swap disabled','info')" class="rounded accent-blue-600"> Auto-swap</label>
             </div>
           </div>`;
        }).join('')}
      </div>
    </div>`;
}
