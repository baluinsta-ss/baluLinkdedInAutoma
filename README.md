# LinkedIn Automation Hub - README

Note : High Alert, Don't use this on your professional account. This is just for learning and exploring purpose. Try onnew fake linkedin account

## 🚀 Overview

LinkedIn Automation Hub is a comprehensive automation platform that helps you manage LinkedIn content creation, posting, and resource curation. Built with Python and Streamlit, it features AI-powered content generation, automated posting, and resource management.[1][2]

## ✨ Features

- **Content Enhancer**: Transform ideas into professional LinkedIn posts with AI assistance
- **Post Scheduler**: Schedule and manage LinkedIn posts with manual or AI-generated content
- **Resource Curator**: Search, download, and share educational PDFs from multiple sources
- **Automation Scheduler**: Background jobs for automated posting and curation
- **Google Sheets Integration**: Central data storage for posts, resources, and enhanced content[1]

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser (version 141)
- Google Cloud account (for Sheets API)
- LinkedIn account
- Google Gemini API key[2][1]

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd linkedin-automation-hub
```

### 2. Create Virtual Environment

```bash
# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install streamlit pandas gspread oauth2client python-dotenv
pip install selenium undetected-chromedriver
pip install google-generativeai
pip install requests beautifulsoup4
pip install googlesearch-python
pip install apscheduler
```

Or create a `requirements.txt`:

```txt
streamlit>=1.28.0
pandas>=2.0.0
gspread>=5.11.0
oauth2client>=4.1.3
python-dotenv>=1.0.0
selenium>=4.15.0
undetected-chromedriver>=3.5.0
google-generativeai>=0.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0
googlesearch-python>=1.2.3
apscheduler>=3.10.0
```

Then install:
```bash
pip install -r requirements.txt
```

## 🔑 Configuration

### 1. Set Up Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API and Google Drive API
4. Create Service Account credentials:
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
   - Rename it to `credentials.json`
   - Place it in the project root directory[1]

### 2. Share Google Sheets with Service Account

1. Open the downloaded `credentials.json` file
2. Copy the `client_email` value
3. Create three Google Sheets:
   - `LinkedIn_Posts`
   - `LinkedIn_Resources`
   - `LinkedIn_Enhanced_Content`
4. Share each sheet with the service account email (Editor access)[1]

### 3. Create Environment File

Create a `.env` file in the project root:

```env
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# Optional: Telegram Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

**How to get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file[2]

## 📁 Project Structure

```
linkedin-automation-hub/
├── app.py                      # Main Streamlit application
├── services/
│   ├── ai_service.py          # AI content generation service
│   ├── linkedin_service.py    # LinkedIn posting automation
│   ├── curation_service.py    # PDF search and download
│   ├── scheduler_service.py   # Background job scheduler
│   └── notification_service.py # Telegram notifications
├── credentials.json            # Google Sheets credentials
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── curated_pdfs/              # Downloaded PDFs directory
└── temp_images/               # Temporary image uploads
```

## 🚀 Running the Application

### 1. Start the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`[1]

### 2. First-Time Setup

1. **Navigate to Settings** (⚙️ Settings page)
2. Verify API keys and credentials are loaded
3. Go back to Dashboard to confirm Google Sheets are initialized[1]

## 📖 Usage Guide

### Dashboard (🏠)

- View pending, published posts, and curated resources
- Monitor automation statistics
- Quick overview of upcoming posts[1]

### Content Enhancer (✨)

1. Enter your idea or draft content
2. Choose number of variations (1-5)
3. Toggle professional emojis on/off
4. Click "Enhance Content"
5. Review generated versions
6. Copy or add to post queue[1]

### Post Scheduler (📅)

**Manual Post:**
1. Enter series name and topic
2. Write content
3. Set schedule date and time
4. Upload image (optional)
5. Add to queue or post instantly[1]

**AI Auto-Generate:**
1. Enter series name and topic
2. Choose number of posts (1-30)
3. Set start date and time
4. Click "Generate Series"
5. Review generated posts
6. Schedule all or save as drafts[1]

### Resource Curator (📚)

1. Enter topics (one per line)
2. Set max results per topic
3. Click "Search & Download PDFs"
4. Review downloaded resources with AI-generated post drafts
5. Post directly or schedule for later[1]

### Automation Scheduler

- Toggle scheduler on/off from sidebar
- View next scheduled post and curation times
- Configure schedule times in Settings[1]

## ⚠️ Important Notes

### LinkedIn Automation

- **CAPTCHA Handling**: If LinkedIn shows CAPTCHA during login, solve it manually in the browser window[2]
- **Human-like Behavior**: The automation includes random delays and scrolling to mimic human behavior[2]
- **Rate Limits**: Don't post too frequently to avoid LinkedIn's anti-automation detection
- **Draft Detection**: If posts are saved as drafts instead of publishing, this indicates LinkedIn's anti-automation is active[2]

### Google Sheets API Limits

- Free tier: 300 requests per minute per project
- The app includes retry logic with exponential backoff for quota errors[1]

### Chrome Browser

- The app requires Chrome 141 compatibility
- Undetected ChromeDriver is used to bypass automation detection[2]

## 🐛 Troubleshooting

### Issue: `credentials.json not found`
**Solution**: Ensure the Google Service Account JSON file is in the project root directory[1]

### Issue: `Gemini API key not configured`
**Solution**: Check `.env` file has `GEMINI_API_KEY` set correctly[2]

### Issue: LinkedIn login fails
**Solution**: 
- Verify credentials in `.env` file
- Solve CAPTCHA if it appears
- Check if LinkedIn account has 2FA enabled (disable or use app password)[2]

### Issue: Posts saved as drafts
**Solution**: This indicates LinkedIn's anti-automation detection. Post manually from drafts or wait before trying again[2]

### Issue: Google Sheets quota exceeded
**Solution**: Wait for quota to reset or reduce API call frequency[1]

## 📝 Development

### Creating Services Directory

If the `services/` directory doesn't exist, create it and add `__init__.py`:

```bash
mkdir services
touch services/__init__.py
```

Then add the service files:
- `ai_service.py`
- `linkedin_service.py`
- `curation_service.py`
- `scheduler_service.py`
- `notification_service.py`

## 🔒 Security

- Never commit `.env` or `credentials.json` to version control
- Add them to `.gitignore`:

```gitignore
.env
credentials.json
curated_pdfs/
temp_images/
*.pyc
__pycache__/
venv/
```

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error screenshots saved in the project directory
3. Check browser console for Selenium errors[2]

## 🎯 Best Practices

1. **Test with small batches**: Start with 1-2 posts before scheduling 30
2. **Review AI content**: Always review AI-generated content before posting
3. **Backup data**: Export Google Sheets regularly
4. **Monitor automation**: Check scheduler status in sidebar
5. **Stay within limits**: Don't exceed LinkedIn's posting frequency guidelines[2][1]

---

**Built with**: Streamlit, Selenium, Google Gemini AI, Google Sheets API[2][1]
