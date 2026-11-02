function renderFeed(state) {
  return `
    <div class="space-y-6 animate-fadeIn">
      <div class="flex items-center justify-between"><h2 class="text-2xl font-bold tracking-tight">Published Schedules</h2><button onclick="toast('Your schedule published (demo)','success')" class="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm font-semibold inline-flex items-center gap-1">${icon('plus','w-4 h-4')} Publish mine</button></div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        ${DATA.published.map(p => {
           const vote = state.feedVotes[p.id] || 0;
           return `<div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5">
             <div class="flex items-start justify-between">
               <div class="flex items-center gap-3">
                 <div class="w-10 h-10 rounded-full bg-gradient-to-br from-slate-300 to-slate-400 dark:from-slate-600 dark:to-slate-700 flex items-center justify-center text-white font-bold">${p.author[0]}</div>
                 <div><div class="font-semibold text-sm">${p.author}</div><div class="text-xs text-slate-500">${p.term}</div></div>
               </div>
               <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-700 rounded-lg p-1">
                 <button onclick="voteFeed('${p.id}',1)" class="p-1 rounded hover:bg-white dark:hover:bg-slate-600 ${vote===1?'text-blue-600':''}">${icon('thumbUp','w-4 h-4')}</button>
                 <span class="text-sm font-bold w-5 text-center">${p.votes + vote}</span>
                 <button onclick="voteFeed('${p.id}',-1)" class="p-1 rounded hover:bg-white dark:hover:bg-slate-600 ${vote===-1?'text-rose-600':''}">${icon('thumbDown','w-4 h-4')}</button>
               </div>
             </div>
             <div class="mt-3 flex flex-wrap gap-2">${p.courses.map(c => `<span class="px-2 py-1 rounded-md text-xs bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-700">${c}</span>`).join('')}</div>
             <div class="mt-4 flex items-center justify-between text-sm text-slate-500">
               <span>${p.forks} forks · ${p.comments} comments</span>
               <button onclick="toast('Forked schedule into builder','success')" class="text-blue-600 font-medium hover:underline inline-flex items-center gap-1">${icon('arrowPath','w-4 h-4')} Fork</button>
             </div>
           </div>`;
        }).join('')}
      </div>
    </div>`;
}
