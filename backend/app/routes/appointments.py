"""Appointment and care navigation routes"""
from flask import Blueprint

bp = Blueprint('appointments', __name__)


@bp.route('', methods=['POST'])
def schedule_appointment():
    """Schedule appointment endpoint"""
    return {'message': 'Schedule appointment endpoint - to be implemented'}, 501


@bp.route('', methods=['GET'])
def list_appointments():
    """List appointments endpoint"""
    return {'message': 'List appointments endpoint - to be implemented'}, 501


@bp.route('/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update appointment endpoint"""
    return {'message': 'Update appointment endpoint - to be implemented'}, 501
