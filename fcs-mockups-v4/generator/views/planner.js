function renderPlanner(state) {
  const semesters = [1,2,3,4,5,6,7,8];
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Semester Path Planner</h2>
      <p class="text-slate-500 text-sm">Drag courses between semesters to balance load and difficulty.</p>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        ${semesters.map(sem => {
           const load = state.planner[sem].reduce((a,id) => a + (DATA.courses.find(c => c.id === id)?.credits || 0), 0);
           return `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-4 min-h-[220px]">
             <div class="flex justify-between items-center mb-3"><h3 class="font-bold text-sm">Semester ${sem}</h3><span class="text-xs ${load>18?'text-rose-600':load>15?'text-amber-600':'text-emerald-600'} font-semibold">${load} cr</span></div>
             <div class="space-y-2 min-h-[120px] rounded-xl bg-slate-50 dark:bg-slate-900 p-2" ondragover="event.preventDefault()" ondrop="dropPlanner(${sem}, event)">
               ${state.planner[sem].map((id,i) => `<div draggable="true" ondragstart="event.dataTransfer.setData('text','${id}|${sem}')" class="cursor-move px-2 py-1.5 rounded-lg bg-white dark:bg-slate-700 shadow-sm text-xs flex justify-between items-center"><span>${courseCode(id)}</span><button onclick="app.planner[${sem}].splice(${i},1); render();" class="text-slate-400 hover:text-rose-500">${icon('trash','w-3 h-3')}</button></div>`).join('')}
             </div>
             <div class="mt-2 text-xs text-slate-400 text-center">drop here</div>
           </div>`;
        }).join('')}
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
        <h3 class="font-semibold mb-2">Course Pool</h3>
        <div class="flex flex-wrap gap-2" ondragover="event.preventDefault()" ondrop="dropPlanner('pool',event)">
          ${DATA.courses.filter(c => !Object.values(state.planner).flat().includes(c.id)).map(c => `<div draggable="true" ondragstart="event.dataTransfer.setData('text','${c.id}|pool')" class="cursor-move px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium">${c.code}</div>`).join('')}
        </div>
      </div>
    </div>`;
}
