document.addEventListener("DOMContentLoaded", () => {

    // =========================
    // Hybrid Formula Editor
    // =========================
    //
    // This editor allows:
    // - normal Persian/English text
    // - LaTeX formulas
    // - text + formula together
    //
    // Example:
    // مساحت مستطیل برابر است با \( \frac47 \) مترمربع
    // =========================

    function createFormulaEditor(field) {

        if (!field) {
            return;
        }

        // =========================
        // Formula button
        // =========================

        const formulaButton = document.createElement("button");

        formulaButton.type = "button";
        formulaButton.textContent = "＋ درج فرمول";

        formulaButton.style.marginBottom = "10px";
        formulaButton.style.padding = "8px 14px";
        formulaButton.style.cursor = "pointer";


        // =========================
        // Formula editor container
        // =========================

        const formulaEditor = document.createElement("div");

        formulaEditor.style.display = "none";
        formulaEditor.style.marginBottom = "10px";
        formulaEditor.style.padding = "10px";
        formulaEditor.style.border = "1px solid #ccc";
        formulaEditor.style.borderRadius = "6px";
        formulaEditor.style.boxSizing = "border-box";


        // =========================
        // MathLive field
        // =========================

        const mathField = document.createElement("math-field");

        mathField.style.width = "100%";
        mathField.style.minHeight = "60px";
        mathField.style.fontSize = "1.2rem";
        mathField.style.padding = "10px";
        mathField.style.boxSizing = "border-box";


        formulaEditor.appendChild(mathField);


        // =========================
        // Buttons container
        // =========================

        const buttonsContainer = document.createElement("div");

        buttonsContainer.style.marginTop = "10px";


        // =========================
        // Insert button
        // =========================

        const insertButton = document.createElement("button");

        insertButton.type = "button";
        insertButton.textContent = "درج فرمول";

        insertButton.style.marginLeft = "8px";
        insertButton.style.padding = "7px 12px";
        insertButton.style.cursor = "pointer";


        // =========================
        // Cancel button
        // =========================

        const cancelButton = document.createElement("button");

        cancelButton.type = "button";
        cancelButton.textContent = "لغو";

        cancelButton.style.padding = "7px 12px";
        cancelButton.style.cursor = "pointer";


        // =========================
        // Piecewise function button
        // =========================

        const piecewiseButton = document.createElement("button");

        piecewiseButton.type = "button";
        piecewiseButton.textContent = "تابع چندضابطه‌ای";

        piecewiseButton.style.marginLeft = "8px";
        piecewiseButton.style.padding = "7px 12px";
        piecewiseButton.style.cursor = "pointer";


        // Insert buttons

        buttonsContainer.appendChild(piecewiseButton);
        buttonsContainer.appendChild(insertButton);
        buttonsContainer.appendChild(cancelButton);

        formulaEditor.appendChild(buttonsContainer);


        // =========================
        // Piecewise function
        // =========================

        piecewiseButton.addEventListener("click", () => {

            mathField.value =
                "\\begin{cases}" +
                " & " +
                "\\\\" +
                " & " +
                "\\end{cases}";

            mathField.focus();

        });


        // =========================
        // Add editor to page
        // =========================

        field.parentNode.insertBefore(
            formulaButton,
            field
        );

        field.parentNode.insertBefore(
            formulaEditor,
            field
        );


        // =========================
        // Saved cursor position
        // =========================

        let savedSelectionStart = 0;
        let savedSelectionEnd = 0;


        // =========================
        // Open formula editor
        // =========================

        formulaButton.addEventListener("click", () => {

            /*
             * Save the exact position where
             * the formula should be inserted.
             */
            savedSelectionStart = field.selectionStart;
            savedSelectionEnd = field.selectionEnd;

            formulaEditor.style.display = "block";

            mathField.value = "";

            mathField.focus();

        });


        // =========================
        // Insert formula
        // =========================

        insertButton.addEventListener("click", () => {

            const latex = mathField.value.trim();

            if (!latex) {
                return;
            }

            // One complete MathJax inline formula
            const formula = `\\(${latex}\\)`;


            const before =
                field.value.substring(
                    0,
                    savedSelectionStart
                );

            const after =
                field.value.substring(
                    savedSelectionEnd
                );


            field.value =
                before +
                formula +
                after;


            // =========================
            // Restore cursor
            // =========================

            const newCursorPosition =
                savedSelectionStart + formula.length;

            field.focus();

            field.setSelectionRange(
                newCursorPosition,
                newCursorPosition
            );


            // =========================
            // Close editor
            // =========================

            formulaEditor.style.display = "none";

            mathField.value = "";

        });


        // =========================
        // Cancel
        // =========================

        cancelButton.addEventListener("click", () => {

            formulaEditor.style.display = "none";

            mathField.value = "";

            field.focus();

        });

    }


    // =========================
    // Quiz Options
    // =========================

    const optionFields = [
        "id_option_a",
        "id_option_b",
        "id_option_c",
        "id_option_d",
    ];

    optionFields.forEach((fieldId) => {

        const field = document.getElementById(fieldId);

        if (!field) {
            return;
        }

        createFormulaEditor(field);

    });


    // =========================
    // Question
    // =========================

    const questionField =
        document.getElementById("id_question");

    if (questionField) {

        createFormulaEditor(questionField);

    }

});