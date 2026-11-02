function renderMemory(state) {
  return `
    <div class="space-y-6 animate-fadeIn max-w-3xl mx-auto">
      <h2 class="text-2xl font-bold tracking-tight">Agent Memory</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-5">
        ${Object.entries(state.memory).map(([k,v]) => {
           const label = k.charAt(0).toUpperCase() + k.slice(1);
           const val = Array.isArray(v) ? v.join(', ') : v;
           return `<div><label class="text-sm font-medium text-slate-500 uppercase tracking-wide">${label}</label><input type="text" value="${val}" onchange="app.memory['${k}']=this.value.split(',').map(s=>s.trim()); render();" class="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent"></div>`;
        }).join('')}
        <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-sm text-blue-800 dark:text-blue-200">The agent uses this context to personalize suggestions, warnings, and career advice.</div>
      </div>
    </div>`;
}
