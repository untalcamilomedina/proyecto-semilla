/**
 * Types for the setup wizard
 */

export interface SystemRequirements {
  database_connected: boolean;
  redis_connected: boolean;
  ports_available: boolean;
  disk_space_sufficient: boolean;
  all_requirements_met: boolean;
  issues: string[];
  warnings: string[];
}

export interface SetupConfiguration {
  database_password: string;
  jwt_secret: string;
  cookie_secure: boolean;
  cors_origins: string[];
  environment: 'development' | 'production';
}

export interface SetupStatus {
  needs_setup: boolean;
  real_user_count: number;
  total_user_count: number;
  setup_completed: boolean;
  message: string;
}

export interface ProductionReadiness {
  ready_for_production: boolean;
  issues: string[];
  warnings: string[];
  checks_passed: number;
  total_checks: number;
}

export interface GeneratedSecrets {
  jwt_secret: string;
  db_password: string;
  note: string;
}

export interface WizardStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}
