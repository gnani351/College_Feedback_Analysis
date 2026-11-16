
const API_URL = "http://127.0.0.1:5000/api/feedback";

const feedbackForm = document.getElementById("feedbackForm");

// Submit feedback
feedbackForm.addEventListener("submit", async function(e) {

    e.preventDefault();

    const student = document.getElementById("student").value.trim();
    const department = document.getElementById("department").value.trim();
    const category = document.getElementById("category").value;
    const feedback = document.getElementById("feedback").value.trim();

    const result = document.getElementById("result");

    try {

        const response = await fetch(API_URL, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                student: student,
                department: department,
                category: category,
                feedback: feedback
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.message || "Submission failed");
        }

        // Display sentiment result
        result.style.display = "block";
        result.className = "result " + data.sentiment.toLowerCase();

        result.innerHTML =
            "<strong>Feedback Submitted Successfully!</strong><br>" +
            "Sentiment Result: <strong>" +
            data.sentiment + "</strong>";

        feedbackForm.reset();

        // Refresh dashboard and history
        loadFeedback();

    } catch (error) {

        result.style.display = "block";
        result.className = "result negative";

        result.textContent = "Error: " + error.message;

        console.error(error);
    }

});


// Load feedback from MySQL through Flask
async function loadFeedback() {

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Unable to load feedback");
        }

        const records = await response.json();

        updateDashboard(records);
        updateTable(records);

    } catch (error) {

        console.error("Loading feedback error:", error);

    }

}


// Update dashboard statistics
function updateDashboard(records) {

    const total = records.length;

    const positive = records.filter(
        r => r.sentiment === "Positive"
    ).length;

    const negative = records.filter(
        r => r.sentiment === "Negative"
    ).length;

    const neutral = records.filter(
        r => r.sentiment === "Neutral"
    ).length;

    document.getElementById("total").textContent = total;

    document.getElementById("positiveCount").textContent = positive;

    document.getElementById("negativeCount").textContent = negative;

    document.getElementById("neutralCount").textContent = neutral;

    const values = [
        ["positive", positive],
        ["negative", negative],
        ["neutral", neutral]
    ];

    values.forEach(([name, count]) => {

        const percent = total
            ? Math.round((count / total) * 100)
            : 0;

        document.getElementById(name + "Percent").textContent =
            percent + "%";

        document.getElementById(name + "Bar").style.width =
            percent + "%";

    });

}


// Display feedback history
function updateTable(records) {

    const table = document.getElementById("feedbackTable");

    table.innerHTML = "";

    if (records.length === 0) {

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.textContent = "No feedback submitted yet.";

        row.appendChild(cell);
        table.appendChild(row);

        return;
    }

    records.forEach(record => {

        const row = document.createElement("tr");

        [
            record.student,
            record.department,
            record.category,
            record.feedback,
            record.sentiment
        ].forEach(value => {

            const cell = document.createElement("td");

            cell.textContent = value;

            row.appendChild(cell);

        });

        table.appendChild(row);

    });

}


// Load existing database records when page opens
document.addEventListener("DOMContentLoaded", loadFeedback);
