'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../../stores/auth-store';

interface RegisterFormData {
  nombre_completo: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
  telefono?: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState<RegisterFormData>({
    nombre_completo: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    telefono: ''
  });
  const [successMessage, setSuccessMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setSuccessMessage('');

    // Validar que las contraseñas coincidan
    if (formData.password !== formData.confirmPassword) {
      // Usar el error del store para mostrar este error
      return;
    }

    // Validar longitud mínima de contraseña
    if (formData.password.length < 6) {
      return;
    }

    try {
      // Preparar datos para el auth store
      const registerData = {
        first_name: formData.nombre_completo.split(' ')[0] || '',
        last_name: formData.nombre_completo.split(' ').slice(1).join(' ') || '',
        email: formData.email,
        password: formData.password,
        tenant_id: '' // El backend maneja la creación automática de tenant si no se proporciona
      };

      await register(registerData);

      // Registro exitoso
      setSuccessMessage('¡Registro exitoso! Redirigiendo al login...');

      // Redirigir al login después de 2 segundos
      setTimeout(() => {
        router.push('/login?registered=true');
      }, 2000);

    } catch (err) {
      // Error is handled by the store
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Crear Cuenta
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Regístrate en Proyecto Semilla
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {successMessage}
          </div>
        )}
        
        <div className="space-y-4">
          {/* Nombre Completo */}
          <div>
            <label 
              htmlFor="nombre_completo" 
              className="block text-sm font-medium text-gray-700"
            >
              Nombre Completo *
            </label>
            <input
              id="nombre_completo"
              name="nombre_completo"
              type="text"
              placeholder="Juan Pérez"
              value={formData.nombre_completo}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isLoading}
            />
          </div>

          {/* Email */}
          <div>
            <label 
              htmlFor="email" 
              className="block text-sm font-medium text-gray-700"
            >
              Email *
            </label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder="usuario@ejemplo.com"
              value={formData.email}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isLoading}
            />
          </div>

          {/* Username */}
          <div>
            <label 
              htmlFor="username" 
              className="block text-sm font-medium text-gray-700"
            >
              Nombre de Usuario *
            </label>
            <input
              id="username"
              name="username"
              type="text"
              placeholder="juanperez"
              value={formData.username}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isLoading}
            />
          </div>

          {/* Teléfono (opcional) */}
          <div>
            <label
              htmlFor="telefono"
              className="block text-sm font-medium text-gray-700"
            >
              Teléfono (opcional)
            </label>
            <input
              id="telefono"
              name="telefono"
              type="tel"
              placeholder="+57 300 123 4567"
              value={formData.telefono}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              disabled={isLoading}
            />
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Contraseña *
            </label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isLoading}
              minLength={6}
            />
            <p className="mt-1 text-xs text-gray-500">
              Mínimo 6 caracteres
            </p>
          </div>

          {/* Confirmar Password */}
          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700"
            >
              Confirmar Contraseña *
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={isLoading}
              minLength={6}
            />
            {formData.confirmPassword && formData.password !== formData.confirmPassword && (
              <p className="mt-1 text-xs text-red-600">
                Las contraseñas no coinciden
              </p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || (!!formData.confirmPassword && formData.password !== formData.confirmPassword)}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Registrando...' : 'Crear Cuenta'}
        </button>

        <div className="text-sm text-center">
          <span className="text-gray-600">¿Ya tienes cuenta? </span>
          <a 
            href="/login" 
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Inicia sesión aquí
          </a>
        </div>

        <div className="text-xs text-center text-gray-500 mt-4">
          <p>* Campos obligatorios</p>
        </div>
      </form>
    </div>
  );
}