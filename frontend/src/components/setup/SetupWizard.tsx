'use client';

import { useState } from 'react';
import { SystemRequirements, WizardStep } from '@/types/setup';
import Step1Requirements from './Step1Requirements';
import Step2CreateAdmin from './Step2CreateAdmin';
import Step3Completion from './Step3Completion';

const STEPS: WizardStep[] = [
  {
    id: 1,
    title: 'Verificación del Sistema',
    description: 'Comprobando requisitos',
    completed: false
  },
  {
    id: 2,
    title: 'Crear Superadministrador',
    description: 'Configurar usuario administrador',
    completed: false
  },
  {
    id: 3,
    title: 'Finalización',
    description: 'Todo listo',
    completed: false
  }
];

export default function SetupWizard() {
  const [currentStep, setCurrentStep] = useState(1);
  const [steps, setSteps] = useState<WizardStep[]>(STEPS);
  const [requirementsData, setRequirementsData] = useState<SystemRequirements | null>(null);
  const [adminEmail, setAdminEmail] = useState('');

  const markStepCompleted = (stepId: number) => {
    setSteps(prev => prev.map(step =>
      step.id === stepId ? { ...step, completed: true } : step
    ));
  };

  const goToNextStep = () => {
    markStepCompleted(currentStep);
    setCurrentStep(prev => Math.min(prev + 1, steps.length));
  };

  const goToPreviousStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const onRequirementsChecked = (data: SystemRequirements) => {
    setRequirementsData(data);
    if (data.all_requirements_met) {
      goToNextStep();
    }
  };

  const onAdminCreated = (email: string) => {
    setAdminEmail(email);
    goToNextStep();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4 shadow-lg">
            <span className="text-4xl">🌱</span>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Bienvenido a Proyecto Semilla
          </h1>
          <p className="text-lg text-gray-600">
            Configuración inicial en 3 pasos simples
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex-1 flex items-center">
                {/* Step Circle */}
                <div className="relative flex flex-col items-center flex-1">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all ${
                      step.completed
                        ? 'bg-green-500 text-white'
                        : currentStep === step.id
                        ? 'bg-indigo-600 text-white ring-4 ring-indigo-200'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {step.completed ? '✓' : step.id}
                  </div>
                  <div className="mt-2 text-center">
                    <div
                      className={`text-sm font-medium ${
                        currentStep === step.id ? 'text-indigo-600' : 'text-gray-600'
                      }`}
                    >
                      {step.title}
                    </div>
                    <div className="text-xs text-gray-500">{step.description}</div>
                  </div>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-2 transition-all ${
                      step.completed ? 'bg-green-500' : 'bg-gray-200'
                    }`}
                    style={{ marginTop: '-60px' }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 p-8">
          {currentStep === 1 && (
            <Step1Requirements
              onNext={onRequirementsChecked}
              requirementsData={requirementsData}
            />
          )}

          {currentStep === 2 && (
            <Step2CreateAdmin
              onNext={onAdminCreated}
              onBack={goToPreviousStep}
            />
          )}

          {currentStep === 3 && (
            <Step3Completion
              adminEmail={adminEmail}
              requirementsData={requirementsData}
            />
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            ¿Necesitas ayuda? Consulta la{' '}
            <a
              href="https://github.com/proyecto-semilla"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-600 hover:text-indigo-700 font-medium"
            >
              documentación
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
