const fs = require('fs');
let text = fs.readFileSync('src/pages/PosyanduPage.jsx', 'utf8');

const strToFind = ') : viewMode === "table" ? (';
const strToEnd = '<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">';
const i1 = text.indexOf(strToFind);
const i2 = text.indexOf(strToEnd);

console.log({ i1, i2 });

if (i1 >= 0 && i2 >= 0) {
  const replacement = \) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                  {/* Card Tambah Posyandu */}
                  <div 
                    onClick={() => handleAddClick()}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-gray-500 hover:text-primary-600 hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer min-h-[250px]"
                  >
                    <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span className="font-medium">Tambah Posyandu</span>
                  </div>

\;
  text = text.substring(0, i1) + replacement + text.substring(i2 + strToEnd.length + 1);
  fs.writeFileSync('src/pages/PosyanduPage.jsx', text, 'utf8');
  console.log('Successfully swapped!');
}
