(function() {
    // If the settings don't exist (meaning user is logged out), stop immediately
    if (!window.NexusSettings) return;

    // PROFESSIONAL SETTINGS
    const totalIdleTime = 1200000; // 20 Minutes total
    const warningTime = 60000;     // 60 Second countdown
    const idleLimit = totalIdleTime - warningTime; // 19 Minutes
    
    let idleTimer;
    let countdownTimer;
    let secondsRemaining; // We will set this dynamically

    const warningBox = document.getElementById('inactivity-warning');
    const timerSpan = document.getElementById('timer-seconds');
    const stayBtn = document.getElementById('stay-logged-in');

    const showWarning = () => {
        warningBox.style.display = 'flex';
        
        // Sync the countdown with your variable (60 seconds)
        secondsRemaining = warningTime / 1000; 
        timerSpan.innerText = secondsRemaining;

        countdownTimer = setInterval(() => {
            secondsRemaining--;
            timerSpan.innerText = secondsRemaining;
            
            if (secondsRemaining <= 0) {
                clearInterval(countdownTimer);
                window.location.href = window.NexusSettings.logoutUrl;
            }
        }, 1000);
    };

    const resetEverything = () => {
        warningBox.style.display = 'none';
        clearInterval(countdownTimer);
        clearTimeout(idleTimer);
        
        idleTimer = setTimeout(showWarning, idleLimit);
    };

    stayBtn.addEventListener('click', resetEverything);

    ['mousedown', 'mousemove', 'keydown', 'scroll', 'click'].forEach(event => {
        window.addEventListener(event, () => {
            if (warningBox.style.display === 'none') {
                resetEverything();
            }
        }, true);
    });

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && warningBox.style.display === 'none') {
            resetEverything(); 
        }
    });

    resetEverything();
})();