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

  var pantsTypeInputs = form.querySelectorAll('input[name="options[סוג מכנסיים]"]');
  var checkedInput = form.querySelector('input[name="options[סוג מכנסיים]"]:checked');
  if (checkedInput) {
    populatePantsSizes(checkedInput.value);
  } else {
    var firstLabel = Object.keys(sizeMap)[0];
    if (firstLabel) populatePantsSizes(firstLabel);
  }

  pantsTypeInputs.forEach(function (input) {
    input.addEventListener('change', function () {
      populatePantsSizes(input.value);
    });
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
