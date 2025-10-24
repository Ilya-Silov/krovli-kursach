document.addEventListener('DOMContentLoaded', function() {
    var notification = document.getElementById('notification');
    notification.style.display = 'block';
    setTimeout(function() {
        notification.style.display = 'none';
    }, 5000); // Скрыть через 5 секунд
});

