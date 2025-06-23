# 🕐 RUNTIME SCHEDULER CONFIGURATION

## 🎯 What This Does

The runtime scheduler **automatically limits when your app runs** to save Railway execution hours!

## ⚙️ Default Settings

**Default Operating Hours:** 8:00 AM - 10:00 PM (14 hours/day)
- **Daily Usage:** 14 hours instead of 24 hours
- **Monthly Usage:** ~420 hours instead of 720 hours
- **Railway Free Tier:** 500 hours/month (you'll stay well within limits!)

## 🌍 Timezone Configuration

### In Railway Dashboard, set these environment variables:

```bash
# Set your timezone (examples):
TIMEZONE=UTC                    # Default
TIMEZONE=US/Eastern            # Eastern Time
TIMEZONE=US/Pacific            # Pacific Time  
TIMEZONE=Asia/Manila           # Philippines
TIMEZONE=Europe/London         # UK
TIMEZONE=Asia/Tokyo            # Japan

# Customize operating hours (24-hour format):
RUNTIME_START_HOUR=8           # Start at 8 AM
RUNTIME_END_HOUR=22            # Stop at 10 PM
```

## 📅 Schedule Examples

### **School Hours (8 AM - 6 PM):**
```bash
RUNTIME_START_HOUR=8
RUNTIME_END_HOUR=18
TIMEZONE=US/Eastern
```
**Result:** 10 hours/day = ~300 hours/month

### **Business Hours (9 AM - 5 PM):**
```bash
RUNTIME_START_HOUR=9
RUNTIME_END_HOUR=17
TIMEZONE=US/Pacific
```
**Result:** 8 hours/day = ~240 hours/month

### **Extended Hours (6 AM - 11 PM):**
```bash
RUNTIME_START_HOUR=6
RUNTIME_END_HOUR=23
TIMEZONE=UTC
```
**Result:** 17 hours/day = ~510 hours/month

### **24/7 Operation (No Limits):**
```bash
# Don't set any RUNTIME variables
# App runs continuously
```
**Result:** 24 hours/day = ~720 hours/month (may exceed free tier)

## 🎨 What Users See During Downtime

When the app is "offline", users see a beautiful maintenance page with:
- 🌙 Sleep mode indicator
- ⏰ Current schedule information
- 🕐 When the app will be available next
- 💤 Professional maintenance message

## 🔧 Setup in Railway

1. **Deploy your app normally**
2. **Go to Railway dashboard → Your Project → Variables**
3. **Add environment variables:**
   - `TIMEZONE` = Your timezone
   - `RUNTIME_START_HOUR` = Start hour (0-23)
   - `RUNTIME_END_HOUR` = End hour (0-23)
4. **Redeploy** (Railway auto-redeploys on variable changes)

## 📊 Monitoring Your Schedule

### Check Current Status:
- Visit: `https://yourapp.railway.app/health`
- See: Current schedule and if app is running

### View Schedule Info:
- Visit: `https://yourapp.railway.app/schedule`
- See: Full schedule details

## 💡 Smart Tips

### **Maximize Free Tier:**
- **14 hours/day** = Perfect balance of availability vs. resource conservation
- **School schedule** (8 AM - 6 PM) = Maximum savings
- **Peak hours only** = When most users are actually online

### **For Different Use Cases:**

**Personal Portfolio:**
- Use business hours (9 AM - 5 PM)
- Shows professionalism
- Saves maximum resources

**School Project:**
- Use school hours (8 AM - 8 PM)
- Available when classmates check it
- Stays within free limits

**Demo for Employers:**
- Use extended hours (6 AM - 11 PM)
- Available during most business hours globally
- Still saves resources

## 🚨 Important Notes

1. **Health check endpoint** (`/health`) is **always available**
2. **Static files** (CSS, JS, images) work during downtime
3. **Gradual restart** - app starts instantly when schedule begins
4. **No data loss** - just controlled availability

## 🎯 Benefits

- ✅ **Stay within free tier limits**
- ✅ **Professional scheduled maintenance**
- ✅ **Automatic resource management**
- ✅ **Beautiful offline page**
- ✅ **Timezone awareness**
- ✅ **Flexible scheduling**

Your bulletin board will run **smartly and efficiently** while staying free! 🎉
