$(document).ready(function () {
  document.querySelectorAll(".data-row").forEach((rowElement) => {
    let sqlDetailUrl = rowElement.dataset.sqlDetailUrl;
    rowElement.addEventListener("mousedown", (e) => {
      switch (e.button) {
        case 0:
          window.location = sqlDetailUrl;
          break;
        case 1:
          window.open(sqlDetailUrl);
          break;
        default:
          break;
      }
    });
  });
});
