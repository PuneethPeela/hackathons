"""Notification routes"""
from flask import Blueprint

bp = Blueprint('notifications', __name__)


@bp.route('/history', methods=['GET'])
def get_notification_history():
    """Get notification history endpoint"""
    return {'message': 'Notification history endpoint - to be implemented'}, 501
