<#
install_precommit.ps1
Installs pre-commit into the project's virtual environment (if present) or the active Python.
Usage:
  - Open PowerShell in the project folder and run: .\install_precommit.ps1
#>

# Prefer .venv Python if it exists
$venvPython = "${PWD}\\.venv\\Scripts\\python.exe"
if (Test-Path $venvPython) {
  Write-Host "Using venv python: $venvPython"
  & $venvPython -m pip install --upgrade pip pre-commit
} else {
  Write-Host ".venv not found; installing with the default python in PATH"
  python -m pip install --upgrade pip pre-commit
}

# Install the pre-commit git hook
pre-commit install
Write-Host "pre-commit installed. Run 'pre-commit run --all-files' to test."