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
      tinggi_badan: "",
      berat_badan: "",
      lingkar_lengan: "",
      lingkar_kepala: "",
      catatan: "",
    },
  });

  const watchBalitaId = watch("balita_id");

  useEffect(() => {
    loadBalita();
  }, []);

  useEffect(() => {
    if (watchBalitaId) {
      const balita = balitaList.find((b) => b.id === parseInt(watchBalitaId));
      setSelectedBalita(balita);
      if (balita) {
        setSelectedBalitaOption({
          value: balita.id,
          label: `${censorChildName(balita.nama_lengkap)} - ${balita.nik}`,
        });
      }
    } else {
      setSelectedBalita(null);
      setSelectedBalitaOption(null);
    }
  }, [watchBalitaId, balitaList]);

  const loadBalita = async () => {
    try {
      const data = await balitaService.getAll({ limit: 500 });
      setBalitaList(data);
    } catch (error) {
      console.error("Error loading balita:", error);
      toast.error("Gagal memuat data balita");
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);

      // Convert strings to numbers
      const payload = {
        balita_id: parseInt(data.balita_id),
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

      toast.success(`Pengukuran berhasil disimpan!\nPrediksi: ${result.prediksi_stunting ? "STUNTING" : "NORMAL"} (${(result.confidence_score * 100).toFixed(1)}%)`);

      reset();
      setSelectedBalita(null);
      setSelectedBalitaOption(null);

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
      <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">✏️ Input Data Pengukuran</h2>

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
                <span className="text-gray-600">Usia:</span>
                <span className="ml-2 font-medium">{selectedBalita.usia_bulan} bulan</span>
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
            options={balitaList.map((balita) => ({
              value: balita.id,
              label: `${censorChildName(balita.nama_lengkap)} - ${balita.nik}`,
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
                color: state.isSelected ? "white" : "#1f2937",
                padding: "12px 16px",
                cursor: "pointer",
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
