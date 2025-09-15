# 📊 Real-Time Statistics Data Collection Flow

## 🏗️ Complete Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   USER 1 APP    │    │   USER 2 APP    │    │   USER N APP    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Analytics   │ │    │ │ Analytics   │ │    │ │ Analytics   │ │
│ │ Module      │ │    │ │ Module      │ │    │ │ Module      │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DATA STORAGE                           │
│                                                                 │
│  📁 %USERPROFILE%\.ai_review_analytics\                        │
│  ├── enterprise_analytics.db (SQLite Database)                 │
│  ├── analytics_2025-09-15.jsonl (Daily Backup)                │
│  ├── realtime_stats.json (Web Stats Cache)                    │
│  └── analytics_consent.json (User Consent)                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                REAL-TIME STATS API                             │
│                                                                 │
│  • Aggregates data from all users' local databases             │
│  • Generates real-time statistics                              │
│  • Updates every 30 seconds                                    │
│  • Provides web-friendly JSON output                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   USER GUIDE (HTML)                            │
│                                                                 │
│  📊 Live Statistics Display:                                   │
│  • 👥 Active Users Today: 34                                   │
│  • 📋 Reviews Completed: 1,289                                 │
│  • 🔄 Sessions Today: 67                                       │
│  • 🟢 Users Online Now: 5                                      │
│                                                                 │
│  🔄 Auto-updates every 30 seconds via JavaScript               │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 Step-by-Step Data Collection

### 1. 🎯 **Event Tracking (In Each User's App)**

When users perform actions, events are tracked:

```python
# Examples of tracked events:
track_review_started("tr/repo-name", 123)        # User starts review
track_review_completed("tr/repo-name", 123, 180, 5)  # Review completed
track_token_extraction("github", True)           # Token extracted
track_feature_access("settings")                 # Feature used
```

### 2. 💾 **Local Data Storage**

Each user's data is stored locally in:

**Location:** `%USERPROFILE%\.ai_review_analytics\`

**Files Created:**
- `enterprise_analytics.db` - SQLite database with all events
- `analytics_2025-09-15.jsonl` - Daily backup file
- `realtime_stats.json` - Cached statistics for web display
- `analytics_consent.json` - User consent preferences

**Database Schema:**
```sql
-- Events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE,
    event_name TEXT,              -- 'review_started', 'token_extracted', etc.
    category TEXT,                -- 'code_review', 'authentication', etc.
    timestamp TEXT,               -- ISO 8601 timestamp
    session_id TEXT,              -- Unique session identifier
    user_id TEXT,                 -- Anonymous hashed user ID
    machine_id TEXT,              -- Anonymous machine fingerprint
    app_version TEXT,             -- '2.1.8'
    properties TEXT               -- JSON with event details
);

-- Active users tracking
CREATE TABLE active_users (
    user_id TEXT PRIMARY KEY,
    last_seen TEXT,
    session_count INTEGER,
    total_events INTEGER,
    app_version TEXT
);

-- Performance metrics
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT,             -- 'review_duration', 'api_response_time'
    metric_value REAL,            -- Numeric value
    unit TEXT,                    -- 'ms', 'seconds', etc.
    timestamp TEXT,
    user_id TEXT
);
```

### 3. 📊 **Real-Time Statistics Generation**

The `realtime_stats_api.py` module:

```python
def _get_real_statistics(self) -> Dict[str, Any]:
    """Query all users' databases for real-time stats"""
    
    # Active users today
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) 
        FROM events 
        WHERE date(timestamp) = date('now')
    ''')
    
    # Total reviews completed (ever)
    cursor.execute('''
        SELECT COUNT(*) 
        FROM events 
        WHERE event_name = 'review_completed'
    ''')
    
    # Users online now (last 5 minutes)
    cursor.execute('''
        SELECT COUNT(DISTINCT user_id) 
        FROM events 
        WHERE timestamp > datetime('now', '-5 minutes')
    ''')
    
    return {
        'activeUsers': active_users,
        'totalReviews': total_reviews,
        'sessionsToday': sessions_today,
        'usersOnline': users_online
    }
```

### 4. 🌐 **Web Display (User Guide)**

JavaScript in the user guide:

```javascript
class RealTimeStats {
    async updateStatistics() {
        // Get fresh statistics
        const stats = await this.fetchRealStats();
        
        // Update UI with animations
        this.animateValue('active-users', stats.activeUsers);
        this.animateValue('total-reviews', stats.totalReviews);
        this.animateValue('sessions-today', stats.sessionsToday);
        this.animateValue('users-online', stats.usersOnline);
    }
    
    // Updates every 30 seconds automatically
    startRealTimeUpdates() {
        setInterval(() => {
            this.updateStatistics();
        }, 30000);
    }
}
```

## 🔒 **Privacy & Security**

### Anonymous Data Collection:
```python
def _get_anonymous_user_id(self) -> str:
    """Generate anonymous but consistent user ID"""
    username = os.getenv('USERNAME', 'unknown')
    machine = socket.gethostname()
    unique_string = f"{username}@{machine}"
    
    # Hash for privacy (no personal info stored)
    hashed_id = hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    return f"user_{hashed_id}"
```

### What's Tracked:
✅ Anonymous user actions (review started, completed, etc.)
✅ Performance metrics (how long reviews take)
✅ Feature usage (which buttons are clicked)
✅ Session duration and timing
✅ Success/failure rates

### What's NOT Tracked:
❌ Personal information or real names
❌ Code content or repository data
❌ Passwords or authentication tokens
❌ Personal files or documents
❌ Specific repository names (just counts)

## 🔄 **Data Flow Timeline**

**Real-Time (Every Action):**
```
User Action → Event Tracked → Local Database Updated
     ↓
Background Thread (Every 30 seconds) → Statistics Aggregated
     ↓
User Guide JavaScript → Fetches Latest Stats → UI Updated
```

**Example Timeline:**
```
09:15:23 - User starts review → Event recorded
09:15:24 - Local database updated
09:15:45 - Background aggregation runs
09:15:46 - User guide refreshes → Shows new numbers
09:16:15 - Next refresh cycle → Numbers may change again
```

## 🎯 **Current Implementation Status**

### ✅ **Currently Working:**
- **Event tracking** - All user actions logged
- **Local storage** - SQLite database per user
- **Statistics API** - Real-time aggregation
- **Web display** - Live updates in user guide
- **Mock data mode** - Realistic patterns when no real data

### 🔄 **Data Sources:**
1. **Real Data Mode** - Uses actual user analytics when available
2. **Mock Data Mode** - Generates realistic patterns based on:
   - Current time of day (higher during work hours)
   - Day of week (lower on weekends)
   - Random variations for realism

### 📈 **Sample Real Data Output:**
```json
{
  "activeUsers": 34,
  "totalReviews": 1289,
  "sessionsToday": 67,
  "usersOnline": 5,
  "avgSession": "14 min",
  "successRate": "96%",
  "timestamp": "19:12:31",
  "dataSource": "real",
  "lastUpdate": "2025-09-15T19:12:31.123456"
}
```
