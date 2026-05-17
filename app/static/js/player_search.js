document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.player-selector').forEach(function (container) {
        const input = container.querySelector('.player-search-input');
        const results = container.querySelector('.player-search-results');
        const selected = container.querySelector('.selected-players');

        let debounceTimer;

        input.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const q = this.value.trim();
            if (q.length < 2) {
                results.innerHTML = '';
                results.style.display = 'none';
                return;
            }
            debounceTimer = setTimeout(function () {
                fetch('/api/player-search?q=' + encodeURIComponent(q))
                    .then(function (r) { return r.json(); })
                    .then(function (data) {
                        if (!data.length) {
                            results.innerHTML = '<div class="search-no-results">No players found</div>';
                            results.style.display = 'block';
                            return;
                        }
                        results.innerHTML = '';
                        data.forEach(function (p) {
                            var item = document.createElement('div');
                            item.className = 'search-result-item';
                            item.textContent = p.name;
                            if (p.is_dummy) {
                                var badge = document.createElement('span');
                                badge.className = 'search-result-badge';
                                badge.textContent = 'dummy';
                                item.appendChild(badge);
                            }
                            item.dataset.id = p.id;
                            item.dataset.name = p.name;
                            item.addEventListener('click', function () {
                                addPlayer(p.id, p.name);
                                results.innerHTML = '';
                                results.style.display = 'none';
                                input.value = '';
                                input.focus();
                            });
                            results.appendChild(item);
                        });
                        results.style.display = 'block';
                    });
            }, 300);
        });

        document.addEventListener('click', function (e) {
            if (!container.contains(e.target)) {
                results.innerHTML = '';
                results.style.display = 'none';
            }
        });

        function addPlayer(id, name) {
            var existing = selected.querySelector('.player-chip[data-id="' + id + '"]');
            if (existing) return;

            var chip = document.createElement('span');
            chip.className = 'player-chip';
            chip.dataset.id = id;
            chip.textContent = name + ' ';

            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'chip-remove';
            remove.textContent = '\u00D7';
            remove.addEventListener('click', function () {
                chip.remove();
                var hidden = container.querySelector('input[value="' + id + '"]');
                if (hidden) hidden.remove();
            });
            chip.appendChild(remove);

            var hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'players';
            hidden.value = id;

            selected.appendChild(chip);
            container.appendChild(hidden);
        }

        var preselectedEl = container.querySelector('.preselected-players');
        if (preselectedEl) {
            preselectedEl.querySelectorAll('.preselected-player').forEach(function (el) {
                addPlayer(el.dataset.id, el.dataset.name);
            });
            preselectedEl.remove();
        }
    });
});
