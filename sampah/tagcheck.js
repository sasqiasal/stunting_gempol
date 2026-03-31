const fs = require('fs');
const content = fs.readFileSync('src/pages/EvaluasiModelPage.jsx', 'utf8');

const lines = content.split('\n');
const klasiStart = lines.findIndex(l => l.includes('activeTab === \"klasifikasi\"'));
const klasiEnd = lines.findIndex((l, i) => i > klasiStart && l.includes('Action Button'));

const section = lines.slice(klasiStart, klasiEnd);
let balance = 0;
let fragBalance = 0;
section.forEach((l, i) => {
  const openCount = (l.match(/<div/g) || []).length;
  const closeCount = (l.match(/<\/div/g) || []).length;
  const openFrag = (l.match(/<>/g) || []).length;
  const closeFrag = (l.match(/<\/>/g) || []).length;
  
  balance += (openCount - closeCount);
  fragBalance += (openFrag - closeFrag);
  
  if (openCount !== closeCount || openFrag !== closeFrag) {
     console.log((i + klasiStart + 1) + ': f:' + fragBalance + ' d:' + balance + ' | ' + l.trim());
  }
});
