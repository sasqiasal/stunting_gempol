import re

with open('d:/development/stunting_gempol/src/pages/EvaluasiModelPage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

new_text = re.sub(
    r'<th[^>]*>Data Latih</th>', 
    '''<th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">JK</th>\n                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usia</th>\n                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">BB</th>\n                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TB</th>\n                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LILA</th>\n                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LK</th>''',
    text
)

new_text = re.sub(
    r'<td[^>]*>\s*JK: \{neighbor\.jenis_kelamin\}.*?</td\s*>',
    '''<td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.jenis_kelamin}</td>\n                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.usia_bulan} bln</td>\n                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.berat_badan} kg</td>\n                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.tinggi_badan} cm</td>\n                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.lingkar_lengan || '-'} cm</td>\n                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.lingkar_kepala || '-'} cm</td>''',
    new_text,
    flags=re.DOTALL
)

with open('d:/development/stunting_gempol/src/pages/EvaluasiModelPage.jsx', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Replacement done")
