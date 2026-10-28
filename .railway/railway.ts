// tURL's Railway settings. The CLI evaluates this file; Railway never reads it during a
// deploy, so nothing here takes effect until `railway config apply` runs.
//
// It replaces `turl.toml` (Config as Code), which Railway stops reading on 2026-12-01.
// Every value below is what the service's last deployment actually ran with.
import { defineRailway, github, preserve, project, service } from 'railway/iac'

// Mark 0 also runs Athlo, Slip, Picko, Portfolio and tURL-UI from their own repositories,
// so this file is a named partial: it owns the one tURL service it declares and nothing
// else. The shared Postgres is left alone.
export const partial = 'turl'

/**
 * Variables whose values stay on Railway. A variable the file leaves out is deleted on apply,
 * so every name the service holds is listed here; set a new one in Railway and add its name.
 */
function onRailway(...names: string[]) {
  return Object.fromEntries(names.map((name) => [name, preserve()]))
}

export default defineRailway(() => {
  const api = service('tURL', {
    source: github('SatoriAI/tURL', { branch: 'main', checkSuites: false }),
    build: { buildEnvironment: 'V3', builder: 'DOCKERFILE', dockerfilePath: './Dockerfile' },
    // `sh -c`, because a start command gets no shell and `$PORT` and `$WORKERS` would
    // arrive literally. The worker count is the `WORKERS` variable, not a number here.
    start: "sh -c 'gunicorn -k uvicorn.workers.UvicornWorker source.app:app --bind 0.0.0.0:$PORT --workers $WORKERS'",
    preDeploy: 'uv run --no-sync --no-dev alembic upgrade head',
    healthcheck: '/status',
    // Sleeps when idle: a link shortener's traffic does not justify an always-on
    // container. Set by API on 2026-10-27; declared here so an apply does not undo it.
    deploy: { sleepApplication: true },
    replicas: { 'europe-west4-drams3a': 1 },
    domains: [
      { domain: 'turl.info', port: 8000 },
      { domain: 'www.turl.info', port: 8000 },
    ],
    networking: { privateNetworkEndpoint: 'turl-server' },
    env: onRailway(
      'CORS_ORIGINS',
      'DATABASE_URL',
      'DOMAIN',
      'FRONTEND',
      'MAX_CODE_GENERATION_ATTEMPTS',
      'PORT',
      'RATE_LIMIT_REQUESTS',
      'RATE_LIMIT_WINDOW_SECONDS',
      'WORKERS',
    ),
  })

  return project('Mark 0', { resources: [api] })
})
