/**
 * Post State - blogPost
 * Fetches and renders post state: likes, bookmarks, views, interested posts, scroll restoration.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var slug = config.slug;
    var postSno = config.postSno;

    fetch('/blog/api/' + slug + '/state/')
        .then(function(res) {
            if (res.status === 429) {
                window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search) + '&msg=' + encodeURIComponent('You have reached the request limit. Please login to continue browsing.');
                throw new Error("Rate limited");
            }
            if (!res.ok) {
                throw new Error('Server error (' + res.status + ')');
            }
            return res.json();
        })
        .then(function(data) {
            // Update Views
            var viewsContainer = document.getElementById('post-views-container');
            if (viewsContainer) viewsContainer.innerHTML = '&middot; ' + data.views + ' views';

            // Update Like Button
            var likeSkeletonWrapper = document.getElementById('like-skeleton-wrapper');
            if (likeSkeletonWrapper) likeSkeletonWrapper.classList.add('hidden');

            var likeBtn = document.getElementById('like-btn-' + postSno);
            var likeInteractiveWrapper = document.getElementById('like-interactive-wrapper');
            
            if (likeBtn) {
                var heartIcon = data.liked 
                    ? `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="red" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/></svg>`
                    : `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/></svg>`;
                likeBtn.innerHTML = heartIcon + ` <span id="like-count-${postSno}" class="count text-color-dark">${data.likes}</span>`;
                
                var likeCountSpan = document.getElementById('like-count-' + postSno);
                if (likeCountSpan) {
                    likeCountSpan.setAttribute('data-count-up', '');
                    if (window.animateCountUp) window.animateCountUp(likeCountSpan);
                }
                if (likeInteractiveWrapper) likeInteractiveWrapper.style.display = 'flex';
            }

            // Update Bookmark Button
            var saveBtn = document.getElementById('save-btn-' + postSno);
            if (saveBtn) {
                if (data.bookmarked) {
                    saveBtn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' fill='currentColor' class='bi bi-bookmark-check-fill text-color-darkest' width='18' height='18' viewBox='0 0 16 16'><path fill-rule='evenodd' d='M2 15.5V2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.74.439L8 13.069l-5.26 2.87A.5.5 0 0 1 2 15.5m8.854-9.646a.5.5 0 0 0-.708-.708L7.5 7.793 6.354 6.646a.5.5 0 1 0-.708.708l1.5 1.5a.5.5 0 0 0 .708 0z'/></svg>";
                } else {
                    saveBtn.innerHTML = "<svg xmlns='http://www.w3.org/2000/svg' class='text-color-darkest' width='18' height='18' fill='currentColor' class='bi bi-bookmark' viewBox='0 0 16 16'><path d='M2 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v13.5a.5.5 0 0 1-.777.416L8 13.101l-5.223 2.815A.5.5 0 0 1 2 15.5zm2-1a1 1 0 0 0-1 1v12.566l4.723-2.482a.5.5 0 0 1 .554 0L13 14.566V2a1 1 0 0 0-1-1z'/></svg>";
                }
                saveBtn.style.display = 'inline-flex';
            }

            // Update Interested Posts
            if (data.interestedPosts && data.interestedPosts.length > 0) {
                var interestedContainer = document.getElementById('interested-posts-container');
                var interestedHeading = document.getElementById('interested-posts-heading');
                var interestedHr = document.getElementById('interested-posts-hr');
                
                if (interestedContainer && interestedHeading && interestedHr) {
                    var html = "";
                    data.interestedPosts.forEach(function(p) {
                        html += '\
                        <a href="/blog/' + encodeURIComponent(p.slug) + '" class="bg-white rounded-xl hover:shadow-lg transition relative fade-in post-card block h-full group" style="border-left: 4px solid var(--theme-base);">\
                            <div class="p-5 flex rounded-xl flex-col h-full" style="border: 1px solid #e5e7eb; border-left: none; border-radius: 0 12px 12px 0;">\
                                <div class="text-xs font-medium mb-1" style="color: var(--theme-base);">\
                                    ' + escapeHtml(p.timestamp) + ' &middot; ' + escapeHtml(p.views) + ' views &middot; ' + escapeHtml(p.likes) + ' likes <span class="reading-time-container"><span class="reading-time-separator"> &middot; </span><span style="display: inline-flex; align-items: center; gap: 3px; background: var(--theme-base); color: white; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; white-space: nowrap; vertical-align: middle;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16"><path d="M8 3.5a.5.5 0 0 0-1 0V8a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 7.71z"/><path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16m7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0"/></svg>' + p.reading_time + ' min</span></span>\
                                </div>\
                                <h3 class="text-lg font-semibold mb-1 text-color-darkest group-hover:text-[var(--theme-base)] transition">' + escapeHtml(p.title) + '</h3>\
                                <p class="text-sm mb-2" style="color: #6b7280; font-weight: 500;">Category: ' + escapeHtml(p.category) + '</p>\
                                <p class="text-sm" style="color: #4b5563;">' + escapeHtml(p.summary) + '</p>\
                            </div>\
                        </a>';
                    });
                    interestedContainer.innerHTML = html;
                    interestedContainer.classList.remove('hidden');
                    interestedHeading.classList.remove('hidden');
                    interestedHr.classList.remove('hidden');
                }
            }

            // ── Scroll Restoration ──
            var savedProgress = 0;
            if (window.USER_IS_AUTHENTICATED) {
                savedProgress = data.scroll_progress || 0;
            } else {
                try {
                    var raw = localStorage.getItem('articlio_history');
                    if (raw) {
                        var entries = JSON.parse(raw);
                        var entry = entries.find(function(e) { return e.sno == postSno; });
                        if (entry) savedProgress = entry.scroll_progress || 0;
                    }
                } catch(e) {}
            }
            if (savedProgress > 1) {
                // Delay slightly to let the page render fully
                setTimeout(function() {
                    var contentArea = document.querySelector('.ql-editor');
                    if (!contentArea) return;
                    var contentTop = contentArea.getBoundingClientRect().top + window.scrollY;
                    var contentHeight = contentArea.offsetHeight;
                    var scrollTarget = contentTop + (savedProgress / 100) * contentHeight - window.innerHeight;
                    window.scrollTo({ top: Math.max(0, scrollTarget), behavior: 'smooth' });
                }, 500);
            }
        })
        .catch(function(err) {
            if (err.message === 'Rate limited') return;
            console.error("Error fetching post state:", err);
            showToast('Failed to load post details. Please refresh.', 'error');
            // Remove stuck skeletons and show defaults
            var likeSkeletonWrapper = document.getElementById('like-skeleton-wrapper');
            if (likeSkeletonWrapper) likeSkeletonWrapper.classList.add('hidden');
            var viewsContainer = document.getElementById('post-views-container');
            if (viewsContainer) viewsContainer.innerHTML = '';
            var likeBtn = document.getElementById('like-btn-' + postSno);
            if (likeBtn) {
                likeBtn.style.display = 'inline-flex';
                likeBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/></svg> <span id="like-count-${postSno}" class="count text-color-dark">0</span>`;
            }
        });
})();
