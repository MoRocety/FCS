function renderAgentChat(state) {
  return `
    <div class="space-y-6 animate-fadeIn" style="height:calc(100vh - 8rem)">
      <h2 class="text-2xl font-bold tracking-tight">FCS Agent</h2>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 h-full">
        <div class="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-full">
          <div class="p-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-white">${icon('sparkles','w-5 h-5')}</div>
            <div><div class="font-semibold">FCS Assistant</div><div class="text-xs text-slate-500">Online · Memory on</div></div>
          </div>
          <div id="chatMessages" class="flex-1 overflow-auto p-4 space-y-3">${state.chat.messages.map(m => `<div class="flex ${m.role==='user'?'justify-end':'justify-start'}"><div class="max-w-[80%] px-4 py-2.5 rounded-2xl text-sm ${m.role==='user'?'bg-blue-600 text-white rounded-br-none':'bg-slate-100 dark:bg-slate-700 rounded-bl-none'}">${m.text}</div></div>`).join('')}</div>
          <div class="p-4 border-t border-slate-100 dark:border-slate-700">
            <div class="flex flex-wrap gap-2 mb-2">${['Find me easy CS electives','Build a no-8AM plan','Who teaches Algorithms?'].map(p => `<button onclick="sendAgent('${p}')" class="px-3 py-1 rounded-full text-xs bg-slate-100 dark:bg-slate-700 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-slate-600 dark:text-slate-300 transition">${p}</button>`).join('')}</div>
            <div class="flex gap-2"><input id="chatInput" type="text" onkeydown="if(event.key==='Enter')sendAgent(this.value)" placeholder="Ask anything..." class="flex-1 px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none focus:ring-2 focus:ring-blue-500"><button onclick="sendAgent(document.getElementById('chatInput').value)" class="px-4 py-2 rounded-xl bg-blue-600 text-white font-semibold">${icon('chat','w-5 h-5')}</button></div>
          </div>
        </div>
        <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-5 h-full overflow-auto">
          <h3 class="font-semibold mb-3 flex items-center gap-2">${icon('cog','w-4 h-4')} Tool Calls</h3>
          <div class="space-y-3">${state.chat.audit.length ? state.chat.audit.map(a => `<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 text-xs font-mono border border-slate-100 dark:border-slate-700"><div class="text-blue-600 font-bold mb-1">${a.tool}</div><div class="text-slate-500">${a.args}</div><div class="mt-1 text-emerald-600">${a.result}</div></div>`).join('') : '<div class="text-sm text-slate-500">No tools called yet.</div>'}</div>
        </div>
      </div>
    </div>`;
}
