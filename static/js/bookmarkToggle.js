let bookmarkurl = '/blog/toggle-bookmark/';
let csrf = window.CSRF_TOKEN || (document.querySelector('meta[name="csrf-token"]') && document.querySelector('meta[name="csrf-token"]').getAttribute('content'));

const bookmarkDebounceTimers = {};
const bookmarkToggleCounts = {};
const lastBookmarkRequestTimes = {};
const bookmarkStateBeforeDebounce = {};

function toggleBookmark(postId) {
    // Redirect unauthenticated users to login
    if (!window.USER_IS_AUTHENTICATED) {
        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search) + '&msg=' + encodeURIComponent('Please login to save posts.');
        return;
    }

    const btn = document.getElementById(`save-btn-${postId}`);
    if (!btn) return;

    const originalContent = btn.innerHTML;
    const isSaved = btn.innerHTML.includes('bi-bookmark-check-fill');

    // 1. OPTIMISTIC UI UPDATE
    if (isSaved) {
        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' class='w-6 h-6 cursor-pointer' fill='var(--theme-darkest)' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
    } else {
        btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' fill='var(--theme-darkest)' class='w-6 h-6 bi bi-bookmark-check-fill cursor-pointer' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
    }

    // 2. DEBOUNCE THE SERVER SYNC
    if (!bookmarkToggleCounts[postId]) {
        bookmarkStateBeforeDebounce[postId] = isSaved;
    }
    bookmarkToggleCounts[postId] = (bookmarkToggleCounts[postId] || 0) + 1;
    
    clearTimeout(bookmarkDebounceTimers[postId]);
    bookmarkDebounceTimers[postId] = setTimeout(() => {
        // Only send ONE request if the net number of clicks was odd
        if (bookmarkToggleCounts[postId] % 2 !== 0) {
            const requestTime = Date.now();
            lastBookmarkRequestTimes[postId] = requestTime;

            fetch(bookmarkurl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf
                },
                body: JSON.stringify({ 
                    post_id: postId,
                    timestamp: requestTime
                })
            })
            .then(res => res.json())
            .then(data => {
                // If a newer request was sent, ignore this response
                if (data.timestamp && data.timestamp < lastBookmarkRequestTimes[postId]) return;
                
                // Keep server truth
                if (data.status === "unsave") {
                    btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' class='w-6 h-6 cursor-pointer' fill='var(--theme-darkest)' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
                } else {
                    btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' fill='var(--theme-darkest)' class='w-6 h-6 bi bi-bookmark-check-fill cursor-pointer' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
                }
            })
            .catch(err => {
                console.error("Error toggling bookmark:", err);
                if (window.showToast) showToast('Failed to update bookmark. Please try again.', 'error');
                // Revert to pre-debounce state
                if (bookmarkStateBeforeDebounce[postId]) {
                    btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' fill='var(--theme-darkest)' class='w-6 h-6 bi bi-bookmark-check-fill cursor-pointer' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
                } else {
                    btn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' class='w-6 h-6 cursor-pointer' fill='var(--theme-darkest)' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
                }
            });
        }
        bookmarkToggleCounts[postId] = 0;
    }, 400);
}

document.body.addEventListener("click", function (e) {
    const btn = e.target.closest(".saveSVG");
    if (btn) {
        const sno = btn.dataset.sno;
        toggleBookmark(sno);
    }
});


