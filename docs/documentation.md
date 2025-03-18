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
      

