document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('doc-form');
    const repoUrlInput = document.getElementById('repo-url');
    const guideTypeSelect = document.getElementById('guide-type');
    const projectDescTextarea = document.getElementById('project-desc');
    const btnSubmit = document.getElementById('btn-submit');
    const charCounterSpan = document.getElementById('current-chars');
    const btnViewDoc = document.getElementById('btn-view-doc');

    const stateCapture = document.getElementById('state-capture');
    const stateLoading = document.getElementById('state-loading');
    const stateResolution = document.getElementById('state-resolution');

    // Validation Regex for github.com URLs
    const githubRegex = /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/;

    // Real-time GitHub URL validation
    repoUrlInput.addEventListener('input', () => {
        validateRepoUrl();
    });

    function validateRepoUrl() {
        const value = repoUrlInput.value.trim();
        const formGroup = repoUrlInput.closest('.form-group');
        
        if (value === "") {
            formGroup.classList.remove('has-error');
            formGroup.classList.remove('is-valid');
            return false;
        }

        if (githubRegex.test(value)) {
            formGroup.classList.remove('has-error');
            formGroup.classList.add('is-valid');
            return true;
        } else {
            formGroup.classList.add('has-error');
            formGroup.classList.remove('is-valid');
            return false;
        }
    }

    // Textarea character count
    projectDescTextarea.addEventListener('input', () => {
        const count = projectDescTextarea.value.length;
        charCounterSpan.textContent = count;
    });

    // Form Submission / State Transitions
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const isUrlValid = validateRepoUrl();
        const isSelectValid = guideTypeSelect.value !== "";
        const isDescValid = projectDescTextarea.value.trim() !== "";

        if (!isUrlValid) {
            repoUrlInput.closest('.form-group').classList.add('has-error');
            repoUrlInput.focus();
            return;
        }

        if (!isSelectValid || !isDescValid) {
            alert('Please fill in all form fields.');
            return;
        }

        // State 2: Processing (prevent duplicate submissions)
        disableInputs(true);
        transitionState(stateCapture, stateLoading);

        try {
            // Call the orchestration API in the backend
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    repo_url: repoUrlInput.value.trim(),
                    guide_type: guideTypeSelect.value,
                    description: projectDescTextarea.value.trim()
                })
            });

            if (!response.ok) {
                throw new Error('Error generating documentation.');
            }

            const data = await response.json();
            
            // Set output document path / download link
            if (data.session_id) {
                // Link the button to download the zip file
                btnViewDoc.href = `/download/${data.session_id}`;
            } else {
                btnViewDoc.href = '#';
            }

            // State 3: Resolution
            setTimeout(() => {
                transitionState(stateLoading, stateResolution);
            }, 1000); // Small fluid transition buffer

        } catch (error) {
            console.error(error);
            alert('An error occurred while processing the request. Please try again.');
            disableInputs(false);
            transitionState(stateLoading, stateCapture);
        }
    });

    // Disable all inputs
    function disableInputs(disable) {
        repoUrlInput.disabled = disable;
        guideTypeSelect.disabled = disable;
        projectDescTextarea.disabled = disable;
        btnSubmit.disabled = disable;
    }

    // Switch between states with smooth transitions
    function transitionState(fromView, toView) {
        fromView.style.opacity = '0';
        fromView.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
            fromView.classList.remove('active');
            toView.classList.add('active');
            // Allow CSS renderer to apply class change first
            setTimeout(() => {
                toView.style.opacity = '1';
                toView.style.transform = 'translateY(0)';
            }, 50);
        }, 400);
    }
});
