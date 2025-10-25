from utils.api_fetch import api_fetcher

def test_api():
    print("🧪 Testing API Fetcher...")
    
    # Test with real Twitter accounts
    test_accounts = [
        "https://twitter.com/elonrusk",
        "https://twitter.com/Twitter", 
        "https://twitter.com/NASA"
    ]
    
    for account in test_accounts:
        print(f"\n🔍 Testing: {account}")
        result = api_fetcher.fetch_profile_data(account)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Success: {result['username']}")
            print(f"   Followers: {result['followers_count']}")
            print(f"   Following: {result['following_count']}")
            print(f"   Tweets: {result['tweet_count']}")
            print(f"   Verified: {result['verified']}")

if __name__ == "__main__":
    test_api()