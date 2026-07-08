/**
 * Code Blocks Enhancements - Articlio Blog
 * Handles syntax highlighting, copy to clipboard, and modern code header layouts.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Select all code blocks inside the ql-editor content
    const codeBlocks = document.querySelectorAll(".ql-editor pre");

    if (codeBlocks.length === 0) return;

    // Check if highlight.js is loaded
    if (typeof hljs === "undefined") {
        console.warn("Highlight.js is not loaded.");
        return;
    }

    // Heuristics-based language detection for common programming languages
    function guessLanguage(code) {
        const trimmed = code.trim();
        
        // JSON
        if (trimmed.startsWith('{') && trimmed.endsWith('}') && trimmed.includes('":')) {
            return 'json';
        }
        
        // HTML
        if (/<[a-z][\s\S]*>/i.test(code) && (code.includes('</div>') || code.includes('href=') || code.includes('class='))) {
            return 'html';
        }
        
        // CSS
        if (code.includes('{') && code.includes('}') && (code.includes('margin:') || code.includes('padding:') || code.includes('color:') || code.includes('background:'))) {
            return 'css';
        }
        
        // SQL
        if (/\b(select|insert|update|delete|create table|alter table|from|where)\b/i.test(code)) {
            return 'sql';
        }
        
        // JavaScript / TypeScript
        if (code.includes('console.log') || /\b(const|let|var)\b\s+\w+\s*=/i.test(code) || code.includes('=>') || code.includes('function ') || code.includes('document.addEventListener')) {
            return 'javascript';
        }
        
        // Python
        if (/\b(def|import|from|class|if|elif|else|print|for|while|try|except)\b/g.test(code) && (code.includes(':') || code.includes('print('))) {
            if (!code.includes('console.log') && !code.includes('cout') && !code.includes('System.out')) {
                return 'python';
            }
        }
        
        // C++
        if (code.includes('#include') || code.includes('std::') || code.includes('cout <<') || code.includes('cin >>')) {
            return 'cpp';
        }
        
        // Java
        if (code.includes('System.out.println') || code.includes('public class ') || code.includes('public static void main')) {
            return 'java';
        }
        
        // Bash / Shell / Command Line
        if (code.includes('npm ') || code.includes('pip install') || code.includes('python manage.py') || code.includes('git ') || code.includes('docker ') || code.includes('sudo ')) {
            return 'bash';
        }

        return null;
    }

    codeBlocks.forEach(function (pre) {
        const codeText = pre.textContent || pre.innerText || "";
        
        // 1. Identify pre-existing language class or guess it
        let definedLanguage = pre.getAttribute("data-language") || "";
        
        if (!definedLanguage) {
            pre.classList.forEach(function (cls) {
                if (cls.startsWith("language-")) {
                    definedLanguage = cls.replace("language-", "");
                } else if (cls !== "ql-syntax" && cls !== "hljs") {
                    definedLanguage = cls;
                }
            });
        }
        
        // If not found, use our custom heuristics
        let isPlainText = false;
        if (!definedLanguage) {
            const guessed = guessLanguage(codeText);
            if (guessed) {
                definedLanguage = guessed;
            } else {
                definedLanguage = "plaintext";
                isPlainText = true;
            }
        }

        // 2. Set language class on pre block and highlight it
        pre.className = "ql-syntax language-" + definedLanguage;
        
        hljs.highlightElement(pre);

        // 3. Determine the display language name
        let displayLanguage = definedLanguage.toUpperCase();
        if (isPlainText || displayLanguage === "PLAINTEXT" || !displayLanguage) {
            displayLanguage = "CODE";
        }
        if (displayLanguage === "CPP") displayLanguage = "C++";
        if (displayLanguage === "CSHARP") displayLanguage = "C#";
        if (displayLanguage === "JAVASCRIPT") displayLanguage = "JS";

        // 4. Create the wrapping elements
        const wrapper = document.createElement("div");
        wrapper.className = "code-block-wrapper";

        const header = document.createElement("div");
        header.className = "code-block-header";

        // OS-style window control dots + Language Badge
        header.innerHTML = `
            <div class="window-controls">
                <span class="window-dot dot-red"></span>
                <span class="window-dot dot-yellow"></span>
                <span class="window-dot dot-green"></span>
                <span class="lang-badge">${displayLanguage}</span>
            </div>
            <button class="code-copy-btn" aria-label="Copy code block">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="copy-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                <span class="copy-btn-text">Copy</span>
            </button>
        `;

        // 5. Rearrange elements in DOM
        pre.parentNode.insertBefore(wrapper, pre);
        wrapper.appendChild(header);
        wrapper.appendChild(pre);

        // 6. Setup Copy Event Listener
        const copyBtn = header.querySelector(".code-copy-btn");
        copyBtn.addEventListener("click", function () {
            navigator.clipboard.writeText(codeText).then(function () {
                // Success feedback
                copyBtn.classList.add("copied");
                copyBtn.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5" class="check-icon">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="copy-btn-text">Copied!</span>
                `;

                // Revert feedback after 2 seconds
                setTimeout(function () {
                    copyBtn.classList.remove("copied");
                    copyBtn.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" class="copy-icon">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                        </svg>
                        <span class="copy-btn-text">Copy</span>
                    `;
                }, 2000);
            }).catch(function (err) {
                console.error("Failed to copy code: ", err);
            });
        });
    });
});
