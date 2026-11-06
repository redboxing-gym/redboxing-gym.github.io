/* Progressive enhancement: every article link remains in the initial HTML. */
document.querySelectorAll('[data-article-list]').forEach(list => {
    const filters = list.querySelector('[data-category-filter]');
    const buttons = [...filters.querySelectorAll('button[data-category]')];
    const cards = [...list.querySelectorAll('[data-article-card]')];
    const status = list.querySelector('[data-category-status]');
    const empty = list.querySelector('[data-category-empty]');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            let count = 0;
            cards.forEach(card => {
                card.hidden = category !== 'all' && card.dataset.category !== category;
                if (!card.hidden) count += 1;
            });
            buttons.forEach(option => {
                option.setAttribute('aria-pressed', String(option === button));
            });
            status.textContent = `${button.textContent.trim()} · ${count}개 글`;
            empty.hidden = count !== 0;
        });
    });
    filters.hidden = false;
});
