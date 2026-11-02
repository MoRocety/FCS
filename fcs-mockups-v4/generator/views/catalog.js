function renderCatalog(state) {
  const depts = ['All', ...new Set(DATA.courses.map(c => c.dept))];
  const filtered = DATA.courses.filter(c => {
    const q = state.catalog.search.toLowerCase();
    const matches = c.title.toLowerCase().includes(q) || c.code.toLowerCase().includes(q) || c.dept.toLowerCase().includes(q);
    return matches && (state.catalog.dept === 'All' || c.dept === state.catalog.dept) && c.credits >= state.catalog.minCredits && c.credits <= state.catalog.maxCredits;
  });
  const pageSize = 6;
  const page = state.catalog.page;
  const total = filtered.length;
  const pages = Math.ceil(total / pageSize) || 1;
  const pageCourses = filtered.slice((page - 1) * pageSize, page * pageSize);
  const rows = pageCourses.map(c => {
    const instNames = [...new Set(c.sections.map(s => instructorName(s.instructor)))].join(', ');
    const avgRating = (c.sections.reduce((a, s) => a + s.rating, 0) / c.sections.length).toFixed(1);
    const selected = state.selectedIds.includes(c.id);
    return `<tr class="border-b border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition cursor-pointer ${selected ? 'bg-blue-50 dark:bg-blue-900/20' : ''}" onclick="toggleCourse('${c.id}')">
      <td class="px-4 py-3"><div class="font-semibold text-slate-900 dark:text-white">${c.code}</div><div class="text-xs text-slate-500">${c.title}</div></td>
      <td class="px-4 py-3 text-sm">${instNames}</td>
      <td class="px-4 py-3 text-sm">${c.sections.map(s => `${dayNameShort(s.days)} ${formatTime(s.start)}-${formatTime(s.start + s.duration)}`).join('<br>')}</td>
      <td class="px-4 py-3 text-center"><span class="px-2 py-1 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-700">${c.credits}</span></td>
      <td class="px-4 py-3 text-center text-sm">${c.sections.map(s => `${s.seats}/${s.capacity}`).join('<br>')}</td>
      <td class="px-4 py-3 text-center"><span class="inline-flex items-center gap-1 text-amber-600 font-semibold text-sm">${icon('star','w-4 h-4')} ${avgRating}</span></td>
    </tr>`;
  }).join('');
  return `
    <div class="space-y-6 animate-fadeIn">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div><h2 class="text-2xl font-bold tracking-tight">Course Catalog</h2><p class="text-slate-500 text-sm">Click a row to add it to your schedule.</p></div>
        <div class="text-sm text-slate-500">${state.selectedIds.length} selected · ${DATA.courses.length} total</div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-4 space-y-4">
        <div class="relative"><span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">${icon('search','w-5 h-5')}</span>
          <input type="text" value="${state.catalog.search}" oninput="app.catalog.search=this.value; app.catalog.page=1; render();" placeholder="Search courses, codes, departments..." class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none"></div>
        <div class="flex flex-wrap gap-2">${depts.map(d => `<button onclick="app.catalog.dept='${d}'; app.catalog.page=1; render();" class="px-3 py-1.5 rounded-full text-sm font-medium transition ${state.catalog.dept===d ? 'bg-blue-600 text-white shadow-md' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'}">${d}</button>`).join('')}</div>
        <div class="flex flex-wrap gap-4 items-center text-sm">
          <label class="text-slate-500">Credits</label>
          <input type="number" min="0" max="12" value="${state.catalog.minCredits}" onchange="app.catalog.minCredits=+this.value; app.catalog.page=1; render();" class="w-16 px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-transparent">
          <span class="text-slate-400">–</span>
          <input type="number" min="0" max="12" value="${state.catalog.maxCredits}" onchange="app.catalog.maxCredits=+this.value; app.catalog.page=1; render();" class="w-16 px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-transparent">
        </div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <table class="w-full text-left"><thead class="bg-slate-50 dark:bg-slate-900/50 text-xs uppercase tracking-wider text-slate-500"><tr><th class="px-4 py-3">Course</th><th class="px-4 py-3">Instructor</th><th class="px-4 py-3">Schedule</th><th class="px-4 py-3 text-center">Credits</th><th class="px-4 py-3 text-center">Seats</th><th class="px-4 py-3 text-center">Rating</th></tr></thead><tbody>${rows || `<tr><td colspan="6" class="px-4 py-8 text-center text-slate-500">No courses match.</td></tr>`}</tbody></table>
        <div class="flex items-center justify-between px-4 py-3 border-t border-slate-100 dark:border-slate-700 text-sm">
          <span class="text-slate-500">Page ${page} of ${pages}</span>
          <div class="flex gap-2"><button onclick="if(app.catalog.page>1){app.catalog.page--; render();}" class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50" ${page===1?'disabled':''}>Prev</button><button onclick="if(app.catalog.page<${pages}){app.catalog.page++; render();}" class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50" ${page===pages?'disabled':''}>Next</button></div>
        </div>
      </div>
    </div>`;
}
