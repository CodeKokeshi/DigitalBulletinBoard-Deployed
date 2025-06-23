# 🇵🇭 PHILIPPINES TIMEZONE CONFIGURATION

## 🕐 Perfect Schedule for Philippines (+8 GMT)

### **Portfolio Mode (Recommended):**
```bash
TIMEZONE=Asia/Manila
RUNTIME_START_HOUR=9          # 9 AM Philippines time
RUNTIME_END_HOUR=21           # 9 PM Philippines time  
RUNTIME_WEEKDAYS_ONLY=true    # Monday-Friday only
```

**Result:** 12 hours/day × 5 weekdays = ~240 hours/month (WELL within free tier!)

### **School Hours:**
```bash
TIMEZONE=Asia/Manila
RUNTIME_START_HOUR=8          # 8 AM Philippines time
RUNTIME_END_HOUR=18           # 6 PM Philippines time
RUNTIME_WEEKDAYS_ONLY=true
```

**Result:** 10 hours/day × 5 weekdays = ~200 hours/month

### **Business Hours:**
```bash
TIMEZONE=Asia/Manila
RUNTIME_START_HOUR=9          # 9 AM Philippines time
RUNTIME_END_HOUR=17           # 5 PM Philippines time
RUNTIME_WEEKDAYS_ONLY=true
```

**Result:** 8 hours/day × 5 weekdays = ~160 hours/month

## 🎯 What Visitors Will See

When your app is offline (nights/weekends), they'll see:

```
📋 Digital Bulletin Board
Smart Resource Management Portfolio Demo

🕐 Available Monday-Friday 9 AM - 9 PM (Philippines Time)

⚡ Next Available: Monday 09:00 Asia/Manila

💡 Portfolio Feature:
This application includes intelligent resource management that 
automatically optimizes server usage during weekends for 
maintenance and optimization.
```

## 📍 Other Asian Timezones (if needed):

- **Singapore:** `Asia/Singapore`
- **Hong Kong:** `Asia/Hong_Kong`
- **Taiwan:** `Asia/Taipei`
- **Malaysia:** `Asia/Kuala_Lumpur`
- **Thailand:** `Asia/Bangkok`

## 🚀 Setup Steps:

1. **Deploy to Railway**
2. **Go to Railway Dashboard → Variables**
3. **Add these variables:**
   ```
   TIMEZONE=Asia/Manila
   RUNTIME_START_HOUR=9
   RUNTIME_END_HOUR=21
   RUNTIME_WEEKDAYS_ONLY=true
   ```
4. **Your app runs Monday-Friday 9 AM - 9 PM Philippines time!**

Perfect for showing off to potential employers during normal business hours! 🎉
