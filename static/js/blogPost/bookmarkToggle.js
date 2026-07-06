/**
 * Bookmark Toggle - blogPost
 * Bookmark/unbookmark button toggle with debounced server sync.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var bookmarkDebounceTimer = null;
    var bookmarkToggleCount = 0;
    var lastBookmarkRequestTime = 0;
    var bookmarkStateBeforeDebounce = null;

    function toggleBookmark(postId) {
        var btn = document.getElementById('save-btn-' + postId);
        if (!btn) return;

        var isSaved = btn.innerHTML.includes('bi-bookmark-check-fill');

        // 1. OPTIMISTIC UI UPDATE
        if (isSaved) {
            btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' class='text-color-darkest' fill='currentColor' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
        } else {
            btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' fill='currentColor' class='bi bi-bookmark-check-fill text-color-darkest' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
        }

        // ── Micro-animation: Bounce ──
        btn.classList.remove('like-bounce');
        void btn.offsetWidth; // force reflow to re-trigger
        btn.classList.add('like-bounce');
        btn.addEventListener('animationend', function onEnd() {
            btn.classList.remove('like-bounce');
            btn.removeEventListener('animationend', onEnd);
        });

        // 2. DEBOUNCE THE SERVER SYNC
        if (bookmarkToggleCount === 0) {
            bookmarkStateBeforeDebounce = isSaved;
        }
        bookmarkToggleCount++;
        
        clearTimeout(bookmarkDebounceTimer);
        bookmarkDebounceTimer = setTimeout(function() {
            // Only send ONE request if the net number of clicks was odd
            if (bookmarkToggleCount % 2 !== 0) {
                var requestTime = Date.now();
                lastBookmarkRequestTime = requestTime;

                fetch(config.toggleBookmarkUrl, {
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
                    // If a newer request was sent, ignore this response
                    if (data.timestamp && data.timestamp < lastBookmarkRequestTime) return;
                    
                    // Keep server truth
                    if (data.status === "unsave") {
                        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' class='text-color-darkest' fill='currentColor' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
                    } else {
                        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' fill='currentColor' class='bi bi-bookmark-check-fill text-color-darkest' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
                    }
                })
                .catch(function(err) {
                    console.error("Error syncing bookmark:", err);
                    showToast('Failed to update bookmark. Please try again.', 'error');
                    // Revert to pre-debounce state
                    if (bookmarkStateBeforeDebounce) {
                        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' fill='currentColor' class='bi bi-bookmark-check-fill text-color-darkest' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
                    } else {
                        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' width='18' height='18' class='text-color-darkest' fill='currentColor' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
                    }
                });
            }
            bookmarkToggleCount = 0;
        }, 400);
    }

    var saveBtn = document.getElementById('save-btn-' + config.postSno);
    if (saveBtn) {
        saveBtn.addEventListener("click", function() {
            toggleBookmark(config.postSno);
        });
    }
})();
