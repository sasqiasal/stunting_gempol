/**
 * Form Tambah/Edit Balita
 * Form untuk input data balita baru
 */

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import Select from 'react-select';
import { balitaService } from '../services/balitaService';
import { posyanduService } from '../services/posyanduService';
import { useAuthStore } from '../store/authStore';

export const BalitaForm = ({ balita, onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [posyanduList, setPosyanduList] = useState([]);
  const [selectedPosyanduOption, setSelectedPosyanduOption] = useState(null);
  const { user } = useAuthStore();
  const isKader = user?.role === 'kader';
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    reset,
  } = useForm({
    defaultValues: balita || {
      nik: '',
      nama_lengkap: '',
      jenis_kelamin: '',
      tanggal_lahir: '',
      nama_orang_tua: '',
      alamat: '',
      posyandu_id: isKader && user?.posyandu_id ? user.posyandu_id : '',
    },
  });

  useEffect(() => {
    loadPosyandu();
  }, []);

  useEffect(() => {
    if (balita && posyanduList.length > 0) {
      const posyandu = posyanduList.find(p => p.id === balita.posyandu_id);
      if (posyandu) {
        setSelectedPosyanduOption({
          value: posyandu.id,
          label: posyandu.nama,
        });
        setValue('posyandu_id', posyandu.id, { shouldValidate: true });
      }
    } else if (isKader && user?.posyandu_id && posyanduList.length > 0) {
      // Auto-fill posyandu untuk kader
      const kaderPosyandu = posyanduList.find(p => p.id === user.posyandu_id);
      if (kaderPosyandu) {
        setSelectedPosyanduOption({
          value: kaderPosyandu.id,
          label: kaderPosyandu.nama,
        });
        setValue('posyandu_id', kaderPosyandu.id, { shouldValidate: true });
        console.log('✅ Auto-filled posyandu untuk kader:', kaderPosyandu.nama, kaderPosyandu.id);
      }
    }
  }, [balita, posyanduList, isKader, user, setValue]);

  const loadPosyandu = async () => {
    try {
      const data = await posyanduService.getAll();
      setPosyanduList(data);
    } catch (error) {
      console.error('Error loading posyandu:', error);
      toast.error('Gagal memuat data posyandu');
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      const payload = {
        ...data,
        posyandu_id: parseInt(data.posyandu_id),
      };
      
      // Untuk kader, pastikan posyandu_id dari user jika tidak ada di form
      if (isKader && !payload.posyandu_id && user?.posyandu_id) {
        payload.posyandu_id = user.posyandu_id;
      }

      if (balita) {
        await balitaService.update(balita.id, payload);
        toast.success('Data balita berhasil diperbarui!');
      } else {
        await balitaService.create(payload);
        toast.success('Data balita berhasil ditambahkan!');
      }
      
      reset();
      setSelectedPosyanduOption(null);
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Error saving balita:', error);
      toast.error(error.response?.data?.detail || 'Gagal menyimpan data balita');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg p-4 sm:p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">
          {balita ? 'Edit Data Balita' : '✏️ Tambah Data Balita'}
        </h2>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* NIK */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              NIK <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              {...register('nik', {
                required: 'NIK harus diisi',
                minLength: { value: 16, message: 'NIK harus 16 digit' },
                maxLength: { value: 16, message: 'NIK harus 16 digit' },
                pattern: { value: /^[0-9]+$/, message: 'NIK harus berupa angka' },
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: 3507120120230001"
              maxLength={16}
            />
            {errors.nik && (
              <p className="mt-1 text-sm text-red-600">{errors.nik.message}</p>
            )}
          </div>

          {/* Nama Lengkap */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nama Lengkap <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              {...register('nama_lengkap', {
                required: 'Nama lengkap harus diisi',
                minLength: { value: 3, message: 'Nama minimal 3 karakter' },
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: Ahmad Zaki"
            />
            {errors.nama_lengkap && (
              <p className="mt-1 text-sm text-red-600">{errors.nama_lengkap.message}</p>
            )}
          </div>

          {/* Jenis Kelamin */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jenis Kelamin <span className="text-red-600">*</span>
            </label>
            <select
              {...register('jenis_kelamin', { required: 'Jenis kelamin harus dipilih' })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">-- Pilih Jenis Kelamin --</option>
              <option value="L">Laki-laki</option>
              <option value="P">Perempuan</option>
            </select>
            {errors.jenis_kelamin && (
              <p className="mt-1 text-sm text-red-600">{errors.jenis_kelamin.message}</p>
            )}
          </div>

          {/* Tanggal Lahir */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tanggal Lahir <span className="text-red-600">*</span>
            </label>
            <input
              type="date"
              {...register('tanggal_lahir', {
                required: 'Tanggal lahir harus diisi',
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            {errors.tanggal_lahir && (
              <p className="mt-1 text-sm text-red-600">{errors.tanggal_lahir.message}</p>
            )}
          </div>

          {/* Nama Orang Tua */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nama Orang Tua <span className="text-red-600">*</span>
            </label>
            <input
              type="text"
              {...register('nama_orang_tua', {
                required: 'Nama orang tua harus diisi',
                minLength: { value: 3, message: 'Nama minimal 3 karakter' },
              })}
              className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Contoh: Budi Santoso"
            />
            {errors.nama_orang_tua && (
              <p className="mt-1 text-sm text-red-600">{errors.nama_orang_tua.message}</p>
            )}
          </div>

          {/* Posyandu */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Posyandu <span className="text-red-600">*</span>
              {isKader && <span className="text-xs text-gray-500 ml-2">(Otomatis terisi sesuai posyandu Anda)</span>}
            </label>
            <Select
              value={selectedPosyanduOption}
              options={posyanduList.map((posyandu) => ({
                value: posyandu.id,
                label: posyandu.nama,
              }))}
              onChange={(selectedOption) => {
                setSelectedPosyanduOption(selectedOption);
                setValue('posyandu_id', selectedOption ? selectedOption.value : '', {
                  shouldValidate: true,
                });
              }}
              placeholder="-- Pilih Posyandu --"
              isClearable={!isKader}
              isSearchable={!isKader}
              isDisabled={isKader}
              className="text-base"
              styles={{
                control: (base, state) => ({
                  ...base,
                  minHeight: '48px',
                  borderColor: state.isFocused ? '#3b82f6' : '#d1d5db',
                  backgroundColor: isKader ? '#f3f4f6' : base.backgroundColor,
                  boxShadow: state.isFocused ? '0 0 0 2px rgba(59, 130, 246, 0.3)' : 'none',
                  '&:hover': {
                    borderColor: '#9ca3af',
                  },
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isSelected
                    ? '#3b82f6'
                    : state.isFocused
                    ? '#dbeafe'
                    : 'white',
                  color: state.isSelected ? 'white' : '#1f2937',
                  padding: '12px 16px',
                  cursor: 'pointer',
                }),
                menu: (base) => ({
                  ...base,
                  zIndex: 9999,
                }),
              }}
            />
            <input
              type="hidden"
              {...register('posyandu_id', { 
                required: isKader ? false : 'Posyandu harus dipilih',
                validate: (value) => {
                  // Untuk kader, gunakan posyandu_id dari user jika tidak ada value
                  if (isKader && !value && user?.posyandu_id) {
                    setValue('posyandu_id', user.posyandu_id);
                    return true;
                  }
                  return isKader || !!value || 'Posyandu harus dipilih';
                }
              })}
            />
            {errors.posyandu_id && (
              <p className="mt-1 text-sm text-red-600">{errors.posyandu_id.message}</p>
            )}
          </div>
        </div>

        {/* Alamat */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Alamat <span className="text-red-600">*</span>
          </label>
          <textarea
            {...register('alamat', {
              required: 'Alamat harus diisi',
              minLength: { value: 10, message: 'Alamat minimal 10 karakter' },
            })}
            rows={3}
            className="w-full px-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Contoh: Jl. Merdeka No. 123, RT 01 RW 02, Desa Gempol"
          ></textarea>
          {errors.alamat && (
            <p className="mt-1 text-sm text-red-600">{errors.alamat.message}</p>
          )}
        </div>

        {/* Submit Buttons */}
        <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 pt-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="w-full sm:w-auto px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 font-medium transition-colors"
              disabled={loading}
            >
              Batal
            </button>
          )}
          <button
            type="submit"
            className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-md transition-colors"
            disabled={loading}
          >
            {loading ? 'Menyimpan...' : 'Simpan'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default BalitaForm;
