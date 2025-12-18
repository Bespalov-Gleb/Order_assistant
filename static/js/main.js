// Общие JavaScript функции для приложения

function showGlobalLoading(message) {
    const overlay = document.getElementById('globalLoading');
    const textElement = document.getElementById('loadingText');
    if (!overlay || !textElement) {
        return;
    }
    textElement.textContent = message || 'Обработка... Пожалуйста, подождите.';
    overlay.style.display = 'flex';
}

function hideGlobalLoading() {
    const overlay = document.getElementById('globalLoading');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Автоматическое скрытие уведомлений через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Индикатор загрузки при загрузке Excel файла
    const uploadModal = document.getElementById('uploadForm');
    if (uploadModal) {
        const uploadForm = uploadModal.querySelector('form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', function() {
                const fileInput = document.getElementById('file');
                if (fileInput && fileInput.files && fileInput.files.length > 0) {
                    const submitButton = uploadForm.querySelector('button[type=\"submit\"]');
                    if (submitButton) {
                        submitButton.disabled = true;
                        submitButton.textContent = 'Загружаю...';
                    }
                    showGlobalLoading('Загружаю и разбираю Excel файл. Это может занять до 10 секунд...');
                }
            });
        }
    }
});

// Функция для закрытия модального окна при клике вне его
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};

// Закрытие модального окна при нажатии Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

