'use client';

import { useRouter } from 'next/navigation';
import { SystemRequirements } from '@/types/setup';

interface Step3Props {
  adminEmail: string;
  requirementsData: SystemRequirements | null;
}

export default function Step3Completion({ adminEmail, requirementsData }: Step3Props) {
  const router = useRouter();

  const handleGoToDashboard = () => {
    // Redirect to dashboard
    router.push('/dashboard');
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-4">
          <span className="text-5xl">🎉</span>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          ¡Configuración Completada!
        </h2>
        <p className="text-lg text-gray-600">
          Tu instancia de Proyecto Semilla está lista para usar
        </p>
      </div>

      {/* Success summary */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6">
        <h3 className="font-semibold text-green-900 mb-4 flex items-center">
          <span className="text-2xl mr-2">✓</span>
          Resumen de Configuración
        </h3>

        <div className="space-y-3">
          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <div>
              <p className="font-medium text-gray-900">Sistema Verificado</p>
              <p className="text-sm text-gray-600">
                Todos los servicios necesarios están funcionando correctamente
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <div>
              <p className="font-medium text-gray-900">Cuenta de Administrador Creada</p>
              <p className="text-sm text-gray-600">
                Email: <span className="font-mono bg-white px-2 py-0.5 rounded">{adminEmail}</span>
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <div>
              <p className="font-medium text-gray-900">Rol de Superadministrador Asignado</p>
              <p className="text-sm text-gray-600">
                Tienes acceso completo a todas las funciones del sistema
              </p>
            </div>
          </div>

          <div className="flex items-start">
            <span className="text-green-600 mr-2">✓</span>
            <div>
              <p className="font-medium text-gray-900">Base de Datos Configurada</p>
              <p className="text-sm text-gray-600">
                Multi-tenancy y seguridad activados
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Next steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-3 flex items-center">
          <span className="text-xl mr-2">💡</span>
          Próximos Pasos Recomendados
        </h3>

        <ol className="space-y-2 list-decimal list-inside text-sm text-gray-700">
          <li>Explora el panel de administración</li>
          <li>Crea tenants adicionales si es necesario</li>
          <li>Invita a otros usuarios y asigna roles</li>
          <li>Personaliza la configuración según tus necesidades</li>
          <li>Configura HTTPS/SSL para producción</li>
        </ol>
      </div>

      {/* Warning for production */}
      {requirementsData?.warnings && requirementsData.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="font-semibold text-yellow-900 mb-3 flex items-center">
            <span className="text-xl mr-2">⚠️</span>
            Recordatorios de Seguridad
          </h3>

          <ul className="space-y-1 list-disc list-inside text-sm text-yellow-800">
            <li>Configura COOKIE_SECURE=true cuando uses HTTPS</li>
            <li>Cambia las credenciales por defecto en producción</li>
            <li>Configura backups automáticos de la base de datos</li>
            <li>Revisa los logs periódicamente</li>
          </ul>
        </div>
      )}

      {/* Resources */}
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-6">
        <h3 className="font-semibold text-gray-900 mb-3">📚 Recursos Útiles</h3>

        <div className="space-y-2 text-sm">
          <a
            href="/api/v1/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-indigo-600 hover:text-indigo-700 hover:underline"
          >
            → Documentación de la API
          </a>
          <a
            href="https://github.com/proyecto-semilla"
            target="_blank"
            rel="noopener noreferrer"
            className="block text-indigo-600 hover:text-indigo-700 hover:underline"
          >
            → Repositorio en GitHub
          </a>
          <a
            href="/dashboard/users"
            className="block text-indigo-600 hover:text-indigo-700 hover:underline"
          >
            → Gestión de Usuarios
          </a>
          <a
            href="/dashboard/roles"
            className="block text-indigo-600 hover:text-indigo-700 hover:underline"
          >
            → Gestión de Roles y Permisos
          </a>
        </div>
      </div>

      {/* Action button */}
      <div className="flex justify-center pt-6">
        <button
          onClick={handleGoToDashboard}
          className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-lg font-semibold rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg flex items-center space-x-2"
        >
          <span>Ir al Dashboard</span>
          <span className="text-2xl">→</span>
        </button>
      </div>

      {/* Footer note */}
      <p className="text-center text-sm text-gray-500 italic mt-6">
        ¡Gracias por elegir Proyecto Semilla! 🌱
      </p>
    </div>
  );
}
