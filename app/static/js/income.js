// app/static/js/income.js

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('other-income-container');
    const addIncomeButton = document.getElementById('add-income');

    // Define frequency options
    const frequencyOptions = `
        <option value="weekly">Weekly</option>
        <option value="biweekly">Biweekly</option>
        <option value="monthly">Monthly</option>
        <option value="bimonthly">Bimonthly</option>
        <option value="annually">Annually</option>
    `;

    addIncomeButton.addEventListener('click', function () {
        const index = container.children.length;
        const newEntry = document.createElement('div');
        newEntry.classList.add('income-entry', 'mb-3');
        newEntry.innerHTML = `
            <label class="form-label">Income Type</label>
            <select class="form-select" name="other_income_sources-${index}-category">
                <option value="rental">Rental Income</option>
                <option value="investment">Investment Dividends</option>
                <option value="business">Business Income</option>
                <option value="side_job">Secondary Employment</option>
                <option value="royalties">Royalties</option>
                <option value="social_security">Social Security</option>
                <option value="pension">Pension</option>
                <option value="other">Other</option>
            </select>

            <label class="form-label mt-2">Name of Income Source</label>
            <input type="text" class="form-control" name="other_income_sources-${index}-name">

            <label class="form-label mt-2">Amount</label>
            <input type="number" class="form-control" name="other_income_sources-${index}-amount">

            <label class="form-label mt-2">Frequency</label>
            <select class="form-select" name="other_income_sources-${index}-frequency">
                ${frequencyOptions}  <!-- Dynamically add all frequency options -->
            </select>

            <button type="button" class="btn btn-danger remove-income mt-2">Remove</button>
        `;
        container.appendChild(newEntry);
    });

    container.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-income')) {
            event.target.parentElement.remove();
        }
    });
});
