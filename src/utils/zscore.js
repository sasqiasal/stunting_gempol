/**
 * Utility untuk menghitung Z-Score pertumbuhan anak berdasarkan standar WHO 2006.
 * Menggunakan metode LMS (Lambda-Mu-Sigma).
 */

import { WHO_WFA_BOYS, WHO_WFA_GIRLS, WHO_HFA_BOYS, WHO_HFA_GIRLS } from "../data/whoChildGrowthStandards";

/**
 * Menghitung interpolasi linear untuk mendapatkan nilai L, M, S pada usia tertentu
 * jika usia tersebut tidak ada secara eksak di dalam tabel.
 *
 * @param {number} ageMonths - Usia dalam bulan
 * @param {object} referenceData - Data referensi WHO (WFA atau HFA)
 * @returns {object|null} - Objek { L, M, S } atau null jika gagal
 */
function interpolateLMS(ageMonths, referenceData) {
  // Jika data tersedia langsung untuk bulan tersebut
  if (referenceData[ageMonths]) {
    return referenceData[ageMonths];
  }

  // Cari dua titik terdekat untuk interpolasi
  // Mengambil keys (usia) dan mengurutkannya sebagai angka
  const ages = Object.keys(referenceData)
    .map(Number)
    .sort((a, b) => a - b);

  // Jika usia di bawah range minimum (biasanya tidak terjadi jika mulai dari 0)
  if (ageMonths < ages[0]) {
    return referenceData[ages[0]];
  }

  // Jika usia di atas range maksimum
  if (ageMonths > ages[ages.length - 1]) {
    return referenceData[ages[ages.length - 1]];
  }

  // Interpolasi linear
  for (let i = 0; i < ages.length - 1; i++) {
    const age1 = ages[i];
    const age2 = ages[i + 1];

    if (ageMonths >= age1 && ageMonths <= age2) {
      const data1 = referenceData[age1];
      const data2 = referenceData[age2];

      // Faktor proporsi (t)
      const t = (ageMonths - age1) / (age2 - age1);

      // Rumus interpolasi: Value = V1 + t * (V2 - V1)
      const L = data1.L + t * (data2.L - data1.L);
      const M = data1.M + t * (data2.M - data1.M);
      const S = data1.S + t * (data2.S - data1.S);

      return { L, M, S };
    }
  }

  return referenceData[ages[0]]; // Fallback
}

/**
 * Menghitung Z-Score menggunakan metode LMS.
 *
 * Rumus WHO:
 * Jika L != 0: Z = ((X/M)^L - 1) / (L * S)
 * Jika L == 0: Z = ln(X/M) / S
 *
 * @param {number} x - Nilai pengukuran anak (TB dalam cm, atau BB dalam kg)
 * @param {number} l - Parameter L (Box-Cox power) dari tabel WHO
 * @param {number} m - Parameter M (Median) dari tabel WHO
 * @param {number} s - Parameter S (Coefficient of Variation) dari tabel WHO
 * @returns {number} Nilai Z-Score (dibulatkan 2 desimal)
 */
export function calculateZScore(x, l, m, s) {
  // Validasi input dasar
  if (x === undefined || x === null || l === undefined || l === null || m === undefined || m === null || s === undefined || s === null) {
    return null;
  }

  // Konversi ke number untuk keamanan
  const X = Number(x);
  const L = Number(l);
  const M = Number(m);
  const S = Number(s);

  if (isNaN(X) || isNaN(L) || isNaN(M) || isNaN(S) || M === 0 || S === 0) {
    return null;
  }

  let zScore;

  // Cek apakah L mendekati 0 (menggunakan epsilon kecil untuk float comparison)
  if (Math.abs(L) < 0.0000001) {
    // Rumus jika L = 0: Z = ln(X/M) / S
    zScore = Math.log(X / M) / S;
  } else {
    // Rumus jika L != 0: Z = ((X/M)^L - 1) / (L * S)
    zScore = (Math.pow(X / M, L) - 1) / (L * S);
  }

  // Pembulatan 2 desimal
  return Math.round(zScore * 100) / 100;
}

/**
 * Menghitung Z-Score Berat Badan per Umur (BB/U)
 *
 * @param {number} berat - Berat badan dalam kg
 * @param {number} usiaBulan - Usia dalam bulan
 * @param {string} jenisKelamin - 'L' (Laki-laki) atau 'P' (Perempuan)
 * @returns {number|null} Z-Score atau null jika invalid
 */
export function calculateZScoreBBU(berat, usiaBulan, jenisKelamin) {
  // Tentukan tabel referensi
  let referenceData;
  if (jenisKelamin === "L") {
    referenceData = WHO_WFA_BOYS;
  } else if (jenisKelamin === "P") {
    referenceData = WHO_WFA_GIRLS;
  } else {
    return null; // Jenis kelamin tidak valid
  }

  // Dapatkan parameter L, M, S (dengan interpolasi jika perlu)
  const lms = interpolateLMS(usiaBulan, referenceData);
  if (!lms) return null;

  return calculateZScore(berat, lms.L, lms.M, lms.S);
}

/**
 * Menghitung Z-Score Tinggi Badan per Umur (TB/U)
 *
 * @param {number} tinggi - Tinggi badan dalam cm
 * @param {number} usiaBulan - Usia dalam bulan
 * @param {string} jenisKelamin - 'L' (Laki-laki) atau 'P' (Perempuan)
 * @returns {number|null} Z-Score atau null jika invalid
 */
export function calculateZScoreTBU(tinggi, usiaBulan, jenisKelamin) {
  // Tentukan tabel referensi
  let referenceData;
  if (jenisKelamin === "L") {
    referenceData = WHO_HFA_BOYS;
  } else if (jenisKelamin === "P") {
    referenceData = WHO_HFA_GIRLS;
  } else {
    return null; // Jenis kelamin tidak valid
  }

  // Dapatkan parameter L, M, S (dengan interpolasi jika perlu)
  const lms = interpolateLMS(usiaBulan, referenceData);
  if (!lms) return null;

  return calculateZScore(tinggi, lms.L, lms.M, lms.S);
}

// -----------------------------------------------------------
// CONTOH PEMANGGILAN FUNGSI
// -----------------------------------------------------------

/**
 * Fungsi helper contoh untuk mendemonstrasikan cara pakai.
 * Ini mensimulasikan data dari tabel WHO.
 */
export function exampleUsage() {
  console.log("--- Demo Perhitungan Z-Score ---");

  // Contoh 1: Z-Score Tinggi Badan/Umur (TB/U)
  // Kasus: Anak Laki-laki, 24 Bulan, Tinggi 82 cm
  // Parameter WHO (Contoh): L=1, M=87.1, S=0.03
  const tb = 82;
  const l_tb = 1;
  const m_tb = 87.1;
  const s_tb = 0.03;

  const zTBU = calculateZScore(tb, l_tb, m_tb, s_tb);
  console.log(`Z-Score TB/U (TB:${tb}cm): ${zTBU}`);

  // Contoh 2: Z-Score Berat Badan/Umur (BB/U)
  // Kasus: Anak Perempuan, 12 Bulan, Berat 7.5 kg
  // Parameter WHO (Contoh): L=0.05, M=8.9, S=0.11
  const bb = 7.5;
  const l_bb = 0.05;
  const m_bb = 8.9;
  const s_bb = 0.11;

  const zBBU = calculateZScore(bb, l_bb, m_bb, s_bb);
  console.log(`Z-Score BB/U (BB:${bb}kg): ${zBBU}`);
}
