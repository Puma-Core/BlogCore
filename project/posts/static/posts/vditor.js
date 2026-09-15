(function () {
  function getCookie(name) {
    var prefix = name + "=";
    return document.cookie.split(";").map(function (cookie) {
      return cookie.trim();
    }).filter(function (cookie) {
      return cookie.indexOf(prefix) === 0;
    }).map(function (cookie) {
      return decodeURIComponent(cookie.slice(prefix.length));
    })[0];
  }

  function getCsrfToken(textarea) {
    var form = textarea.closest("form");
    var input = form && form.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : getCookie("csrftoken");
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("textarea[data-vditor]").forEach(function (textarea) {
      var editor = document.createElement("div");
      editor.id = textarea.id + "-vditor";
      textarea.insertAdjacentElement("afterend", editor);
      textarea.style.display = "none";

      new Vditor(editor.id, {
        cache: { enable: false },
        height: 500,
        width: "100%",
        input: function (value) { textarea.value = value; },
        lang: "en_US",
        mode: "ir",
        resize: { enable: true, position: "bottom" },
        toolbar: [
          "headings",
          "bold",
          "italic",
          "list",
          "ordered-list",
          "upload"
        ],
        value: textarea.value,
        upload: {
          fieldName: "file",
          url: textarea.dataset.vditorUploadUrl,
          setHeaders: function () {
            var csrfToken = getCsrfToken(textarea);
            return csrfToken ? { "X-CSRFToken": csrfToken } : {};
          }
        }
      });
    });
  });
})();
