function renderReview(state) {
  return `
    <div class="space-y-6 animate-fadeIn max-w-3xl mx-auto">
      <h2 class="text-2xl font-bold tracking-tight">Review an Instructor</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 space-y-5">
        <div>
          <label class="text-sm font-medium">Instructor</label>
          <select id="revInst" class="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${DATA.instructors.map(i => `<option value="${i.id}">${i.name}</option>`).join('')}</select>
        </div>
        <div>
          <label class="text-sm font-medium">Course</label>
          <select id="revCourse" class="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${DATA.courses.map(c => `<option value="${c.id}">${c.code}</option>`).join('')}</select>
        </div>
        <div>
          <label class="text-sm font-medium">Rating</label>
          <div class="flex gap-1 mt-1 text-2xl cursor-pointer" id="starBox">${[1,2,3,4,5].map(i => `<span onclick="setReviewStar(${i})" id="rs${i}" class="${i <= (state.reviewStars||0) ? 'text-amber-400' : 'text-slate-300'}">★</span>`).join('')}</div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div><label class="text-sm font-medium">Grade received</label><select id="revGrade" class="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent">${['A','A-','B+','B','B-','C+','C','D','F'].map(g => `<option>${g}</option>`).join('')}</select></div>
          <div class="flex items-end gap-4 pb-2"><label class="flex items-center gap-2 text-sm"><input type="checkbox" id="revRec" class="rounded"> Recommend</label><label class="flex items-center gap-2 text-sm"><input type="checkbox" id="revAnon" class="rounded"> Anonymous</label></div>
        </div>
        <div><label class="text-sm font-medium">Review</label><textarea id="revText" rows="3" class="mt-1 w-full px-3 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent"></textarea></div>
        <button onclick="submitReview()" class="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold">Submit Review</button>
      </div>
      <div class="space-y-3">
        ${state.reviews.map((r,i) => `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-4"><div class="flex items-center gap-2 text-amber-500">${[...Array(5)].map((_,j) => `<span>${j<r.rating?'★':'☆'}</span>`).join('')}<span class="text-xs text-slate-400 ml-2">${r.anon?'Anonymous':r.author}</span></div><p class="text-sm text-slate-700 dark:text-slate-300 mt-1">${r.text}</p></div>`).join('')}
      </div>
    </div>`;
}
