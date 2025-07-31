# Swing Sage Vercel Deployment Script (PowerShell)

Write-Host "🚀 Swing Sage Vercel Deployment" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

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

# Check if git repository is clean
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "⚠️  Uncommitted changes detected. Please commit your changes first:" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor Cyan
    Write-Host "   git commit -m 'Prepare for deployment'" -ForegroundColor Cyan
    Write-Host "   git push" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Repository is clean" -ForegroundColor Green

# Deploy to Vercel
Write-Host "🚀 Deploying to Vercel..." -ForegroundColor Green
vercel --prod

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📝 Check your Vercel dashboard for the deployment URL" -ForegroundColor Cyan
Write-Host "🔧 If you encounter issues, check the DEPLOYMENT_GUIDE.md file" -ForegroundColor Cyan 