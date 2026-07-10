/**
 * Micro Animations - Global
 * 1. Count-up animation for numbers (views, likes, comments)
 * 2. Staggered card entrance animation via IntersectionObserver
 */
(function() {
    'use strict';

    // ── 1. COUNT-UP ANIMATION ──
    // Animates numeric text from 0 to its target value with easing.
    // Targets elements with the [data-count-up] attribute.
    // The attribute's presence triggers the animation; the element's textContent is the target value.

    function easeOutQuart(t) {
        return 1 - Math.pow(1 - t, 4);
    }

    function formatNumber(n) {
        return n.toLocaleString('en-US');
    }

    function animateCountUp(el) {
        if (el.dataset.countAnimated) return; // prevent re-animation
        el.dataset.countAnimated = 'true';

        var text = el.textContent.replace(/,/g, '').trim();
        var target = parseInt(text, 10);
        if (isNaN(target) || target === 0) return;

        var duration = Math.min(800, Math.max(400, target * 2)); // 400ms–800ms
        var startTime = null;

        el.textContent = '0';

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var easedProgress = easeOutQuart(progress);
            var current = Math.round(easedProgress * target);
            el.textContent = formatNumber(current);

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = formatNumber(target);
            }
        }

        requestAnimationFrame(step);
    }

    // Use IntersectionObserver to trigger count-up when elements scroll into view
    if ('IntersectionObserver' in window) {
        var countObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    animateCountUp(entry.target);
                    countObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });

        // Observe existing count elements
        function observeCountElements() {
            document.querySelectorAll('[data-count-up]').forEach(function(el) {
                if (!el.dataset.countAnimated) {
                    countObserver.observe(el);
                }
            });
        }

        // Initial observation
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', observeCountElements);
        } else {
            observeCountElements();
        }

        // Re-observe when new elements are added (e.g. after AJAX loads)
        // Debounced to avoid feedback loop: count-up animation changes textContent,
        // which would trigger the observer, re-querying DOM every animation frame.
        var countDebounceTimer;
        var bodyObserver = new MutationObserver(function(mutations) {
            // Only react to actual node additions, not text/attribute changes
            var hasNewNodes = false;
            for (var i = 0; i < mutations.length; i++) {
                if (mutations[i].addedNodes.length > 0) {
                    hasNewNodes = true;
                    break;
                }
            }
            if (!hasNewNodes) return;
            clearTimeout(countDebounceTimer);
            countDebounceTimer = setTimeout(observeCountElements, 150);
        });
        bodyObserver.observe(document.body, { childList: true, subtree: true });
    }

    // ── 2. STAGGERED CARD ENTRANCE ──
    // Animates .post-card elements with a staggered delay as they enter the viewport.

    if ('IntersectionObserver' in window) {
        var cardObserver = new IntersectionObserver(function(entries) {
            // Group all newly visible cards and stagger them
            var visibleCards = [];
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    visibleCards.push(entry.target);
                    cardObserver.unobserve(entry.target);
                }
            });

            visibleCards.forEach(function(card, index) {
                card.style.animationDelay = (index * 80) + 'ms';
                card.classList.add('card-enter-animate');
            });
        }, { threshold: 0.05 });

        function observeCardElements() {
            document.querySelectorAll('.post-card:not(.card-enter-animate)').forEach(function(el) {
                // Set initial state: invisible until animation runs
                el.style.opacity = '0';
                cardObserver.observe(el);
            });
        }

        // Initial observation
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', observeCardElements);
        } else {
            // Small delay to avoid animating cards already in viewport on page load
            setTimeout(observeCardElements, 100);
        }

        // Re-observe when new cards are added via AJAX (debounced)
        var cardDebounceTimer;
        var cardBodyObserver = new MutationObserver(function(mutations) {
            var hasNewCards = false;
            for (var i = 0; i < mutations.length; i++) {
                var added = mutations[i].addedNodes;
                for (var j = 0; j < added.length; j++) {
                    var node = added[j];
                    if (node.nodeType === 1 && (node.classList.contains('post-card') || node.querySelector('.post-card'))) {
                        hasNewCards = true;
                        break;
                    }
                }
                if (hasNewCards) break;
            }
            if (hasNewCards) {
                clearTimeout(cardDebounceTimer);
                cardDebounceTimer = setTimeout(observeCardElements, 150);
            }
        });
        cardBodyObserver.observe(document.body, { childList: true, subtree: true });
    }

    // Expose count-up utility globally for manual use
    window.animateCountUp = animateCountUp;

})();
