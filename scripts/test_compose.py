"""Validate a running Compose deployment and run isolated backend suites."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SERVICES = ("auth", "catalog", "event", "commerce", "provider")
DATABASES = tuple(f"{service}-db" for service in SERVICES)
SEEDS = tuple(f"{service}-seed" for service in SERVICES)
REQUIRED_RUNNING = SERVICES + DATABASES + ("frontend",)
EXPECTED_SERVICES = set(REQUIRED_RUNNING + SEEDS)
LOG_LINES = 40

WORKER = r'''
import os
from pathlib import Path
import subprocess
import sys
import psycopg
from psycopg import sql
from dotenv import set_key

service = sys.argv[1]
database = {'auth':'auth','catalog':'catalog','event':'events','commerce':'commerce','provider':'providers'}[service]
test_name = f'subsonic_{database}_test'
assert test_name.endswith('_test')
with psycopg.connect(host=os.environ['DB_HOST'], port=os.environ['DB_PORT'],
                     user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
                     dbname='postgres', autocommit=True) as db:
    for name in (test_name, f'subsonic_{database}_seed_test'):
        if not db.execute('SELECT 1 FROM pg_database WHERE datname=%s', (name,)).fetchone():
            db.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
config = {key: os.environ[key] for key in ('DB_HOST','DB_PORT','DB_USER','DB_PASSWORD')}
config['DB_NAME'] = test_name
config['AUTH_SERVICE_URL'] = 'http://auth:8000'
config['EVENT_SERVICE_URL'] = 'http://event:8000'
config['CATALOG_SERVICE_URL'] = 'http://catalog:8000'
for key, value in config.items():
    set_key('.env.test', key, value)
subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'], check=True)
subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q', '-p', 'no:cacheprovider'], check=True)
subprocess.run([sys.executable, '-m', 'pytest', '/app/tests/test_setup.py', '-k', service,
                '-q', '-p', 'no:cacheprovider'], check=True)
'''


class ComposeValidationError(RuntimeError):
    """A Docker/Compose validation phase failed."""


def redact(text):
    """Avoid exposing common credential/token values in captured output."""
    patterns = (
        (r"(?i)(password\s*[=:]\s*)[^\s,]+", r"\1[REDACTED]"),
        (r"(?i)(token\s*[=:]\s*)[^\s,]+", r"\1[REDACTED]"),
        (r"(?i)(authorization:\s*bearer\s+)[^\s]+", r"\1[REDACTED]"),
        (r"(?i)(jwt_secret_key\s*[=:]\s*)[^\s,]+", r"\1[REDACTED]"),
    )
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text


def command(args, project):
    return ["docker", "compose", "-p", project, *args]


def combined_output(result):
    """Return captured command output even when one stream is unavailable."""
    return ((result.stdout or "") + (result.stderr or "")).strip()


def run_command(args, project, *, check=False):
    return subprocess.run(
        command(args, project),
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )


def compose_logs(service, project):
    result = run_command(["logs", "--no-color", "--tail", str(LOG_LINES), service], project)
    output = combined_output(result)
    return redact(output) if output else "<no logs>"


def parse_ps(output):
    """Parse Compose JSON output, accepting array or one-object-per-line forms."""
    output = output.strip()
    if not output:
        return []
    try:
        parsed = json.loads(output)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        records = []
        for line in output.splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ComposeValidationError(
                    f"docker compose ps devolvió JSON inválido: {line!r}"
                ) from exc
        return records


def record_service(record):
    service = record.get("Service") or record.get("service")
    state = record.get("State") or record.get("state") or "unknown"
    health = record.get("Health") or record.get("health") or "none"
    exit_code = record.get("ExitCode", record.get("exitcode"))
    return service, str(state).lower(), str(health).lower(), exit_code


def validate_docker_and_config(project):
    try:
        docker = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise ComposeValidationError(f"Docker no está disponible: {exc}") from exc
    if docker.returncode != 0:
        raise ComposeValidationError(
            "Docker no está disponible o el daemon no responde:\n"
            + redact((docker.stderr or "").strip())
        )
    print(f"[ OK ] Docker daemon disponible ({(docker.stdout or '').strip()})")

    config = run_command(["config", "--quiet"], project)
    if config.returncode != 0:
        raise ComposeValidationError(
            "Fase Compose config: configuración inválida:\n"
            + redact(combined_output(config))
        )
    print("[ OK ] docker compose config --quiet")

    services = run_command(["config", "--services"], project)
    if services.returncode != 0:
        raise ComposeValidationError(
            "Fase Compose services: no se pudieron consultar los servicios:\n"
            + redact((services.stderr or "").strip())
        )
    actual = set((services.stdout or "").split())
    missing = sorted(EXPECTED_SERVICES - actual)
    if missing:
        raise ComposeValidationError(
            "Fase Compose services: faltan servicios esperados: "
            + ", ".join(missing)
        )
    print(f"[ OK ] servicios Compose esperados ({len(EXPECTED_SERVICES)})")


def validate_container_state(project):
    result = run_command(["ps", "--all", "--format", "json"], project)
    if result.returncode != 0:
        raise ComposeValidationError(
            "Fase estado de contenedores: no se pudo ejecutar docker compose ps:\n"
            + redact(combined_output(result))
        )
    records = parse_ps(result.stdout or "")
    states = {}
    for record in records:
        service, state, health, exit_code = record_service(record)
        if service:
            states[service] = (state, health, exit_code)

    for service in REQUIRED_RUNNING:
        if service not in states:
            raise ComposeValidationError(
                f"Fase estado de contenedores: falta el contenedor de {service}."
            )
        state, health, exit_code = states[service]
        if state != "running":
            raise ComposeValidationError(
                f"Fase estado de contenedores: {service} está {state} "
                f"(health={health}, exit={exit_code}).\nLogs:\n{compose_logs(service, project)}"
            )
        if health != "healthy":
            raise ComposeValidationError(
                f"Fase healthcheck: {service} está running pero health={health}; "
                "se esperaba healthy.\n"
                f"Logs:\n{compose_logs(service, project)}"
            )
        print(f"[ OK ] {service}: running, health={health}")

    for service in SEEDS:
        if service not in states:
            raise ComposeValidationError(
                f"Fase seeds: falta el contenedor de inicialización {service}."
            )
        state, health, exit_code = states[service]
        if state == "running":
            print(f"[ OK ] {service}: seed todavía ejecutándose")
        elif state == "exited" and str(exit_code) == "0":
            print(f"[ OK ] {service}: terminó correctamente (exit=0)")
        else:
            raise ComposeValidationError(
                f"Fase seeds: {service} terminó con estado={state}, "
                f"health={health}, exit={exit_code}.\n"
                f"Logs:\n{compose_logs(service, project)}"
            )


def run_service_tests(service, project):
    print(f"[ RUN ] suites de {service}")
    result = subprocess.run(
        command(
            [
                "run", "--rm", "-T", "--no-deps", f"{service}-seed",
                "python", "-", service,
            ],
            project,
        ),
        cwd=ROOT,
        input=WORKER,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    output = redact(combined_output(result))
    if result.returncode != 0:
        raise ComposeValidationError(
            f"Fase tests de {service}: exit={result.returncode}.\n"
            f"Salida:\n{output}\nLogs del servicio:\n{compose_logs(service, project)}"
        )
    print(output or f"[ OK ] suites de {service}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="subsonic")
    parser.add_argument("--service", choices=SERVICES)
    args = parser.parse_args()

    try:
        validate_docker_and_config(args.project)
        validate_container_state(args.project)
        services = (args.service,) if args.service else SERVICES
        for service in services:
            run_service_tests(service, args.project)
    except (ComposeValidationError, OSError) as exc:
        print(f"[FAIL] Validación Docker: {exc}", file=sys.stderr)
        return 1
    print("Overall result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
