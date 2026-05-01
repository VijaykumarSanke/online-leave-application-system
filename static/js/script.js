/*
  Shared UI interactions for LeavePortal.
*/

document.addEventListener('DOMContentLoaded', function () {
  const html = document.documentElement;
  const themeToggles = document.querySelectorAll('#themeToggle');

  themeToggles.forEach((themeToggle) => {
    themeToggle.addEventListener('click', () => {
      const currentTheme = html.getAttribute('data-theme');
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';

      html.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      themeToggle.setAttribute('aria-label', `Switch to ${currentTheme} theme`);
    });
  });

  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      const isOpen = sidebar.classList.toggle('open');
      sidebarToggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', (event) => {
      const clickedInsideSidebar = sidebar.contains(event.target);
      const clickedToggle = sidebarToggle.contains(event.target);

      if (!clickedInsideSidebar && !clickedToggle && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        sidebarToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const togglePw = document.getElementById('togglePw');

  if (togglePw) {
    togglePw.addEventListener('click', function () {
      const pwField = document.getElementById('password');
      const icon = this.querySelector('i');
      const isHidden = pwField.type === 'password';

      pwField.type = isHidden ? 'text' : 'password';
      icon.classList.toggle('bi-eye-fill', !isHidden);
      icon.classList.toggle('bi-eye-slash-fill', isHidden);
      this.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
    });
  }

  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4500);
  });

  const fromDate = document.getElementById('fromDate');
  const toDate = document.getElementById('toDate');

  if (fromDate && toDate) {
    const today = new Date().toISOString().split('T')[0];
    fromDate.min = today;

    fromDate.addEventListener('change', function () {
      toDate.min = this.value;
      if (toDate.value && toDate.value < this.value) {
        toDate.value = this.value;
      }
    });
  }

  const forms = document.querySelectorAll('form[novalidate]');
  forms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach((el) => {
    new bootstrap.Tooltip(el);
  });
});
