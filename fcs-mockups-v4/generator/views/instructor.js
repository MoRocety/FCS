function renderInstructor(state) {
  if (!state.activeInstructor) {
    return `
      <div class="space-y-6 animate-fadeIn">
        <h2 class="text-2xl font-bold tracking-tight">Instructor Profiles</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          ${DATA.instructors.map(inst => `
            <div onclick="app.activeInstructor='${inst.id}'; render();" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 cursor-pointer hover:border-blue-400 transition group">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xl font-bold shadow-md">${inst.name.split(' ').pop()[0]}</div>
                <div><h3 class="font-bold">${inst.name}</h3><p class="text-sm text-slate-500">${inst.dept} · Effectiveness ${inst.effectiveness}</p></div>
              </div>
              <div class="mt-4 flex flex-wrap gap-2">${inst.style.map(t => `<span class="px-2 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-700">${t}</span>`).join('')}</div>
            </div>`).join('')}
        </div>
      </div>`;
  }
  const inst = DATA.instructors.find(i => i.id === state.activeInstructor);
  const dist = inst.gradeDistribution;
  return `
    <div class="space-y-6 animate-fadeIn">
      <button onclick="app.activeInstructor=null; render();" class="text-sm text-blue-600 hover:underline">← Back to instructors</button>
      <div class="flex flex-col md:flex-row gap-6">
        <div class="md:w-1/3 space-y-4">
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 text-center">
            <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">${inst.name.split(' ').pop()[0]}</div>
            <h2 class="mt-4 text-xl font-bold">${inst.name}</h2>
            <p class="text-slate-500 text-sm">${inst.dept}</p>
            <div class="mt-4">${gauge(inst.effectiveness, 'Effectiveness', {r:42})}</div>
            <div class="mt-4 grid grid-cols-3 gap-2 text-sm">
              <div><div class="font-bold text-blue-600">${inst.quality}</div><div class="text-xs text-slate-500">Quality</div></div>
              <div><div class="font-bold text-amber-600">${inst.difficulty}</div><div class="text-xs text-slate-500">Difficulty</div></div>
              <div><div class="font-bold text-emerald-600">${inst.passRate}%</div><div class="text-xs text-slate-500">Pass</div></div>
            </div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-2">Office Hours</h3><p class="text-sm text-slate-600 dark:text-slate-300">${inst.officeHours}</p>
            <h3 class="font-semibold mt-4 mb-2">Teaching Style</h3><div class="flex flex-wrap gap-2">${inst.style.map(t => `<span class="px-2 py-1 rounded-md text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">${t}</span>`).join('')}</div>
          </div>
        </div>
        <div class="md:w-2/3 space-y-4">
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-4">Grade Distribution</h3>
            ${barChart(dist, ['A','B','C','D','F'], {colors:['#2563eb','#3b82f6','#60a5fa','#93c5fd','#cbd5e1']})}
            <div class="mt-2 text-xs text-slate-500 text-center">Average grade: ${inst.avgGrade}</div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3">Course History</h3>
            <div class="flex flex-wrap gap-2">${inst.courseHistory.map(c => `<span class="px-3 py-1 rounded-full text-sm bg-slate-100 dark:bg-slate-700">${c}</span>`).join('')}</div>
          </div>
          <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
            <h3 class="font-semibold mb-3">Student Reviews</h3>
            <div class="space-y-3">${inst.reviews.map(r => `<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900"><div class="flex items-center gap-1 text-amber-500 mb-1">${[...Array(5)].map((_,i)=>`<span class="${i<r.rating?'':'text-slate-300 dark:text-slate-600'}">★</span>`).join('')} <span class="text-xs text-slate-400 ml-2">${r.author}</span></div><p class="text-sm text-slate-700 dark:text-slate-300">"${r.text}"</p></div>`).join('')}</div>
          </div>
        </div>
      </div>
    </div>`;
}
