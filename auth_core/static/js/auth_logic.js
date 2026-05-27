document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.querySelector('.auth-form');
    const submitBtn = document.querySelector('.btn-primary');

    if (authForm && submitBtn) {
        authForm.addEventListener('submit', (e) => {
            // Check if form is valid (if using browser validation)
            if (!authForm.checkValidity()) {
                return; 
            }

            // Trigger loading state
            submitBtn.classList.add('is-loading');

            // Add spinner if not already there
            if (!submitBtn.querySelector('.spinner')) {
                const spinner = document.createElement('div');
                spinner.className = 'spinner';
                submitBtn.appendChild(spinner);
            }
        });
    }
});