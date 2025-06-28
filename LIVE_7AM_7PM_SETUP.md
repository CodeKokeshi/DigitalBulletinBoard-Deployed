# Digital Bulletin Board - Live 7 AM to 7 PM (Philippine Time) Setup

## Current Issue
Your website is down even though it should be live. The scheduler is working locally, but the Railway deployment needs the correct environment variables.

## ✅ Fixed Code Changes
The following files have been updated:
- `runtime_scheduler.py` - Changed default hours to 7 AM - 7 PM
- `railway.toml` - Updated configuration comments
- Added `test_scheduler.py` - Test script to verify settings

## 🚀 Railway Deployment Setup

### Step 1: Set Environment Variables in Railway Dashboard

Go to your Railway project dashboard and set these environment variables:

```
TIMEZONE=Asia/Manila
RUNTIME_START_HOUR=7
RUNTIME_END_HOUR=19
RUNTIME_WEEKDAYS_ONLY=false
```

### Step 2: How to Set Environment Variables in Railway

1. Go to your Railway dashboard
2. Click on your project
3. Go to the "Variables" tab
4. Add each variable:
   - Click "New Variable"
   - Enter the name and value
   - Click "Add"

### Step 3: Deploy the Changes

After setting the environment variables:
1. Push your updated code to your repository
2. Railway will automatically redeploy
3. Your website will now be live from 7 AM to 7 PM Philippine time daily

## 📋 Environment Variables Explained

- `TIMEZONE=Asia/Manila` - Sets Philippine timezone (UTC+8)
- `RUNTIME_START_HOUR=7` - Website goes live at 7 AM
- `RUNTIME_END_HOUR=19` - Website goes offline at 7 PM (19:00 in 24-hour format)
- `RUNTIME_WEEKDAYS_ONLY=false` - Runs daily (Monday-Sunday)

## 🧪 Testing

After deployment, you can test by visiting your website at different times:
- **7:00 AM - 6:59 PM** (Philippine time) = Website should be LIVE
- **7:00 PM - 6:59 AM** (Philippine time) = Website shows maintenance page

You can also run the test script locally:
```bash
python test_scheduler.py
```

## 📊 Resource Usage

- **Daily Hours**: 12 hours (7 AM - 7 PM)
- **Monthly Hours**: ~360 hours (within Railway free tier limits)
- **Savings**: ~360 hours per month vs 24/7 operation

## 🔧 Quick Fix Commands

If you want to test different hours quickly, you can set these in Railway:

### For 6 AM - 8 PM:
```
RUNTIME_START_HOUR=6
RUNTIME_END_HOUR=20
```

### For 8 AM - 6 PM:
```
RUNTIME_START_HOUR=8
RUNTIME_END_HOUR=18
```

### For weekdays only:
```
RUNTIME_WEEKDAYS_ONLY=true
```

## ⚠️ Important Notes

1. **Philippine Time**: All times are in Philippine timezone (UTC+8)
2. **24-hour format**: Use 24-hour format for hours (7 = 7 AM, 19 = 7 PM)
3. **Redeploy Required**: Environment variable changes require a redeploy
4. **Test First**: Always test with the test script after changes

Your website should be live immediately after setting these environment variables in Railway!
