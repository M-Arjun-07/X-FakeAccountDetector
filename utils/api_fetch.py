import tweepy
import requests
import time
import json
import re
from datetime import datetime
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

class SocialMediaAPI:
    def __init__(self):
        self.twitter_client = None
        self.instagram_session = None
        self.setup_clients()
    
    def setup_clients(self):
        """Initialize API clients with credentials from environment variables"""
        # Twitter API setup
        twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if twitter_bearer_token:
            try:
                self.twitter_client = tweepy.Client(bearer_token=twitter_bearer_token)
                print("Twitter API client initialized successfully")
            except Exception as e:
                print(f"Twitter API setup failed: {e}")
        
        # Instagram (using session - note: official API is restricted)
        self.instagram_session = requests.Session()
    
    def extract_username_from_url(self, url):
        """Extract username from various social media URLs"""
        if not url:
            return None
            
        # Remove protocol and www
        clean_url = re.sub(r'^(https?://)?(www\.)?', '', url)
        
        # Platform-specific patterns
        patterns = {
            'twitter': [
                r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)',
                r'(?:twitter\.com|x\.com)/@([a-zA-Z0-9_]+)'
            ],
            'instagram': [
                r'instagram\.com/([a-zA-Z0-9_.]+)',
                r'instagr\.am/([a-zA-Z0-9_.]+)'
            ],
            'tiktok': [
                r'tiktok\.com/@([a-zA-Z0-9_.]+)',
                r'tiktok\.com/([a-zA-Z0-9_.]+)'
            ],
            'facebook': [
                r'facebook\.com/([a-zA-Z0-9_.]+)',
                r'fb\.com/([a-zA-Z0-9_.]+)'
            ]
        }
        
        for platform, platform_patterns in patterns.items():
            for pattern in platform_patterns:
                match = re.search(pattern, clean_url)
                if match:
                    username = match.group(1)
                    # Remove query parameters and paths
                    username = username.split('/')[0].split('?')[0]
                    return username, platform
        
        # If no URL pattern matches, assume it's just a username
        if re.match(r'^[a-zA-Z0-9_.]+$', clean_url):
            return clean_url, 'unknown'
        
        return None, None
    
    def fetch_twitter_profile(self, username):
        """Fetch Twitter profile data using API v2"""
        if not self.twitter_client:
            return {'error': 'Twitter API not configured'}
        
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Get user data with extended fields
            user_response = self.twitter_client.get_user(
                username=username,
                user_fields=[
                    'created_at', 'description', 'entities', 'location', 
                    'pinned_tweet_id', 'profile_image_url', 'protected',
                    'public_metrics', 'url', 'verified', 'withheld'
                ]
            )
            
            if not user_response.data:
                return {'error': f'Twitter user {username} not found'}
            
            user = user_response.data
            user_data = {
                'platform': 'twitter',
                'username': user.username,
                'display_name': user.name,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'description': user.description,
                'location': user.location,
                'profile_image_url': user.profile_image_url,
                'protected': user.protected,
                'verified': user.verified,
                'followers_count': user.public_metrics['followers_count'],
                'following_count': user.public_metrics['following_count'],
                'tweet_count': user.public_metrics['tweet_count'],
                'listed_count': user.public_metrics['listed_count'],
                'url': user.url
            }
            
            # Get recent tweets for additional analysis
            tweets_data = self.fetch_twitter_tweets(user.id)
            user_data['recent_tweets'] = tweets_data
            
            return user_data
            
        except tweepy.TweepyException as e:
            return {'error': f'Twitter API error: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def fetch_twitter_tweets(self, user_id, max_tweets=50):
        """Fetch recent tweets from a user"""
        if not self.twitter_client:
            return []
        
        try:
            tweets_response = self.twitter_client.get_users_tweets(
                id=user_id,
                max_results=max_tweets,
                tweet_fields=[
                    'created_at', 'text', 'public_metrics', 'context_annotations',
                    'entities', 'conversation_id', 'referenced_tweets', 'attachments'
                ],
                exclude='retweets'
            )
            
            if not tweets_response.data:
                return []
            
            tweets_data = []
            for tweet in tweets_response.data:
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'like_count': tweet.public_metrics['like_count'],
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'quote_count': tweet.public_metrics['quote_count'],
                    'has_media': bool(tweet.attachments) if hasattr(tweet, 'attachments') else False
                }
                tweets_data.append(tweet_info)
            
            return tweets_data
            
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def fetch_instagram_profile(self, username):
        """Fetch Instagram profile data (limited without official API)"""
        try:
            # Note: This is a basic implementation without official API access
            # For hackathon, we'll simulate data or use basic web scraping
            
            # Simulated response for hackathon
            simulated_data = {
                'platform': 'instagram',
                'username': username,
                'display_name': username.title(),
                'is_private': False,
                'is_verified': False,
                'follower_count': 150,  # Simulated
                'following_count': 1200,  # Simulated
                'post_count': 15,  # Simulated
                'description': 'Sample bio',  # Simulated
                'profile_pic_url': None,
                'external_url': None
            }
            
            # TODO: For production, implement proper Instagram data fetching
            # This would require official API access or careful web scraping
            
            return simulated_data
            
        except Exception as e:
            return {'error': f'Instagram fetch error: {str(e)}'}
    
    def fetch_tiktok_profile(self, username):
        """Fetch TikTok profile data"""
        try:
            # Simulated response for hackathon
            # TikTok API requires official access
            
            simulated_data = {
                'platform': 'tiktok',
                'username': username,
                'display_name': username.title(),
                'follower_count': 200,  # Simulated
                'following_count': 50,  # Simulated
                'like_count': 500,  # Simulated
                'video_count': 8,  # Simulated
                'description': 'TikTok creator',  # Simulated
                'is_verified': False,
                'profile_pic_url': None
            }
            
            return simulated_data
            
        except Exception as e:
            return {'error': f'TikTok fetch error: {str(e)}'}
    
    def fetch_facebook_profile(self, username):
        """Fetch Facebook profile data"""
        try:
            # Facebook Graph API requires extensive permissions
            # Simulated for hackathon
            
            simulated_data = {
                'platform': 'facebook',
                'username': username,
                'display_name': username.title(),
                'follower_count': 300,  # Simulated
                'friend_count': 150,  # Simulated
                'is_verified': False,
                'profile_pic_url': None
            }
            
            return simulated_data
            
        except Exception as e:
            return {'error': f'Facebook fetch error: {str(e)}'}
    
    def fetch_profile_data(self, input_text):
        """
        Main method to fetch profile data from any supported platform
        Automatically detects platform from URL or uses specified platform
        """
        start_time = time.time()
        
        # Extract username and platform from input
        username, detected_platform = self.extract_username_from_url(input_text)
        
        if not username:
            # If no URL pattern, assume it's a username for Twitter
            username = input_text.strip().lstrip('@')
            detected_platform = 'twitter'
        
        print(f"Fetching data for: {username} on {detected_platform}")
        
        # Platform-specific data fetching
        if detected_platform == 'twitter':
            profile_data = self.fetch_twitter_profile(username)
        elif detected_platform == 'instagram':
            profile_data = self.fetch_instagram_profile(username)
        elif detected_platform == 'tiktok':
            profile_data = self.fetch_tiktok_profile(username)
        elif detected_platform == 'facebook':
            profile_data = self.fetch_facebook_profile(username)
        else:
            # Default to Twitter for unknown platforms
            profile_data = self.fetch_twitter_profile(username)
        
        # Add metadata
        if 'error' not in profile_data:
            profile_data['fetch_time'] = round(time.time() - start_time, 2)
            profile_data['timestamp'] = datetime.now().isoformat()
            profile_data['input_processed'] = input_text
        
        return profile_data
    
    def batch_fetch_profiles(self, usernames, platform='twitter', delay=1):
        """Fetch multiple profiles with rate limiting"""
        results = []
        
        for username in usernames:
            try:
                if platform == 'twitter':
                    profile_data = self.fetch_twitter_profile(username)
                elif platform == 'instagram':
                    profile_data = self.fetch_instagram_profile(username)
                else:
                    profile_data = self.fetch_twitter_profile(username)
                
                results.append({
                    'username': username,
                    'data': profile_data,
                    'success': 'error' not in profile_data
                })
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                results.append({
                    'username': username,
                    'data': {'error': str(e)},
                    'success': False
                })
        
        return results

# Singleton instance
api_fetcher = SocialMediaAPI()

# Utility functions
def test_api_connection():
    """Test if API connections are working"""
    test_username = "twitter"  # Using Twitter's official account for testing
    
    print("Testing API connections...")
    
    # Test Twitter
    if api_fetcher.twitter_client:
        try:
            result = api_fetcher.fetch_twitter_profile(test_username)
            if 'error' not in result:
                print("✅ Twitter API: Connected successfully")
            else:
                print(f"❌ Twitter API: {result['error']}")
        except Exception as e:
            print(f"❌ Twitter API: {e}")
    else:
        print("❌ Twitter API: Not configured")
    
    print("API connection test completed")

if __name__ == "__main__":
    # Test the module
    test_api_connection()
    
    # Example usage
    if api_fetcher.twitter_client:
        test_profile = api_fetcher.fetch_profile_data("https://twitter.com/elonmusk")
        print("\nSample profile data:")
        print(json.dumps(test_profile, indent=2, default=str))