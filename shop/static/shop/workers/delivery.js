document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("confirm-button");
    const hiddenDiv = document.getElementById("incident-block");

    button.addEventListener("click", function () {
        // INTERFACE
        // Hide the button
        button.style.display = "none";
        console.log("BEBRA");

        // Show the hidden div
        hiddenDiv.removeAttribute("hidden");


        // BACKEND

    });
});

$(document).ready(function () {
    // Courier form submission
    $('#courierForm').on('submit', function (e) {
        e.preventDefault(); // Prevent page redirection
        var form = $(this);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            success: function (response) {
                // Handle success (you can update the UI or show a message)
                alert('Courier compensation accepted!');
            },
            error: function (xhr, status, error) {
                // Handle error (you can show an error message)
                alert('An error occurred, please try again.');
            }
        });
    });

    // Client form submission
    $('#clientForm').on('submit', function (e) {
        e.preventDefault(); // Prevent page redirection
        var form = $(this);

        $.ajax({
            type: form.attr('method'),
            url: form.attr('action'),
            success: function (response) {
                // Handle success (you can update the UI or show a message)
                alert('Client compensation accepted!');
            },
            error: function (xhr, status, error) {
                // Handle error (you can show an error message)
                alert('An error occurred, please try again.');
            }
        });
    });
});

document.getElementById("confirm-button").addEventListener("click", function () {
    const deliveryId = this.getAttribute("data-delivery-id");

    fetch(`/confirm_incident/${deliveryId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            "Content-Type": "application/json"
        },
    })
        .then(response => {
            if (response.ok) {
                alert("Incident confirmed successfully.");
            } else {
                alert("Error confirming incident.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An unexpected error occurred.");
        });
});