/* ================================================================
   AI Study Hub — Core JavaScript
   ================================================================
   Responsibilities:
     1. Theme (light / dark) — persist in localStorage
     2. Sidebar — mobile open/close with overlay + keyboard
     3. Alert auto-dismiss
     4. Confirm dialogs for destructive actions
     5. Form submit-once guard (prevent double-submit)
   ================================================================ */

(function () {
    'use strict';

    /* ── 1. Theme Management ────────────────────────────────── */
    const html         = document.documentElement;
    const THEME_KEY    = 'ai-study-hub-theme';
    const ICON_MOON    = `<svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>`;
    const ICON_SUN     = `<svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/></svg>`;

    function getPreferredTheme() {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored === 'dark' || stored === 'light') return stored;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);

        const btn = document.getElementById('theme-toggle-btn');
        if (!btn) return;

        // Swap icon and label
        btn.innerHTML = theme === 'dark' ? ICON_SUN : ICON_MOON;
        btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        btn.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    }

    // Apply immediately (before DOMContentLoaded) to avoid flash
    applyTheme(getPreferredTheme());

    document.addEventListener('DOMContentLoaded', function () {

        /* ── Theme toggle button ──────────────────────────── */
        const themeBtn = document.getElementById('theme-toggle-btn');
        if (themeBtn) {
            // Re-apply to ensure icon is rendered after DOM is ready
            applyTheme(getPreferredTheme());

            themeBtn.addEventListener('click', function () {
                const current = html.getAttribute('data-theme');
                applyTheme(current === 'dark' ? 'light' : 'dark');
            });
        }

        /* ── 2. Sidebar + Overlay ─────────────────────────── */
        const sidebar        = document.querySelector('.sidebar');
        const toggleBtn      = document.getElementById('sidebar-toggle-btn');
        let   overlay        = document.getElementById('sidebar-overlay');

        // Create overlay if it doesn't exist in the DOM
        if (!overlay && sidebar) {
            overlay = document.createElement('div');
            overlay.id        = 'sidebar-overlay';
            overlay.className = 'sidebar-overlay';
            overlay.setAttribute('aria-hidden', 'true');
            document.body.appendChild(overlay);
        }

        function openSidebar() {
            if (!sidebar) return;
            sidebar.classList.add('open');
            if (overlay) overlay.classList.add('active');
            document.body.style.overflow = 'hidden';   // prevent bg scroll
            if (toggleBtn) {
                toggleBtn.setAttribute('aria-expanded', 'true');
                toggleBtn.setAttribute('aria-label', 'Close navigation');
            }
            // Move focus into sidebar for keyboard users
            const firstLink = sidebar.querySelector('a.nav-item');
            if (firstLink) firstLink.focus();
        }

        function closeSidebar() {
            if (!sidebar) return;
            sidebar.classList.remove('open');
            if (overlay) overlay.classList.remove('active');
            document.body.style.overflow = '';
            if (toggleBtn) {
                toggleBtn.setAttribute('aria-expanded', 'false');
                toggleBtn.setAttribute('aria-label', 'Open navigation');
            }
        }

        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', 'false');
            toggleBtn.setAttribute('aria-controls', 'main-sidebar');
            toggleBtn.addEventListener('click', function () {
                sidebar && sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
            });
        }

        if (overlay) {
            overlay.addEventListener('click', closeSidebar);
        }

        // Close sidebar on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
                closeSidebar();
                if (toggleBtn) toggleBtn.focus();
            }
        });

        // Close sidebar when a nav link is clicked (mobile navigation)
        if (sidebar) {
            sidebar.querySelectorAll('a.nav-item').forEach(function (link) {
                link.addEventListener('click', function () {
                    if (window.innerWidth <= 768) closeSidebar();
                });
            });
        }

        // Re-open sidebar state after resize back to desktop
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768) {
                closeSidebar();          // clean up mobile state
                document.body.style.overflow = '';
            }
        });

        /* ── 3. Alert Auto-dismiss (5 s) ──────────────────── */
        document.querySelectorAll('.alert').forEach(function (alert) {
            // Add close button to each alert
            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '&times;';
            closeBtn.setAttribute('aria-label', 'Dismiss alert');
            closeBtn.style.cssText = 'background:none;border:none;font-size:1.15rem;line-height:1;cursor:pointer;color:inherit;opacity:.7;padding:0 0 0 .5rem;flex-shrink:0;';
            closeBtn.addEventListener('click', function () { dismissAlert(alert); });
            alert.appendChild(closeBtn);

            // Auto-dismiss after 5 s
            const timer = setTimeout(function () { dismissAlert(alert); }, 5000);
            alert.dataset.timerId = timer;
        });

        function dismissAlert(alert) {
            clearTimeout(parseInt(alert.dataset.timerId, 10));
            alert.style.transition = 'opacity .4s ease, max-height .4s ease';
            alert.style.opacity = '0';
            alert.style.maxHeight = '0';
            alert.style.overflow  = 'hidden';
            alert.style.marginBottom = '0';
            alert.style.paddingTop   = '0';
            alert.style.paddingBottom = '0';
            setTimeout(function () { alert.remove(); }, 420);
        }

        /* ── 4. Confirm destructive actions ───────────────── */
        // Any <a> or <button> with data-confirm="..." shows a confirm dialog
        document.addEventListener('click', function (e) {
            const el = e.target.closest('[data-confirm]');
            if (!el) return;
            const msg = el.dataset.confirm || 'Are you sure? This action cannot be undone.';
            if (!window.confirm(msg)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });

        /* ── 5. Form submit-once guard ────────────────────── */
        // Prevents accidental double-form-submit on slow connections
        // Apply to forms with data-submit-once attribute
        document.querySelectorAll('form[data-submit-once]').forEach(function (form) {
            form.addEventListener('submit', function () {
                const submitBtn = form.querySelector('[type="submit"]');
                if (!submitBtn) return;
                submitBtn.disabled = true;
                const orig = submitBtn.textContent;
                submitBtn.textContent = 'Processing…';
                // Re-enable after 12 s as a safety net
                setTimeout(function () {
                    submitBtn.disabled = false;
                    submitBtn.textContent = orig;
                }, 12000);
            });
        });

        /* ── 6. Active nav-item highlight ────────────────── */
        // Fine-tune: also mark parent section active for sub-pages
        // (base.html uses app_name check; this JS handles edge cases)
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-item').forEach(function (link) {
            const href = link.getAttribute('href');
            if (!href || href === '/') return;
            if (currentPath.startsWith(href) && !link.classList.contains('active')) {
                // Only add if no other link is already marked active for this path
                // and the href is a proper prefix (not just '/')
                if (href.length > 1) {
                    link.classList.add('active');
                }
            }
        });

    }); // end DOMContentLoaded

})();
