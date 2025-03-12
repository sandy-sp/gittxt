// Add form validation and dynamic UI updates
document.addEventListener('DOMContentLoaded', function() {
    // Handle multiple select styling
    const outputFormat = document.querySelector('select[name="output_format"]');
    if (outputFormat) {
        outputFormat.setAttribute('multiple', 'true');
        outputFormat.style.height = '100px';
    }

    // Add loading state to form submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            const button = this.querySelector('button[type="submit"]');
            button.disabled = true;
            button.textContent = 'Scanning...';
        });
    }
});
