document.addEventListener('DOMContentLoaded', function() {
    // Find all alert messages
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        // 1. Make it appear smoothly
        // We use a tiny timeout so the transition actually triggers
        setTimeout(() => {
            alert.classList.add('show');
        }, 100);

        // 2. Set a timer to make it disappear after 3 seconds
        setTimeout(() => {
            alert.classList.add('fade-out');
            
            // 3. Remove from the DOM completely after the fade animation finishes
            alert.addEventListener('transitionend', () => {
                alert.remove();
            });
        }, 3000); // 3 seconds
    });
});