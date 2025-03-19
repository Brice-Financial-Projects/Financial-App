"""Tax rates API routes."""
from flask import jsonify, request
from . import tax_rates_bp
from .models import (
    TaxBracket, FederalTaxData, StateTaxData, FICATaxData,
    TaxCalculationRequest, TaxCalculationResponse
)
from .data import federal_tax_data, state_tax_data, fica_tax_data
from datetime import datetime
from http import HTTPStatus

@tax_rates_bp.route('/federal/<int:year>', methods=['GET'])
def get_federal_tax_brackets(year):
    """Get federal tax brackets for a specific year."""
    try:
        # Get the tax brackets for the specified year
        brackets = federal_tax_data.get_federal_tax_brackets(year)
        if not brackets:
            return jsonify({
                'error': 'Tax brackets not found for specified year'
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            'year': year,
            'brackets': [bracket.to_dict() for bracket in brackets],
            'standard_deduction': federal_tax_data.get_standard_deduction(year)
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@tax_rates_bp.route('/state/<string:state>/<int:year>', methods=['GET'])
def get_state_tax_brackets(state, year):
    """Get state tax brackets for a specific state and year."""
    try:
        # Convert state to uppercase for consistency
        state = state.upper()
        
        # Get the tax brackets for the specified state and year
        brackets = state_tax_data.get_state_tax_brackets(state, year)
        if not brackets:
            return jsonify({
                'error': 'Tax brackets not found for specified state and year'
            }), HTTPStatus.NOT_FOUND

        return jsonify({
            'state': state,
            'year': year,
            'brackets': [bracket.to_dict() for bracket in brackets],
            'has_state_tax': state_tax_data.has_state_income_tax(state)
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@tax_rates_bp.route('/fica/<int:year>', methods=['GET'])
def get_fica_rates(year):
    """Get FICA (Social Security and Medicare) rates for a specific year."""
    try:
        fica_data = fica_tax_data.get_fica_rates(year)
        if not fica_data:
            return jsonify({
                'error': 'FICA rates not found for specified year'
            }), HTTPStatus.NOT_FOUND

        return jsonify(fica_data.to_dict()), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@tax_rates_bp.route('/calculate', methods=['POST'])
def calculate_taxes():
    """Calculate taxes based on income and other factors."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), HTTPStatus.BAD_REQUEST

        # Create a tax calculation request object
        tax_request = TaxCalculationRequest(
            year=data.get('year', datetime.now().year),
            income=data.get('income'),
            state=data.get('state', '').upper(),
            filing_status=data.get('filing_status'),
            pay_frequency=data.get('pay_frequency'),
            additional_withholding=data.get('additional_withholding', 0.0),
            pretax_deductions=data.get('pretax_deductions', 0.0)
        )

        # Validate the request
        if not tax_request.is_valid():
            return jsonify({
                'error': 'Invalid request data',
                'details': tax_request.validation_errors()
            }), HTTPStatus.BAD_REQUEST

        # Calculate federal tax
        federal_tax = federal_tax_data.calculate_tax(
            tax_request.income,
            tax_request.year,
            tax_request.filing_status
        )

        # Calculate state tax if applicable
        state_tax = 0.0
        if state_tax_data.has_state_income_tax(tax_request.state):
            state_tax = state_tax_data.calculate_tax(
                tax_request.income,
                tax_request.state,
                tax_request.year,
                tax_request.filing_status
            )

        # Calculate FICA
        fica = fica_tax_data.calculate_fica(
            tax_request.income,
            tax_request.year
        )

        # Create response
        response = TaxCalculationResponse(
            federal_tax=federal_tax,
            state_tax=state_tax,
            social_security_tax=fica['social_security'],
            medicare_tax=fica['medicare'],
            total_tax=federal_tax + state_tax + fica['total'],
            effective_tax_rate=((federal_tax + state_tax + fica['total']) / tax_request.income) * 100
        )

        return jsonify(response.to_dict()), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@tax_rates_bp.route('/years', methods=['GET'])
def get_available_years():
    """Get list of years for which tax data is available."""
    try:
        federal_years = federal_tax_data.get_available_years()
        state_years = state_tax_data.get_available_years()
        fica_years = fica_tax_data.get_available_years()

        return jsonify({
            'federal_years': sorted(federal_years),
            'state_years': sorted(state_years),
            'fica_years': sorted(fica_years),
            'common_years': sorted(set(federal_years) & set(state_years) & set(fica_years))
        }), HTTPStatus.OK

    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR 