function renderTextbooks(state) {
  const selected = DATA.courses.filter(c => state.selectedIds.includes(c.id));
  const total = selected.reduce((a, c) => a + c.textbook, 0);
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Textbook Cost Calculator</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-3">Selected Courses</h3>
          <div class="space-y-2">${selected.length ? selected.map(c => `<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-700 last:border-0"><span>${c.code}</span><span class="font-semibold">$${c.textbook}</span></div>`).join('') : '<div class="text-sm text-slate-500">No courses selected.</div>'}</div>
          <div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 flex justify-between text-lg font-bold"><span>Total</span><span class="text-emerald-600">$${total}</span></div>
        </div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
          <h3 class="font-semibold mb-3">Money-Saving Tips</h3>
          <ul class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
            <li class="flex gap-2">${icon('check','w-4 h-4 text-emerald-500')} Buy used / rent to save ~40%</li>
            <li class="flex gap-2">${icon('check','w-4 h-4 text-emerald-500')} Check library reserve copies</li>
            <li class="flex gap-2">${icon('check','w-4 h-4 text-emerald-500')} Look for open-access editions</li>
          </ul>
        </div>
      </div>
    </div>`;
}
