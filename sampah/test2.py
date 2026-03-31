with open('d:/development/stunting_gempol/src/pages/EvaluasiModelPage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

import re

old_table = '''                              <thead className="bg-gray-50">
                                <tr>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Latih</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status (Label)</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {(displayNeighbors || []).map((neighbor, nIdx) => (
                                  <tr key={nIdx} className={nIdx === 0 ? "bg-blue-50/50" : ""}>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">#{nIdx + 1}</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">
                                      JK: {neighbor.jenis_kelamin}, {neighbor.usia_bulan} bln, {neighbor.tinggi_badan} cm, {neighbor.berat_badan} kg
                                    </td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs font-mono text-gray-600">{neighbor.distance}</td>
                                    <td className="px-4 py-2 whitespace-nowrap">
                                      <span className={px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full }>
                                        {neighbor.label}
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>'''

new_table = '''                              <thead className="bg-gray-50">
                                <tr>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">JK</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usia</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">BB</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TB</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LILA</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">LK</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Label</th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {(displayNeighbors || []).map((neighbor, nIdx) => (
                                  <tr key={nIdx} className={nIdx === 0 ? "bg-blue-50/50" : ""}>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">#{nIdx + 1}</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.jenis_kelamin}</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.usia_bulan} bln</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.berat_badan} kg</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.tinggi_badan} cm</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.lingkar_lengan || '-'} cm</td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">{neighbor.lingkar_kepala || '-'} cm</td>
                                    <td className="px-4 py-2 whitespace-nowrap">
                                      <span className={px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full }>
                                        {neighbor.label}
                                      </span>
                                    </td>
                                    <td className="px-4 py-2 whitespace-nowrap text-xs font-mono text-gray-600">{neighbor.distance}</td>
                                  </tr>
                                ))}
                              </tbody>'''

# Replace backticks with escaped backticks for safe string representation
old_table = old_table.replace('', '\\')
new_table = new_table.replace('', '\\')

text = text.replace(old_table.replace('\\', ''), new_table.replace('\\', ''))

with open('d:/development/stunting_gempol/src/pages/EvaluasiModelPage.jsx', 'w', encoding='utf-8') as f:
    f.write(text)
