document
  .getElementById("loanForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Processing...
    `;

    try {
      // Get form data
      const applicantIncome =
        parseFloat(document.getElementById("applicant_income").value) || 0;
      const coapplicantIncome =
        parseFloat(document.getElementById("coapplicant_income").value) || 0;
      const loanAmount =
        parseFloat(document.getElementById("loan_amount").value) || 0;
      const loanTerm =
        parseFloat(document.getElementById("loan_term").value) || 360;

      // Compute additional required features
      const EMI = loanAmount / loanTerm;
      const Balance_Income = applicantIncome + coapplicantIncome - EMI * 1000;
      const Total_Income = applicantIncome + coapplicantIncome;
      const LoanAmount_log = Math.log(loanAmount + 1);
      const Total_Income_log = Math.log(Total_Income + 1);

      // Prepare the request payload
      const formData = {
        Gender: document.getElementById("gender").value,
        Married: document.getElementById("married").value,
        Dependents: document.getElementById("dependents").value || "0",
        Education: document.getElementById("education").value,
        Self_Employed: document.getElementById("self_employed").value || "No",
        ApplicantIncome: applicantIncome,
        CoapplicantIncome: coapplicantIncome,
        LoanAmount: loanAmount,
        Loan_Amount_Term: loanTerm,
        Credit_History:
          parseFloat(document.getElementById("credit_history").value) || 0,
        Property_Area: document.getElementById("property_area").value,
        model_type: document.getElementById("model_type").value,
        EMI: EMI,
        Balance_Income: Balance_Income,
        LoanAmount_log: LoanAmount_log,
        Total_Income: Total_Income,
        Total_Income_log: Total_Income_log,
      };

      console.log("Submitting:", formData);

      // Fetch request
      const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      console.log("API Response:", data); // Debugging

      if (!response.ok) {
        throw new Error(data.error || "Request failed");
      }

      if (data.status === "success") {
        // Show results in UI
        document.getElementById("prediction").innerHTML = data.prediction;
        document.getElementById(
          "probability"
        ).innerHTML = `${data.probability}%`;
        document.getElementById("result").classList.remove("hidden");
        document.getElementById("result").style.display = "block";
      } else {
        throw new Error(data.error || "Prediction failed");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error: " + error.message);
    } finally {
      // Reset button state
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  });
