# 🚀 Swing Sage Vercel Deployment Guide

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Vercel CLI** (optional): `npm i -g vercel`

## ⚠️ Important Limitations

### Vercel Serverless Constraints:
- **Execution Time**: Maximum 60 seconds per function
- **Memory**: Limited to 3008MB
- **File Size**: Upload limits may affect video processing
- **Cold Starts**: First request may be slower

### Recommended Adjustments:
- Use shorter videos (< 30 seconds)
- Optimize video processing for speed
- Consider client-side processing for heavy tasks

## 🛠️ Deployment Steps

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to Git**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push
   ```

2. **Verify file structure**:
   ```
   swing-sage-final/
   ├── api/
   │   ├── index.py          # Main serverless function
   │   └── requirements.txt   # Vercel-specific dependencies
   ├── templates/            # HTML templates
   ├── static/              # CSS, JS, images
   ├── video_processor.py   # Video analysis module
   ├── coaching_engine.py   # Coaching feedback module
   ├── utils.py            # Utility functions
   ├── vercel.json         # Vercel configuration
   └── requirements.txt    # Original requirements
   ```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)**
2. **Click "New Project"**
3. **Import your Git repository**
4. **Configure the project**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

5. **Click "Deploy"**

#### Option B: Using Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from your project directory**:
   ```bash
   cd swing-sage-final
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Confirm deployment settings
   - Wait for deployment to complete

### Step 3: Configure Environment Variables

1. **Go to your Vercel project dashboard**
2. **Navigate to Settings → Environment Variables**
3. **Add any necessary environment variables**:
   ```
   FLASK_ENV=production
   FLASK_SECRET_KEY=your-secret-key-here
   ```

### Step 4: Test Your Deployment

1. **Visit your deployed URL** (provided by Vercel)
2. **Test the health endpoint**: `https://your-app.vercel.app/health`
3. **Test video upload and processing**

## 🔧 Troubleshooting

### Common Issues:

#### 1. **Build Failures**
- **Solution**: Check that all dependencies are in `api/requirements.txt`
- **Check**: Ensure `opencv-python-headless` is used instead of `opencv-python`

#### 2. **Function Timeout**
- **Solution**: Reduce video processing time or use smaller videos
- **Check**: Monitor function execution time in Vercel dashboard

#### 3. **Memory Issues**
- **Solution**: Optimize video processing for lower memory usage
- **Check**: Use `opencv-python-headless` for smaller package size

#### 4. **Import Errors**
- **Solution**: Ensure all modules are properly imported in `api/index.py`
- **Check**: Verify file paths and module structure

### Debugging:

1. **Check Vercel Function Logs**:
   - Go to your project dashboard
   - Click on "Functions" tab
   - View logs for any errors

2. **Test Locally with Vercel Dev**:
   ```bash
   vercel dev
   ```

3. **Check Build Logs**:
   - Review build output for dependency issues
   - Ensure all files are properly included

## 📊 Performance Optimization

### For Better Performance:

1. **Use Smaller Videos**: Limit to 30 seconds or less
2. **Optimize Video Processing**: Reduce frame processing
3. **Use CDN**: Consider using external video storage
4. **Client-Side Processing**: Move heavy processing to browser

### Monitoring:

1. **Vercel Analytics**: Monitor function performance
2. **Error Tracking**: Set up error monitoring
3. **Performance Metrics**: Track response times

## 🔒 Security Considerations

1. **Environment Variables**: Store secrets in Vercel environment variables
2. **File Upload Limits**: Implement proper file size restrictions
3. **Input Validation**: Validate all user inputs
4. **CORS**: Configure CORS if needed

## 📈 Scaling Considerations

### For High Traffic:

1. **Edge Functions**: Consider using Vercel Edge Functions
2. **Database**: Use external database for session storage
3. **File Storage**: Use external storage (AWS S3, etc.)
4. **CDN**: Implement CDN for static assets

## 🎯 Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure monitoring and alerts**
3. **Implement analytics tracking**
4. **Set up CI/CD pipeline**
5. **Optimize for production use**

## 📞 Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Swing Sage Issues**: Create issues in your repository

---

**Happy Deploying! 🏌️⛳** 