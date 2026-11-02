function renderCareer(state) {
  const paths = DATA.career;
  const current = paths[state.career] || paths.industry;
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">AI Career Path Advisor</h2>
      <div class="flex gap-2 mb-4">
        ${Object.keys(paths).map(k => `<button onclick="app.career='${k}'; render();" class="px-4 py-2 rounded-xl text-sm font-semibold ${state.career===k?'bg-blue-600 text-white':'bg-slate-100 dark:bg-slate-700'}">${k==='med'?'Med School':k==='industry'?'Industry':'Grad School'}</button>`).join('')}
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-8 overflow-x-auto">
        <div class="min-w-[600px] flex items-center justify-between relative">
          <div class="absolute top-1/2 left-0 right-0 h-1 bg-slate-100 dark:bg-slate-700 -translate-y-1/2 z-0"></div>
          ${current.map((step,i) => `<div class="relative z-10 flex flex-col items-center gap-3 w-32">
            <div class="w-12 h-12 rounded-full ${i<=1?'bg-blue-600 text-white':'bg-slate-100 dark:bg-slate-700 text-slate-500'} flex items-center justify-center font-bold shadow-md">${i+1}</div>
            <div class="text-center text-sm font-medium">${step}</div>
          </div>`).join('')}
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5"><h3 class="font-semibold mb-2">Recommended Courses</h3><ul class="list-disc list-inside text-sm text-slate-600 dark:text-slate-300"><li>CS 301 Algorithms</li><li>MATH 250 Linear Algebra</li><li>${state.career==='med'?'CHEM 201':'CS 401 Capstone'}</li></ul></div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5"><h3 class="font-semibold mb-2">Skill Gap</h3><div class="space-y-2">${['Statistics','Public Speaking','Research Methods'].map(s => `<div class="flex justify-between text-sm"><span>${s}</span><span class="text-amber-600">Medium</span></div>`).join('')}</div></div>
      </div>
    </div>`;
}
