function renderCompare(state) {
  const [id1, id2] = state.compare;
  const a = DATA.instructors.find(i => i.id === id1), b = DATA.instructors.find(i => i.id === id2);
  function pred(inst) {
    const base = 3.0;
    const gpa = Math.min(4.0, Math.max(2.0, base + (inst.quality - 3) * 0.25 - (inst.difficulty - 3) * 0.15)).toFixed(2);
    const letter = gpa >= 3.7 ? 'A-' : gpa >= 3.3 ? 'B+' : gpa >= 3.0 ? 'B' : gpa >= 2.7 ? 'B-' : 'C+';
    return {gpa, letter};
  }
  const pa = pred(a), pb = pred(b);
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Instructor Comparison</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 flex flex-col md:flex-row gap-4">
        <select onchange="app.compare[0]=this.value; render();" class="flex-1 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${DATA.instructors.map(i => `<option value="${i.id}" ${i.id===id1?'selected':''}>${i.name}</option>`).join('')}</select>
        <select onchange="app.compare[1]=this.value; render();" class="flex-1 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${DATA.instructors.map(i => `<option value="${i.id}" ${i.id===id2?'selected':''}>${i.name}</option>`).join('')}</select>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        ${[a,b].map((inst, idx) => `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 ${idx===0?'border-l-4 border-l-blue-500':'border-l-4 border-l-indigo-500'}">
          <h3 class="text-xl font-bold">${inst.name}</h3>
          <p class="text-sm text-slate-500 mb-4">${inst.dept}</p>
          <div class="space-y-3">
            <div class="flex justify-between text-sm"><span>Effectiveness</span><span class="font-semibold">${inst.effectiveness}</span></div>
            <div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2"><div class="bg-blue-500 h-2 rounded-full" style="width:${inst.effectiveness}%"></div></div>
            <div class="flex justify-between text-sm"><span>Quality</span><span class="font-semibold">${inst.quality}</span></div>
            <div class="flex justify-between text-sm"><span>Difficulty</span><span class="font-semibold">${inst.difficulty}</span></div>
            <div class="flex justify-between text-sm"><span>Pass Rate</span><span class="font-semibold">${inst.passRate}%</span></div>
          </div>
          <div class="mt-5 p-4 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 text-center">
            <div class="text-xs text-slate-500 uppercase">Predicted GPA</div>
            <div class="text-3xl font-bold text-slate-900 dark:text-white">${idx===0?pa.letter:pb.letter}</div>
            <div class="text-sm text-slate-500">${idx===0?pa.gpa:pb.gpa} average</div>
          </div>
        </div>`).join('')}
      </div>
    </div>`;
}
