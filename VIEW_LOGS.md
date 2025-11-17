# 📊 How to View Application Logs

## 🚀 Quick Methods

### Option 1: View Recent Logs (Last 30 Lines)
```bash
cd /Users/conwaysolomon/Documents/Coding/KansasCityFIFA-Signup
tail -30 flask.log
```

### Option 2: Watch Logs in Real-Time (Recommended)
```bash
cd /Users/conwaysolomon/Documents/Coding/KansasCityFIFA-Signup
tail -f flask.log
```
Press `Ctrl+C` to stop watching

### Option 3: Use the Log Viewer Script
```bash
cd /Users/conwaysolomon/Documents/Coding/KansasCityFIFA-Signup
./scripts/view_logs.sh
```

### Option 4: Run Flask in Foreground (See Logs Directly)
```bash
# Stop background Flask
pkill -f "flask run"

# Start in foreground (logs show directly)
cd /Users/conwaysolomon/Documents/Coding/KansasCityFIFA-Signup
source venv/bin/activate
flask run --host=0.0.0.0 --port=5001
```
Press `Ctrl+C` to stop

## 📝 Log Filtering

### Show Only Errors
```bash
tail -f flask.log | grep ERROR
```

### Show Only Signups
```bash
tail -f flask.log | grep signup
```

### Show Last 100 Lines
```bash
tail -100 flask.log
```

### Search for Specific Text
```bash
grep "text to search" flask.log
```

### Show Logs from Last Hour
```bash
tail -f flask.log | grep "$(date +%H):"
```

## 🎯 What You'll See in Logs

### Normal Operation
```
INFO:werkzeug:127.0.0.1 - - [15/Nov/2025 23:22:21] "GET / HTTP/1.1" 200 -
INFO:app:{"event": "form_displayed", "ip": "127.0.0.1", ...}
```

### Form Submission
```
INFO:app:{"event": "signup_completed", "signup_id": 1, "email": "test@example.com", ...}
INFO:werkzeug:127.0.0.1 - - [15/Nov/2025 23:24:00] "POST /signup HTTP/1.1" 302 -
```

### Errors (if any)
```
ERROR:app:{"event": "signup_error", "error": "...", ...}
```

### Health Checks
```
INFO:werkzeug:127.0.0.1 - - [15/Nov/2025 23:22:21] "GET /health HTTP/1.1" 200 -
```

## 🐛 Debugging Tips

### Clear Old Logs
```bash
> flask.log  # Clear the file
# Or delete it
rm flask.log
```

### Check Log File Size
```bash
ls -lh flask.log
```

### Monitor Multiple Things at Once

**Terminal 1 - Watch Logs:**
```bash
tail -f flask.log
```

**Terminal 2 - Run Commands:**
```bash
# Test the app, submit forms, etc.
curl http://localhost:5001/health
```

## 📊 Advanced Log Analysis

### Count Total Requests
```bash
grep "GET\|POST" flask.log | wc -l
```

### Count Signups
```bash
grep "signup_completed" flask.log | wc -l
```

### Show Unique IP Addresses
```bash
grep "werkzeug" flask.log | awk '{print $1}' | sort -u
```

### Find Slow Requests (if timing is logged)
```bash
grep "werkzeug" flask.log | grep -E "[5-9][0-9][0-9]ms|[0-9]{4}ms"
```

## 🔄 Restart with Fresh Logs

```bash
# Stop Flask
pkill -f "flask run"

# Backup old logs (optional)
mv flask.log flask.log.backup

# Start Flask again
cd /Users/conwaysolomon/Documents/Coding/KansasCityFIFA-Signup
source venv/bin/activate
nohup flask run --host=0.0.0.0 --port=5001 > flask.log 2>&1 &

# Watch new logs
tail -f flask.log
```

## 🎨 Better Log Viewing (Optional)

### Install ccze for Colored Logs
```bash
brew install ccze
tail -f flask.log | ccze -A
```

### Install multitail for Advanced Viewing
```bash
brew install multitail
multitail flask.log
```

## 💡 Quick Reference

| Command | Purpose |
|---------|---------|
| `tail -f flask.log` | Watch logs in real-time |
| `tail -30 flask.log` | Show last 30 lines |
| `grep ERROR flask.log` | Show only errors |
| `> flask.log` | Clear log file |
| `./scripts/view_logs.sh` | Easy log viewer |

---

**Tip**: Keep a terminal open with `tail -f flask.log` while testing to see what's happening in real-time! 🚀

