const PRELYR_RUNTIME = "http://127.0.0.1:8765";

chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {
        if (message.type !== "PRELYR_PROCESS") {
            return;
        }

        processWithPreLyr(message.text)
            .then((result) => {
                sendResponse({
                    success: true,
                    result: result
                });
            })
            .catch((error) => {
                console.error(
                    "PreLyr runtime error:",
                    error
                );

                sendResponse({
                    success: false,
                    error: error.message
                });
            });

        return true;
    }
);


async function processWithPreLyr(text) {
    const response = await fetch(
        `${PRELYR_RUNTIME}/process`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            `PreLyr runtime returned ${response.status}`
        );
    }

    return await response.json();
}
async function processWithPreLyr(text) {
    const response = await fetch(
        `${PRELYR_RUNTIME}/process`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            `PreLyr runtime returned ${response.status}`
        );
    }

    return await response.json();
}


chrome.runtime.onInstalled.addListener(() => {
    console.log("PreLyr extension installed.");
});