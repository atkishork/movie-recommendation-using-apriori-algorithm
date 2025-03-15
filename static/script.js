function sendMail(event) {
    event.preventDefault(); // Prevents page reload on form submission

    let parms = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        subject: document.getElementById("subject").value,
        message: document.getElementById("message").value,
    };

    // Send email using EmailJS
    emailjs.send("service_1cxv3yc", "template_jhkng9y", parms)
        .then(function(response) {
            console.log("SUCCESS!", response);
            document.getElementById("response-message").innerHTML = 
                "<span style='color: green;'>✅ Email Sent Successfully!</span>";
            document.getElementById("contactForm").reset(); // Clear form after successful submission
        })
        .catch(function(error) {
            console.error("ERROR:", error);
            document.getElementById("response-message").innerHTML = 
                "<span style='color: red;'>❌ Failed to send email. Please try again!</span>";
        });
}
