function renderSubstitute(state) {
  const query = state.substitutionQuery || 'humanities elective';
  const results = DATA.courses.filter(c => c.tags.some(t => t.toLowerCase().includes('elective') || query.toLowerCase().includes(c.dept.toLowerCase()) || c.title.toLowerCase().includes(query.toLowerCase()))).slice(0, 5);
  return `
    <div class="space-y-6 animate-fadeIn max-w-3xl mx-auto">
      <h2 class="text-2xl font-bold tracking-tight">Substitution Finder</h2>
      <div class="flex gap-2">
        <input type="text" value="${query}" oninput="app.substitutionQuery=this.value; render();" placeholder="I need a humanities elective..." class="flex-1 px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none focus:ring-2 focus:ring-blue-500">
        <button onclick="render();" class="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold">${icon('search','w-5 h-5')}</button>
      </div>
      <div class="space-y-3">
        ${results.map((c,i) => `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 flex items-center justify-between">
          <div><h3 class="font-bold">${c.code}</h3><p class="text-sm text-slate-500">${c.title}</p></div>
          <div class="text-right"><div class="text-lg font-bold text-blue-600">${90 - i*8}%</div><div class="text-xs text-slate-500">match</div></div>
        </div>`).join('')}
      </div>
    </div>`;
}
