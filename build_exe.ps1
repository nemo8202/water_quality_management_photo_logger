# Install dependencies if not already installed
python -m pip install nuitka zstandard PySide6 Pillow

# Clean old distribution folder
if (Test-Path "dist") {
    Write-Host "Cleaning old build files..." -ForegroundColor Cyan
    Remove-Item -Path "dist" -Recurse -Force
}

# Compile using Nuitka
# Note: We let Nuitka use the default 'main.dist' name first, then rename it.
python -m nuitka `
    --standalone `
    --enable-plugin=pyside6 `
    --windows-console-mode=disable `
    --windows-icon-from-ico=favicon.ico `
    --include-data-file=favicon.ico=favicon.ico `
    --include-data-file=favicon.png=favicon.png `
    --output-dir=dist `
    --company-name="DCriders" `
    --product-name="Construction Photo Logger" `
    --file-version=1.0.0 `
    --product-version=1.0.0 `
    --file-description="Management and annotation tool for construction site photos" `
    --assume-yes-for-downloads `
    main.py

if ($LASTEXITCODE -eq 0) {
    # Rename the output folder and executable for a professional look
    Write-Host "Polishing distribution folder..." -ForegroundColor Cyan
    
    $oldDistDir = "dist/main.dist"
    $newDistDir = "dist/ConstructionPhotoLogger"
    
    if (Test-Path $oldDistDir) {
        Rename-Item -Path $oldDistDir -NewName "ConstructionPhotoLogger"
        Rename-Item -Path "$newDistDir/main.exe" -NewName "ConstructionPhotoLogger.exe"
        
        Write-Host "Compilation complete!" -ForegroundColor Green
        Write-Host "The standalone application is in: $newDistDir" -ForegroundColor White
        Write-Host "Run '$newDistDir/ConstructionPhotoLogger.exe' to start." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Compilation failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
