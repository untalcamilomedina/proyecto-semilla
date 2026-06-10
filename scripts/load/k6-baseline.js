/**
 * Prueba de carga base con k6 (https://k6.io).
 *
 * Mide la línea base del seed: login JWT + lecturas autenticadas del
 * dashboard y miembros. Publica números reales antes de prometer escala.
 *
 * Uso (contra el stack local con datos demo):
 *   make seed   # crea admin@demo.com / password y el dominio localhost
 *   k6 run scripts/load/k6-baseline.js
 *
 * Variables: BASE_URL (http://localhost:8000), HOST_HEADER (localhost),
 *            EMAIL (admin@demo.com), PASSWORD (password), VUS (20), DURATION (1m)
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const HOST = __ENV.HOST_HEADER || "localhost";
const EMAIL = __ENV.EMAIL || "admin@demo.com";
const PASSWORD = __ENV.PASSWORD || "password";

const errors = new Rate("errors");

export const options = {
  scenarios: {
    baseline: {
      executor: "constant-vus",
      vus: Number(__ENV.VUS || 20),
      duration: __ENV.DURATION || "1m",
    },
  },
  thresholds: {
    // Criterios de aceptación de la línea base — ajusta y versiona los tuyos.
    http_req_duration: ["p(95)<500", "p(99)<1200"],
    errors: ["rate<0.01"],
  },
};

const params = (token) => ({
  headers: {
    Host: HOST,
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  },
});

export function setup() {
  const res = http.post(
    `${BASE_URL}/api/v1/auth/token/`,
    JSON.stringify({ email: EMAIL, password: PASSWORD }),
    params()
  );
  check(res, { "login 200": (r) => r.status === 200 });
  return { access: res.json("access") };
}

export default function (data) {
  const auth = params(data.access);

  const me = http.get(`${BASE_URL}/api/v1/me/`, auth);
  errors.add(me.status !== 200);
  check(me, { "me 200": (r) => r.status === 200 });

  const dashboard = http.get(`${BASE_URL}/api/v1/dashboard/`, auth);
  errors.add(dashboard.status !== 200);
  check(dashboard, { "dashboard 200": (r) => r.status === 200 });

  const members = http.get(`${BASE_URL}/api/v1/memberships/`, auth);
  errors.add(members.status !== 200);
  check(members, { "members 200": (r) => r.status === 200 });

  sleep(1);
}
