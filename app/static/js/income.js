// app/static/js/income.js

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('other-income-container');
    const addIncomeButton = document.getElementById('add-income');

    addIncomeButton.addEventListener('click', function () {
        const index = container.children.length;
        const newEntry = document.createElement('div');
        newEntry.classList.add('income-entry', 'mb-3');
        
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;
        
        newEntry.innerHTML = `
            <input type="hidden" name="other_income_sources-${index}-csrf_token" value="${csrfToken}">
            
            <div class="mb-3">
                <label class="form-label" for="other_income_sources-${index}-category">Income Type</label>
                <select class="form-select" id="other_income_sources-${index}-category" name="other_income_sources-${index}-category" required>
                    <option value="">Select Income Type</option>
                    <option value="rental">Rental Income</option>
                    <option value="investment">Investment Dividends</option>
                    <option value="business">Business Income</option>
                    <option value="side_job">Secondary Employment</option>
                    <option value="royalties">Royalties</option>
                    <option value="social_security">Social Security</option>
                    <option value="pension">Pension</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="mb-3">
                <label class="form-label" for="other_income_sources-${index}-name">Income Source Name</label>
                <input type="text" class="form-control" id="other_income_sources-${index}-name" name="other_income_sources-${index}-name" required>
            </div>

            <div class="mb-3">
                <label class="form-label" for="other_income_sources-${index}-amount">Amount</label>
                <input type="number" class="form-control" id="other_income_sources-${index}-amount" name="other_income_sources-${index}-amount" required step="0.01" min="0">
            </div>

            <div class="mb-3">
                <label class="form-label" for="other_income_sources-${index}-frequency">Frequency</label>
                <select class="form-select" id="other_income_sources-${index}-frequency" name="other_income_sources-${index}-frequency" required>
                    <option value="">Select Frequency</option>
                    <option value="weekly">Weekly</option>
                    <option value="biweekly">Biweekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="bimonthly">Bimonthly</option>
                    <option value="annually">Annually</option>
                </select>
            </div>

            <button type="button" class="btn btn-danger remove-income">Remove</button>
        `;
        container.appendChild(newEntry);
    });

    // Handle removal of income sources
    container.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-income')) {
            const entry = event.target.closest('.income-entry');
            if (entry) {
                entry.remove();
                // Reindex remaining entries
                const entries = container.querySelectorAll('.income-entry');
                entries.forEach((entry, index) => {
                    entry.querySelectorAll('[name^="other_income_sources-"]').forEach(input => {
                        const fieldName = input.name.split('-').pop();
                        input.name = `other_income_sources-${index}-${fieldName}`;
                        if (input.id) {
                            input.id = `other_income_sources-${index}-${fieldName}`;
                        }
                    });
                });
            }
        }
    });
});

