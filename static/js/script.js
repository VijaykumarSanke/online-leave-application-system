/* ============================================================
   Online Leave Application System — Custom JS
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar Toggle (Mobile) ──────────────────────────────
  const sidebar        = document.getElementById('sidebar');
  const sidebarToggle  = document.getElementById('sidebarToggle');

  // Create overlay element for mobile
  const overlay = document.createElement('div');
  overlay.classList.add('sidebar-overlay');
  document.body.appendChild(overlay);

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('show');
    });
  }

  overlay.addEventListener('click', function () {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
  });

  // ── Password Toggle (Login Page) ────────────────────────
  const togglePwBtn  = document.getElementById('togglePw');
  const toggleIcon   = document.getElementById('toggleIcon');
  const passwordInput = document.getElementById('password');

  if (togglePwBtn && passwordInput) {
    togglePwBtn.addEventListener('click', function () {
      const isPassword = passwordInput.type === 'password';
      passwordInput.type = isPassword ? 'text' : 'password';
      toggleIcon.classList.toggle('bi-eye-fill', !isPassword);
      toggleIcon.classList.toggle('bi-eye-slash-fill', isPassword);
    });
  }

  // ── Auto-dismiss flash alerts after 4 seconds ───────────
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4000);
  });

  // ── Date Validation: to_date >= from_date ───────────────
  const fromDate = document.getElementById('fromDate');
  const toDate   = document.getElementById('toDate');

  if (fromDate && toDate) {
    // Set today as the minimum for from_date
    const today = new Date().toISOString().split('T')[0];
    fromDate.min = today;

    fromDate.addEventListener('change', function () {
      toDate.min = this.value;
      // Reset to_date if it's now before from_date
      if (toDate.value && toDate.value < this.value) {
        toDate.value = this.value;
      }
    });
  }

  // ── Client-side Form Validation ─────────────────────────
  const forms = document.querySelectorAll('form[novalidate]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    });
  });

  // ── Tooltips (Bootstrap) ────────────────────────────────
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });

});
