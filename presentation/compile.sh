#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Compile the Ph.D. Qualification Beamer Presentation
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$DIR")"

echo "==> Compiling Beamer Presentation via Docker (texlive:TL2021-historic)..."

mkdir -p "${DIR}/output"

docker run --rm \
  -v "${ROOT_DIR}:/workdir" \
  -w /workdir/presentation \
  texlive/texlive:TL2021-historic \
  pdflatex -interaction=nonstopmode -output-directory=output main_presentation.tex

# Second pass for cross-references, outlines, and page counts
docker run --rm \
  -v "${ROOT_DIR}:/workdir" \
  -w /workdir/presentation \
  texlive/texlive:TL2021-historic \
  pdflatex -interaction=nonstopmode -output-directory=output main_presentation.tex

# Synchronize output/main_presentation.pdf -> main_presentation.pdf (if not locked by Windows viewer)
if cp -f "${DIR}/output/main_presentation.pdf" "${DIR}/main_presentation.pdf" 2>/dev/null; then
  echo "==> Synchronized main_presentation.pdf"
else
  echo "==> Note: ${DIR}/main_presentation.pdf is currently open/locked in a Windows viewer."
  echo "    Please close the viewer to update that copy directly, or view ${DIR}/output/main_presentation.pdf."
fi

echo "==> PDF generated successfully at:"
echo "    - ${DIR}/output/main_presentation.pdf (Updated)"
echo "    - ${DIR}/main_presentation.pdf"
