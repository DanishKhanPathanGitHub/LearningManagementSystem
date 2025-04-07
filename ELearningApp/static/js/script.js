document.addEventListener('DOMContentLoaded', function() {
    // UTC to local time conversion
    document.querySelectorAll('.utc-time').forEach(function(element) {
        var utcDate = element.getAttribute('data-utc');
        var format = element.getAttribute('data-format') || 'date-time'; // Default to date-time if not specified

        if (utcDate) {
            var localDate;
            if (format === 'date-only') {
                localDate = moment.utc(utcDate).local().format('YYYY-MM-DD'); // Format for date only
            } else {
                localDate = moment.utc(utcDate).local().format('YYYY-MM-DD HH:mm:ss'); // Format for date and time
            }
            element.textContent = localDate;
        } else {
            console.error('Missing data-utc attribute for element:', element);
        }
    });
    
});
