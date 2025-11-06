'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { SystemRequirements } from '@/types/setup';

interface Step1Props {
  onNext: (data: SystemRequirements) => void;
  requirementsData: SystemRequirements | null;
}

export default function Step1Requirements({ onNext, requirementsData }: Step1Props) {
  const [loading, setLoading] = useState(false);
  const [requirements, setRequirements] = useState<SystemRequirements | null>(
    requirementsData
  );
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Auto-check on mount if not already checked
    if (!requirements) {
      handleCheck();
    }
  }, []);

  const handleCheck = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.checkSystemRequirements();
      setRequirements(data);

      if (data.all_requirements_met) {
        // Auto-advance after a short delay to show success
        setTimeout(() => {
          onNext(data);
        }, 1500);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al verificar requisitos del sistema');
      console.error('Requirements check failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderCheckItem = (
    label: string,
    status: boolean | undefined,
    icon: string
  ) => (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{icon}</span>
        <span className="font-medium text-gray-700">{label}</span>
      </div>
      <div>
        {status === undefined ? (
          <div className="w-6 h-6 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"></div>
        ) : status ? (
          <span className="text-green-500 text-2xl">✓</span>
        ) : (
          <span className="text-red-500 text-2xl">✗</span>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Verificación del Sistema
        </h2>
        <p className="text-gray-600">
          Comprobando que todos los servicios necesarios estén funcionando
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start">
            <span className="text-red-500 text-xl mr-2">⚠️</span>
            <div>
              <p className="font-medium text-red-800">Error de verificación</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {renderCheckItem(
          'Conexión a Base de Datos',
          requirements?.database_connected,
          '🗄️'
        )}
        {renderCheckItem(
          'Conexión a Redis',
          requirements?.redis_connected,
          '⚡'
        )}
        {renderCheckItem(
          'Puertos Disponibles',
          requirements?.ports_available,
          '🔌'
        )}
        {renderCheckItem(
          'Espacio en Disco',
          requirements?.disk_space_sufficient,
          '💾'
        )}
      </div>

      {requirements && requirements.issues.length > 0 && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="font-medium text-red-800 mb-2">Problemas Encontrados:</h4>
          <ul className="list-disc list-inside space-y-1">
            {requirements.issues.map((issue, index) => (
              <li key={index} className="text-sm text-red-600">
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      {requirements && requirements.warnings.length > 0 && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-medium text-yellow-800 mb-2">Advertencias:</h4>
          <ul className="list-disc list-inside space-y-1">
            {requirements.warnings.map((warning, index) => (
              <li key={index} className="text-sm text-yellow-600">
                {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      {requirements && requirements.all_requirements_met && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-green-500 text-2xl mr-2">✓</span>
            <div>
              <p className="font-medium text-green-800">
                ¡Todos los requisitos cumplidos!
              </p>
              <p className="text-sm text-green-600 mt-1">
                Avanzando al siguiente paso...
              </p>
            </div>
          </div>
        </div>
      )}

      {!loading && requirements && !requirements.all_requirements_met && (
        <div className="flex justify-end mt-6">
          <button
            onClick={handleCheck}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
          >
            Reintentar Verificación
          </button>
        </div>
      )}

      {loading && (
        <div className="flex justify-center mt-6">
          <div className="flex items-center space-x-2 text-indigo-600">
            <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Verificando sistema...</span>
          </div>
        </div>
      )}
    </div>
  );
}
