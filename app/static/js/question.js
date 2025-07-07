document.querySelector('textarea').value = ''
function toggleAnswer(button) {
    const container = button.parentElement.parentElement;
    const textEl = container.querySelector("p");
    const isExpanded = textEl.classList.contains("expanded");
    if (isExpanded) {
        textEl.classList.remove("expanded");
        textEl.classList.add("line-clamp-5");
        button.textContent = "Показать полностью";
    } else {
        textEl.classList.remove("line-clamp-5");
        textEl.classList.add("expanded");
        button.textContent = "Скрыть";
    }
}
document.addEventListener("DOMContentLoaded", function () {
    // Проверка для показа кнопки "Показать полностью"
    document.querySelectorAll(".line-clamp-5").forEach(el => {
        const parentButton = el.closest(".bg-white").querySelector("button[onclick]");
        const lineHeight = 20;
        const lines = el.scrollHeight / lineHeight;
        const maxLines = parseInt(el.getAttribute("data-max-lines")) || 5;
        if (lines > maxLines) {
            parentButton.classList.remove("hidden");
        }
    });
    // Валидация формы: запрет отправки пустого ответа
    const textarea = document.querySelector('textarea[name="content"]');
    const submitBtn = document.querySelector('button[type="submit"]');
    if (textarea && submitBtn) {
        textarea.addEventListener("input", function () {
            if (textarea.value.trim() === "") {
                submitBtn.disabled = true;
            } else {
                submitBtn.disabled = false;
            }
        });
    }
});
function validateAnswer() {
    const textarea = document.querySelector('textarea[name="content"]');
    const value = textarea.value;
    if (!value || value.trim().length === 0) {
        alert("Пожалуйста, введите текст ответа.");
        textarea.focus();
        return false;
    }
    return true;
}
// Функции для работы с лайками
function showLoginAlert() {
    alert("Чтобы поставить лайк, войдите через Telegram.");
}
async function likeAnswer(answerId, userId) {
    try {
        const response = await fetch('/answer/like/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                answer_id: answerId,
                user_id: userId
            })
        });
        if (!response.ok) {
            throw new Error('Ошибка при отправке лайка');
        }
        const result = await response.json();
        
        // Обновляем UI без перезагрузки страницы
        const likeButton = document.querySelector(`button[onclick="likeAnswer('${answerId}', '${userId}')"]`);
        const likeCountSpan = likeButton.previousElementSibling;
        const heartIcon = likeButton.querySelector('svg');
        
        if (result.action === 'liked') {
            heartIcon.setAttribute('fill', 'red');
            likeCountSpan.textContent = parseInt(likeCountSpan.textContent) + 1;
        } else {
            heartIcon.setAttribute('fill', 'gray');
            likeCountSpan.textContent = parseInt(likeCountSpan.textContent) - 1;
        }
        
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при обработке лайка');
    }
}