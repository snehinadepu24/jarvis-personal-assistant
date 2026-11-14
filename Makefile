# Makefile for Jarvis Personal Assistant
# -------------------------------------------------
# This Makefile provides convenient shortcuts to start the frontend (Vite/Tauri) and backend servers,
# as well as commands for building production packages for both parts and creating a combined executable.
# It is designed for Windows PowerShell as the default shell.

SHELL = powershell

# Directories
FRONTEND_DIR = apps/desktop
BACKEND_SCRIPT = .\\start_jarvis.ps1
BACKEND_ENTRY = backend\\server.py

# -------------------------------------------------------------------
# Frontend commands
# -------------------------------------------------------------------
frontend:
	@Write-Host "Starting Vite dev server..."
	cd $(FRONTEND_DIR); npm run dev

# Run full Tauri dev (frontend + Rust backend for Tauri)
# This command also starts the Vite dev server internally.
taure:
	@Write-Host "Running Tauri dev (frontend + Rust backend)..."
	cd $(FRONTEND_DIR); npm run tauri dev

# -------------------------------------------------------------------
# Backend commands (Python FastAPI server)
# -------------------------------------------------------------------
backend:
	@Write-Host "Starting Jarvis backend (FastAPI)..."
	& $(BACKEND_SCRIPT)

# -------------------------------------------------------------------
# Combined development environment
# -------------------------------------------------------------------
# Starts both frontend (Vite) and backend simultaneously in separate windows.
# Uses PowerShell Start-Process to open new terminals.

develop:
	@Write-Host "Launching frontend and backend..."
	Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd $(FRONTEND_DIR); npm run dev'
	Start-Process powershell -ArgumentList '-NoExit', '-Command', '& $(BACKEND_SCRIPT)'

# -------------------------------------------------------------------
# Production build commands
# -------------------------------------------------------------------
# Build the frontend assets (static files for production)
build-frontend:
	@Write-Host "Building frontend production bundle..."
	cd $(FRONTEND_DIR); npm run build

# Package the Python backend as a single‑file executable using PyInstaller.
# Ensure PyInstaller is installed in the virtual environment (pip install pyinstaller).
build-backend:
	@Write-Host "Packaging backend with PyInstaller..."
	# Activate virtual environment
	& .\.venv\\Scripts\\Activate.ps1
	pyinstaller --onefile --name jarvis_backend $(BACKEND_ENTRY)

# Create a combined distributable: backend exe + built frontend static files.
# This target assumes `build-frontend` has been run.
package-combined:
	@Write-Host "Creating combined distribution archive..."
	# Ensure previous builds are fresh
	$(MAKE) build-frontend
	$(MAKE) build-backend
	# Create a directory to stage files
	if (!(Test-Path -Path dist_combined)) { New-Item -ItemType Directory -Path dist_combined }
	# Copy backend exe
	Copy-Item -Path .\\dist\\jarvis_backend.exe -Destination dist_combined -Force
	# Copy frontend build output (usually located in apps/desktop/dist)
	Copy-Item -Path $(FRONTEND_DIR)\\dist\\* -Destination dist_combined -Recurse -Force
	# Zip the combined package
	Compress-Archive -Path dist_combined\\* -DestinationPath jarvis_full_package.zip -Force

# -------------------------------------------------------------------
# Build the Tauri desktop application (production bundle)
# -------------------------------------------------------------------
# This creates a native executable that already bundles the Rust backend and the frontend.
build-tauri:
	@Write-Host "Building Tauri application..."
	cd $(FRONTEND_DIR); npm run tauri build

# -------------------------------------------------------------------
# Cleaning
# -------------------------------------------------------------------
clean:
	@Write-Host "Cleaning node_modules, build artifacts, and PyInstaller outputs..."
	cd $(FRONTEND_DIR); npm run clean
	# Remove PyInstaller build directories if they exist
	if (Test-Path -Path "dist") { Remove-Item -Recurse -Force dist }
	if (Test-Path -Path "build") { Remove-Item -Recurse -Force build }
	if (Test-Path -Path "__pycache__") { Remove-Item -Recurse -Force __pycache__ }

.PHONY: frontend tauri backend develop build-frontend build-backend package-combined build-tauri clean
