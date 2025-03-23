document.addEventListener("DOMContentLoaded", () => {
    let cards = document.querySelectorAll(".subject-card");

    if (cards.length === 0) {
        console.error("No .subject-card elements found! Check your HTML.");
    } else {
        console.log("3D effect applied to", cards.length, "cards.");
    }

    // Attach event listeners to all subject cards
    cards.forEach((card) => {
        let subjectId = card.getAttribute("data-id");

        // 3D Tilt Effect
        card.addEventListener("mousemove", (e) => {
            let rect = card.getBoundingClientRect();
            let x = e.clientX - rect.left; // Mouse X inside card
            let y = e.clientY - rect.top;  // Mouse Y inside card

            let centerX = rect.width / 2;
            let centerY = rect.height / 2;

            let rotateX = ((y - centerY) / centerY) * 10; // Reduced tilt to 10deg
            let rotateY = ((centerX - x) / centerX) * 10;

            card.style.transform = `perspective(600px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(600px) rotateX(0deg) rotateY(0deg)";
        });

        // Open Add Chapter on Click (Fixed)
        card.addEventListener("click", () => {
            console.log("Clicked on subject:", subjectId);
            if (subjectId) {
                window.location.href = `/add_chapter/${subjectId}`;  // Now opens add_chapter.html
            } else {
                console.error("No subject ID found!");
            }
        });

        // Right-click to show delete menu
        card.addEventListener("contextmenu", (event) => {
            event.preventDefault(); // Prevent default right-click menu
            showDeleteMenu(event, subjectId);
        });
    });
});

// Delete Subject Function
function deleteSubject(subjectId) {
    if (confirm("Are you sure you want to delete this subject?")) {
        fetch(`/delete_subject/${subjectId}`, { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert("Error deleting subject.");
                }
            });
    }
}

// Show right-click delete menu
function showDeleteMenu(event, subjectId) {
    let deleteMenu = document.getElementById("delete-menu");

    if (!deleteMenu) {
        console.error("Delete menu element not found!");
        return;
    }

    deleteMenu.style.display = "block";
    deleteMenu.style.left = `${event.pageX}px`;
    deleteMenu.style.top = `${event.pageY}px`;

    // Assign delete function to button
    deleteMenu.innerHTML = `<button onclick="deleteSubject(${subjectId})">Delete Subject</button>`;

    // Hide menu on click anywhere else
    document.addEventListener("click", () => {
        deleteMenu.style.display = "none";
    }, { once: true });
}
