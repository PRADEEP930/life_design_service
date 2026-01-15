# Life Design Backend Service
Simple REST API for tracking personal growth activities.

## 📦 Project Structure
```
life_design_service/
├── app/
│   ├── __init__.py
│   ├── main.py          # Flask app factory
│   ├── config.py        # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py    # All API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── activity_service.py
│   │   └── insight_service.py
│   ├── repository/
│   │   ├── __init__.py
│   │   └── activity_repository.py
│   └── models/
│       ├── __init__.py
│       └── activity.py
├── requirements.txt
├── README.md
└── run.py              # Entry point to run the app
```
#### Framework Choice: Flask
## 🚀 Features Implemented
### Part 1: API Endpoints
- POST /activities – Log a user activity.

- GET /dashboard/{goal_id} – Get summary of activities for a goal.

- GET /insights/optimization – Get personalized productivity recommendations.

### Part 2: Data Interpretation Logic
- Consistency Score: Calculated based on consecutive daily logs.

- Threshold Alert: Wellness warning if weekly health activities < 150 minutes.

- Recommendation Engine: Suggests rebalancing if learning is high but physical wellness is low.

### Part 3: System Design
- Modular: Clean separation between API, services, models, and repository.

- Scalable: Folder structure supports growth and team collaboration.

- Interface Pattern: Repository pattern allows easy swap from in-memory storage to real DB.

## How to Run
### Clone the repository (or extract the project folder).
```
git clone https://github.com/PRADEEP930/life_design_service
cd life_design_service
```

### Install dependencies:
```
pip install -r requirements.txt
```

### Run the server:
```
python run.py
```

### Access interactive API docs at:
```
http://localhost:5000
```

## API Endpoints
1. Log Activity
- POST /activities     #Log Activity
- Content-Type: application/json
```
{
  "goal_id": 1,
  "activity_type": "Learning",
  "value": 120,
  "notes": "Optional note"
}
```
2. Get Dashboard
```
GET /dashboard/1
```
3. Get Insights
```
GET /insights/optimization?goal_id=1
```

## Test with curl or Postman or Thunder client on vs code
- GET/POST              > Method;
- http://localhost:5000 > URL;
- Path                  > API endpoint;
- -H                    > Head section; 
- -d                    > Body section;

### Test the API
```
curl http://localhost:5000/
```
### Log a learning activity
```
curl -X POST http://localhost:5000/activities \
  -H "Content-Type: application/json" \
  -d '{"goal_id":1,"activity_type":"Learning","value":120}'
```

### Log a health activity  
```
curl -X POST http://localhost:5000/activities \
  -H "Content-Type: application/json" \
  -d '{"goal_id":1,"activity_type":"Health","value":60}'
```

### Get dashboard
```
curl http://localhost:5000/dashboard/1
```

### Get insights
```
curl "http://localhost:5000/insights/optimization?goal_id=1"
```

## 🚀 Technical Rationale: Scalability Design

```markdown
The data interpretation logic is designed for efficiency as user logs grow:
- **Consistency Score**: Uses O(n) algorithm that only processes unique dates, not all activities
- **Threshold Alert**: Weekly health total is calculated with time-range filtering, not scanning all history  
- **Recommendation Engine**: Maintains running totals with O(1) lookups for common checks
- **In-Memory to DB Migration**: Repository pattern allows easy swap to PostgreSQL/MongoDB

**Design Patterns Used:**
1. **Repository Pattern**: Abstracts data layer for easy database switching
2. **Service Layer**: Separates business logic from API routes
3. **Dependency Injection**: Services receive repository instances
4. **Blueprint Pattern**: Modular API routing in Flask

**Performance Optimizations:**
1. In-memory indexing by goal_id for O(1) goal-based queries
2. Date-based filtering instead of full scans
3. Lazy calculation of expensive metrics

**As logs scale to millions:** (Future scope)
1. Add database indexing on (goal_id, timestamp)
2. Implement Redis caching for frequent dashboard requests
3. Add background jobs for consistency score calculations
4. Use pagination for activity lists (limit/offset)
5. Implement read replicas for analytics queries

```
# Note.
HOW THIS (system design) ALLOWS EASY DATABASE SWAP:
Current → Future PostgreSQL version:

## app/repository/postgres_repository.py
```python
import psycopg2
from app.repository import BaseRepository  # Same interface!
from app.models.activity import Activity

class PostgresActivityRepository(BaseRepository):  # ← SAME INTERFACE
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def add(self, activity_data: dict) -> Activity:  # ← SAME METHOD SIGNATURE
        # PostgreSQL implementation
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO activities (goal_id, activity_type, value, timestamp, notes)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (activity_data['goal_id'], activity_data['activity_type'], 
              activity_data['value'], activity_data.get('timestamp'), 
              activity_data.get('notes')))
        
        activity_id = cursor.fetchone()[0]
        self.conn.commit()
        
        return Activity(
            id=activity_id,
            **activity_data
        )

        # Other methods with PostgreSQL queries...
```
### Swapping is ONE LINE change:

```python
# Change from:
repository = InMemoryActivityRepository()

# To:
repository = PostgresActivityRepository("postgresql://user:pass@localhost/db")
```
### No other code changes needed! The services continue to call repository.add(), repository.get_by_goal(), etc.