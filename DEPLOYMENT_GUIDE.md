# Streamlit Deployment Guide

## Overview
Deploy your Mental Health Chatbot as a web application using Streamlit Cloud (free) or other hosting platforms.

## Quick Start (Local Testing)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

### 3. Run Locally
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## Deploy to Streamlit Cloud (FREE)

### Prerequisites
- GitHub account
- Groq API key (free at https://console.groq.com)
- Gemini API key (free at https://ai.google.dev)

### Step-by-Step Deployment

#### 1. Push Code to GitHub
```bash
git init
git add .
git commit -m "Mental health chatbot ready for deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/mhc-agentic.git
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/mhc-agentic`
5. Set main file path: `streamlit_app.py`
6. Click "Advanced settings"
7. Add secrets (environment variables):
   ```toml
   GROQ_API_KEY = "your_groq_api_key"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
8. Click "Deploy!"

Your app will be live at: `https://YOUR_USERNAME-mhc-agentic.streamlit.app`

### 3. Custom Domain (Optional)
Streamlit Cloud supports custom domains:
1. Go to app settings
2. Click "Custom domain"
3. Follow DNS configuration instructions

## Alternative Deployment Options

### Option 1: Heroku

#### Requirements
- Heroku account
- Heroku CLI installed

#### Additional Files Needed

**Procfile:**
```
web: sh setup.sh && streamlit run streamlit_app.py
```

**setup.sh:**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### Deploy Commands
```bash
heroku login
heroku create your-mhc-chatbot
heroku config:set GROQ_API_KEY=your_key
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

### Option 2: AWS EC2

#### Setup Steps
1. Launch EC2 instance (Ubuntu)
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```
4. Set environment variables in `~/.bashrc`
5. Run with screen or systemd:
   ```bash
   screen -S chatbot
   streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

### Option 3: Google Cloud Run

#### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0
```

#### Deploy Commands
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/mhc-chatbot
gcloud run deploy mhc-chatbot --image gcr.io/PROJECT_ID/mhc-chatbot --platform managed
```

### Option 4: Railway

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Add environment variables in dashboard
4. Railway auto-detects Streamlit and deploys

### Option 5: Render

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
6. Add environment variables

## Configuration for Production

### Streamlit Config (.streamlit/config.toml)
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#3498db"
backgroundColor = "#f5f7fa"
secondaryBackgroundColor = "#ecf0f1"
textColor = "#2c3e50"
```

### Security Best Practices

1. **Never commit API keys**
   - Use `.gitignore` to exclude `.env`
   - Always use secrets management (Streamlit secrets, env vars)

2. **Rate Limiting**
   - Implement request throttling to prevent abuse
   - Consider adding authentication for production

3. **Session Management**
   - Sessions auto-expire after inactivity
   - Consider adding user authentication for persistent sessions

4. **HTTPS**
   - Streamlit Cloud includes HTTPS automatically
   - For custom deployments, use SSL certificates

### Monitoring

1. **Streamlit Cloud Dashboard**
   - View app logs
   - Monitor resource usage
   - Track errors

2. **Custom Logging**
   - Add logging to track usage patterns
   - Monitor API call volumes
   - Track response times

### Scaling Considerations

**For High Traffic:**
1. **Use caching** (`@st.cache_resource`, `@st.cache_data`)
2. **Optimize API calls** (batch requests where possible)
3. **Consider load balancing** for multiple instances
4. **Use CDN** for static assets

**Cost Management:**
- Monitor API usage (Groq/Gemini free tiers)
- Implement request limits per session
- Cache frequent responses
- Consider paid tiers for high volume

## Maintenance

### Updating the App
```bash
git add .
git commit -m "Update chatbot features"
git push origin main
```

Streamlit Cloud auto-deploys on push to main branch.

### Monitoring Logs
```bash
# Local
streamlit run streamlit_app.py --logger.level=debug

# Streamlit Cloud
View logs in dashboard under "Manage app" > "Logs"
```

### Backup Sessions
Sessions are stored in `sessions/` directory:
- Automatically created on deployment
- Consider periodic backups for user data
- Implement export functionality for users

## Features Available in Web Version

✅ **All Core Features:**
- Multi-agent collaborative system
- Multi-label emotion detection
- Mood tracking across conversation
- Therapist micro-skills
- RAG knowledge base
- Clinical assessment (non-diagnostic)
- Crisis detection
- Conversation memory

✅ **Web-Specific Features:**
- Clean, responsive UI
- Real-time chat interface
- Session management
- Crisis resource sidebar
- Mood trend visualization
- Debug mode toggle
- Mobile-friendly design

## Troubleshooting

### Issue: App won't start
**Solution:** Check logs for missing dependencies or API key errors

### Issue: Slow response times
**Solution:** 
- Check API rate limits
- Optimize caching
- Reduce conversation history length

### Issue: Session data not persisting
**Solution:** 
- Ensure `sessions/` directory exists
- Check file permissions
- Consider database for production

### Issue: Memory errors on Streamlit Cloud
**Solution:**
- Reduce knowledge base size
- Optimize caching strategy
- Limit conversation history
- Upgrade to paid plan for more resources

## Support & Resources

- **Streamlit Docs:** https://docs.streamlit.io
- **Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum:** https://discuss.streamlit.io
- **Status Page:** https://streamlit.statuspage.io

## Next Steps

1. **Test locally** with `streamlit run streamlit_app.py`
2. **Push to GitHub** if deployment ready
3. **Deploy to Streamlit Cloud** (easiest, free)
4. **Share URL** with users
5. **Monitor usage** and iterate

## Cost Estimate

**Free Tier (Streamlit Cloud + Free APIs):**
- Streamlit Cloud: FREE (public apps)
- Groq API: FREE (generous limits)
- Gemini API: FREE (60 requests/min)
- **Total: $0/month** for moderate usage

**Paid Tier (High Traffic):**
- Streamlit Cloud: $250/month (private, more resources)
- Groq Pro: Pay per token
- Consider AWS/GCP for infrastructure
- **Estimate: $50-500/month** depending on traffic

---

**Your chatbot is now ready for deployment! 🚀**
