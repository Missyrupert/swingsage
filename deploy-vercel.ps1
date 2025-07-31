# Swing Sage Vercel Deployment Script

Write-Host "🚀 Swing Sage Vercel Deployment" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "api/index.py")) {
    Write-Host "❌ Error: api/index.py not found. Make sure you're in the swing-sage-final directory." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ Error: vercel.json not found. Make sure you're in the swing-sage-final directory." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found required files" -ForegroundColor Green

# Check if Vercel CLI is installed
try {
    $vercelVersion = vercel --version
    Write-Host "✅ Vercel CLI found: $vercelVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Vercel CLI not found. Installing..." -ForegroundColor Red
    npm install -g vercel
}

# Check if user is logged in
try {
    $whoami = vercel whoami
    Write-Host "✅ Logged in as: $whoami" -ForegroundColor Green
}
catch {
    Write-Host "🔐 Please login to Vercel..." -ForegroundColor Yellow
    vercel login
}

# Force Vercel to recognize this as a Python project
Write-Host "🔧 Configuring Vercel for Python/Flask deployment..." -ForegroundColor Yellow

# Deploy to Vercel with explicit Python configuration
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Green
Write-Host "Note: This will create a new project if one doesn't exist" -ForegroundColor Cyan

vercel --prod --yes

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📝 Check your Vercel dashboard for the deployment URL" -ForegroundColor Cyan
Write-Host "🔧 If you encounter issues, check the DEPLOYMENT_GUIDE.md file" -ForegroundColor Cyan 