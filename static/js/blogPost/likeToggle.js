/**
 * Like Toggle - blogPost
 * Like/unlike button toggle with debounced server sync.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var lastLikeRequestTime = 0;
    var likeDebounceTimer = null;
    var likeToggleCount = 0;
    var likeStateBeforeDebounce = null;
    var likeCountBeforeDebounce = null;

    function toggleLike(postId) {
        if (config.isAuthenticated !== true) {
            window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search) + '&msg=' + encodeURIComponent('Please login to like posts.');
            return;
        }

        var btn = document.getElementById('like-btn-' + postId);
        if (!btn) return;

        var countSpan = document.getElementById('like-count-' + postId);
        if (!countSpan) return;

        var isLiked = btn.innerHTML.includes('bi-heart-fill');
        var originalCount = parseInt(countSpan.innerText) || 0;
        var newCount = isLiked ? Math.max(0, originalCount - 1) : originalCount + 1;

        // 1. IMMEDIATE OPTIMISTIC UPDATE
        var heartIcon = isLiked
            ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/></svg>`
            : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/></svg>`;
        
        btn.innerHTML = heartIcon + ` <span id="like-count-${postId}" class="count text-color-dark">${newCount}</span>`;

        // ── Micro-animation: Bounce + Particle burst ──
        btn.classList.remove('like-bounce');
        void btn.offsetWidth; // force reflow to re-trigger animation
        btn.classList.add('like-bounce');
        btn.addEventListener('animationend', function onEnd() {
            btn.classList.remove('like-bounce');
            btn.removeEventListener('animationend', onEnd);
        });

        // Particle burst (only on "like", not "unlike")
        if (!isLiked) {
            var btnRect = btn.getBoundingClientRect();
            var wrapper = btn.parentElement;
            if (wrapper) {
                wrapper.style.position = 'relative';
                for (var i = 0; i < 6; i++) {
                    var particle = document.createElement('span');
                    particle.className = 'like-particle';
                    var angle = (Math.PI * 2 / 6) * i + (Math.random() * 0.5 - 0.25);
                    var dist = 18 + Math.random() * 14;
                    particle.style.setProperty('--px', Math.cos(angle) * dist + 'px');
                    particle.style.setProperty('--py', Math.sin(angle) * dist + 'px');
                    particle.style.left = (btn.offsetLeft + btn.offsetWidth / 2 - 3) + 'px';
                    particle.style.top = (btn.offsetTop + btn.offsetHeight / 2 - 3) + 'px';
                    var colors = ['var(--theme-base)', 'var(--theme-light)', 'var(--theme-dark)', '#f59e0b', '#ef4444', '#10b981'];
                    particle.style.background = colors[i % colors.length];
                    wrapper.appendChild(particle);
                    particle.addEventListener('animationend', function() { this.remove(); });
                }
            }
        }

        // 2. DEBOUNCE THE SERVER SYNC
        if (likeToggleCount === 0) {
            likeStateBeforeDebounce = isLiked;
            likeCountBeforeDebounce = originalCount;
        }
        likeToggleCount++;
        
        clearTimeout(likeDebounceTimer);
        likeDebounceTimer = setTimeout(function() {
            // Only send ONE request if the net number of clicks was odd
            if (likeToggleCount % 2 !== 0) {
                var requestTime = Date.now();
                lastLikeRequestTime = requestTime;

                fetch(config.toggleLikeUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": window.CSRF_TOKEN
                    },
                    body: JSON.stringify({ 
                        post_id: postId,
                        timestamp: requestTime 
                    })
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.timestamp && data.timestamp < lastLikeRequestTime) return;
                    
                    var heart = data.status === "liked"
                        ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/></svg>`
                        : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/></svg>`;
                    btn.innerHTML = heart + ` <span id="like-count-${postId}" class="count text-color-dark">${data.likes}</span>`;
                })
                .catch(function(err) {
                    console.error("Error syncing like:", err);
                    showToast('Failed to update like. Please try again.', 'error');
                    // Revert to pre-debounce state
                    var heart = likeStateBeforeDebounce
                        ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/></svg>`
                        : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/></svg>`;
                    btn.innerHTML = heart + ` <span id="like-count-${postId}" class="count text-color-dark">${likeCountBeforeDebounce}</span>`;
                });
            }
            likeToggleCount = 0;
        }, 400);
    }

    var likeBtn = document.getElementById('like-btn-' + config.postSno);
    if (likeBtn) {
        likeBtn.addEventListener("click", function() {
            toggleLike(config.postSno);
        });
    }
})();
