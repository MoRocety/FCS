function renderBuilder(state) {
  const selected = DATA.courses.filter(c => state.selectedIds.includes(c.id));
  const schedule = state.builder.generated[state.builder.currentIdx] || null;
  const stats = schedule ? schedule.metrics : {credits: 0, avgStart: '—', compactness: 0, rating: '—', score: 0};
  return `
    <div class="space-y-6 animate-fadeIn">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div><h2 class="text-2xl font-bold tracking-tight">Schedule Builder</h2><p class="text-slate-500 text-sm">Generate ranked combinations from your selections.</p></div>
        <button onclick="generateSchedules()" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold shadow-lg shadow-blue-600/20 transition transform hover:scale-105">${icon('bolt','w-5 h-5')} Generate</button>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-4 space-y-4">
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3 flex items-center gap-2">${icon('academic','w-5 h-5')} Selected Courses</h3>
            ${selected.length ? `<div class="space-y-2 max-h-64 overflow-auto pr-1">${selected.map(c => `<div class="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-700"><div><div class="font-medium text-sm">${c.code}</div><div class="text-xs text-slate-500 truncate max-w-[180px]">${c.title}</div></div><button onclick="toggleCourse('${c.id}')" class="text-slate-400 hover:text-rose-500">${icon('trash','w-4 h-4')}</button></div>`).join('')}</div>` : `<div class="text-sm text-slate-500 py-6 text-center">No courses selected. Go to Catalog.</div>`}
            <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 flex justify-between text-sm font-medium"><span>Total credits</span><span class="text-blue-600">${selected.reduce((a,c)=>a+c.credits,0)}</span></div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 space-y-5">
            <h3 class="font-semibold">Constraints</h3>
            <div><label class="text-xs text-slate-500 uppercase tracking-wide">Credit range</label>
              <div class="flex items-center gap-3 mt-2"><input type="range" min="3" max="21" value="${state.builder.minCredits}" oninput="app.builder.minCredits=Math.min(+this.value, app.builder.maxCredits); render();" class="w-full accent-blue-600"><span class="text-sm w-6">${state.builder.minCredits}</span><span class="text-slate-400">-</span><input type="range" min="3" max="21" value="${state.builder.maxCredits}" oninput="app.builder.maxCredits=Math.max(+this.value, app.builder.minCredits); render();" class="w-full accent-blue-600"><span class="text-sm w-6">${state.builder.maxCredits}</span></div></div>
            <div><label class="text-xs text-slate-500 uppercase tracking-wide">Exclude days</label>
              <div class="flex gap-2 mt-2">${['M','T','W','R','F'].map(d => `<button onclick="toggleDay('${d}')" class="w-9 h-9 rounded-lg font-semibold text-sm transition ${state.builder.excludedDays.includes(d) ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/30' : 'bg-slate-100 dark:bg-slate-700 hover:bg-slate-200'}">${d}</button>`).join('')}</div></div>
          </div>
        </div>
        <div class="lg:col-span-8 space-y-4">
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <div class="flex items-center justify-between mb-4">
              <h3 class="font-semibold">${schedule ? `Combo ${state.builder.currentIdx+1} of ${state.builder.generated.length}` : 'No schedule generated'}</h3>
              <div class="flex items-center gap-2">${schedule ? `<button onclick="prevCombo()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">${icon('chevronLeft','w-5 h-5')}</button><button onclick="nextCombo()" class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">${icon('chevronRight','w-5 h-5')}</button>` : ''}<button onclick="saveCurrentSchedule()" class="ml-2 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium inline-flex items-center gap-1">${icon('bookmark','w-4 h-4')} Save</button></div>
            </div>
            ${schedule ? renderTimetable(schedule.sections, {height:'380px'}) : `<div class="h-80 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center text-slate-400"><p>Generate to see timetable</p></div>`}
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="text-xs text-slate-500 uppercase">Credits</div><div class="text-xl font-bold text-slate-900 dark:text-white">${stats.credits}</div></div>
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="text-xs text-slate-500 uppercase">Avg start</div><div class="text-xl font-bold text-slate-900 dark:text-white">${stats.avgStart}</div></div>
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="text-xs text-slate-500 uppercase">Compactness</div><div class="text-xl font-bold text-slate-900 dark:text-white">${stats.compactness}%</div></div>
              <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-center"><div class="text-xs text-slate-500 uppercase">Rating</div><div class="text-xl font-bold text-slate-900 dark:text-white">${stats.rating}</div></div>
            </div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3">Ranked alternatives</h3>
            <div class="space-y-2 max-h-56 overflow-auto">${state.builder.generated.length ? state.builder.generated.map((s,i) => `<button onclick="app.builder.currentIdx=${i}; render();" class="w-full flex items-center justify-between p-3 rounded-xl border ${i===state.builder.currentIdx ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700'} transition"><div class="flex items-center gap-3"><span class="text-sm font-bold w-6">${i+1}</span><span class="text-sm text-slate-600 dark:text-slate-300">${s.sections.map(sec => sectionCode(sec.id)).join(' + ')}</span></div><span class="text-sm font-semibold ${s.score>=80?'text-emerald-600':s.score>=60?'text-amber-600':'text-rose-600'}">${s.score} pts</span></button>`).join('') : '<div class="text-sm text-slate-500 text-center py-4">No generated combos yet.</div>'}</div>
          </div>
        </div>
      </div>
    </div>`;
}
