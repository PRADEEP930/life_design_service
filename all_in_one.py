from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from typing import List, Dict
import json

app = Flask(__name__)

# ========== STORAGE ==========
activities_db = []
next_id = 1

# ========== HELPER FUNCTIONS ==========
def calculate_consistency_score(goal_activities: List[dict]) -> float:
    """Calculate consistency score 0.0 to 1.0"""
    if not goal_activities:
        return 0.0
    
    # Get unique dates
    dates = sorted(set(datetime.fromisoformat(a["timestamp"]).date() 
                       for a in goal_activities))
    
    if len(dates) < 2:
        return 0.5
    
    # Find longest streak
    max_streak = 0
    current_streak = 1
    
    for i in range(1, len(dates)):
        days_diff = (dates[i] - dates[i-1]).days
        if days_diff == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    score = max_streak / len(dates)
    return round(min(score, 1.0), 2)

def get_weekly_health_total(goal_activities: List[dict]) -> float:
    """Calculate total health activities for past week"""
    one_week_ago = datetime.now() - timedelta(days=7)
    
    health_total = 0
    for activity in goal_activities:
        if activity["activity_type"] == "Health":
            activity_time = datetime.fromisoformat(activity["timestamp"])
            if activity_time >= one_week_ago:
                health_total += activity["value"]
    
    return health_total

def generate_recommendation(goal_activities: List[dict]) -> str:
    """Generate personalized recommendation"""
    if not goal_activities:
        return "Start logging activities to get personalized recommendations!"
    
    # Calculate totals
    health_total = 0
    learning_total = 0
    
    for activity in goal_activities:
        if activity["activity_type"] == "Health":
            health_total += activity["value"]
        elif activity["activity_type"] == "Learning":
            learning_total += activity["value"]
    
    weekly_health = get_weekly_health_total(goal_activities)
    
    # Generate recommendations
    if weekly_health < 150:
        if learning_total > 300:
            return "High learning activity detected but physical wellness is low. Consider rebalancing your growth plan."
        else:
            return "Try to reach 150+ minutes of health activities per week."
    
    if learning_total > 400:
        return "Great learning consistency! Keep up the good work."
    
    return "You're making progress! Continue tracking your activities."

# ========== API ENDPOINTS ==========
@app.route('/activities', methods=['POST'])
def create_activity():
    """Log a new activity"""
    global next_id
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['goal_id', 'activity_type', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create activity
        activity = {
            "id": next_id,
            "goal_id": data['goal_id'],
            "activity_type": data['activity_type'],
            "value": float(data['value']),
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "notes": data.get('notes')
        }
        
        activities_db.append(activity)
        next_id += 1
        
        return jsonify(activity), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/dashboard/<int:goal_id>', methods=['GET'])
def get_dashboard(goal_id):
    """Get dashboard for a specific goal"""
    goal_activities = [a for a in activities_db if a["goal_id"] == goal_id]
    
    if not goal_activities:
        return jsonify({
            "goal_id": goal_id,
            "message": "No activities found",
            "total_activities": 0,
            "activities": []
        })
    
    # Calculate summary
    total_value = sum(a["value"] for a in goal_activities)
    
    # Group by activity type
    activity_by_type = {}
    for activity in goal_activities:
        activity_type = activity["activity_type"]
        if activity_type not in activity_by_type:
            activity_by_type[activity_type] = {"count": 0, "total_value": 0}
        activity_by_type[activity_type]["count"] += 1
        activity_by_type[activity_type]["total_value"] += activity["value"]
    
    # Calculate metrics
    consistency_score = calculate_consistency_score(goal_activities)
    weekly_health = get_weekly_health_total(goal_activities)
    wellness_warning = weekly_health < 150
    recommendation = generate_recommendation(goal_activities)
    
    # Get last activity time
    last_activity = max(goal_activities, 
                       key=lambda x: datetime.fromisoformat(x["timestamp"]))
    
    return jsonify({
        "goal_id": goal_id,
        "summary": {
            "total_activities": len(goal_activities),
            "total_value": total_value,
            "average_value": total_value / len(goal_activities),
            "activity_by_type": activity_by_type,
            "last_activity": last_activity["timestamp"]
        },
        "activities": goal_activities,
        "consistency_score": consistency_score,
        "wellness_warning": wellness_warning,
        "recommendation": recommendation
    })

@app.route('/insights/optimization', methods=['GET'])
def get_optimization_insights():
    """Get optimization insights"""
    goal_id = request.args.get('goal_id', type=int)
    
    if not goal_id:
        return jsonify({"error": "Missing goal_id parameter"}), 400
    
    goal_activities = [a for a in activities_db if a["goal_id"] == goal_id]
    
    if not goal_activities:
        return jsonify({
            "goal_id": goal_id,
            "message": "No activities found",
            "consistency_score": 0.0,
            "wellness_warning": False
        })
    
    # Calculate metrics
    consistency_score = calculate_consistency_score(goal_activities)
    weekly_health = get_weekly_health_total(goal_activities)
    wellness_warning = weekly_health < 150
    
    # Calculate type totals
    health_total = 0
    learning_total = 0
    for activity in goal_activities:
        if activity["activity_type"] == "Health":
            health_total += activity["value"]
        elif activity["activity_type"] == "Learning":
            learning_total += activity["value"]
    
    # Generate recommendation
    recommendation = generate_recommendation(goal_activities)
    
    return jsonify({
        "goal_id": goal_id,
        "consistency_score": consistency_score,
        "weekly_health_total": weekly_health,
        "wellness_warning": wellness_warning,
        "recommendation": recommendation,
        "learning_total": learning_total,
        "health_total": health_total
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Life Design Backend Service",
        "version": "1.0.0",
        "endpoints": {
            "POST /activities": "Log a new activity",
            "GET /dashboard/<goal_id>": "Get dashboard for a goal",
            "GET /insights/optimization?goal_id=<id>": "Get optimization insights"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# ========== RUN THE APP ==========
if __name__ == '__main__':
    print("Starting Life Design Service...")
    print("API will be available at: http://localhost:5000")
    print("Add some activities:")
    print("  curl -X POST http://localhost:5000/activities -H 'Content-Type: application/json' -d '{\"goal_id\":1,\"activity_type\":\"Learning\",\"value\":120}'")
    app.run(debug=True, host='0.0.0.0', port=5000)