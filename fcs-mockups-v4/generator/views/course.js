function renderCourse(state) {
  if (!state.activeCourse) {
    return `
      <div class="space-y-6 animate-fadeIn">
        <h2 class="text-2xl font-bold tracking-tight">Course Detail</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          ${DATA.courses.map(c => `
            <div onclick="app.activeCourse='${c.id}'; render();" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 cursor-pointer hover:shadow-md transition">
              <div class="flex justify-between items-start"><div><h3 class="font-bold">${c.code}</h3><p class="text-sm text-slate-500 line-clamp-1">${c.title}</p></div><span class="px-2 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-700">${c.credits} cr</span></div>
              <p class="mt-3 text-sm text-slate-600 dark:text-slate-300 line-clamp-2">${c.description}</p>
            </div>`).join('')}
        </div>
      </div>`;
  }
  const c = DATA.courses.find(x => x.id === state.activeCourse);
  const diff = c.difficultyTrend;
  const work = c.workloadTrend;
  return `
    <div class="space-y-6 animate-fadeIn">
      <button onclick="app.activeCourse=null; render();" class="text-sm text-blue-600 hover:underline">← Back to courses</button>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div><h2 class="text-2xl font-bold">${c.code}: ${c.title}</h2><p class="text-slate-500">${c.dept} · ${c.credits} credits</p></div>
          <div class="flex gap-2">${c.tags.map(t => `<span class="px-3 py-1 rounded-full text-xs font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">${t}</span>`).join('')}</div>
        </div>
        <p class="mt-4 text-slate-700 dark:text-slate-300">${c.description}</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-3">Grade Distribution</h3>${barChart(c.gradeDistribution, ['A','B','C','D','F'], {colors:['#2563eb','#3b82f6','#60a5fa','#93c5fd','#cbd5e1']})}</div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-3">Difficulty Trend</h3>
          <div class="h-32 flex items-end gap-2 relative">${diff.map((v,i) => `<div class="flex-1 rounded-t-md bg-amber-500/80 relative group" style="height:${(v/5)*100}%"><span class="absolute -top-5 left-1/2 -translate-x-1/2 text-xs opacity-0 group-hover:opacity-100 transition">${v}</span></div>`).join('')}<div class="absolute bottom-0 left-0 w-full h-px bg-slate-200 dark:bg-slate-700"></div></div>
          <div class="flex justify-between text-xs text-slate-500 mt-2">${['2021','2022','2023','2024'].map(y => `<span>${y}</span>`).join('')}</div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-rose-600">${c.retakeRate}%</div><div class="text-sm text-slate-500">Retake Rate</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-slate-900 dark:text-white">${c.prereqs.length ? c.prereqs.join(' → ') : 'None'}</div><div class="text-sm text-slate-500">Prerequisite Chain</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-emerald-600">${work[work.length-1]}h</div><div class="text-sm text-slate-500">Weekly Workload</div></div>
      </div>
    </div>`;
}
