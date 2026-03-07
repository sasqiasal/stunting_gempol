/**
 * Helper functions
 */

/**
 * Sensor nama anak untuk privasi
 * Mengubah nama lengkap menjadi "Baby [Inisial]"
 * Contoh: "Dimas Aswito" -> "Baby DA"
 * @param {string} nama - Nama lengkap
 * @returns {string} - Nama yang disensor
 */
export const censorChildName = (nama) => {
  if (!nama) return '-';
  
  const words = nama.trim().split(' ').filter(word => word.length > 0);
  
  if (words.length === 0) return 'Baby';
  
  // Ambil inisial dari setiap kata
  const initials = words.map(word => word.charAt(0).toUpperCase()).join('');
  
  return `Baby ${initials}`;
};

/**
 * Sensor nama orang tua
 * Mengubah nama lengkap menjadi inisial saja
 * Contoh: "Santi Anya" -> "SA"
 * @param {string} nama - Nama lengkap
 * @returns {string} - Initials
 */
export const censorParentName = (nama) => {
  if (!nama) return '-';
  
  const words = nama.trim().split(' ').filter(word => word.length > 0);
  
  if (words.length === 0) return '-';
  
  // Ambil inisial dari setiap kata
  const initials = words.map(word => word.charAt(0).toUpperCase()).join('');
  
  return initials;
};

/**
 * Format tanggal ke format Indonesia (DD/MM/YYYY)
 * @param {string|Date} date - Tanggal
 * @returns {string}
 */
export const formatDate = (date) => {
  if (!date) return '-';
  
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  
  return `${day}/${month}/${year}`;
};

/**
 * Format tanggal dan waktu
 * @param {string|Date} datetime - Datetime
 * @returns {string}
 */
export const formatDateTime = (datetime) => {
  if (!datetime) return '-';
  
  const d = new Date(datetime);
  const date = formatDate(d);
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  
  return `${date} ${hours}:${minutes}`;
};

/**
 * Get status color based on status gizi
 * @param {string} status - Status gizi
 * @returns {string} - Tailwind color class
 */
export const getStatusColor = (status) => {
  if (!status) return 'gray';
  
  const lowerStatus = status.toLowerCase();
  
  if (lowerStatus.includes('stunting') || lowerStatus.includes('severely')) {
    return 'danger';
  }
  
  if (lowerStatus.includes('underweight') || lowerStatus.includes('wasting')) {
    return 'yellow';
  }
  
  if (lowerStatus.includes('normal')) {
    return 'success';
  }
  
  return 'gray';
};

/**
 * Get badge style based on status
 * @param {string} status - Status gizi
 * @returns {string} - Tailwind classes
 */
export const getStatusBadge = (status) => {
  const color = getStatusColor(status);
  
  const colorMap = {
    danger: 'bg-danger-100 text-danger-700 border-danger-200',
    yellow: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    success: 'bg-success-100 text-success-700 border-success-200',
    gray: 'bg-gray-100 text-gray-700 border-gray-200',
  };
  
  return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorMap[color]}`;
};

/**
 * Calculate age from birth date
 * @param {string|Date} birthDate - Tanggal lahir
 * @returns {Object} - { years, months, totalMonths }
 */
export const calculateAge = (birthDate) => {
  if (!birthDate) return { years: 0, months: 0, totalMonths: 0 };
  
  const birth = new Date(birthDate);
  const today = new Date();
  
  let years = today.getFullYear() - birth.getFullYear();
  let months = today.getMonth() - birth.getMonth();
  
  if (months < 0) {
    years--;
    months += 12;
  }
  
  const totalMonths = years * 12 + months;
  
  return { years, months, totalMonths };
};

/**
 * Format number with decimal
 * @param {number} num - Number
 * @param {number} decimals - Decimal places
 * @returns {string}
 */
export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '-';
  return Number(num).toFixed(decimals);
};

/**
 * Validate NIK (16 digits)
 * @param {string} nik - NIK
 * @returns {boolean}
 */
export const validateNIK = (nik) => {
  return /^\d{16}$/.test(nik);
};

/**
 * Validate phone number
 * @param {string} phone - Phone number
 * @returns {boolean}
 */
export const validatePhone = (phone) => {
  return /^(\+62|62|0)[0-9]{9,12}$/.test(phone);
};

/**
 * Get jenis kelamin label
 * @param {string} jk - L atau P
 * @returns {string}
 */
export const getJenisKelaminLabel = (jk) => {
  return jk === 'L' ? 'Laki-laki' : jk === 'P' ? 'Perempuan' : '-';
};

/**
 * Get role label
 * @param {string} role - admin atau kader
 * @returns {string}
 */
export const getRoleLabel = (role) => {
  const roleMap = {
    admin: 'Administrator',
    kader: 'Kader Posyandu',
  };
  return roleMap[role] || role;
};

/**
 * Get role badge
 * @param {string} role - admin atau kader
 * @returns {string}
 */
export const getRoleBadge = (role) => {
  const colorMap = {
    admin: 'bg-primary-100 text-primary-700 border-primary-200',
    kader: 'bg-purple-100 text-purple-700 border-purple-200',
  };
  
  return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorMap[role]}`;
};
