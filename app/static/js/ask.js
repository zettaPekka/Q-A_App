document.addEventListener('DOMContentLoaded', function() {
    const tagInput = document.getElementById('tag-input');
    const tagInputContainer = document.getElementById('tag-input-container');
    const tagsContainer = document.getElementById('tags-container');
    const addTagBtn = document.getElementById('add-tag-btn');
    const tagSuggestions = document.getElementById('tag-suggestions');
    const maxTags = 5;
    let selectedTags = [];
    const allTags = [
        'программирование', 'технологии', 'образование', 'наука', 'бизнес',
        'математика', 'физика', 'история', 'искусство', 'дизайн',
        'маркетинг', 'стартапы', 'аналитика', 'данные', 'алгоритмы',
        'веб-разработка', 'мобильная разработка', 'искусственный интеллект',
        'машинное обучение', 'нейросети', 'кибербезопасность', 'блокчейн'
    ];
    // Add tag button click handler
    addTagBtn.addEventListener('click', function() {
        tagInputContainer.classList.remove('hidden');
        tagInput.focus();
        addTagBtn.classList.add('hidden');
    });
    // Tag input handler
    tagInput.addEventListener('input', function() {
        const input = this.value.trim().toLowerCase();
        if (input.length > 1) {
            const filtered = allTags.filter(tag => 
                tag.toLowerCase().includes(input) && 
                !selectedTags.includes(tag)
            );
            showSuggestions(filtered);
        } else {
            hideSuggestions();
        }
    });
    // Tag input keydown handler
    tagInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tag = this.value.trim();
            if (tag && !selectedTags.includes(tag)) {
                addTag(tag);
                this.value = '';
                hideSuggestions();
            }
        }
    });
    // Show tag suggestions
    function showSuggestions(tags) {
        if (tags.length === 0) {
            tagSuggestions.innerHTML = '<div class="p-2 text-gray-500">Нет подходящих тегов</div>';
        } else {
            tagSuggestions.innerHTML = tags.map(tag => `
                <div class="p-2 hover:bg-indigo-50 cursor-pointer" data-tag="${tag}">${tag}</div>
            `).join('');
        }
        tagSuggestions.classList.remove('hidden');
    }
    // Hide suggestions
    function hideSuggestions() {
        tagSuggestions.classList.add('hidden');
    }
    // Click on suggestion
    tagSuggestions.addEventListener('click', function(e) {
        if (e.target.dataset.tag) {
            addTag(e.target.dataset.tag);
            tagInput.value = '';
            hideSuggestions();
        }
    });
    // Add tag function
    function addTag(tag) {
        if (selectedTags.length >= maxTags) return;
        if (tag && !selectedTags.includes(tag)) {
            selectedTags.push(tag);
            renderTags();
        }
    }
    // Remove tag function
    function removeTag(tag) {
        selectedTags = selectedTags.filter(t => t !== tag);
        renderTags();
    }
    // Render tags function
    function renderTags() {
        tagsContainer.innerHTML = selectedTags.map(tag => `
            <div class="flex items-center bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm">
                ${tag}
                <button type="button" class="ml-1 text-indigo-600 hover:text-indigo-800" data-tag="${tag}">
                    &times;
                </button>
            </div>
        `).join('');
        if (selectedTags.length < maxTags) {
            const addBtn = `
                <button type="button" id="add-tag-btn" class="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 hover:bg-indigo-200 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                </button>
            `;
            tagsContainer.innerHTML += addBtn;
            document.getElementById('add-tag-btn').addEventListener('click', function() {
                tagInputContainer.classList.remove('hidden');
                tagInput.focus();
                this.classList.add('hidden');
            });
        }
        // Add event listeners to remove buttons
        document.querySelectorAll('#tags-container button[data-tag]').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                removeTag(this.dataset.tag);
            });
        });
    }
    // Form submit handler with validation
    document.getElementById('question-form').addEventListener('submit', function(e) {
        const title = document.getElementById('title').value.trim();
        const content = document.getElementById('content').value.trim();
        // Сброс предыдущих ошибок
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('input, textarea').forEach(el => el.classList.remove('border-red-500'));
        let isValid = true;
        // Проверка заголовка
        if (!title) {
            e.preventDefault();
            isValid = false;
            const error = document.createElement('div');
            error.className = 'text-red-500 text-sm mt-1 error-message';
            error.textContent = 'Заголовок не может быть пустым.';
            document.getElementById('title').parentNode.appendChild(error);
            document.getElementById('title').classList.add('border-red-500');
        } else if (title.length > 200) {
            e.preventDefault();
            isValid = false;
            const error = document.createElement('div');
            error.className = 'text-red-500 text-sm mt-1 error-message';
            error.textContent = 'Заголовок не должен превышать 200 символов.';
            document.getElementById('title').parentNode.appendChild(error);
            document.getElementById('title').classList.add('border-red-500');
        }
        // Проверка содержания
        if (!content) {
            e.preventDefault();
            isValid = false;
            const error = document.createElement('div');
            error.className = 'text-red-500 text-sm mt-1 error-message';
            error.textContent = 'Содержание не может быть пустым.';
            document.getElementById('content').parentNode.appendChild(error);
            document.getElementById('content').classList.add('border-red-500');
        } else if (content.length < 10 || content.length > 5000) {
            e.preventDefault();
            isValid = false;
            const error = document.createElement('div');
            error.className = 'text-red-500 text-sm mt-1 error-message';
            error.textContent = 'Описание должно содержать от 10 до 5000 символов.';
            document.getElementById('content').parentNode.appendChild(error);
            document.getElementById('content').classList.add('border-red-500');
        }
        // Если всё валидно — готовим теги и отправляем
        if (isValid) {
            const tagsHiddenContainer = document.getElementById('tags-hidden-inputs');
            tagsHiddenContainer.innerHTML = '';
            selectedTags.forEach(tag => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'tags';
                input.value = tag;
                tagsHiddenContainer.appendChild(input);
            });
            // Форма будет отправлена автоматически
        } else {
            e.preventDefault(); // Блокируем отправку, если есть ошибки
        }
    });
    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!tagInput.contains(e.target) && !tagSuggestions.contains(e.target)) {
            hideSuggestions();
        }
    });
});