#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
out="$(mktemp -d "${TMPDIR:-/tmp}/subsonic-openapi.XXXXXXXX")"
version=7.26.0
input_mount="$root"
output_mount="$out"
if command -v cygpath >/dev/null 2>&1; then
  input_mount="$(cygpath -w "$root")"
  output_mount="$(cygpath -w "$out")"
fi
echo "Generating review candidates in $out (existing generated/ is never overwritten)"
for service in auth catalog event commerce provider; do
  if [[ -n "${OPENAPI_GENERATOR_JAR:-}" ]]; then
    java -jar "$OPENAPI_GENERATOR_JAR" generate -g python-fastapi \
      -i "$root/$service-service/openapi.yaml" -o "$out/$service-service"
  else
    MSYS_NO_PATHCONV=1 docker run --rm -v "$input_mount:/input:ro" -v "$output_mount:/output" \
      "openapitools/openapi-generator-cli:v$version" generate -g python-fastapi \
      -i "/input/$service-service/openapi.yaml" -o "/output/$service-service"
  fi
done
echo "Review and port changes manually from $out; do not replace handwritten implementations."
