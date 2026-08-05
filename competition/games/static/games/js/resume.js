class ResumeEngine {

    constructor({
        sessionId,
        saveUrl,
        collectState,
        debounceDelay = 500,
    }) {

        this.sessionId = sessionId;

        this.saveUrl = saveUrl;

        this.collectState = collectState;

        this.debounceDelay = debounceDelay;

        this.saveTimeout = null;

    }


    scheduleSave() {

        if (this.saveTimeout) {

            clearTimeout(
                this.saveTimeout
            );

        }

        this.saveTimeout = setTimeout(
            () => {

                this.save();

            },
            this.debounceDelay
        );

    }


    async save() {

        const state = this.collectState();

        const payload = {
            state: state,
        };

        try {

            await fetch(
                this.saveUrl,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify(
                        payload
                    ),
                }
            );

        } catch (error) {

            console.error(
                "Resume save failed.",
                error
            );

        }

    }

}