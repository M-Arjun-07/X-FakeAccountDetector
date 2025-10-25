# X-FakeAccountDetector 🔍

A machine learning-powered tool that detects fake Twitter accounts using real-time API data and behavioral analysis.

## Prerequisites
- Python 3.8+
- Twitter Developer Account
- Twitter API Bearer Token

## Installation

### Clone the repository
```
git clone https://github.com/yourusername/twitter-fake-account-detector.git
cd twitter-fake-account-detector
```

### Install dependencies
```
pip install -r requirements.txt
```

## Setup environment
```
# Create .env file and add your Twitter token
echo "TWITTER_BEARER_TOKEN=your_token_here" > .env
```
### 🛠️ Configuration
Get your Twitter Bearer Token from: Twitter Developer Portal
Add it to .env file:
```
TWITTER_BEARER_TOKEN=your_actual_bearer_token_here
```

### Check API connection
```
python train_api.py
```

## Run the application
```
python app.py
```

### Open in browser
```
http://localhost:5000
```

# 🎯 How to Use
Web Interface
Enter any Twitter profile URL to get instant analysis

API Endpoint
Use /api/analyze for programmatic access

Results
Get trust score, fake probability, and detailed reasons

## 🔧 API Usage
```
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://twitter.com/username"}'
```

# 📊 Features
✅ Real-time Twitter API integration

✅ Machine Learning analysis (Random Forest)

✅ Trust scoring (0-1000)

✅ Detailed fake account reasoning

✅ Web interface & REST API

✅ Cross-platform support

