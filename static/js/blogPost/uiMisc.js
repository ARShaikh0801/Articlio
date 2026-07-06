/**
 * UI Miscellaneous - blogPost
 * Scroll-to-top button, auth-based like button styling, related post card overlay.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;

    // ── Scroll-to-Top Button ──
    var btn = document.getElementById("toTopBtn");

    if (btn) {
        window.addEventListener("scroll", function() {
            if (window.scrollY > 100) {
                btn.classList.remove("hidden");
            } else {
                btn.classList.add("hidden");
            }
        });

        btn.addEventListener("click", function() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // ── Auth-based Like Button Styling ──
    var likeBtn = document.getElementById("like-btn-" + config.postSno);
    if (likeBtn) {
        if (!config.isAuthenticated) {
            likeBtn.disabled = true;
            likeBtn.style.cursor = "not-allowed";
            likeBtn.classList.remove("theme-medium", "theme-medium-btn", "text-color-lightest");
            likeBtn.classList.add("opacity-50", "cursor-not-allowed");
        } else {
            likeBtn.disabled = false;
            likeBtn.style.cursor = "pointer";
            likeBtn.classList.remove("opacity-50", "cursor-not-allowed");
        }
    }

    // ── Related Post Card Click Overlay ──
    var interestedContainer = document.getElementById('interested-posts-container');
    if (interestedContainer) {
        interestedContainer.addEventListener('click', function(e) {
            var card = e.target.closest('a');
            if (card && !card.querySelector('.related-card-overlay')) {
                var overlay = document.createElement('div');
                overlay.className = 'related-card-overlay';
                overlay.innerHTML = '<svg class="w-8 h-8 animate-spin text-[var(--theme-base)]" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" /></svg>';
                card.appendChild(overlay);
            }
        });
    }
})();
