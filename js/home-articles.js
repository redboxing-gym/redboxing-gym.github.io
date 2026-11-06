/* Category rotation is independent of the complete article-list filter. */
document.querySelectorAll('[data-home-articles]').forEach(root => {
    const panels = [...root.querySelectorAll('[data-home-panel]')];
    if (!panels.length) return;
    const controls = root.querySelector('[data-home-controls]');
    const tabs = [...controls.querySelectorAll('[role="tab"]')];
    const stage = root.querySelector('[data-home-stage]');
    const previous = root.querySelector('[data-home-prev]');
    const next = root.querySelector('[data-home-next]');
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
    let active = 0;
    let timer;
    let ready = false;
    let pageActive = document.hasFocus();
    let hovering = false;
    let interacting = false;
    let gesture = null;
    let suppressSwipeClick = false;

    const paused = () => !ready || document.hidden || !pageActive || reducedMotion.matches
        || hovering || interacting || root.contains(document.activeElement);

    function restart() {
        clearTimeout(timer);
        if (panels.length > 1 && !paused()) {
            timer = setTimeout(() => {
                if (!paused()) select(active + 1);
            }, 10000);
        }
    }

    function select(index) {
        const target = (index + panels.length) % panels.length;
        // Automatic changes are paused during focus. A deliberate swipe can
        // replace a focused card, so give focus a visible, stable destination.
        if (target !== active && panels[active].contains(document.activeElement)) {
            tabs[target].focus({preventScroll: true});
        }
        active = target;
        panels.forEach((panel, i) => { panel.hidden = i !== active; });
        tabs.forEach((tab, i) => {
            tab.setAttribute('aria-selected', String(i === active));
            tab.tabIndex = i === active ? 0 : -1;
        });
        restart();
    }

    function measure() {
        // Measure bounded panels in one grid cell, without showing inactive
        // links. Reserve the tallest panel so the map/CTA below cannot jump.
        root.classList.add('home-articles-measuring');
        stage.style.minHeight = '';
        const height = Math.max(...panels.map(panel => panel.getBoundingClientRect().height));
        stage.style.minHeight = `${Math.ceil(height)}px`;
        root.classList.remove('home-articles-measuring');
    }

    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => select(index));
        tab.addEventListener('keydown', event => {
            let target;
            if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
            else if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
            else if (event.key === 'Home') target = 0;
            else if (event.key === 'End') target = tabs.length - 1;
            else return;
            event.preventDefault();
            tabs[target].focus({preventScroll: true});
            select(target);
        });
    });
    previous.addEventListener('click', () => select(active - 1));
    next.addEventListener('click', () => select(active + 1));
    previous.disabled = next.disabled = panels.length < 2;

    root.addEventListener('focusin', restart);
    root.addEventListener('focusout', () => queueMicrotask(restart));
    root.addEventListener('pointerenter', event => {
        if (event.pointerType === 'mouse') { hovering = true; restart(); }
    });
    root.addEventListener('pointerleave', event => {
        if (event.pointerType === 'mouse') { hovering = false; restart(); }
    });
    root.addEventListener('pointerdown', () => {
        interacting = true;
        suppressSwipeClick = false;
        restart();
    });
    stage.addEventListener('pointerdown', event => {
        if (event.isPrimary && ['touch', 'pen'].includes(event.pointerType)) {
            gesture = {id: event.pointerId, x: event.clientX, y: event.clientY};
        }
    });
    document.addEventListener('pointerup', event => {
        interacting = false;
        if (gesture && gesture.id === event.pointerId) {
            const dx = event.clientX - gesture.x;
            const dy = event.clientY - gesture.y;
            if (Math.abs(dx) >= 60 && Math.abs(dx) > Math.abs(dy) * 1.5) {
                suppressSwipeClick = true;
                select(active + (dx < 0 ? 1 : -1));
            }
        }
        gesture = null;
        restart();
    });
    document.addEventListener('pointercancel', () => {
        interacting = false;
        gesture = null;
        restart();
    });
    stage.addEventListener('click', event => {
        if (suppressSwipeClick && event.detail > 0) {
            event.preventDefault();
            event.stopPropagation();
        }
        suppressSwipeClick = false;
    }, true);
    stage.addEventListener('dragstart', event => event.preventDefault());
    document.addEventListener('visibilitychange', restart);
    window.addEventListener('blur', () => {
        pageActive = false;
        interacting = false;
        gesture = null;
        restart();
    });
    window.addEventListener('focus', () => { pageActive = true; restart(); });
    reducedMotion.addEventListener('change', restart);

    // Existing 991.98px card breakpoint and image typography remain unchanged.
    let width = 0;
    new ResizeObserver(entries => {
        const nextWidth = entries[0].contentRect.width;
        if (width !== nextWidth) { width = nextWidth; measure(); }
    }).observe(stage);
    controls.hidden = false;
    measure();
    const images = [...stage.querySelectorAll('img')];
    Promise.allSettled([...images.map(img => img.decode()), document.fonts.ready]).then(() => {
        measure();
        ready = true;
        root.dataset.homeReady = 'true';
        restart();
    });
});
