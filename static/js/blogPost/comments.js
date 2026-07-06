/**
 * Comments - blogPost
 * Comment loading, rendering, optimistic submit, and pagination.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var commentsPage = 1;
    var commentsHasNext = false;

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    var loadMoreBtn = document.getElementById('read-more-comments');
    var sidebarLoadMoreBtn = document.getElementById('sidebar-read-more-comments');

    function updateLoadMoreVisibility() {
        var show = commentsHasNext;
        if (loadMoreBtn && loadMoreBtn.parentElement) {
            loadMoreBtn.parentElement.style.display = show ? 'block' : 'none';
        }
        var sidebarLoadMoreContainer = document.getElementById('sidebar-read-more-container');
        if (sidebarLoadMoreContainer) {
            sidebarLoadMoreContainer.style.display = show ? 'block' : 'none';
        }
    }

    // Initial setup
    updateLoadMoreVisibility();

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            commentsPage++;
            loadMoreComments();
        });
    }
    if (sidebarLoadMoreBtn) {
        sidebarLoadMoreBtn.addEventListener('click', function() {
            commentsPage++;
            loadMoreComments();
        });
    }

    // Side bar elements
    var sidebar = document.getElementById('comments-sidebar');
    var sidebarBtn = document.getElementById('sidebar-comment-btn');
    var closeSidebarBtn = document.getElementById('close-comments-sidebar');
    var sidebarOverlay = document.getElementById('comments-sidebar-overlay');
    var sidebarList = document.getElementById('sidebar-comments-list');
    var sidebarForm = document.getElementById('sidebar-comment-form');

    function syncCommentsToSidebar() {
        if (!sidebarList) return;
        var mainContainer = document.getElementById('comments-container');
        if (!mainContainer) return;
        
        // Mirror the html content
        sidebarList.innerHTML = mainContainer.innerHTML;

        // Re-bind forms in both containers
        document.querySelectorAll('form[action="/blog/postComment"]').forEach(function(form) {
            form.removeEventListener('submit', handleCommentSubmit);
            form.addEventListener('submit', handleCommentSubmit);
        });
    }

    function toggleSidebar(open) {
        if (!sidebar || !sidebarOverlay) return;
        if (open) {
            if (window.innerWidth < 640) {
                var nav = document.getElementById('main-nav');
                var navHeight = nav ? nav.offsetHeight : 98;
                sidebar.style.top = navHeight + 'px';
                sidebar.style.height = 'calc(100% - ' + navHeight + 'px)';
            } else {
                sidebar.style.top = '';
                sidebar.style.height = '';
            }
            sidebar.classList.remove('translate-x-full');
            sidebarOverlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // prevent background scroll
        } else {
            sidebar.classList.add('translate-x-full');
            sidebarOverlay.classList.add('hidden');
            document.body.style.overflow = '';
        }
    }

    if (sidebarBtn) {
        sidebarBtn.addEventListener('click', function() {
            toggleSidebar(true);
        });
    }
    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', function() {
            toggleSidebar(false);
        });
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            toggleSidebar(false);
        });
    }

    if (sidebarForm) {
        sidebarForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var input = sidebarForm.querySelector('input[name="comment"]');
            var commentText = input.value.trim();
            if (!commentText) return;

            // We can submit using the main top-level form submission flow or invoke it
            var mainForm = document.querySelector('form[action="/blog/postComment"]:not(#sidebar-comment-form)');
            if (mainForm) {
                var mainInput = mainForm.querySelector('input[name="comment"]');
                if (mainInput) {
                    mainInput.value = commentText;
                    // Trigger submit on main form
                    var event = new Event('submit', { cancelable: true });
                    mainForm.dispatchEvent(event);
                    input.value = "";
                }
            } else {
                // If main form doesn't exist (e.g. not authenticated, though both or neither would be), fallback
                handleCommentSubmit(e);
            }
        });
    }

    // Handle comment/reply submissions optimistically
    function handleCommentSubmit(e) {
        e.preventDefault(); // Stop standard submission
        
        var form = e.currentTarget;
        var commentInput = form.querySelector('input[name="comment"]');
        var commentText = commentInput.value.trim();
        if (!commentText) return;

        var parentSnoInput = form.querySelector('input[name="parentSno"]');
        var parentSno = parentSnoInput ? parentSnoInput.value : null;
        var postSnoInput = form.querySelector('input[name="postSno"]');
        var postSno = postSnoInput ? postSnoInput.value : (config ? config.postSno : '');
        var username = window.CURRENT_USER || '';

        // Generate a temporary ID for the optimistic element
        var tempId = "temp-" + Date.now();
        
        // Clear the input
        commentInput.value = "";

        // Construct optimistic HTML
        var newCommentHTML = "";
        if (parentSno) {
            // It's a reply
            newCommentHTML = '\
            <div id="' + tempId + '" class="flex gap-3 ml-8 pl-4 opacity-70 items-start reply-item" style="border-left: 1px solid var(--theme-light)">\
                <img loading="lazy" src="/static/img/user.webp" class="w-9 h-9 rounded-full" alt="' + username + '">\
                <div class="flex-1 min-w-0">\
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">\
                        <b class="text-color-darkest font-semibold text-sm sm:text-base break-all">' + username + '</b>\
                        <span class="text-xs text-color-dark">Just now</span>\
                    </div>\
                    <p class="text-color-darkest text-sm sm:text-base break-words mt-0.5">' + commentText + '</p>\
                </div>\
                <div class="flex flex-col items-center justify-start flex-shrink-0">\
                    <button class="comment-like-btn" data-comment-sno="" style="display: none;">\
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>\
                        <span class="comment-like-count">0</span>\
                    </button>\
                </div>\
            </div>';
            
            // Find the parent comment's reply container and append in main container
            var mainParentItem = document.querySelector('#comments-container .comment-item[data-comment-sno="' + parentSno + '"]');
            if (mainParentItem) {
                var replyContainer = mainParentItem.querySelector('.mt-4.space-y-4');
                if (replyContainer) {
                    replyContainer.insertAdjacentHTML('beforeend', newCommentHTML);
                }
            }
            
            // Mirror it to sidebar too
            var sidebarParentItem = document.querySelector('#sidebar-comments-list .comment-item[data-comment-sno="' + parentSno + '"]');
            if (sidebarParentItem) {
                var sReplyContainer = sidebarParentItem.querySelector('.mt-4.space-y-4');
                if (sReplyContainer) {
                    sReplyContainer.insertAdjacentHTML('beforeend', newCommentHTML);
                }
            }

            // Optionally close details tag in both
            document.querySelectorAll('.comment-item[data-comment-sno="' + parentSno + '"] details').forEach(function(d) {
                d.removeAttribute('open');
            });

        } else {
            // Top-level comment
            newCommentHTML = '\
            <div id="' + tempId + '" class="comment-item bg-white rounded-xl mb-6 card-shadow opacity-70" style="border-left: 4px solid var(--theme-base);">\
                <div class="p-4 flex flex-col h-full rounded-xl" style="border: 1px solid #e5e7eb; border-left: none; border-radius: 0 12px 12px 0;">\
                    <div class="flex items-start gap-4">\
                        <img loading="lazy" src="/static/img/user.webp" class="w-12 h-12 rounded-full" alt="' + username + '">\
                        <div class="flex-1 min-w-0">\
                            <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">\
                                <b class="font-semibold text-color-darkest text-sm sm:text-base break-all">' + username + ' (You)</b>\
                                <span class="text-xs text-color-dark">Just now</span>\
                            </div>\
                            <p class="text-color-darkest text-sm sm:text-base break-words mt-1">' + commentText + '</p>\
                            <div class="mt-3">\
                                <details>\
                                    <summary class="cursor-pointer text-sm text-color-darkest hover:underline">Reply</summary>\
                                    <form action="/blog/postComment" method="post" class="mt-3 w-full flex items-stretch gap-2 optimistic-form" data-ajax>\
                                        <input type="hidden" name="csrfmiddlewaretoken" value="' + window.CSRF_TOKEN + '">\
                                        <input type="hidden" name="postSno" value="' + postSno + '">\
                                        <input type="hidden" name="parentSno" value="">\
                                        <input type="text" name="comment" placeholder="Write a reply..." class="w-full all-border theme-medium theme-medium-btn text-color-lightest rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 input-box text-xs sm:text-sm placeholder:text-xs sm:placeholder:text-sm focus:outline-none">\
                                        <button type="submit" class="all-border theme-medium flex items-center gap-1.5 sm:gap-2 theme-medium-btn text-color-lightest px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition">\
                                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-send" viewBox="0 0 16 16">\
                                                <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/>\
                                            </svg>\
                                            <span class="hidden sm:inline">Reply</span>\
                                        </button>\
                                    </form>\
                                </details>\
                            </div>\
                            <div class="mt-4 space-y-4"></div>\
                        </div>\
                        <div class="flex flex-col items-center justify-start flex-shrink-0">\
                            <button class="comment-like-btn" data-comment-sno="" style="display: none;">\
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>\
                                <span class="comment-like-count">0</span>\
                            </button>\
                        </div>\
                    </div>\
                </div>\
            </div>';
            
            var commentsContainer = document.getElementById('comments-container');
            if (commentsContainer) {
                if (commentsContainer.innerHTML.includes('No comments yet.')) {
                    commentsContainer.innerHTML = '';
                }
                commentsContainer.insertAdjacentHTML('afterbegin', newCommentHTML);
            }
            if (sidebarList) {
                if (sidebarList.innerHTML.includes('No comments yet.')) {
                    sidebarList.innerHTML = '';
                }
                sidebarList.insertAdjacentHTML('afterbegin', newCommentHTML);
            }

            // Bind events on new forms
            document.querySelectorAll('#' + tempId + ' form').forEach(function(f) {
                f.addEventListener('submit', handleCommentSubmit);
            });
            
            var heading = document.getElementById('comments-section');
            var sideCountSpan = document.getElementById('sidebar-comment-count');
            var currentCount = 0;
            if (heading) {
                var countMatch = heading.innerText.match(/\d+/);
                if (countMatch) {
                    currentCount = parseInt(countMatch[0]);
                }
            }
            var newCount = currentCount + 1;
            if (heading) heading.innerText = 'Comments (' + newCount + ')';
            if (sideCountSpan) sideCountSpan.innerText = newCount;
            var bottomSideCountSpan = document.getElementById('bottom-sidebar-comment-count');
            if (bottomSideCountSpan) bottomSideCountSpan.innerText = newCount;
        }

        fetch("/blog/postComment", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.CSRF_TOKEN
            },
            body: JSON.stringify({
                comment: commentText,
                postSno: postSno,
                parentSno: parentSno
            })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.status === "success") {
                // Update elements in both main list and sidebar
                document.querySelectorAll('#' + tempId).forEach(function(tempEl) {
                    tempEl.classList.remove('opacity-70');
                    tempEl.setAttribute('data-comment-sno', data.comment_sno);
                    
                    var likeBtn = tempEl.querySelector('.comment-like-btn');
                    if (likeBtn) {
                        likeBtn.setAttribute('data-comment-sno', data.comment_sno);
                        likeBtn.style.display = 'flex';
                    }

                    if (!parentSno) {
                        var newParentInput = tempEl.querySelector('input[name="parentSno"]');
                        if (newParentInput) newParentInput.value = data.comment_sno;
                    }
                });
            } else {
                document.querySelectorAll('#' + tempId).forEach(function(tempEl) {
                    tempEl.remove();
                });
                commentInput.value = commentText; 
                console.error("Error posting comment:", data.message);
            }
        })
        .catch(function(err) {
            document.querySelectorAll('#' + tempId).forEach(function(tempEl) {
                tempEl.remove();
            });
            commentInput.value = commentText; 
            console.error("Error posting comment:", err);
            showToast('Failed to post comment. Please try again.', 'error');
        });
    }

    // Shared comment renderer
    function renderComment(c, isOwn) {
        var repliesHtml = "";
        c.replies.forEach(function(r, index) {
            var replyLikedClass = r.liked ? 'liked' : '';
            var replyHeartFill = r.liked ? 'currentColor' : 'none';
            var replyLikeBtn = '\
            <button class="comment-like-btn ' + replyLikedClass + '" data-comment-sno="' + r.sno + '">\
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="' + replyHeartFill + '" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>\
                <span class="comment-like-count">' + r.likes_count + '</span>\
            </button>';

            var isHidden = index >= 3 ? 'style="display: none;" data-hidden-reply="true"' : '';
            var ownLabel = r.is_own ? ' (You)' : '';

            repliesHtml += '\
            <div class="flex gap-3 ml-8 pl-4 items-start reply-item" ' + isHidden + ' style="border-left: 1px solid var(--theme-light)">\
                <img loading="lazy" src="/static/img/user.webp" class="w-9 h-9 rounded-full" alt="' + escapeHtml(r.username) + '">\
                <div class="flex-1 min-w-0">\
                    <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">\
                        <b class="text-color-darkest font-semibold text-sm sm:text-base break-all">' + escapeHtml(r.username) + ownLabel + '</b>\
                        <span class="text-xs text-color-dark">' + escapeHtml(r.timestamp) + '</span>\
                    </div>\
                    <p class="text-color-darkest text-sm sm:text-base break-words mt-0.5">' + escapeHtml(r.comment) + '</p>\
                </div>\
                <div class="flex flex-col items-center justify-start flex-shrink-0">\
                    ' + replyLikeBtn + '\
                </div>\
            </div>';
        });

        if (c.replies.length > 3) {
            repliesHtml += '\
            <div class="ml-8 pl-4 mt-2 read-more-replies-wrapper">\
                <button class="read-more-replies-btn text-xs font-semibold hover:underline cursor-pointer focus:outline-none" style="color: var(--theme-base); background: transparent; border: none; padding: 0;">\
                    Read more replies (' + (c.replies.length - 3) + ' remaining)\
                </button>\
            </div>';
        }

        var replyForm = window.USER_IS_AUTHENTICATED === true ? '\
            <details>\
                <summary class="cursor-pointer text-sm text-color-darkest hover:underline">Reply</summary>\
                <form action="/blog/postComment" method="post" class="mt-3 w-full flex items-stretch gap-2" data-ajax>\
                    <input type="hidden" name="csrfmiddlewaretoken" value="' + window.CSRF_TOKEN + '">\
                    <input type="hidden" name="postSno" value="' + config.postSno + '">\
                    <input type="hidden" name="parentSno" value="' + c.sno + '">\
                    <input type="text" name="comment" placeholder="Write a reply..." class="w-full all-border theme-medium theme-medium-btn text-color-lightest rounded-lg px-3 sm:px-4 py-1.5 sm:py-2 input-box text-xs sm:text-sm placeholder:text-xs sm:placeholder:text-sm focus:outline-none">\
                    <button type="submit" class="all-border theme-medium flex items-center gap-1.5 sm:gap-2 theme-medium-btn text-color-lightest px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm transition">\
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" class="bi bi-send" viewBox="0 0 16 16"><path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576zm6.787-8.201L1.591 6.602l4.339 2.76z"/></svg>\
                        <span class="hidden sm:inline">Reply</span>\
                    </button>\
                </form>\
            </details>' : '';

        var commentLikedClass = c.liked ? 'liked' : '';
        var commentHeartFill = c.liked ? 'currentColor' : 'none';
        var commentLikeBtn = '\
        <button class="comment-like-btn ' + commentLikedClass + '" data-comment-sno="' + c.sno + '">\
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="' + commentHeartFill + '" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>\
            <span class="comment-like-count">' + c.likes_count + '</span>\
        </button>';

        return '\
        <div class="comment-item bg-white rounded-xl mb-6 card-shadow fade-in comment-enter-animate" data-comment-sno="' + c.sno + '" style="border-left: 4px solid var(--theme-base);">\
            <div class="p-4 flex flex-col h-full rounded-xl" style="border: 1px solid #e5e7eb; border-left: none; border-radius: 0 12px 12px 0;">\
                <div class="flex items-start gap-4">\
                    <img loading="lazy" src="/static/img/user.webp" class="w-12 h-12 rounded-full" alt="' + escapeHtml(c.username) + '">\
                    <div class="flex-1 min-w-0">\
                        <div class="flex flex-wrap items-center gap-x-2 gap-y-0.5">\
                            <b class="font-semibold text-color-darkest text-sm sm:text-base break-all">' + escapeHtml(c.username) + ' ' + (isOwn ? '(You)' : '') + '</b>\
                            <span class="text-xs text-color-dark">' + escapeHtml(c.timestamp) + '</span>\
                        </div>\
                        <p class="text-color-darkest text-sm sm:text-base break-words mt-1">' + escapeHtml(c.comment) + '</p>\
                        <div class="mt-3">\
                            ' + replyForm + '\
                        </div>\
                        <div class="mt-4 space-y-4">\
                            ' + repliesHtml + '\
                        </div>\
                    </div>\
                    <div class="flex flex-col items-center justify-start flex-shrink-0">\
                        ' + commentLikeBtn + '\
                    </div>\
                </div>\
            </div>\
        </div>';
    }

    // Load more comments (appends to existing)
    function loadMoreComments() {
        var commentsContainer = document.getElementById('comments-container');
        if (!commentsContainer) return;

        // Add 5 skeleton loaders to main container
        var mainSkeletonHtml = Array(5).fill('\
            <div class="comment-item bg-white rounded-xl mb-6 card-shadow skeleton-comment fade-in" style="border-left: 4px solid var(--theme-base); height: 120px;">\
                <div class="p-4 flex h-full rounded-xl skeleton" style="border: 1px solid #e5e7eb; border-left: none; border-radius: 0 12px 12px 0;"></div>\
            </div>').join('');
        commentsContainer.insertAdjacentHTML('beforeend', mainSkeletonHtml);

        // Add 5 custom skeleton cards to sidebar container
        if (sidebarList) {
            var sidebarSkeletonHtml = Array(5).fill('\
                <div class="sidebar-skeleton-card skeleton-comment fade-in"></div>').join('');
            sidebarList.insertAdjacentHTML('beforeend', sidebarSkeletonHtml);
        }

        fetch('/blog/api/' + config.slug + '/comments/?page=' + commentsPage)
            .then(function(res) {
                if (!res.ok) throw new Error('Server error (' + res.status + ')');
                return res.json();
            })
            .then(function(data) {
                var container = document.getElementById('comments-container');
                if (!container) return;

                // Remove skeleton loaders
                container.querySelectorAll('.skeleton-comment').forEach(function(s) { s.remove(); });
                if (sidebarList) {
                    sidebarList.querySelectorAll('.skeleton-comment').forEach(function(s) { s.remove(); });
                }

                var html = "";
                data.other_comments.forEach(function(c) { html += renderComment(c, false); });
                container.insertAdjacentHTML('beforeend', html);

                commentsHasNext = data.has_next;
                updateLoadMoreVisibility();

                syncCommentsToSidebar();
            })
            .catch(function(err) {
                console.error("Error loading more comments:", err);
                showToast('Failed to load more comments.', 'error');
                commentsPage--; // Revert page increment on error
                
                var container = document.getElementById('comments-container');
                if (container) {
                    container.querySelectorAll('.skeleton-comment').forEach(function(s) { s.remove(); });
                }
                if (sidebarList) {
                    sidebarList.querySelectorAll('.skeleton-comment').forEach(function(s) { s.remove(); });
                }
            });
    }

    // Expose loadMoreComments globally
    window.loadMoreComments = loadMoreComments;

    // Initial comments fetch (page 1)
    fetch('/blog/api/' + config.slug + '/comments/?page=1')
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
            var commentsContainer = document.getElementById('comments-container');
            if (!commentsContainer) return;
            
            var heading = document.getElementById('comments-section');
            if (heading) heading.innerText = 'Comments (' + data.total + ')';
            var sideCountSpan = document.getElementById('sidebar-comment-count');
            if (sideCountSpan) {
                sideCountSpan.innerText = data.total;
                sideCountSpan.setAttribute('data-count-up', '');
                if (window.animateCountUp) window.animateCountUp(sideCountSpan);
            }
            var bottomSideCountSpan = document.getElementById('bottom-sidebar-comment-count');
            if (bottomSideCountSpan) {
                bottomSideCountSpan.innerText = data.total;
                bottomSideCountSpan.setAttribute('data-count-up', '');
                if (window.animateCountUp) window.animateCountUp(bottomSideCountSpan);
            }

            // Hide comment skeletons and show actual comment buttons
            var commentSkeleton = document.getElementById('comment-btn-skeleton');
            if (commentSkeleton) commentSkeleton.style.display = 'none';
            var commentBtn = document.getElementById('sidebar-comment-btn');
            if (commentBtn) commentBtn.style.display = 'flex';

            var bottomCommentSkeleton = document.getElementById('bottom-comment-btn-skeleton');
            if (bottomCommentSkeleton) bottomCommentSkeleton.style.display = 'none';
            var bottomCommentBtn = document.getElementById('bottom-sidebar-comment-btn');
            if (bottomCommentBtn) bottomCommentBtn.style.display = 'flex';
            
            var html = "";
            data.own_comments.forEach(function(c) { html += renderComment(c, true); });
            data.other_comments.forEach(function(c) { html += renderComment(c, false); });
            
            commentsContainer.innerHTML = html || '<p class="text-color-darkest mb-6">No comments yet.</p>';

            // Stagger comment entrance animations
            var commentCards = commentsContainer.querySelectorAll('.comment-enter-animate');
            commentCards.forEach(function(card, index) {
                card.style.animationDelay = (index * 80) + 'ms';
            });
            
            commentsHasNext = data.has_next;
            updateLoadMoreVisibility();
            
            syncCommentsToSidebar();
        })
        .catch(function(err) {
            console.error("Error loading initial comments:", err);
            
            var commentsContainer = document.getElementById('comments-container');
            if (commentsContainer) {
                commentsContainer.innerHTML = '<p class="text-color-darkest mb-6">Failed to load comments.</p>';
            }
            if (sidebarList) {
                sidebarList.innerHTML = '<p class="text-color-darkest mb-6 p-4">Failed to load comments.</p>';
            }

            // Hide comment skeletons and show actual comment buttons
            var commentSkeleton = document.getElementById('comment-btn-skeleton');
            if (commentSkeleton) commentSkeleton.style.display = 'none';
            var commentBtn = document.getElementById('sidebar-comment-btn');
            if (commentBtn) commentBtn.style.display = 'flex';

            var bottomCommentSkeleton = document.getElementById('bottom-comment-btn-skeleton');
            if (bottomCommentSkeleton) bottomCommentSkeleton.style.display = 'none';
            var bottomCommentBtn = document.getElementById('bottom-sidebar-comment-btn');
            if (bottomCommentBtn) bottomCommentBtn.style.display = 'flex';
        });

    function handleCommentLike(btn) {
        if (window.USER_IS_AUTHENTICATED !== true) {
            window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search) + '&msg=' + encodeURIComponent('Please login to like comments and replies.');
            return;
        }

        var commentSno = btn.getAttribute('data-comment-sno');
        if (!commentSno) return; // Not ready yet

        // Optimistic UI updates
        var isLiked = btn.classList.contains('liked');
        var countSpan = btn.querySelector('.comment-like-count');
        var currentCount = parseInt(countSpan.textContent) || 0;

        // Toggle state
        var newLiked = !isLiked;
        var newCount = newLiked ? currentCount + 1 : Math.max(0, currentCount - 1);

        // Find all matching buttons for this comment (in main list and sidebar) and update them
        var allMatchingButtons = document.querySelectorAll('.comment-like-btn[data-comment-sno="' + commentSno + '"]');
        allMatchingButtons.forEach(function(el) {
            if (newLiked) {
                el.classList.add('liked');
                var svg = el.querySelector('svg');
                if (svg) {
                    svg.setAttribute('fill', 'currentColor');
                }
                // Add bounce animation
                el.classList.add('bounce');
                // Remove bounce class after animation completes so it can run again
                setTimeout(function() {
                    el.classList.remove('bounce');
                }, 400);
            } else {
                el.classList.remove('liked');
                var svg = el.querySelector('svg');
                if (svg) {
                    svg.setAttribute('fill', 'none');
                }
            }
            var countEl = el.querySelector('.comment-like-count');
            if (countEl) countEl.textContent = newCount;
        });

        // Send request
        fetch('/blog/toggle-comment-like/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({ comment_id: commentSno })
        })
        .then(function(res) {
            if (!res.ok) throw new Error('Failed to toggle like');
            return res.json();
        })
        .then(function(data) {
            // Update with final count from server
            allMatchingButtons.forEach(function(el) {
                var countEl = el.querySelector('.comment-like-count');
                if (countEl) countEl.textContent = data.likes_count;
                
                if (data.status === 'liked') {
                    el.classList.add('liked');
                    var svg = el.querySelector('svg');
                    if (svg) svg.setAttribute('fill', 'currentColor');
                } else {
                    el.classList.remove('liked');
                    var svg = el.querySelector('svg');
                    if (svg) svg.setAttribute('fill', 'none');
                }
            });
        })
        .catch(function(err) {
            console.error('Error toggling like:', err);
            // Revert state on error
            allMatchingButtons.forEach(function(el) {
                if (isLiked) {
                    el.classList.add('liked');
                    var svg = el.querySelector('svg');
                    if (svg) svg.setAttribute('fill', 'currentColor');
                } else {
                    el.classList.remove('liked');
                    var svg = el.querySelector('svg');
                    if (svg) svg.setAttribute('fill', 'none');
                }
                var countEl = el.querySelector('.comment-like-count');
                if (countEl) countEl.textContent = currentCount;
            });
            if (window.showToast) {
                window.showToast('Failed to like comment.', 'error');
            } else {
                alert('Failed to like comment.');
            }
        });
    }

    // Set up event delegation for comment/reply likes and replies pagination
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.comment-like-btn');
        if (btn) {
            handleCommentLike(btn);
            return;
        }

        var readMoreBtn = e.target.closest('.read-more-replies-btn');
        if (readMoreBtn) {
            var commentItem = readMoreBtn.closest('.comment-item');
            if (!commentItem) return;
            var commentSno = commentItem.getAttribute('data-comment-sno');
            if (!commentSno) return;

            // Update all instances of this comment card (both main view and sidebar view)
            var allInstances = document.querySelectorAll('.comment-item[data-comment-sno="' + commentSno + '"]');
            allInstances.forEach(function(instance) {
                var hiddenReplies = Array.from(instance.querySelectorAll('.reply-item[data-hidden-reply="true"]'));
                var countToReveal = Math.min(hiddenReplies.length, 3);

                for (var i = 0; i < countToReveal; i++) {
                    hiddenReplies[i].style.display = 'flex';
                    hiddenReplies[i].removeAttribute('data-hidden-reply');
                }

                var instanceBtn = instance.querySelector('.read-more-replies-btn');
                if (instanceBtn) {
                    var remainingCount = hiddenReplies.length - countToReveal;
                    if (remainingCount > 0) {
                        instanceBtn.textContent = 'Read more replies (' + remainingCount + ' remaining)';
                    } else {
                        var wrapper = instanceBtn.closest('.read-more-replies-wrapper');
                        if (wrapper) wrapper.remove();
                    }
                }
            });
        }
    });

})();
