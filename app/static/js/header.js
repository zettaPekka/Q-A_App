    const searchToggle = document.getElementById('search-toggle');
    const searchPanel = document.getElementById('search-panel');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    let debounceTimeout = null;

    // Переключение видимости поля поиска
    searchToggle.addEventListener('click', (e) => {
        e.preventDefault();
        const isHidden = searchPanel.classList.contains('hidden');
        searchPanel.classList.toggle('hidden', !isHidden);

        if (isHidden) {
            searchInput.focus(); // Фокус при открытии
        } else {
            // Опционально: сброс при закрытии
            searchResults.innerHTML = '';
            searchResults.classList.add('hidden');
            searchInput.value = '';
        }
    });

    // Закрытие при клике вне
    document.addEventListener('click', (e) => {
        if (!searchToggle.contains(e.target) &&
            !searchPanel.contains(e.target)) {
            searchPanel.classList.add('hidden');
            searchResults.classList.add('hidden');
        }
    });

    // Логика поиска
    searchInput.addEventListener('input', function () {
        const query = this.value.trim();
        clearTimeout(debounceTimeout);

        if (query === '') {
            searchResults.classList.add('hidden');
            return;
        }

        debounceTimeout = setTimeout(async () => {
            try {
                const response = await fetch('/search/question/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: query })
                });

                if (!response.ok) throw new Error('Ошибка сети');

                const questions = await response.json();
                searchResults.innerHTML = '';
                searchResults.classList.remove('hidden');

                if (Array.isArray(questions) && questions.length === 0) {
                    const li = document.createElement('li');
                    li.className = 'px-4 py-2 text-gray-500 text-sm italic';
                    li.textContent = 'Пока ничего не найдено';
                    searchResults.appendChild(li);
                } else {
                    questions.forEach(question => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = `/question/${question.question_id}/`;
                        a.className = 'block px-4 py-2 hover:bg-indigo-50 hover:text-indigo-700 border-b border-gray-100 last:border-b-0';
                        a.textContent = question.title;
                        li.appendChild(a);
                        searchResults.appendChild(li);
                    });
                }
            } catch (err) {
                console.error('Ошибка поиска:', err);
                searchResults.innerHTML = '<li class="px-4 py-2 text-red-500 text-sm">Ошибка поиска</li>';
                searchResults.classList.remove('hidden');
            }
        }, 300);
    });