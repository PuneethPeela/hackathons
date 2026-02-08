"""Medication management routes"""
from flask import Blueprint

bp = Blueprint('medications', __name__)


@bp.route('', methods=['POST'])
def add_medication():
    """Add medication endpoint"""
    return {'message': 'Add medication endpoint - to be implemented'}, 501


@bp.route('', methods=['GET'])
def list_medications():
    """List medications endpoint"""
    return {'message': 'List medications endpoint - to be implemented'}, 501


@bp.route('/<medication_id>', methods=['PUT'])
def update_medication(medication_id):
    """Update medication endpoint"""
    return {'message': 'Update medication endpoint - to be implemented'}, 501


@bp.route('/<medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    """Delete medication endpoint"""
    return {'message': 'Delete medication endpoint - to be implemented'}, 501


@bp.route('/<medication_id>/adherence', methods=['POST'])
def record_adherence(medication_id):
    """Record adherence endpoint"""
    return {'message': 'Record adherence endpoint - to be implemented'}, 501


@bp.route('/<medication_id>/adherence-report', methods=['GET'])
def get_adherence_report(medication_id):
    """Get adherence report endpoint"""
    return {'message': 'Adherence report endpoint - to be implemented'}, 501
