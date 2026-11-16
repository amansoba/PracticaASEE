#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
out="$(mktemp -d "${TMPDIR:-/tmp}/subsonic-openapi.XXXXXXXX")"
version=7.26.0
echo "Generating review candidates in $out (existing generated/ is never overwritten)"
for service in auth catalog event commerce provider; do
  if [[ -n "${OPENAPI_GENERATOR_JAR:-}" ]]; then
    java -jar "$OPENAPI_GENERATOR_JAR" generate -g python-fastapi \
      -i "$root/$service-service/openapi.yaml" -o "$out/$service-service"
  else
    docker run --rm -v "$root:/input:ro" -v "$out:/output" \
      "openapitools/openapi-generator-cli:v$version" generate -g python-fastapi \
      -i "/input/$service-service/openapi.yaml" -o "/output/$service-service"
  fi
done
echo "Review and port changes manually from $out; do not replace handwritten implementations."
