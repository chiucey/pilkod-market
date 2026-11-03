(() => {
  const command = document.querySelector("[data-review-command]");
  const toast = document.querySelector("[data-review-toast]");
  const buttons = document.querySelectorAll("[data-copy-command]");
  let toastTimer;

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => {
      toast.classList.remove("is-visible");
    }, 1800);
  };

  buttons.forEach((button) => {
    button.addEventListener("click", async () => {
      const value = command?.textContent?.trim();
      if (!value) {
        showToast("当前还没有下一步命令");
        return;
      }

      try {
        await navigator.clipboard.writeText(value);
        showToast(`已复制：${value}`);
      } catch {
        showToast(`请手动复制：${value}`);
      }
    });
  });
})();
