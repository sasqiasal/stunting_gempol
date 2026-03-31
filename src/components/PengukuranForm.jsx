/**
 * Form Input Pengukuran untuk Kader
 * Form untuk menginput data pengukuran balita dengan prediksi stunting otomatis
 * Mobile-First Responsive Design
 */

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import Select from "react-select";
import { pengukuranService } from "../services/pengukuranService";
import { balitaService } from "../services/balitaService";
import { censorChildName } from "../utils/helpers";

export const PengukuranForm = ({ balitaId, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [balitaList, setBalitaList] = useState([]);
  const [selectedBalita, setSelectedBalita] = useState(null);
  const [selectedBalitaOption, setSelectedBalitaOption] = useState(null);
  const [calculatedAge, setCalculatedAge] = useState(null);
  const [measuredBalitasThisMonth, setMeasuredBalitasThisMonth] = useState([]);

  // 4-class classification labels
  const getClassificationLabel = (classNum) => {
    // Handle berbagai tipe input
    const num = Number(classNum);
    const classMap = {
      0: "Normal + Gizi Baik",
      1: "Normal + Kurang Gizi",
      2: "Stunting + Gizi Baik",
      3: "Stunting + Kurang Gizi"
    };
    
    // Debug: log jika ada nilai yang tidak dikenal
    if (!(num in classMap)) {
      console.warn(`Unknown classification value: ${classNum} (type: ${typeof classNum})`);
    }
    
    return classMap[num] || `Unknown Class ${classNum}`;
  };

  // Helper: Calculate age in months from birthdate to measurement month
  const calculateAgeAtMeasurement = (birthDate, selectedMonth) => {
    if (!birthDate || !selectedMonth) return null;
    
    const birth = new Date(birthDate);
    const [year, month] = selectedMonth.split('-').map(Number);
    
    // Create measurement date as last day of selected month
    const lastDay = new Date(year, month, 0).getDate();
    const measurement = new Date(year, month - 1, lastDay);
    
    // Calculate total months between two dates
    const yearsDiff = measurement.getFullYear() - birth.getFullYear();
    const monthsDiff = measurement.getMonth() - birth.getMonth();
    let totalMonths = yearsDiff * 12 + monthsDiff;
    
    // Adjust if measurement day is before birth day
    if (measurement.getDate() < birth.getDate()) {
      totalMonths--;
    }
    
    return Math.max(0, totalMonths);
  };

  // Helper: Get allowed months (current month + 3 months back)
  const getAllowedMonths = () => {
    const months = [];
    const today = new Date();
    
    for (let i = 3; i >= 0; i--) {
      const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const monthYear = `${year}-${month}`;
      
      const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
      const label = `${monthNames[date.getMonth()]} ${year}`;
      
      months.push({ value: monthYear, label });
    }
    
    return months;
  };

  // Default bulan pengukuran = bulan ini (format YYYY-MM)
  const todayMonth = (() => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    return `${year}-${month}`;
  })();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    reset,
    watch,
    setValue,
  } = useForm({
    defaultValues: {
      balita_id: balitaId || "",
      bulan_pengukuran: todayMonth,
      tinggi_badan: "",
      berat_badan: "",
      lingkar_lengan: "",
      lingkar_kepala: "",
      catatan: "",
    },
  });

  const watchBalitaId = watch("balita_id");
  const watchBulanPengukuran = watch("bulan_pengukuran");

  useEffect(() => {
    loadBalita();
  }, []);

  useEffect(() => {
    if (watchBulanPengukuran) {
      loadMeasuredBalitas(watchBulanPengukuran);
    }
  }, [watchBulanPengukuran]);

  useEffect(() => {
    if (watchBalitaId) {
      const balita = balitaList.find((b) => b.id === parseInt(watchBalitaId));
      setSelectedBalita(balita);
      if (balita) {
        setSelectedBalitaOption({
          value: balita.id,
          label: `${censorChildName(balita.nama_lengkap)} - ${balita.nik}`,
        });
        // Hitung usia saat bulan pengukuran
        const ageAtMonth = calculateAgeAtMeasurement(balita.tanggal_lahir, watchBulanPengukuran);
        setCalculatedAge(ageAtMonth);
      }
    } else {
      setSelectedBalita(null);
      setSelectedBalitaOption(null);
      setCalculatedAge(null);
    }
  }, [watchBalitaId, watchBulanPengukuran, balitaList]);

  const loadBalita = async () => {
    try {
      const data = await balitaService.getAll({ limit: 500 });
      setBalitaList(data);
    } catch (error) {
      console.error("Error loading balita:", error);
      toast.error("Gagal memuat data balita");
    }
  };

  const loadMeasuredBalitas = async (monthParam) => {
    try {
      const params = { limit: 500, bulan: monthParam };
      const data = await pengukuranService.getAll(params);
      // Extract unique balita_id dari pengukuran bulan ini
      const balitaIds = data.map((p) => p.balita_id);
      setMeasuredBalitasThisMonth([...new Set(balitaIds)]);
    } catch (error) {
      console.error("Error loading measured balitas:", error);
      // Silently fail, jangan toast error karena ini background operation
      setMeasuredBalitasThisMonth([]);
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);

      // Convert bulan_pengukuran (YYYY-MM) to tanggal_pengukuran (YYYY-MM-DD)
      // Logic: 
      // - Jika bulan dipilih adalah bulan sekarang → gunakan tanggal hari ini
      // - Jika bulan dipilih adalah bulan sebelumnya/lewat → gunakan tanggal 1 bulan itu
      const [year, month] = data.bulan_pengukuran.split('-').map(Number);
      const today = new Date();
      const currentYear = today.getFullYear();
      const currentMonth = today.getMonth() + 1;
      
      let tanggalPengukuran;
      
      if (year === currentYear && month === currentMonth) {
        // Bulan sekarang → gunakan tanggal hari ini
        const day = String(today.getDate()).padStart(2, '0');
        tanggalPengukuran = `${year}-${String(month).padStart(2, '0')}-${day}`;
      } else {
        // Bulan lalu atau lewat → gunakan tanggal 1
        tanggalPengukuran = `${year}-${String(month).padStart(2, '0')}-01`;
      }

      // Convert strings to numbers
      const payload = {
        balita_id: parseInt(data.balita_id),
        tanggal_pengukuran: tanggalPengukuran,
        usia_bulan: calculatedAge, // Usia saat diukur (bukan usia balita saat ini)
        tinggi_badan: parseFloat(data.tinggi_badan),
        berat_badan: parseFloat(data.berat_badan),
        lingkar_lengan: parseFloat(data.lingkar_lengan),
        lingkar_kepala: parseFloat(data.lingkar_kepala),
      };

      // Hanya tambahkan catatan jika ada isinya
      if (data.catatan && data.catatan.trim() !== "") {
        payload.catatan = data.catatan;
      }

      const result = await pengukuranService.create(payload);

      // Display 4-class classification in toast
      const classLabel = getClassificationLabel(result.prediksi_stunting);
      toast.success(`Pengukuran berhasil disimpan!\nKlasifikasi: ${classLabel} (${(result.confidence_score * 100).toFixed(1)}%)`);

      reset();
      setSelectedBalita(null);
      setSelectedBalitaOption(null);
      setCalculatedAge(null);

      if (onSuccess) {
        onSuccess(result);
      }
    } catch (error) {
      console.error("Error creating pengukuran:", error);
      toast.error(error.response?.data?.detail || "Gagal menyimpan pengukuran");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto">
      {/* Header dengan Title + Bulan Pengukuran di pojok kanan */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Input Data Pengukuran</h2>
        
        <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center w-full sm:w-auto">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">Bulan Pengukuran:</label>
          <select
            {...register("bulan_pengukuran", { required: "Bulan pengukuran harus dipilih" })}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full sm:w-auto"
          >
            {getAllowedMonths().map((month) => (
              <option key={month.value} value={month.value}>
                {month.label}
              </option>
            ))}
          </select>
          {errors.bulan_pengukuran && (
            <p className="text-xs text-red-600 col-span-full sm:col-span-1">{errors.bulan_pengukuran.message}</p>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Info Balita - Moved to Top */}
        {selectedBalita && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-3 sm:p-4">
            <h3 className="font-semibold text-blue-900 mb-2 text-sm sm:text-base">Informasi Balita</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm">
              <div className="flex items-center">
                <span className="text-gray-600">Jenis Kelamin:</span>
                <span className="ml-2 font-medium">{selectedBalita.jenis_kelamin === "L" ? "Laki-laki" : "Perempuan"}</span>
              </div>
              <div className="flex items-center">
                <span className="text-gray-600">Usia saat pengukuran:</span>
                <span className="ml-2 font-medium text-blue-700">{calculatedAge !== null ? `${calculatedAge} bulan` : 'Pilih bulan'}</span>
              </div>
            </div>
          </div>
        )}

        {/* Pilih Balita with Select2 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Pilih Balita <span className="text-red-600">*</span>
          </label>
          <Select
            value={selectedBalitaOption}
            options={balitaList
              .sort((a, b) => {
                // Balita belum diukur di atas, sudah diukur di bawah
                const aIsMeasured = measuredBalitasThisMonth.includes(a.id);
                const bIsMeasured = measuredBalitasThisMonth.includes(b.id);
                if (aIsMeasured === bIsMeasured) return 0;
                return aIsMeasured ? 1 : -1;
              })
              .map((balita) => ({
                value: balita.id,
                label: measuredBalitasThisMonth.includes(balita.id) 
                  ? `${censorChildName(balita.nama_lengkap)} - ${balita.nik} (Sudah diukur)` 
                  : `${censorChildName(balita.nama_lengkap)} - ${balita.nik}`,
                isDisabled: measuredBalitasThisMonth.includes(balita.id),
              }))}
            onChange={(selectedOption) => {
              setSelectedBalitaOption(selectedOption);
              setValue("balita_id", selectedOption ? selectedOption.value : "", {
                shouldValidate: true,
              });
              if (selectedOption) {
                const balita = balitaList.find((b) => b.id === selectedOption.value);
                setSelectedBalita(balita);
              } else {
                setSelectedBalita(null);
              }
            }}
            placeholder="-- Pilih Balita --"
            isClearable
            isSearchable
            isDisabled={!!balitaId}
            className="text-base"
            styles={{
              control: (base, state) => ({
                ...base,
                minHeight: "48px",
                borderColor: state.isFocused ? "#3b82f6" : "#d1d5db",
                boxShadow: state.isFocused ? "0 0 0 2px rgba(59, 130, 246, 0.3)" : "none",
                "&:hover": {
                  borderColor: "#9ca3af",
                },
              }),
              option: (base, state) => ({
                ...base,
                backgroundColor: state.isSelected ? "#3b82f6" : state.isFocused ? "#dbeafe" : "white",
                color: state.isDisabled ? "#9ca3af" : state.isSelected ? "white" : "#1f2937",
                padding: "12px 16px",
                cursor: state.isDisabled ? "not-allowed" : "pointer",
                opacity: state.isDisabled ? 0.6 : 1,
              }),
              menu: (base) => ({
                ...base,
                zIndex: 9999,
              }),
            }}
          />
          <input type="hidden" {...register("balita_id", { required: "Balita harus dipilih" })} />
          {errors.balita_id && <p className="mt-1 text-sm text-red-600">{errors.balita_id.message}</p>}
        </div>

        {/* Data Pengukuran - Touch-Friendly Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Berat Badan - FIRST */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Berat Badan (kg) <span className="text-red-600">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              inputMode="decimal"
              {...register("berat_badan", {
                required: "Berat badan harus diisi",
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: 12.5"
            />
            {errors.berat_badan && <p className="mt-1 text-xs sm:text-sm text-red-600">{errors.berat_badan.message}</p>}
          </div>

          {/* Tinggi Badan - SECOND */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tinggi Badan (cm) <span className="text-red-600">*</span>
            </label>
            <input
              type="number"
              step="0.1"
              inputMode="decimal"
              {...register("tinggi_badan", {
                required: "Tinggi badan harus diisi",
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: 85.5"
            />
            {errors.tinggi_badan && <p className="mt-1 text-xs sm:text-sm text-red-600">{errors.tinggi_badan.message}</p>}
          </div>

          {/* Lingkar Lengan */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lingkar Lengan Atas (cm) <span className="text-red-600">*</span>
            </label>
            <input
              type="number"
              step="0.1"
              inputMode="decimal"
              {...register("lingkar_lengan", {
                required: "Lingkar lengan harus diisi",
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: 14.2"
            />
            {errors.lingkar_lengan && <p className="mt-1 text-xs sm:text-sm text-red-600">{errors.lingkar_lengan.message}</p>}
          </div>

          {/* Lingkar Kepala */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lingkar Kepala (cm) <span className="text-red-600">*</span>
            </label>
            <input
              type="number"
              step="0.1"
              inputMode="decimal"
              {...register("lingkar_kepala", {
                required: "Lingkar kepala harus diisi",
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: 47.5"
            />
            {errors.lingkar_kepala && <p className="mt-1 text-xs sm:text-sm text-red-600">{errors.lingkar_kepala.message}</p>}
          </div>
        </div>

        {/* Catatan */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Catatan (Opsional)</label>
          <textarea
            {...register("catatan")}
            rows={3}
            className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Catatan tambahan..."
          ></textarea>
        </div>

        {/* Submit Buttons - Mobile Stack */}
        <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 pt-2">
          <button type="button" onClick={() => reset()} className="w-full sm:w-auto px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium transition-colors" disabled={loading}>
            Reset Form
          </button>
          <button type="submit" className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-md transition-colors" disabled={loading}>
            {loading ? "Menyimpan..." : "Simpan"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PengukuranForm;
