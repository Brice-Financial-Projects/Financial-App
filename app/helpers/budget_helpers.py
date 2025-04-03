"""app/helpers/budget_helpers.py"""

def get_category_name(category_type, item_id):
    """Helper function to map category IDs to names"""
    category_mapping = {
        'housing': {
            'rent': 'Rent/Mortgage',
            'property_tax': 'Property Tax',
            'hoa': 'HOA Fee',
            'home_insurance': 'Home Insurance',
            'home_repairs': 'Home Repairs'
        },
        'utility': {
            'electricity': 'Electricity',
            'water': 'Water',
            'gas': 'Gas',
            'trash': 'Trash',
            'sewer': 'Sewer'
        },
        'bill': {
            'internet': 'Internet',
            'cell_phone': 'Cell Phone',
            'cable': 'Cable/Streaming',
            'insurance': 'Insurance',
            'gym': 'Gym Membership',
            'cloud_storage': 'Cloud Storage'
        },
        'transport': {
            'car_payment': 'Car Payment',
            'car_insurance': 'Car Insurance',
            'fuel': 'Fuel',
            'maintenance': 'Maintenance',
            'public_transport': 'Public Transportation'
        }
        # Add more category types as needed
    }

    # If category type exists in mapping and item_id exists in that type
    if category_type in category_mapping and item_id in category_mapping[category_type]:
        return category_mapping[category_type][item_id]

    # Fallback: return the item_id with spaces and capitalization
    return item_id.replace('_', ' ').title()
