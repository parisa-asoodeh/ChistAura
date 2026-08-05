console.log(
    "Quiz play JS loaded"
);

function collectQuizState() {

    const answers = {};

    document
        .querySelectorAll(
            "input[type='radio']:checked"
        )
        .forEach(
            (input) => {

                answers[
                    input.name.replace(
                        "question_",
                        ""
                    )
                ] = input.value;

            }
        );

    return answers;

}

console.log(
    "QUIZ STATE:",
    collectQuizState()
);

const resumeEngine = new ResumeEngine({

    sessionId: RESUME_CONFIG.sessionId,

    saveUrl: RESUME_CONFIG.saveUrl,

    collectState: collectQuizState,

});

console.log(
    "RESUME ENGINE:",
    resumeEngine
);