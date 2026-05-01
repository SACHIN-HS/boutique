/*!
 * Auto Bootstrap validation tooltips for all forms.
 *
 * - Adds `needs-validation` + `novalidate` to all forms (unless opted out)
 * - Injects `.valid-tooltip` and `.invalid-tooltip` for controls when missing
 * - Uses native constraint validation messages (el.validationMessage)
 *
 * Opt-out per form: add `data-no-auto-validate="true"`
 */
(function () {
  "use strict";

  function closestValidationHost(el) {
    // Prefer a Bootstrap grid column/field wrapper if present.
    return (
      el.closest(".position-relative") ||
      el.closest(".mb-3") ||
      el.closest(".col") ||
      el.closest('[class*="col-"]') ||
      el.parentElement
    );
  }

  function ensureTooltip(el, klass, defaultText) {
    var host = closestValidationHost(el);
    if (!host) return null;

    // Tooltips require positioned ancestor.
    if (!host.classList.contains("position-relative")) {
      host.classList.add("position-relative");
    }

    // For input groups, Bootstrap expects `has-validation`.
    var inputGroup = el.closest(".input-group");
    if (inputGroup && !inputGroup.classList.contains("has-validation")) {
      inputGroup.classList.add("has-validation");
    }

    var existing = host.querySelector("." + klass);
    if (existing) return existing;

    var div = document.createElement("div");
    div.className = klass;
    div.textContent = defaultText || "";
    host.appendChild(div);
    return div;
  }

  function isFormControl(el) {
    if (!el || !el.tagName) return false;
    var tag = el.tagName.toLowerCase();
    if (tag === "input") {
      var type = (el.getAttribute("type") || "text").toLowerCase();
      if (type === "hidden" || type === "submit" || type === "button" || type === "reset" || type === "file") {
        return false;
      }
    }
    return tag === "input" || tag === "select" || tag === "textarea";
  }

  function defaultInvalidText(el) {
    var label = "";
    if (el.id) {
      var l = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
      if (l) label = (l.textContent || "").trim();
    }
    if (!label) label = (el.getAttribute("name") || "this field").replace(/_/g, " ");
    return "Please provide a valid " + label + ".";
  }

  window.addEventListener("load", function () {
    var forms = Array.prototype.slice.call(document.querySelectorAll("form"));

    forms.forEach(function (form) {
      if (form.getAttribute("data-no-auto-validate") === "true") return;

      form.classList.add("needs-validation");
      form.setAttribute("novalidate", "");

      var controls = Array.prototype.slice
        .call(form.querySelectorAll("input, select, textarea"))
        .filter(isFormControl);

      controls.forEach(function (el) {
        // Only add tooltips for controls that participate in validation.
        // If it has required/pattern/minlength/maxlength/type=email/url/number/etc, it will validate.
        if (el.willValidate === false) return;

        ensureTooltip(el, "valid-tooltip", "Looks good!");
        ensureTooltip(el, "invalid-tooltip", defaultInvalidText(el));

        el.addEventListener("invalid", function (e) {
          // Prevent default browser bubble tooltip
          e.preventDefault();
          var inv = ensureTooltip(el, "invalid-tooltip", defaultInvalidText(el));
          if (inv) inv.textContent = el.validationMessage || defaultInvalidText(el);
          form.classList.add("was-validated");
        });

        function refresh() {
          var inv = ensureTooltip(el, "invalid-tooltip", defaultInvalidText(el));
          if (inv && !el.checkValidity()) {
            inv.textContent = el.validationMessage || defaultInvalidText(el);
          }
        }

        el.addEventListener("input", refresh);
        el.addEventListener("change", refresh);
      });

      // Keep default behaviour: prevent submit if invalid, add was-validated.
      form.addEventListener(
        "submit",
        function (event) {
          if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
          }
          form.classList.add("was-validated");
        },
        false
      );
    });
  });
})();

