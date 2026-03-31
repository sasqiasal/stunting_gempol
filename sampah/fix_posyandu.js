const fs = require('fs');

let text = fs.readFileSync('src/pages/PosyanduPage.jsx', 'utf-8');

// 1. Remove view mode
text = text.replace(/const \[viewMode, setViewMode\] = useState\("cards"\);\s*\/\/ 'cards' or 'table'/, '');

// 2. Remove Toggle UI
text = text.replace(/\{\/\* View Mode Toggle \*\/\}.*?(?=\{loading \?)/s, '');

// 3. Replace the table view / cards view conditional
text = text.replace(/\) : viewMode === "table" \? \([\s\S]*?\) : \(\n\s*\/\/ Cards View\n\s*<>\n\s*<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n/, ') : (\n              <>\n                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n\n                  {/* Card Tambah Posyandu */}\n                  <div \n                    onClick={() => handleAddClick()}\n                    className="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center text-gray-500 hover:text-primary-600 hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer min-h-[250px]"\n                  >\n                    <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">\n                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />\n                    </svg>\n                    <span className="font-medium">Tambah Posyandu</span>\n                  </div>\n\n');

// 4. Remove kader_penanggungjawab field from editForm payload state default
text = text.replace(/kecamatan\s*:\s*"",\n\s*kader_penanggungjawab\s*:\s*"",/, 'kecamatan: "",');

// 5. Remove manual edit kader_penanggungjawab logic from handleEditClick
text = text.replace(/kecamatan\s*:\s*posyandu\.kecamatan \|\| "Gempol",\n\s*kader_penanggungjawab\s*:\s*posyandu\.kader_penanggungjawab \|\| "",/, 'kecamatan: posyandu.kecamatan || "Gempol",');

// Add handleAddClick if not exists
if (!text.includes('const handleAddClick')) {
    const handleAddStr = 
  const handleAddClick = () => {
    setSelectedPosyandu(null);
    setEditForm({
      nama: "",
      alamat: "",
      kelurahan: "Gempol",
      kecamatan: "Gempol",
    });
    setShowEditModal(true);
  };
;
    text = text.replace('const handleEditClick = (posyandu) => {', handleAddStr + '\n  const handleEditClick = (posyandu) => {');
}

// 6. Make Modal Title dynamic
text = text.replace('<h2 className="text-xl font-bold text-gray-900">Kelola Unit Posyandu</h2>', '<h2 className="text-xl font-bold text-gray-900">{selectedPosyandu ? "Kelola Unit Posyandu" : "Tambah Posyandu Baru"}</h2>');

// 7. Modify Save logic to handle create and update
const saveStr = const handleUpdatePosyandu = async (e) => {
    e.preventDefault();
    
    try {
      if (selectedPosyandu) {
        await posyanduService.update(selectedPosyandu.id, editForm);
        toast.success("Data posyandu berhasil diupdate");
      } else {
        await posyanduService.create(editForm);
        toast.success("Data posyandu berhasil ditambahkan");
      }
      setShowEditModal(false);
      loadPosyandu();
    } catch (error) {
      console.error("Error saving posyandu:", error);
      toast.error("Gagal menyimpan data posyandu");
    }
  };;

text = text.replace(/const handleUpdatePosyandu = async \(e\) => \{[\s\S]*?toast\.error\("Gagal update data posyandu"\);\n\s*\}\n\s*\};/, saveStr);


// 8. Remove the manual text input block for Ketua Kader
text = text.replace(/\{\/\* Ketua Kader \*\/\}.*?(?=\{\/\* Info Akun Kader \*\/\})/s, '');

fs.writeFileSync('src/pages/PosyanduPage.jsx', text, 'utf-8');
console.log('PosyanduPage.jsx updated successfully');
