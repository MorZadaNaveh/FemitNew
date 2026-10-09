document.addEventListener('DOMContentLoaded', function () {
  var wrapper = document.querySelector('[data-femit-bundle-options]');
  if (!wrapper) return;

  var form = document.querySelector('form[data-type="add-to-cart-form"]');
  if (!form) return;

  var originalParent = wrapper.parentElement;
  var badge = originalParent.querySelector('[data-femit-discount-badge]');

  var mapScript = originalParent.querySelector('[data-femit-pants-size-map]');
  var sizeMap = {};
  if (mapScript) {
    try {
      sizeMap = JSON.parse(mapScript.textContent);
    } catch (e) {
      sizeMap = {};
    }
  }

  // Dawn's variant-picker radios/selects live in their own component outside
  // the add-to-cart form (only the hidden variant-id input is inside it), and
  // their name attribute is "<option name>-<id>", not "options[<option name>]".
  // Find them by name prefix across the whole document instead of assuming
  // either the exact name or that they're form descendants.
  function findOptionInputs(optionName) {
    if (!optionName) return [];
    var prefix = optionName + '-';
    return Array.prototype.filter.call(document.querySelectorAll('input, select'), function (el) {
      return el.name && el.name.indexOf(prefix) === 0;
    });
  }

  function currentOptionValue(optionName) {
    var inputs = findOptionInputs(optionName);
    for (var i = 0; i < inputs.length; i++) {
      var el = inputs[i];
      if (el.tagName === 'SELECT') return el.value;
      if (el.checked) return el.value;
    }
    return null;
  }

  var pantsSizeSelect = wrapper.querySelector('[data-pants-size-select]');

  function populatePantsSizes(typeLabel) {
    if (!pantsSizeSelect) return;
    var sizes = sizeMap[typeLabel] || [];
    pantsSizeSelect.innerHTML = '';
    sizes.forEach(function (size) {
      var option = document.createElement('option');
      option.value = size;
      option.textContent = size;
      pantsSizeSelect.appendChild(option);
    });
  }

  var initialPantsType = currentOptionValue('סוג מכנסיים');
  if (initialPantsType) {
    populatePantsSizes(initialPantsType);
  } else {
    var firstLabel = Object.keys(sizeMap)[0];
    if (firstLabel) populatePantsSizes(firstLabel);
  }

  // Conditional fields: shown only when the product's own real variant
  // option (radio or select, name taken from each field's data attribute)
  // is currently set to a specific value.
  var conditionalFields = wrapper.querySelectorAll('[data-conditional-field]');
  function updateConditionalFields() {
    conditionalFields.forEach(function (field) {
      var optionName = field.getAttribute('data-option-name');
      var optionValue = field.getAttribute('data-option-value');
      if (!optionName) return;
      field.hidden = currentOptionValue(optionName) !== optionValue;
    });
  }
  updateConditionalFields();

  // Dawn's variant-picker re-renders its own markup (new DOM nodes) after
  // each selection via the section rendering API, so listeners bound to a
  // specific input go stale after the first change. Delegate on `document`
  // instead, which is never replaced, and re-query live state on every event.
  document.addEventListener('change', function (event) {
    var name = event.target && event.target.name;
    if (!name) return;
    if (name.indexOf('סוג מכנסיים-') === 0) {
      populatePantsSizes(event.target.value);
    }
    updateConditionalFields();
  });

  // Move the fields into the real product form so they submit as
  // properties[...] alongside the variant id, right before the submit button.
  var submitButton = form.querySelector('.product-form__buttons') || form.querySelector('.product-form__submit');
  var fields = wrapper.querySelector('[data-femit-bundle-options-fields]');
  if (fields && submitButton) {
    submitButton.insertAdjacentElement('beforebegin', wrapper);
    wrapper.classList.add('femit-bundle-options-moved');
  }

  // Drop the discount badge onto the native product image gallery, matching
  // the same badge style used on shop/homepage product cards.
  var mediaWrapper = document.querySelector('.product__media-wrapper');
  if (badge && mediaWrapper) {
    mediaWrapper.style.position = mediaWrapper.style.position || 'relative';
    mediaWrapper.appendChild(badge);
    badge.hidden = false;
  }
});
