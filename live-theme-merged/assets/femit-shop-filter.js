document.addEventListener('DOMContentLoaded', function () {
  var chips = document.querySelectorAll('[data-filter-collection]');
  var grid = document.querySelector('.femit-product-grid__grid');
  var activeTitle = document.querySelector('[data-active-title]');

  if (!chips.length || !grid) return;

  var cards = grid.querySelectorAll('[data-collections]');

  function toggleEmptyState(isEmpty) {
    var existing = grid.parentElement.querySelector('.femit-product-grid__empty--filtered');
    if (isEmpty && !existing) {
      var msg = document.createElement('p');
      msg.className = 'femit-product-grid__empty femit-product-grid__empty--filtered';
      msg.textContent = 'לא נמצאו מוצרים בקטגוריה זו.';
      grid.insertAdjacentElement('afterend', msg);
    } else if (!isEmpty && existing) {
      existing.remove();
    }
  }

  function applyFilter(handle) {
    var visibleCount = 0;
    cards.forEach(function (card) {
      var collections = (card.getAttribute('data-collections') || '').split(',');
      var show = !handle || handle === 'all' || collections.indexOf(handle) !== -1;
      card.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });
    toggleEmptyState(visibleCount === 0);
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function (e) {
      e.preventDefault();
      var handle = chip.getAttribute('data-filter-collection');
      var title = chip.getAttribute('data-filter-title') || chip.textContent.trim();

      var activeClass = chip.classList.contains('femit-shop-header__icon-pill')
        ? 'femit-shop-header__icon-pill--active'
        : 'femit-shop-header__pill--active';

      chips.forEach(function (c) {
        c.classList.remove('femit-shop-header__pill--active');
        c.classList.remove('femit-shop-header__icon-pill--active');
      });
      chip.classList.add(activeClass);

      applyFilter(handle);

      if (activeTitle) activeTitle.textContent = title;
    });
  });
});
