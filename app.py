from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import re
import os
from datetime import datetime
from utils.api_fetch import api_fetcher  # Import your API fetcher

# Create required directories
def setup_directories():
    directories = ['models', 'templates', 'static']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

setup_directories()

app = Flask(__name__)

class FakeAccountDetector:
    def __init__(self):
        # Load trained ML model
        try:
            self.model = joblib.load('models/xgboost_model.pkl')
            self.scaler = joblib.load('models/feature_scaler.pkl')
            self.feature_names = [
                'no_of_friends', 'no_of_followers', 'no_of_likes', 
                'no_of_comments', 'no_of_abuse_reports', 'no_of_rejected_friends',
                'no_of_friend_requests', 'friends_followers_ratio', 'engagement_ratio'
            ]
            print("✅ ML models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            print("⚠️ Using rule-based detection as fallback")
            self.model = None
            self.scaler = None

    def extract_features_from_api_data(self, api_data):
        """Extract features from real API data"""
        features = {}
        
        # Basic metrics from Twitter API
        features['no_of_friends'] = api_data.get('following_count', 0)
        features['no_of_followers'] = api_data.get('followers_count', 0)
        features['no_of_likes'] = self.calculate_total_likes(api_data.get('recent_tweets', []))
        features['no_of_comments'] = self.calculate_total_comments(api_data.get('recent_tweets', []))
        
        # Synthetic features (you can replace these with real data if available)
        features['no_of_abuse_reports'] = self.estimate_abuse_reports(api_data)
        features['no_of_rejected_friends'] = self.estimate_rejected_friends(api_data)
        features['no_of_friend_requests'] = self.estimate_friend_requests(api_data)
        
        # Calculate derived features
        features['friends_followers_ratio'] = (
            features['no_of_friends'] / (features['no_of_followers'] + 1)
        )
        features['engagement_ratio'] = (
            (features['no_of_likes'] + features['no_of_comments']) / 
            (features['no_of_followers'] + 1)
        )
        
        return features

    def calculate_total_likes(self, tweets):
        """Calculate total likes from recent tweets"""
        if not tweets:
            return 0
        return sum(tweet.get('like_count', 0) for tweet in tweets)

    def calculate_total_comments(self, tweets):
        """Calculate total comments/replies from recent tweets"""
        if not tweets:
            return 0
        return sum(tweet.get('reply_count', 0) for tweet in tweets)

    def estimate_abuse_reports(self, api_data):
        """Estimate abuse reports based on account patterns"""
        # This is synthetic - replace with real data if available
        base_reports = 0
        if api_data.get('protected', False):
            base_reports += 2
        if not api_data.get('verified', False):
            base_reports += 1
        return base_reports

    def estimate_rejected_friends(self, api_data):
        """Estimate rejected friend requests"""
        # Synthetic - replace with real data if available
        followers = api_data.get('followers_count', 0)
        following = api_data.get('following_count', 0)
        
        if following > followers * 10:  # Following way more than followers
            return int(following * 0.1)  # Estimate 10% rejection rate
        return int(following * 0.01)  # Normal accounts have 1% rejection

    def estimate_friend_requests(self, api_data):
        """Estimate pending friend requests"""
        # Synthetic - replace with real data if available
        followers = api_data.get('followers_count', 0)
        return int(followers * 0.05)  # Estimate 5% of followers as pending requests

    def predict_fake_account(self, features_dict):
        """Make prediction using ML model"""
        if self.model is None or self.scaler is None:
            # Fallback to rule-based prediction
            return self.rule_based_prediction(features_dict)
        
        try:
            # Convert features to array in correct order
            feature_vector = [features_dict.get(feature, 0) for feature in self.feature_names]
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            prediction = self.model.predict(feature_vector_scaled)[0]
            probability = self.model.predict_proba(feature_vector_scaled)[0][1]
            
            return bool(prediction), float(probability)
        except Exception as e:
            print(f"ML prediction failed: {e}")
            return self.rule_based_prediction(features_dict)

    def rule_based_prediction(self, features):
        """Fallback rule-based prediction"""
        score = 0
        
        # Fake account indicators (add points)
        if features.get('friends_followers_ratio', 1) < 0.01:
            score += 3  # Many followers but few friends
        if features.get('engagement_ratio', 0) < 0.001:
            score += 2  # Low engagement
        if features.get('no_of_abuse_reports', 0) > 5:
            score += 2  # Many abuse reports
        if features.get('no_of_rejected_friends', 0) > 100:
            score += 2  # Many rejected friends
        if features.get('no_of_friend_requests', 0) > 500:
            score += 1  # Many pending requests
            
        # Real account indicators (remove points)
        if 0.1 <= features.get('friends_followers_ratio', 0) <= 10:
            score -= 2  # Balanced ratio
        if features.get('engagement_ratio', 0) > 0.01:
            score -= 2  # Good engagement
        if features.get('no_of_abuse_reports', 0) <= 2:
            score -= 1  # Few abuse reports
        
        probability = min(0.95, max(0.05, score / 10))
        prediction = probability > 0.6
        
        return prediction, probability

    def generate_trust_score(self, probability, features, api_data):
        """Generate comprehensive trust score (0-1000)"""
        base_score = (1 - probability) * 800
        
        # Adjust based on positive factors from API data
        if api_data.get('verified', False):
            base_score += 100
        if features.get('engagement_ratio', 0) > 0.01:
            base_score += 50
        if 0.1 <= features.get('friends_followers_ratio', 0) <= 10:
            base_score += 50
        if features.get('no_of_abuse_reports', 0) <= 2:
            base_score += 30
            
        # Account age bonus (if we have created_at)
        if 'created_at' in api_data:
            try:
                account_age = (datetime.now() - datetime.fromisoformat(api_data['created_at'].replace('Z', '+00:00'))).days
                if account_age > 365:
                    base_score += 50
            except:
                pass
            
        return min(1000, max(0, int(base_score)))

    def generate_reasons(self, prediction, probability, features, api_data):
        """Generate detailed reasons for prediction"""
        reasons = []
        
        if prediction:  # Fake account
            reasons.append(f"High probability ({probability:.1%}) of being fake based on ML analysis")
            
            if features.get('friends_followers_ratio', 1) < 0.01:
                reasons.append("Suspicious follower-to-friends ratio (many followers, few friends)")
            if features.get('engagement_ratio', 0) < 0.001:
                reasons.append("Very low engagement rate compared to follower count")
            if features.get('no_of_abuse_reports', 0) > 5:
                reasons.append("Multiple abuse reports received")
            if features.get('no_of_rejected_friends', 0) > 100:
                reasons.append("Unusually high number of rejected friend requests")
            if features.get('no_of_friend_requests', 0) > 500:
                reasons.append("Suspiciously high number of pending friend requests")
            if not api_data.get('verified', False):
                reasons.append("Account is not verified")
            if not api_data.get('description', '').strip():
                reasons.append("No bio description provided")
                
        else:  # Real account
            reasons.append(f"High probability ({1-probability:.1%}) of being genuine")
            
            if api_data.get('verified', False):
                reasons.append("Account is officially verified")
            if 0.1 <= features.get('friends_followers_ratio', 0) <= 10:
                reasons.append("Healthy balance between friends and followers")
            if features.get('engagement_ratio', 0) > 0.01:
                reasons.append("Good engagement rate with content")
            if features.get('no_of_abuse_reports', 0) <= 2:
                reasons.append("Very few or no abuse reports")
            if features.get('no_of_rejected_friends', 0) < 50:
                reasons.append("Normal friend request acceptance rate")
            if api_data.get('description', '').strip():
                reasons.append("Detailed bio description available")
                
        return reasons

detector = FakeAccountDetector()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_profile():
    try:
        profile_url = request.form.get('profile_url', '').strip()
        
        if not profile_url:
            return render_template('index.html', error='Please enter a profile URL')
        
        print(f"🔍 Analyzing profile: {profile_url}")
        
        # Fetch REAL data from Twitter API
        api_data = api_fetcher.fetch_profile_data(profile_url)
        
        if 'error' in api_data:
            error_msg = api_data['error']
            print(f"❌ API Error: {error_msg}")
            return render_template('index.html', error=f'Failed to fetch profile: {error_msg}')
        
        print(f"✅ Successfully fetched data for: {api_data.get('username', 'Unknown')}")
        
        # Extract features from real API data
        features = detector.extract_features_from_api_data(api_data)
        
        # Make prediction
        prediction, probability = detector.predict_fake_account(features)
        
        # Generate results
        trust_score = detector.generate_trust_score(probability, features, api_data)
        reasons = detector.generate_reasons(prediction, probability, features, api_data)
        
        # Prepare result data
        result = {
            'username': api_data.get('username', 'Unknown'),
            'display_name': api_data.get('display_name', ''),
            'profile_url': f"https://twitter.com/{api_data.get('username', '')}",
            'is_fake': prediction,
            'probability': probability,
            'trust_score': trust_score,
            'trust_level': get_trust_level(trust_score),
            'reasons': reasons,
            'account_details': {
                'friends': api_data.get('following_count', 0),
                'followers': api_data.get('followers_count', 0),
                'tweets': api_data.get('tweet_count', 0),
                'likes': features.get('no_of_likes', 0),
                'comments': features.get('no_of_comments', 0),
                'verified': api_data.get('verified', False),
                'account_created': api_data.get('created_at', 'Unknown'),
                'bio': api_data.get('description', 'No bio available'),
                'location': api_data.get('location', 'Not specified'),
                'profile_pic': api_data.get('profile_image_url', ''),
                'engagement_rate': f"{features.get('engagement_ratio', 0)*100:.4f}%"
            },
            'is_real_data': True
        }
        
        return render_template('result.html', result=result)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return render_template('index.html', error=f'Analysis failed: {str(e)}')

@app.route('/api/analyze', methods=['POST'])
def api_analyze_profile():
    """JSON API endpoint for profile analysis"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        profile_url = data.get('profile_url', '').strip()
        
        if not profile_url:
            return jsonify({'error': 'profile_url is required'}), 400
        
        print(f"🔍 API Analyzing profile: {profile_url}")
        
        # Fetch REAL data from Twitter API
        api_data = api_fetcher.fetch_profile_data(profile_url)
        
        if 'error' in api_data:
            return jsonify({'error': api_data['error']}), 404
        
        # Extract features from real API data
        features = detector.extract_features_from_api_data(api_data)
        
        # Make prediction
        prediction, probability = detector.predict_fake_account(features)
        
        # Generate results
        trust_score = detector.generate_trust_score(probability, features, api_data)
        reasons = detector.generate_reasons(prediction, probability, features, api_data)
        
        # Prepare result data
        result = {
            'username': api_data.get('username', 'Unknown'),
            'profile_url': f"https://twitter.com/{api_data.get('username', '')}",
            'is_fake': prediction,
            'fake_probability': probability,
            'trust_score': trust_score,
            'trust_level': get_trust_level(trust_score),
            'reasons': reasons,
            'account_details': {
                'friends': api_data.get('following_count', 0),
                'followers': api_data.get('followers_count', 0),
                'tweets': api_data.get('tweet_count', 0),
                'verified': api_data.get('verified', False),
                'account_created': api_data.get('created_at', 'Unknown'),
                'bio': api_data.get('description', 'No bio available')
            },
            'status': 'success',
            'data_source': 'twitter_api'
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Analysis error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}', 'status': 'error'}), 500

def get_trust_level(score):
    """Convert trust score to level"""
    if score >= 800:
        return "VERY HIGH"
    elif score >= 600:
        return "HIGH"
    elif score >= 400:
        return "MEDIUM"
    elif score >= 200:
        return "LOW"
    else:
        return "VERY LOW"

# Custom filter for template
@app.template_filter('format_number')
def format_number(value):
    """Format large numbers with K/M suffix"""
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        return str(value)
    except:
        return str(value)

@app.template_filter('format_date')
def format_date(date_string):
    """Format ISO date string"""
    try:
        if not date_string or date_string == 'Unknown':
            return 'Unknown'
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%b %d, %Y')
    except:
        return date_string

if __name__ == '__main__':
    print("🚀 Fake Account Detector Web App Starting...")
    print("📡 Using REAL Twitter API data")
    print("🔧 Testing API connection...")
    
    # Test API connection
    try:
        test_result = api_fetcher.fetch_profile_data("https://twitter.com/Twitter")
        if 'error' in test_result:
            print(f"❌ API Test Failed: {test_result['error']}")
        else:
            print("✅ Twitter API connection successful!")
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)