# Documentation

## Notes on progress:

- Date: 3/16/2025
    Progress
      - Fixed route.py so profile page, dashboard, expenses, and income pages all commit to the db.
      - DB properly references table ids
      - Fixed the CSRF Token errors
      - The view and delete button from the dashboard work.
      - The edit button needs to be debugged

    Needs Improvement
      - Budget logic
      - Preview budget html page
      - Edit budget from dashboard
      - Transition from page to page
      - Flash message displays are inaccurate

- Date: 3/18/2025
    Progress
      - Enhanced Profile model with comprehensive tax-related fields
      - Added detailed pre-tax benefit tracking (health insurance, HSA, FSA)
      - Improved profile form UI with organized sections and proper validation
      - Set up tax rate API infrastructure (models, cache, configuration)
      - Fixed database migration issues with proper default values
      - Added proper handling for retirement contributions (pre-tax/post-tax)
      - Improved form validation and error handling
      - Enhanced UI with Bootstrap cards and proper input formatting

    Needs Improvement
      - Implement live tax rate API integration
      - Connect tax calculation logic to budget processing
      - Add tax bracket visualization in results
      - Implement caching for tax rate data
      - Add tax calculation documentation
      - Add unit tests for tax calculations
      - Add validation for tax-related fields
      - Add help tooltips for tax-related inputs
      - Implement state-specific tax rules
      - Add tax summary to budget preview
      - Add tax withholding calculator
      - Add annual tax projection report

- Date: 3/18/2025 (Update 2)
    Progress
      - Implemented internal Tax Rate API with the following endpoints:

        1. Get Federal Tax Brackets
           ```
           GET /api/v1/tax/federal/<year>
           ```
           Returns federal tax brackets and standard deduction for specified year.

        2. Get State Tax Brackets
           ```
           GET /api/v1/tax/state/<state>/<year>
           ```
           Returns state tax brackets and information for specified state and year.

        3. Get FICA Rates
           ```
           GET /api/v1/tax/fica/<year>
           ```
           Returns Social Security and Medicare rates for specified year.

        4. Calculate Taxes
           ```
           POST /api/v1/tax/calculate
           ```
           Calculates total tax liability based on provided income and details.
           Request body example:
           ```json
           {
               "year": 2024,
               "income": 75000,
               "state": "CA",
               "filing_status": "single",
               "pay_frequency": "biweekly",
               "additional_withholding": 100,
               "pretax_deductions": 5000
           }
           ```

        5. Get Available Tax Years
           ```
           GET /api/v1/tax/years
           ```
           Returns list of years for which tax data is available.

    Needs Improvement
      - Implement data modules for federal, state, and FICA tax calculations
      - Add request/response models validation
      - Add comprehensive API tests
      - Add API documentation with example responses
      - Implement caching for API responses
      - Add rate limiting for API endpoints
      - Add authentication for sensitive endpoints
      

