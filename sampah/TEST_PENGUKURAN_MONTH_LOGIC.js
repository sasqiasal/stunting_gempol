/**
 * Test Suite untuk PengukuranForm Helper Functions
 * Test: calculateAgeAtMeasurement & getAllowedMonths
 */

// Mock current date untuk testing
const mockToday = new Date('2026-03-25');

/**
 * Helper: Calculate age in months from birthdate to measurement month
 * (Copied from PengukuranForm.jsx)
 */
function calculateAgeAtMeasurement(birthDate, selectedMonth) {
  if (!birthDate || !selectedMonth) return null;
  
  const birth = new Date(birthDate);
  const [year, month] = selectedMonth.split('-').map(Number);
  // Use last day of the selected month for accurate calculation
  const lastDay = new Date(year, month, 0).getDate();
  const measurement = new Date(year, month - 1, lastDay);
  
  const diffTime = measurement.getTime() - birth.getTime();
  const diffDate = new Date(diffTime);
  const months = (diffDate.getUTCFullYear() - 1970) * 12 + diffDate.getUTCMonth();
  
  return Math.max(0, months);
}

/**
 * Test Cases
 */
console.log("=== TEST: calculateAgeAtMeasurement ===\n");

// Test Case 1: Birth 15 Jan 2025, Measurement March 2026
let birthDate1 = "2025-01-15";
let age1_mar2026 = calculateAgeAtMeasurement(birthDate1, "2026-03");
let age1_feb2026 = calculateAgeAtMeasurement(birthDate1, "2026-02");
let age1_jan2026 = calculateAgeAtMeasurement(birthDate1, "2026-01");
let age1_dec2025 = calculateAgeAtMeasurement(birthDate1, "2025-12");

console.log(`Test 1: Balita born Jan 15, 2025`);
console.log(`  March 2026: ${age1_mar2026} months (expect ~14)`);
console.log(`  Feb 2026: ${age1_feb2026} months (expect ~13)`);
console.log(`  Jan 2026: ${age1_jan2026} months (expect ~12)`);
console.log(`  Dec 2025: ${age1_dec2025} months (expect ~11)`);
console.log(`  ✓ PASS if decrement by 1 each month backwards\n`);

// Test Case 2: Birth 1 Jan 2024, Measurement March 2026
let birthDate2 = "2024-01-01";
let age2_mar2026 = calculateAgeAtMeasurement(birthDate2, "2026-03");
let age2_jan2024 = calculateAgeAtMeasurement(birthDate2, "2024-01");

console.log(`Test 2: Balita born Jan 1, 2024`);
console.log(`  March 2026: ${age2_mar2026} months (expect ~26)`);
console.log(`  Jan 2024: ${age2_jan2024} months (expect 0)`);
console.log(`  ✓ PASS if 26 - 0 = 26 months difference\n`);

// Test Case 3: Edge case - Birth on last day of month
let birthDate3 = "2025-02-28";
let age3_feb2026 = calculateAgeAtMeasurement(birthDate3, "2026-02");
let age3_mar2026 = calculateAgeAtMeasurement(birthDate3, "2026-03");

console.log(`Test 3: Balita born Feb 28, 2025`);
console.log(`  Feb 2026: ${age3_feb2026} months (expect ~12)`);
console.log(`  March 2026: ${age3_mar2026} months (expect ~13)`);
console.log(`  ✓ PASS if increases by 1 each month\n`);

// Test Case 4: Current month vs 3 months back
console.log(`Test 4: Allowed Months Validation`);
console.log(`  Current: March 2026 (month 3)`);
console.log(`  Allowed: March 2026, Feb 2026, Jan 2026, Dec 2025`);
console.log(`  Range: 2025-12-01 to 2026-03-31`);
console.log(`  ✓ VERIFY manually in UI\n`);

// Test Case 5: Message about dropdown limiting
console.log(`Test 5: Frontend Validation`);
console.log(`  User tries to pick: November 2025 (4 months back) → Should NOT be in dropdown`);
console.log(`  User tries to pick: April 2026 (future) → Should NOT be in dropdown`);
console.log(`  ✓ VERIFY: getAllowedMonths() returns exactly 4 months\n`);

console.log("=== MANUAL VERIFICATION NEEDED ===");
console.log("1. Open PengukuranForm in browser");
console.log("2. Select a Balita");
console.log("3. Change Bulan Pengukuran dropdown - verify Usia updates:");
console.log("   - Current month: Show normal usia balita");
console.log("   - 1 month back: Usia - 1");
console.log("   - 2 months back: Usia - 2");
console.log("   - 3 months back: Usia - 3");
console.log("4. Submit form with past month data");
console.log("5. Verify database saved dengan tanggal_pengukuran dan usia_bulan yang benar");
console.log("6. Check Z-score calculation matches expected age");
