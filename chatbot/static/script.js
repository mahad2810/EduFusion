document.getElementById("studyPlanForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const course_name = document.getElementById("course_name").value.trim();
    const num_days = document.getElementById("num_days").value.trim();
    const hours_per_day = document.getElementById("hours_per_day").value.trim();

    const output = document.getElementById("output");
    output.innerHTML = "<p>Generating study plan... Please wait.</p>";

    try {
        const response = await fetch("/study-plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ course_name, num_days, hours_per_day })
        });

        const data = await response.json();

        if (response.ok) {
            // Render the HTML study plan
            output.innerHTML = data.roadmap;
        } else {
            // Show error message
            output.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        }
    } catch (err) {
        // Handle network or unexpected errors
        output.innerHTML = "<p style='color: red;'>An error occurred while generating the study plan. Please try again later.</p>";
    }
});
