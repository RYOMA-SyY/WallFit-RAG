$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    Write-Host "Shutting down WahibaFit API (PID: $($conn.OwningProcess))..." -ForegroundColor Cyan
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Host "Server stopped." -ForegroundColor Green
} else {
    Write-Host "No server found running on port 8000." -ForegroundColor Yellow
}
