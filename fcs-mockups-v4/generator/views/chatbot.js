function renderChatbot(state) {
  return `
    <div class="space-y-6 animate-fadeIn">
      <h2 class="text-2xl font-bold tracking-tight">Chatbot</h2>
      <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm p-6 min-h-[500px] flex flex-col">
        <div class="flex-1 space-y-3 overflow-auto">${state.chat.messages.map(m => `<div class="flex ${m.role==='user'?'justify-end':'justify-start'}"><div class="max-w-[80%] px-4 py-2.5 rounded-2xl text-sm ${m.role==='user'?'bg-blue-600 text-white rounded-br-none':'bg-slate-100 dark:bg-slate-700 rounded-bl-none'}">${m.text}</div></div>`).join('')}</div>
        <div class="mt-4 flex gap-2"><input id="botInput" type="text" onkeydown="if(event.key==='Enter')sendAgent(this.value)" placeholder="Ask FCS..." class="flex-1 px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 outline-none focus:ring-2 focus:ring-blue-500"><button onclick="sendAgent(document.getElementById('botInput').value)" class="px-5 py-2 rounded-xl bg-blue-600 text-white font-semibold">${icon('chat','w-5 h-5')}</button></div>
      </div>
    </div>`;
}
