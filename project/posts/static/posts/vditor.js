(function () {
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("textarea[data-vditor]").forEach(function (textarea) {
      var editor = document.createElement("div");
      editor.id = textarea.id + "-vditor";
      textarea.insertAdjacentElement("afterend", editor);
      textarea.style.display = "none";

      new Vditor(editor.id, {
        cache: { enable: false },
        input: function (value) { textarea.value = value; },
        mode: "sv",
        value: textarea.value
      });
    });
  });
})();
