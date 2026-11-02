function renderHistory(state) {
  const grades = ['A','A-','B+','B','B-','C+','C','D','F'];
  const gpa = state.history.length ? (state.history.reduce((a, h) => a + gpaPoints(h.grade), 0) / state.history.length).toFixed(2) : '0.00';
  return `
    <div class="space-y-6 animate-fadeIn max-w-3xl mx-auto">
      <h2 class="text-2xl font-bold tracking-tight">Course History</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-5">
        <div class="flex gap-2">
          <select id="histCourse" class="flex-1 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${DATA.courses.map(c => `<option value="${c.id}">${c.code} ${c.title}</option>`).join('')}</select>
          <select id="histGrade" class="w-24 px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${grades.map(g => `<option>${g}</option>`).join('')}</select>
          <button onclick="addHistory(document.getElementById('histCourse').value, document.getElementById('histGrade').value)" class="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold">${icon('plus','w-5 h-5')}</button>
        </div>
        <div class="space-y-2">${state.history.map((h,i) => `<div class="flex justify-between items-center p-3 rounded-xl bg-slate-50 dark:bg-slate-900"><span class="font-medium">${courseCode(h.courseId)}</span><span class="px-2 py-1 rounded-md text-sm font-bold bg-slate-200 dark:bg-slate-700">${h.grade}</span><button onclick="app.history.splice(${i},1); render();" class="text-slate-400 hover:text-rose-500">${icon('trash','w-4 h-4')}</button></div>`).join('')}</div>
        <div class="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-700"><span class="font-semibold">Cumulative GPA</span><span class="text-2xl font-bold text-blue-600">${gpa}</span></div>
        <button onclick="toast('Transcript imported (demo)','success')" class="w-full py-2 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 font-medium inline-flex items-center justify-center gap-1">${icon('document','w-4 h-4')} Import Transcript PDF</button>
      </div>
    </div>`;
}
