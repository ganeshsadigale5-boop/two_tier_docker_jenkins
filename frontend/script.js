const API_URL = "/api/tasks";

const form = document.getElementById("task-form");
const taskList = document.getElementById("task-list");

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

async function loadTasks() {
    try {
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error("Unable to load tasks");
        }

        const tasks = await response.json();

        taskList.innerHTML = "";

        if (tasks.length === 0) {
            taskList.textContent = "No tasks available.";
            return;
        }

        tasks.forEach(task => {
            const card = document.createElement("div");
            card.className = "task";

            card.innerHTML = `
                <h3>${escapeHTML(task.title)}</h3>
                <p>${escapeHTML(task.description)}</p>
                <p>Status: ${escapeHTML(task.status)}</p>

                <select id="status-${task.id}">
                    <option value="pending">Pending</option>
                    <option value="in-progress">In Progress</option>
                    <option value="completed">Completed</option>
                </select>

                <button onclick="updateTask(${task.id})">
                    Update
                </button>

                <button onclick="deleteTask(${task.id})">
                    Delete
                </button>
            `;

            taskList.appendChild(card);
        });

        tasks.forEach(task => {
            document.getElementById(`status-${task.id}`).value =
                task.status;
        });

    } catch (error) {
        taskList.textContent = error.message;
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title, description })
        });

        if (!response.ok) {
            throw new Error("Unable to create task");
        }

        form.reset();
        loadTasks();

    } catch (error) {
        alert(error.message);
    }
});

async function updateTask(id) {
    const status = document.getElementById(`status-${id}`).value;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: document.querySelector(
                    `.task select#status-${id}`
                ).closest(".task").querySelector("h3").textContent,
                description: document.querySelector(
                    `.task select#status-${id}`
                ).closest(".task").querySelector("p").textContent,
                status
            })
        });

        if (!response.ok) {
            throw new Error("Unable to update task");
        }

        loadTasks();

    } catch (error) {
        alert(error.message);
    }
}

async function deleteTask(id) {
    if (!confirm("Delete this task?")) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Unable to delete task");
        }

        loadTasks();

    } catch (error) {
        alert(error.message);
    }
}

loadTasks();

