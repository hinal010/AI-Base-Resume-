
function editEducation(id, degreeId, courseId, instituteId, start, end, grade){

    document.getElementById("edu_id").value = id;

    document.getElementById("degree").value = degreeId;

    fetch(`/get_courses/${degreeId}`)
    .then(res => res.json())
    .then(data => {

        let courseDropdown = document.getElementById("course");
        courseDropdown.innerHTML = '<option>Select Course</option>';

        data.forEach(c => {
            courseDropdown.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });

        courseDropdown.value = courseId;

        return fetch(`/get_institutes/${courseId}`);
    })
    .then(res => res.json())
    .then(data => {

        let instituteDropdown = document.getElementById("institute");
        instituteDropdown.innerHTML = '<option>Select Institute</option>';

        data.forEach(i => {
            instituteDropdown.innerHTML += `<option value="${i.id}">${i.name}</option>`;
        });

        instituteDropdown.value = instituteId;
    });

    document.querySelector('[name="start_year"]').value = start;
    document.querySelector('[name="end_year"]').value = end;
    document.querySelector('[name="grade"]').value = grade;

    window.scrollTo({ top: 0, behavior: 'smooth' });
}
document.getElementById("degree").addEventListener("change", function() {
    let degreeId = this.value;

    fetch(`/get_courses/${degreeId}`)
        .then(response => response.json())
        .then(data => {
            let courseDropdown = document.getElementById("course");
            courseDropdown.innerHTML = '<option value="">Select Course</option>';

            data.forEach(course => {
                courseDropdown.innerHTML += 
                    `<option value="${course.id}">${course.name}</option>`;
            });
        });
});
// Course → Institute
document.getElementById("course").addEventListener("change", function () {

    let courseId = this.value;

    fetch(`/get_institutes/${courseId}`)
        .then(res => res.json())
        .then(data => {

            let institute = document.getElementById("institute");
            institute.innerHTML = '<option>Select Institute</option>';

            data.forEach(i => {
                institute.innerHTML += `<option value="${i.id}">${i.name}</option>`;
            });

        });
});

document.getElementById("job_title").addEventListener("change", function () {
    let customInput = document.getElementById("custom_job_title");

    if (this.value === "other") {
        customInput.style.display = "block";
        customInput.required = true;
    } else {
        customInput.style.display = "none";
        customInput.required = false;
        customInput.value = "";
    }
});
function editExperienceFromButton(btn) {
    editExperience(
        btn.dataset.id,
        btn.dataset.type,
        btn.dataset.jobid,
        btn.dataset.jobtext,
        btn.dataset.company,
        btn.dataset.start,
        btn.dataset.end,
        btn.dataset.current,
        btn.dataset.responsibilities
    );
}
function editExperience(id, experienceType, jobTitleId, jobTitleText, companyName, startYear, endYear, currentJob, responsibilities) {
    document.getElementById("exp_id").value = id;
    document.getElementById("experience_type").value = experienceType;
    document.getElementById("job_title").value = jobTitleId;
    document.getElementById("company_name").value = companyName;
    document.getElementById("exp_start_year").value = startYear;
    document.getElementById("exp_end_year").value = endYear;
    document.getElementById("current_job").checked = currentJob == "1";
    document.getElementById("responsibilities").value = responsibilities;

    let customInput = document.getElementById("custom_job_title");
    if (jobTitleId === "other") {
        customInput.style.display = "block";
        customInput.required = true;
        customInput.value = jobTitleText;
    } else {
        customInput.style.display = "none";
        customInput.required = false;
        customInput.value = "";
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}
function commonDelete(url, message = "Are you sure you want to delete this item?") {
    if (!confirm(message)) return;

    fetch(url, { method: "POST" })
        .then(() => {
            window.location.reload();
        })
        .catch(err => {
            alert("Delete failed");
            console.error(err);
        });
}
function editCertification(id, name, organization, date) {
    document.getElementById("cert_id").value = id;
    document.getElementById("certification_name").value = name;
    document.getElementById("organization").value = organization;
    document.getElementById("cert_date").value = date;

    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        const msg = document.querySelector(".success");
        if (msg) msg.style.display = "none";
    }, 3000);
});