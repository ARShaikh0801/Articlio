/**
 * Text-to-Speech (TTS) - blogPost
 * TTS player: play/pause, stop, skip, speed control, word-by-word highlighting.
 */
(function() {
    'use strict';

    var toggleBtn = document.getElementById('tts-toggle-btn');
    var playerBar = document.getElementById('tts-player-bar');
    var playPauseBtn = document.getElementById('tts-play-pause-btn');
    var playIcon = document.getElementById('tts-play-icon');
    var pauseIcon = document.getElementById('tts-pause-icon');
    var skipBtn = document.getElementById('tts-skip-btn');
    var speedBtn = document.getElementById('tts-speed-btn');
    var speedLabel = document.getElementById('tts-speed-label');
    var stopBtn = document.getElementById('tts-stop-btn');
    var statusLabel = document.getElementById('tts-status-label');
    var loader = document.getElementById('tts-loader');

    if (!toggleBtn || !playerBar) return;

    var speeds = [1.0, 1.25, 1.5, 2.0, 0.8];
    var currentSpeedIndex = 0;
    var isPlaying = false;
    var isPaused = false;
    var currentIndex = 0;
    var speechChunks = [];
    var activeToken = 0;
    var currentUtterance = null;

    function initChunks() {
        speechChunks = [];
        var editor = document.querySelector('.ql-editor');
        if (!editor) return;
        var elements = editor.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, blockquote');
        elements.forEach(function(el) {
            var txt = el.textContent ? el.textContent.trim() : '';
            if (txt.length > 0) {
                speechChunks.push({ element: el, text: txt });
            }
        });
    }

    function prepareWordSpans(element) {
        if (element.dataset.ttsOriginal) return;
        element.dataset.ttsOriginal = element.innerHTML;
        var walk = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
        var textNodes = [];
        var node;
        while (node = walk.nextNode()) {
            textNodes.push(node);
        }
        var globalCharOffset = 0;
        textNodes.forEach(function(tNode) {
            var nodeText = tNode.nodeValue;
            var words = nodeText.split(/(\s+)/);
            var frag = document.createDocumentFragment();
            var localOffset = 0;
            words.forEach(function(w) {
                if (w.trim().length > 0) {
                    var span = document.createElement('span');
                    span.className = 'tts-word-span';
                    var wordStart = globalCharOffset + localOffset;
                    var wordEnd = wordStart + w.length;
                    span.dataset.startIdx = wordStart;
                    span.dataset.endIdx = wordEnd;
                    span.textContent = w;
                    frag.appendChild(span);
                } else {
                    frag.appendChild(document.createTextNode(w));
                }
                localOffset += w.length;
            });
            globalCharOffset += nodeText.length;
            if (tNode.parentNode) tNode.parentNode.replaceChild(frag, tNode);
        });
    }

    function restoreElementHtml(element) {
        if (element && element.dataset.ttsOriginal) {
            element.innerHTML = element.dataset.ttsOriginal;
            delete element.dataset.ttsOriginal;
        }
    }

    function clearHighlights() {
        document.querySelectorAll('.tts-reading-highlight').forEach(function(el) {
            el.classList.remove('tts-reading-highlight');
            restoreElementHtml(el);
        });
    }

    function showLoader(show) {
        if (!loader) return;
        if (show) {
            loader.classList.remove('hidden');
        } else {
            loader.classList.add('hidden');
        }
    }

    function updateUIState() {
        if (isPlaying && !isPaused) {
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
            toggleBtn.classList.add('active');
        } else {
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
            if (!isPlaying && !isPaused) {
                toggleBtn.classList.remove('active');
            }
        }
        if (speedLabel) speedLabel.textContent = speeds[currentSpeedIndex] + 'x';
    }

    function cancelActiveSpeech() {
        activeToken++;
        if (currentUtterance) {
            currentUtterance.onstart = null;
            currentUtterance.onend = null;
            currentUtterance.onerror = null;
            currentUtterance.onboundary = null;
            currentUtterance = null;
        }
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }

    function speakCurrentChunk() {
        if (!('speechSynthesis' in window)) {
            alert('Text-to-Speech is not supported in your browser.');
            return;
        }

        cancelActiveSpeech();
        clearHighlights();

        if (currentIndex < 0 || currentIndex >= speechChunks.length) {
            stopTTS();
            if (statusLabel) statusLabel.textContent = 'Finished reading aloud';
            return;
        }

        var token = ++activeToken;
        var chunk = speechChunks[currentIndex];
        prepareWordSpans(chunk.element);
        chunk.element.classList.add('tts-reading-highlight');
        chunk.element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        showLoader(true);
        if (statusLabel) {
            statusLabel.textContent = 'Preparing section ' + (currentIndex + 1) + ' of ' + speechChunks.length + '...';
        }

        var utterance = new SpeechSynthesisUtterance(chunk.text);
        utterance.rate = speeds[currentSpeedIndex];
        currentUtterance = utterance;

        utterance.onboundary = function(e) {
            if (token !== activeToken) return;
            var charIndex = e.charIndex;
            var spans = chunk.element.querySelectorAll('.tts-word-span');
            if (spans.length > 0) {
                spans.forEach(function(s) {
                    var start = parseInt(s.dataset.startIdx, 10);
                    var end = parseInt(s.dataset.endIdx, 10);
                    if (charIndex >= start && charIndex < end) {
                        s.classList.add('tts-word-active');
                    } else {
                        s.classList.remove('tts-word-active');
                    }
                });
            }
        };

        utterance.onstart = function() {
            if (token !== activeToken) return;
            showLoader(false);
            if (statusLabel) {
                statusLabel.textContent = 'Reading section ' + (currentIndex + 1) + ' of ' + speechChunks.length;
            }
        };

        utterance.onend = function() {
            if (token !== activeToken) return;
            showLoader(false);
            restoreElementHtml(chunk.element);
            if (isPlaying && !isPaused) {
                currentIndex++;
                speakCurrentChunk();
            }
        };

        utterance.onerror = function(e) {
            if (token !== activeToken) return;
            console.error('Speech synthesis error:', e);
            showLoader(false);
            restoreElementHtml(chunk.element);
            if (isPlaying && !isPaused) {
                currentIndex++;
                speakCurrentChunk();
            }
        };

        window.speechSynthesis.speak(utterance);
    }

    function startOrToggleTTS() {
        if (!('speechSynthesis' in window)) {
            alert('Text-to-Speech is not supported in your browser.');
            return;
        }

        if (playerBar.classList.contains('hidden')) {
            playerBar.classList.remove('hidden');
            playerBar.classList.add('flex');
        }

        if (!isPlaying && !isPaused) {
            initChunks();
            if (speechChunks.length === 0) {
                if (statusLabel) statusLabel.textContent = 'No text found to read';
                return;
            }
            isPlaying = true;
            isPaused = false;
            currentIndex = 0;
            updateUIState();
            speakCurrentChunk();
        } else if (isPlaying && !isPaused) {
            cancelActiveSpeech();
            isPlaying = false;
            isPaused = true;
            showLoader(false);
            if (statusLabel) statusLabel.textContent = 'Playback paused';
            updateUIState();
        } else if (isPaused) {
            isPlaying = true;
            isPaused = false;
            updateUIState();
            speakCurrentChunk();
        }
    }

    function stopTTS() {
        cancelActiveSpeech();
        isPlaying = false;
        isPaused = false;
        currentIndex = 0;
        clearHighlights();
        showLoader(false);
        updateUIState();
        playerBar.classList.add('hidden');
        playerBar.classList.remove('flex');
        if (statusLabel) statusLabel.textContent = 'Ready to read aloud';
    }

    function skipForward() {
        if (!isPlaying && !isPaused) return;
        currentIndex++;
        isPaused = false;
        isPlaying = true;
        updateUIState();
        speakCurrentChunk();
    }

    function cycleSpeed() {
        currentSpeedIndex = (currentSpeedIndex + 1) % speeds.length;
        if (speedLabel) speedLabel.textContent = speeds[currentSpeedIndex] + 'x';
        if (isPlaying && !isPaused) {
            speakCurrentChunk();
        }
    }

    toggleBtn.addEventListener('click', startOrToggleTTS);
    playPauseBtn.addEventListener('click', startOrToggleTTS);
    stopBtn.addEventListener('click', stopTTS);
    skipBtn.addEventListener('click', skipForward);
    speedBtn.addEventListener('click', cycleSpeed);

    window.addEventListener('beforeunload', function() {
        cancelActiveSpeech();
    });
})();
