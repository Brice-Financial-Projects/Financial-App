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

# app/api/tax_rates/routes.py

from flask import Blueprint, request, jsonify
from .data.federal_tax_data import (
    get_federal_tax_brackets,
    get_standard_deduction,
    get_available_years,
    calculate_tax
)

federal_tax_bp = Blueprint('federal_tax', __name__)


@federal_tax_bp.route('/api/v1/federal/tax-brackets', methods=['GET'])
def get_tax_brackets():
    """Get federal tax brackets for a specific year"""
    year = request.args.get('year', type=int)

    if not year:
        return jsonify({
            'error': 'Year parameter is required'
        }), 400

    try:
        brackets = get_federal_tax_brackets(year)
        return jsonify({
            'year': year,
            'brackets': brackets
        })
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 404


@federal_tax_bp.route('/api/v1/federal/standard-deduction', methods=['GET'])
def get_deduction():
    """Get standard deduction for a specific year and filing status"""
    year = request.args.get('year', type=int)
    filing_status = request.args.get('filing_status')

    if not year or not filing_status:
        return jsonify({
            'error': 'Both year and filing_status parameters are required'
        }), 400

    try:
        deduction = get_standard_deduction(year, filing_status)
        return jsonify({
            'year': year,
            'filing_status': filing_status,
            'standard_deduction': deduction
        })
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 404


@federal_tax_bp.route('/api/v1/federal/calculate', methods=['POST'])
def calculate_federal_tax():
    """Calculate federal tax based on income and other parameters"""
    data = request.get_json()

    required_fields = ['income', 'year', 'filing_status']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': f'Missing required fields. Required: {required_fields}'
        }), 400

    try:
        income = float(data['income'])
        year = int(data['year'])
        filing_status = data['filing_status']

        # Optional parameters
        itemized_deductions = data.get('itemized_deductions', 0)

        tax_result = calculate_tax(
            income=income,
            year=year,
            filing_status=filing_status,
            itemized_deductions=itemized_deductions
        )

        return jsonify({
            'income': income,
            'year': year,
            'filing_status': filing_status,
            'tax_brackets_applied': tax_result['brackets_used'],
            'taxable_income': tax_result['taxable_income'],
            'total_tax': tax_result['total_tax'],
            'effective_rate': tax_result['effective_rate'],
            'marginal_rate': tax_result['marginal_rate']
        })

    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@federal_tax_bp.route('/api/v1/federal/available-years', methods=['GET'])
def available_tax_years():
    """Get list of available tax years"""
    years = get_available_years()
    return jsonify({
        'available_years': years
    })


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