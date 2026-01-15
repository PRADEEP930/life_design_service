from flask import Flask, jsonify
from app.config import config
from app.api.routes import api_bp

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            "service": "Life Design Backend Service",
            "version": "1.0.0",
            "endpoints": {
                "POST /api/activities": "Log a new activity",
                "GET /api/dashboard/{goal_id}": "Get dashboard for a goal",
                "GET /api/insights/optimization?goal_id={id}": "Get optimization insights",
                "GET /api/health": "Health check"
            },
            "documentation": "See README.md for detailed API usage"
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "message": "Check the API documentation at /"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "Something went wrong on our end"
        }), 500
    
    return app