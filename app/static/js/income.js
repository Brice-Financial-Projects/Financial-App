// app/static/js/income.js

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('other-income-container');
    const addIncomeButton = document.getElementById('add-income');

    addIncomeButton.addEventListener('click', function () {
        const index = container.children.length;
        const newEntry = document.createElement('div');
        newEntry.classList.add('income-entry', 'mb-3');
        newEntry.innerHTML = `
            <label class="form-label">Name of Income Source</label>
            <input type="text" class="form-control" name="other_income_sources-${index}-name">
            <label class="form-label mt-2">Amount</label>
            <input type="number" class="form-control" name="other_income_sources-${index}-amount">
            <label class="form-label mt-2">Frequency</label>
            <select class="form-select" name="other_income_sources-${index}-frequency">
                <option value="monthly">Monthly</option>
                <option value="annually">Annually</option>
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
