/**
 * Highlight - blogPost
 * Toolbar Highlight tool (with inline color picker) + Eraser tool.
 * Immediate frontend feedback & background server synchronization.
 */
(function() {
    'use strict';

    var config = window.BlogPostConfig;
    var qlEditor = document.querySelector('.ql-editor');
    
    // Toolbar buttons
    var hlToolBtn = document.getElementById('hl-tool-btn');
    var eraserToolBtn = document.getElementById('eraser-tool-btn');
    var hlColorPicker = document.getElementById('hl-color-picker');
    var colorDots = document.querySelectorAll('.hl-color-dot');

    var postSno = config.postSno;
    var postSlug = config.slug;
    var isAuth = window.USER_IS_AUTHENTICATED === true;
    
    var highlights = []; // [{ id, start, end, text, note, color }]
    var activeTool = null; // 'highlight', 'eraser', or null
    var activeColor = 'yellow'; // default color

    // Helper: get text nodes in order
    function getCharacterRanges(root) {
        var textNodes = [];
        var walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
        var node;
        while (node = walk.nextNode()) {
            textNodes.push(node);
        }
        return textNodes;
    }

    // Helper: Get character offsets of selection relative to editor root
    function getSelectionOffsets(root) {
        var selection = window.getSelection();
        if (!selection.rangeCount) return null;
        var range = selection.getRangeAt(0);
        
        if (!root.contains(range.startContainer) || !root.contains(range.endContainer)) {
            return null;
        }
        
        var preSelectionRange = range.cloneRange();
        preSelectionRange.selectNodeContents(root);
        preSelectionRange.setEnd(range.startContainer, range.startOffset);
        var start = preSelectionRange.toString().length;
        
        return {
            start: start,
            end: start + range.toString().length,
            text: range.toString()
        };
    }

    // Helper: Restore original HTML text nodes by removing spans
    function clearHighlightsFromDOM() {
        document.querySelectorAll('.articlio-highlight').forEach(function(span) {
            var parent = span.parentNode;
            if (parent) {
                var textNode = document.createTextNode(span.textContent);
                parent.replaceChild(textNode, span);
            }
        });
        if (qlEditor) qlEditor.normalize();
    }

    // Helper: Apply highlight wrapping to DOM
    function applyHighlightToDOM(start, end, id, color) {
        if (!qlEditor) return;
        var textNodes = getCharacterRanges(qlEditor);
        var currentLen = 0;
        var nodesToWrap = [];
        
        for (var i = 0; i < textNodes.length; i++) {
            var node = textNodes[i];
            var nodeLen = node.nodeValue.length;
            var nodeStart = currentLen;
            var nodeEnd = currentLen + nodeLen;
            
            if (nodeEnd > start && nodeStart < end) {
                nodesToWrap.push({
                    node: node,
                    start: Math.max(start, nodeStart) - nodeStart,
                    end: Math.min(end, nodeEnd) - nodeStart
                });
            }
            currentLen += nodeLen;
        }
        
        // Wrap in reverse order to keep offsets correct
        for (var i = nodesToWrap.length - 1; i >= 0; i--) {
            var item = nodesToWrap[i];
            var node = item.node;
            var s = item.start;
            var e = item.end;
            
            var text = node.nodeValue;
            var beforeText = text.substring(0, s);
            var matchText = text.substring(s, e);
            var afterText = text.substring(e);
            
            var parent = node.parentNode;
            if (!parent) continue;
            
            var span = document.createElement('span');
            span.className = 'articlio-highlight highlight-' + color;
            span.dataset.highlightId = id;
            span.textContent = matchText;
            
            var afterNode = document.createTextNode(afterText);
            var beforeNode = document.createTextNode(beforeText);
            
            parent.replaceChild(afterNode, node);
            parent.insertBefore(span, afterNode);
            parent.insertBefore(beforeNode, span);
        }
    }

    // Load highlights from server (or localStorage)
    function loadHighlights() {
        if (isAuth) {
            fetch('/blog/api/' + postSlug + '/highlights/')
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    highlights = data.highlights || [];
                    renderAllHighlights();
                })
                .catch(function(err) { console.error("Error loading highlights:", err); });
        } else {
            try {
                var saved = localStorage.getItem('articlio_highlights_' + postSno);
                highlights = saved ? JSON.parse(saved) : [];
                renderAllHighlights();
            } catch(e) {
                console.error("Error loading highlights from localStorage", e);
            }
        }
    }

    // Save highlights locally + globally in background
    function saveHighlightToServer(hl, tempId) {
        if (isAuth) {
            fetch('/blog/api/highlights/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN
                },
                body: JSON.stringify({
                    post_sno: postSno,
                    start: hl.start,
                    end: hl.end,
                    text: hl.text,
                    note: '',
                    color: hl.color
                })
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.status === 'success') {
                    var realId = data.highlight.id;
                    // Update ID in local highlights array
                    var idx = highlights.findIndex(function(h) { return h.id === tempId; });
                    if (idx !== -1) highlights[idx].id = realId;
                    
                    // Update dataset attribute on DOM spans
                    document.querySelectorAll('.articlio-highlight[data-highlight-id="' + tempId + '"]').forEach(function(span) {
                        span.dataset.highlightId = realId;
                    });
                    persistLocal();
                } else {
                    showToast('Failed to save highlight to database.', 'error');
                }
            })
            .catch(function(err) {
                console.error("Error saving highlight:", err);
            });
        } else {
            // Unauthenticated: create unique local ID
            var realId = 'hl_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            var idx = highlights.findIndex(function(h) { return h.id === tempId; });
            if (idx !== -1) highlights[idx].id = realId;
            document.querySelectorAll('.articlio-highlight[data-highlight-id="' + tempId + '"]').forEach(function(span) {
                span.dataset.highlightId = realId;
            });
            persistLocal();
        }
    }

    // Delete highlight from DOM & local storage + background server request
    function deleteHighlight(id) {
        // Immediately remove from array
        highlights = highlights.filter(function(h) { return h.id !== id && h.id != id; });
        persistLocal();

        // Immediately remove from DOM
        document.querySelectorAll('.articlio-highlight[data-highlight-id="' + id + '"]').forEach(function(span) {
            var parent = span.parentNode;
            if (parent) {
                var textNode = document.createTextNode(span.textContent);
                parent.replaceChild(textNode, span);
            }
        });
        if (qlEditor) qlEditor.normalize();

        // Send background request
        if (isAuth) {
            fetch('/blog/api/highlights/' + id + '/delete/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.CSRF_TOKEN
                }
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.status !== 'success') {
                    console.error("Failed to delete highlight from DB");
                }
            })
            .catch(function(err) {
                console.error("Error deleting highlight:", err);
            });
        }
    }

    // Erase highlights overlapping with a selection range
    function eraseOverlappingHighlights(offsets) {
        var start = offsets.start;
        var end = offsets.end;
        var toDelete = [];

        highlights.forEach(function(hl) {
            if (!(hl.end <= start || hl.start >= end)) {
                toDelete.push(hl.id);
            }
        });

        toDelete.forEach(function(id) {
            deleteHighlight(id);
        });
    }

    function persistLocal() {
        try {
            localStorage.setItem('articlio_highlights_' + postSno, JSON.stringify(highlights));
        } catch(e) {}
    }

    function renderAllHighlights() {
        clearHighlightsFromDOM();
        // Sort highlights descending by start offset to avoid index shifting when inserting spans
        var sorted = highlights.slice().sort(function(a, b) { return b.start - a.start; });
        sorted.forEach(function(hl) {
            applyHighlightToDOM(hl.start, hl.end, hl.id, hl.color);
        });
    }

    // Bind Toolbar Buttons Actions
    if (hlToolBtn) {
        hlToolBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (activeTool === 'highlight') {
                // Toggle off
                activeTool = null;
                hlToolBtn.classList.remove('active');
                hlColorPicker.classList.add('hidden');
            } else {
                // Toggle on
                activeTool = 'highlight';
                hlToolBtn.classList.add('active');
                hlColorPicker.classList.remove('hidden');
                
                // Disable eraser
                if (eraserToolBtn) {
                    eraserToolBtn.classList.remove('active');
                }
            }
        });
    }

    if (eraserToolBtn) {
        eraserToolBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            if (activeTool === 'eraser') {
                // Toggle off
                activeTool = null;
                eraserToolBtn.classList.remove('active');
            } else {
                // Toggle on
                activeTool = 'eraser';
                eraserToolBtn.classList.add('active');
                
                // Disable highlight
                if (hlToolBtn) {
                    hlToolBtn.classList.remove('active');
                }
                if (hlColorPicker) {
                    hlColorPicker.classList.add('hidden');
                }
            }
        });
    }

    // Color picker selection
    colorDots.forEach(function(dot) {
        dot.addEventListener('click', function(e) {
            e.stopPropagation();
            activeColor = dot.dataset.color;
            colorDots.forEach(function(d) { d.classList.remove('active'); });
            dot.classList.add('active');
        });
    });

    // Handle selection and mouse/touch release
    function handleTextSelection() {
        if (!qlEditor) return;
        var offsets = getSelectionOffsets(qlEditor);
        if (!offsets || offsets.text.trim().length === 0) return;

        if (activeTool === 'highlight') {
            var tempId = 'hl_temp_' + Date.now() + '_' + Math.round(Math.random() * 100000);
            var hl = {
                id: tempId,
                start: offsets.start,
                end: offsets.end,
                text: offsets.text,
                color: activeColor,
                note: ''
            };
            
            // Highlight immediately in DOM
            applyHighlightToDOM(hl.start, hl.end, hl.id, hl.color);
            highlights.push(hl);
            
            // Clear selection immediately
            window.getSelection().removeAllRanges();
            
            // Save to DB in background
            saveHighlightToServer(hl, tempId);
        } else if (activeTool === 'eraser') {
            eraseOverlappingHighlights(offsets);
            window.getSelection().removeAllRanges();
        }
    }

    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);

    // Clicking directly on an highlight span to erase when Eraser is active
    if (qlEditor) {
        qlEditor.addEventListener('click', function(e) {
            var target = e.target.closest('.articlio-highlight');
            if (target) {
                var id = target.dataset.highlightId;
                if (activeTool === 'eraser') {
                    e.stopPropagation();
                    deleteHighlight(id);
                }
            }
        });
    }

    // Initialize on load
    loadHighlights();
})();
