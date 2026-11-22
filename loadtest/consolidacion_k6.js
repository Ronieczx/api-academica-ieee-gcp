import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

// Instrumentacion primaria: tiempo interno del servidor (sin ruido de red externa)
const tiempoServidor = new Trend('tiempo_servidor', true);
// Instrumentacion auxiliar: tiempo end-to-end observado por el cliente k6
const tiempoE2E = new Trend('tiempo_e2e', true);

const BASE_URL = (__ENV.BASE_URL || '').replace(/\/$/, '');
const STAGE = (__ENV.STAGE || 'm0').toLowerCase();
const BATCH_SIZE = Number(__ENV.BATCH_SIZE || 100);
const COMMIT_SHA = __ENV.COMMIT_SHA || 'unknown';
const ENFORCE_THRESHOLD = (__ENV.ENFORCE_THRESHOLD || 'false').toLowerCase() === 'true';

const thresholdsConfig = {
  checks: ['rate==1.00'],
};
if (ENFORCE_THRESHOLD) {
  // Umbral operativo predeclarado en la Seccion I: p95 <= 1000 ms (1.0 s)
  thresholdsConfig.tiempo_servidor = ['p(95)<=1000'];
}

export const options = {
  scenarios: {
    secuencial_controlado: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 35, // 5 iteraciones de calentamiento (descartadas) + 30 medidas
      maxDuration: '45m',
    },
  },
  thresholds: thresholdsConfig,
};

function buildStudentCodes(size) {
  const codes = [];
  for (let i = 1; i <= size; i += 1) {
    const padded = String(i).padStart(5, '0');
    codes.push(`STU${padded}`);
  }
  return codes;
}

const PAYLOAD = JSON.stringify({
  student_codes: buildStudentCodes(BATCH_SIZE),
});

export default function () {
  const tags = {
    stage: STAGE,
    batch_size: String(BATCH_SIZE),
    commit: COMMIT_SHA,
  };

  const res = http.post(`${BASE_URL}/api/v1/consolidate`, PAYLOAD, {
    headers: { 'Content-Type': 'application/json' },
    timeout: '180s',
    tags,
  });

  const ok = check(
    res,
    {
      'status es 200': (r) => r.status === 200,
      'etapa coincide': (r) => r.headers['X-Engine-Stage'] === STAGE,
      'batch completo': (r) => {
        try {
          return r.json('batch_size') === BATCH_SIZE;
        } catch (_e) {
          return false;
        }
      },
    },
    tags
  );

  if (ok) {
    const headerMs = Number(res.headers['X-Process-Time-Ms']);
    if (!Number.isNaN(headerMs)) {
      tiempoServidor.add(headerMs, tags);
    }
    tiempoE2E.add(res.timings.duration, tags);
  }
}
