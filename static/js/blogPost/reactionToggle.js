/**
 * Reaction Toggle - blogPost
 * Handles Fire, Insightful, Celebrate, and Surprised reactions with debounced batch sync.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    if (!config) return;

    var postId = config.postSno;
    var isAuthenticated = config.isAuthenticated;
    var syncUrl = config.addReactionsBatchUrl;

    // State
    var totalReactions = { fire: 0, insightful: 0, celebrate: 0, surprised: 0 };
    var userReactions = { fire: 0, insightful: 0, celebrate: 0, surprised: 0 };
    
    // localIncrements tracks counts accumulated since the last sync was initiated.
    var localIncrements = { fire: 0, insightful: 0, celebrate: 0, surprised: 0 };
    
    // pendingSync tracks increments currently in-flight to the server.
    var pendingSync = { fire: 0, insightful: 0, celebrate: 0, surprised: 0 };

    var syncTimeout = null;
    var EMOJIS = {
        fire: '🔥',
        insightful: '💡',
        celebrate: '🎉',
        surprised: '😮'
    };

    // Initialize state (called from postState.js)
    window.initReactionsState = function(initialTotals, initialUser) {
        if (initialTotals) {
            for (var key in totalReactions) {
                if (initialTotals.hasOwnProperty(key)) totalReactions[key] = initialTotals[key];
            }
        }
        if (initialUser) {
            for (var key in userReactions) {
                if (initialUser.hasOwnProperty(key)) userReactions[key] = initialUser[key];
            }
        }
        updateReactionUI();
    };

    function updateReactionUI() {
        ['top', 'bottom'].forEach(function(suffix) {
            var container = document.getElementById('reactions-container-' + suffix);
            if (container) {
                container.style.display = 'inline-flex';
            }
            for (var rType in totalReactions) {
                var btn = document.getElementById('react-btn-' + rType + '-' + suffix);
                var countSpan = document.getElementById('react-count-' + rType + '-' + suffix);
                
                if (countSpan) {
                    countSpan.innerText = totalReactions[rType];
                }
                
                if (btn) {
                    var userCount = userReactions[rType];
                    if (userCount > 0) {
                        btn.classList.add('user-reacted');
                    } else {
                        btn.classList.remove('user-reacted');
                    }
                }
            }
        });
    }

    function handleReactionClick(rType, suffix, event) {
        if (event) {
            event.stopPropagation();
        }

        if (!isAuthenticated) {
            window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname + window.location.search) + '&msg=' + encodeURIComponent('Please login to react to posts.');
            return;
        }

        // 1. OPTIMISTIC UPDATE
        totalReactions[rType]++;
        userReactions[rType]++;
        localIncrements[rType]++;

        // Update UI immediately for both top and bottom
        updateReactionUI();

        // 2. TRIGGER ANIMATIONS ON BOTH INSTANCES
        ['top', 'bottom'].forEach(function(sfx) {
            var btn = document.getElementById('react-btn-' + rType + '-' + sfx);
            if (btn) {
                triggerBounce(btn);
                // Only shoot particles from the clicked button to avoid visual clutter
                if (sfx === suffix) {
                    triggerParticles(btn);
                }
            }
        });

        // 3. DEBOUNCED SYNC
        clearTimeout(syncTimeout);
        syncTimeout = setTimeout(syncReactionsToServer, 1000);
    }

    function triggerBounce(el) {
        el.classList.remove('reaction-bounce');
        void el.offsetWidth; // force reflow
        el.classList.add('reaction-bounce');
        el.addEventListener('animationend', function onEnd() {
            el.classList.remove('reaction-bounce');
            el.removeEventListener('animationend', onEnd);
        });
    }

    function triggerParticles(el) {
        var rect = el.getBoundingClientRect();
        var wrapper = el.parentElement;
        if (!wrapper) return;

        var relativeParent = wrapper;
        // Ensure relativeParent has a relative position
        var computedStyle = window.getComputedStyle(relativeParent);
        if (computedStyle.position === 'static') {
            relativeParent.style.position = 'relative';
        }

        for (var i = 0; i < 6; i++) {
            var particle = document.createElement('span');
            particle.className = 'like-particle';

            var angle = (Math.PI * 2 / 6) * i + (Math.random() * 0.5 - 0.25);
            var dist = 18 + Math.random() * 14;

            particle.style.setProperty('--px', Math.cos(angle) * dist + 'px');
            particle.style.setProperty('--py', Math.sin(angle) * dist + 'px');
            particle.style.left = (el.offsetLeft + el.offsetWidth / 2 - 3) + 'px';
            particle.style.top = (el.offsetTop + el.offsetHeight / 2 - 3) + 'px';

            var colors = ['var(--theme-base)', 'var(--theme-light)', 'var(--theme-dark)', '#f59e0b', '#ef4444', '#10b981'];
            particle.style.background = colors[i % colors.length];

            relativeParent.appendChild(particle);
            particle.addEventListener('animationend', function() {
                this.remove();
            });
        }
    }

    function syncReactionsToServer() {
        // Move localIncrements into pendingSync
        var payloadIncrements = {};
        var hasIncrements = false;

        for (var key in localIncrements) {
            if (localIncrements[key] > 0) {
                payloadIncrements[key] = localIncrements[key];
                pendingSync[key] += localIncrements[key];
                localIncrements[key] = 0; // reset local buffer
                hasIncrements = true;
            }
        }

        if (!hasIncrements) return;

        // Capture a local copy of what we are sending so we can deduct it on success
        var sentIncrements = Object.assign({}, payloadIncrements);

        fetch(syncUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({
                post_id: postId,
                increments: sentIncrements
            })
        })
        .then(function(res) {
            if (!res.ok) throw new Error('Reaction sync failed');
            return res.json();
        })
        .then(function(data) {
            if (data.status === 'success') {
                // Deduct successfully synced increments from pendingSync
                for (var key in sentIncrements) {
                    pendingSync[key] = Math.max(0, pendingSync[key] - sentIncrements[key]);
                }

                // Update state: baseline (server state) + currently in-flight clicks (localIncrements + pendingSync)
                if (data.reactions) {
                    for (var key in totalReactions) {
                        if (data.reactions.hasOwnProperty(key)) {
                            totalReactions[key] = data.reactions[key] + localIncrements[key] + pendingSync[key];
                        }
                    }
                }
                if (data.user_reactions) {
                    for (var key in userReactions) {
                        if (data.user_reactions.hasOwnProperty(key)) {
                            userReactions[key] = data.user_reactions[key] + localIncrements[key] + pendingSync[key];
                        }
                    }
                }
                updateReactionUI();
            }
        })
        .catch(function(err) {
            console.error('Error syncing reactions:', err);
            // On failure, revert localIncrements to local buffer so they can be retried
            for (var key in sentIncrements) {
                localIncrements[key] += sentIncrements[key];
                pendingSync[key] = Math.max(0, pendingSync[key] - sentIncrements[key]);
            }
        });
    }

    // Set up click listeners for the inline buttons
    document.addEventListener('DOMContentLoaded', function() {
        ['top', 'bottom'].forEach(function(suffix) {
            for (var rType in EMOJIS) {
                (function(type, sfx) {
                    var btn = document.getElementById('react-btn-' + type + '-' + sfx);
                    if (btn) {
                        btn.addEventListener('click', function(e) {
                            handleReactionClick(type, sfx, e);
                        });
                    }
                })(rType, suffix);
            }
        });
    });
})();
