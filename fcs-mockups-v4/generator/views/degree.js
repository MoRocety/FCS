function renderDegree(state) {
  const required = ['cs101','cs201','cs301','math201','math250','phys101'];
  const completed = state.history.map(h => h.courseId);
  const inProgress = state.selectedIds;
  const statuses = required.map(id => {
    const c = DATA.courses.find(x => x.id === id);
    let status = 'remaining';
    if (completed.includes(id)) status = 'completed';
    else if (inProgress.includes(id)) status = 'inprogress';
    return {id, code: c.code, status};
  });
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Degree Progress</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-emerald-600">${statuses.filter(s => s.status === 'completed').length}</div><div class="text-sm text-slate-500">Completed</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-blue-600">${statuses.filter(s => s.status === 'inprogress').length}</div><div class="text-sm text-slate-500">In Progress</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-slate-400">${statuses.filter(s => s.status === 'remaining').length}</div><div class="text-sm text-slate-500">Remaining</div></div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
        <h3 class="font-semibold mb-4">Prerequisite Chain</h3>
        <div class="flex flex-wrap items-center gap-2">${statuses.map((s,i) => `<div class="flex items-center gap-2"><span class="px-3 py-1.5 rounded-lg text-sm font-medium ${s.status==='completed'?'bg-emerald-100 text-emerald-700':s.status==='inprogress'?'bg-blue-100 text-blue-700':'bg-slate-100 text-slate-600'}">${s.code}</span>${i<statuses.length-1?'<span class="text-slate-400">→</span>':''}</div>`).join('')}</div>
        <div class="mt-4 text-sm text-slate-500">Estimated graduation: <span class="font-semibold text-slate-700 dark:text-slate-300">${new Date().getFullYear()+2}</span></div>
      </div>
    </div>`;
}
