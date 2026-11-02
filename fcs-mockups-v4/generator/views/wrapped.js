function renderWrapped(state) {
  const selected = DATA.courses.filter(c => state.selectedIds.includes(c.id));
  const totalCredits = selected.reduce((a, c) => a + c.credits, 0);
  const avgRating = selected.length ? (selected.reduce((a, c) => a + (c.sections.reduce((s, sec) => s + sec.rating, 0) / c.sections.length), 0) / selected.length).toFixed(1) : '—';
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Semester Wrapped</h2>
      <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden">
        <div class="absolute -right-10 -top-10 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
        <div class="relative z-10 flex flex-col md:flex-row items-center gap-8">
          <div class="w-28 h-28 rounded-full bg-white/20 flex items-center justify-center text-4xl font-bold border-4 border-white/30">${totalCredits || 0}</div>
          <div>
            <div class="text-3xl font-bold">Your Semester at a Glance</div>
            <p class="text-blue-100 mt-1">${selected.length} courses · ${totalCredits} credits · avg rating ${avgRating}</p>
          </div>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-emerald-600">${selected.length ? selected.filter(c => c.dept === 'CS').length : 0}</div><div class="text-sm text-slate-500">CS courses</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-amber-600">${state.saved.length}</div><div class="text-sm text-slate-500">Saved drafts</div></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 text-center"><div class="text-3xl font-bold text-blue-600">${state.feedVotes ? Object.keys(state.feedVotes).length : 0}</div><div class="text-sm text-slate-500">Votes cast</div></div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 flex items-center justify-between">
        <div><h3 class="font-semibold">Shareable Card</h3><p class="text-sm text-slate-500">Generate an image-worthy summary.</p></div>
        <button onclick="toast('Share card copied to clipboard','success')" class="px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 font-medium inline-flex items-center gap-1">${icon('document','w-4 h-4')} Copy</button>
      </div>
    </div>`;
}
