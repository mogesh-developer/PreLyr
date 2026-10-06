(() => {
    const PRELYR_MARKER = "data-prelyr-enabled";

    let processing = false;
    let listenerAttached = false;

    // Prevent our own programmatic send click from
    // entering the PreLyr click handler again.
    let submitting = false;


    // --------------------------------------------------
    // Visibility
    // --------------------------------------------------

    function isVisible(element) {
        if (!element) {
            return false;
        }

        const rect = element.getBoundingClientRect();

        const style = getComputedStyle(element);

        return (
            rect.width > 0 &&
            rect.height > 0 &&
            style.visibility !== "hidden" &&
            style.display !== "none"
        );
    }


    // --------------------------------------------------
    // Composer detection
    // --------------------------------------------------

    function findComposer() {
        const elements = document.querySelectorAll(
            "textarea, [contenteditable='true']"
        );

        // Prefer visible composer inside a form.
        for (const element of elements) {
            if (!isVisible(element)) {
                continue;
            }

            if (element.closest("form")) {
                return element;
            }
        }

        // Fallback.
        for (const element of elements) {
            if (isVisible(element)) {
                return element;
            }
        }

        return null;
    }


    // --------------------------------------------------
    // Read composer
    // --------------------------------------------------

    function getText(element) {
        if (!element) {
            return "";
        }

        if (element.tagName === "TEXTAREA") {
            return element.value || "";
        }

        return (
            element.innerText ||
            element.textContent ||
            ""
        );
    }


    // --------------------------------------------------
    // Write composer
    // --------------------------------------------------

    function setText(element, text) {
        if (!element) {
            return;
        }

        element.focus();

        // TEXTAREA
        if (element.tagName === "TEXTAREA") {
            const descriptor =
                Object.getOwnPropertyDescriptor(
                    HTMLTextAreaElement.prototype,
                    "value"
                );

            if (descriptor && descriptor.set) {
                descriptor.set.call(
                    element,
                    text
                );
            } else {
                element.value = text;
            }

            element.dispatchEvent(
                new Event("input", {
                    bubbles: true
                })
            );

            element.dispatchEvent(
                new Event("change", {
                    bubbles: true
                })
            );

            return;
        }

        // CONTENTEDITABLE
        element.textContent = text;

        element.dispatchEvent(
            new InputEvent("input", {
                bubbles: true,
                inputType: "insertText",
                data: text
            })
        );
    }


    // --------------------------------------------------
    // Enter detection
    // --------------------------------------------------

    function isSendShortcut(event) {
        return (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        );
    }


    // --------------------------------------------------
    // Send button
    // --------------------------------------------------

    function findSendButton() {
        const buttons =
            document.querySelectorAll("button");

        for (const button of buttons) {
            if (!isVisible(button)) {
                continue;
            }

            const ariaLabel = (
                button.getAttribute("aria-label") ||
                ""
            ).toLowerCase();

            const title = (
                button.getAttribute("title") ||
                ""
            ).toLowerCase();

            const dataTestId = (
                button.getAttribute("data-testid") ||
                ""
            ).toLowerCase();

            if (
                ariaLabel.includes("send") ||
                title.includes("send") ||
                dataTestId.includes("send")
            ) {
                return button;
            }
        }

        return null;
    }


    // --------------------------------------------------
    // Submit to ChatGPT
    // --------------------------------------------------

    function submitPrompt() {
        const button = findSendButton();

        if (!button) {
            console.warn(
                "PreLyr: Send button not found."
            );

            return false;
        }

        console.log(
            "PRELYR: Submitting optimized prompt."
        );

        // Important:
        // Tell the click handler that this click
        // was generated by PreLyr itself.
        submitting = true;

        button.click();

        // Give ChatGPT time to consume the click.
        setTimeout(() => {
            submitting = false;
        }, 500);

        return true;
    }


    // --------------------------------------------------
    // Process prompt
    // --------------------------------------------------

    function processCurrentPrompt(event = null) {

        // Prevent duplicate processing.
        if (processing) {
            console.log(
                "PRELYR: Already processing."
            );

            return;
        }

        const composer = findComposer();

        if (!composer) {
            console.warn(
                "PRELYR: Composer not found."
            );

            return;
        }

        const text = getText(composer).trim();

        if (!text) {
            console.log(
                "PRELYR: Composer is empty."
            );

            return;
        }

        console.log(
            "PRELYR: Processing prompt:",
            text
        );

        processing = true;

        // Stop original ChatGPT Enter submission.
        if (event) {
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();
        }

        chrome.runtime.sendMessage(
            {
                type: "PRELYR_PROCESS",
                text: text
            },
            (response) => {

                console.log(
                    "PRELYR RESPONSE:",
                    response
                );

                if (chrome.runtime.lastError) {
                    console.error(
                        "PRELYR MESSAGE ERROR:",
                        chrome.runtime.lastError.message
                    );

                    processing = false;

                    return;
                }

                try {

                    if (
                        !response ||
                        !response.success
                    ) {
                        console.warn(
                            "PreLyr processing failed:",
                            response
                        );

                        return;
                    }

                    const optimizedText =
                        response.result.optimized_text;

                    console.log(
                        "PRELYR OPTIMIZED:",
                        optimizedText
                    );

                    // ChatGPT may rebuild the composer
                    // while the runtime is processing.
                    const currentComposer =
                        findComposer();

                    if (!currentComposer) {
                        console.warn(
                            "PreLyr: Composer disappeared."
                        );

                        return;
                    }

                    setText(
                        currentComposer,
                        optimizedText
                    );

                    console.log(
                        "PRELYR: Optimized text inserted."
                    );

                    // Let React process the input event
                    // before submitting.
                    setTimeout(() => {

                        if (!processing) {
                            return;
                        }

                        submitPrompt();

                    }, 100);

                } finally {

                    // Don't release immediately.
                    // ChatGPT needs time to process
                    // the programmatic submission.
                    setTimeout(() => {
                        processing = false;
                    }, 700);
                }
            }
        );
    }


    // --------------------------------------------------
    // Keyboard listener
    // --------------------------------------------------

    function handleKeydown(event) {

        // Debug logging can be removed later.
        console.log(
            "PRELYR KEY:",
            event.key,
            "shift:",
            event.shiftKey,
            "composing:",
            event.isComposing
        );

        if (!isSendShortcut(event)) {
            return;
        }

        const composer = findComposer();

        if (!composer) {
            return;
        }

        // Only intercept Enter from composer.
        if (
            event.target !== composer &&
            !composer.contains(event.target)
        ) {
            return;
        }

        console.log(
            "PRELYR: Send shortcut detected."
        );

        processCurrentPrompt(event);
    }


    // --------------------------------------------------
    // Send button listener
    // --------------------------------------------------

    function handleClick(event) {

        // IMPORTANT:
        // Ignore the click generated by our own
        // submitPrompt() function.
        if (submitting) {
            console.log(
                "PRELYR: Ignoring own submit click."
            );

            return;
        }

        const button =
            event.target.closest("button");

        if (!button) {
            return;
        }

        const sendButton =
            findSendButton();

        if (
            !sendButton ||
            button !== sendButton
        ) {
            return;
        }

        const composer = findComposer();

        if (!composer) {
            return;
        }

        const text =
            getText(composer).trim();

        if (!text) {
            return;
        }

        console.log(
            "PRELYR: User clicked send button."
        );

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        processCurrentPrompt();
    }


    // --------------------------------------------------
    // Attach listeners once
    // --------------------------------------------------

    function attachListeners() {

        if (listenerAttached) {
            return;
        }

        listenerAttached = true;

        document.documentElement.setAttribute(
            PRELYR_MARKER,
            "true"
        );

        document.addEventListener(
            "keydown",
            handleKeydown,
            true
        );

        document.addEventListener(
            "click",
            handleClick,
            true
        );

        console.log(
            "PRELYR: Content script listeners attached."
        );
    }


    // --------------------------------------------------
    // Initialize
    // --------------------------------------------------

    attachListeners();


    // --------------------------------------------------
    // ChatGPT is a dynamic SPA.
    // Keep observer lightweight.
    // --------------------------------------------------

    const observer =
        new MutationObserver(() => {

            if (!listenerAttached) {
                attachListeners();
            }

        });

    observer.observe(
        document.documentElement,
        {
            childList: true,
            subtree: true
        }
    );


    console.log(
        "PRELYR: Content script initialized."
    );

})();