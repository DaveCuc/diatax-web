document.addEventListener('DOMContentLoaded', () => {
    // Remove skeleton screen on load
    document.body.classList.remove('page-loading');

    // DOM Elements
    const form = document.getElementById('doc-form');
    const repoUrlInput = document.getElementById('repo-url');
    const guideTypeSelect = document.getElementById('guide-type');
    const projectDescTextarea = document.getElementById('project-desc');
    const btnSubmit = document.getElementById('btn-submit');
    const charCounterSpan = document.getElementById('current-chars');
    const btnViewDoc = document.getElementById('btn-view-doc');
    const btnGenerateAnother = document.getElementById('btn-generate-another');
    const mainCard = document.getElementById('main-card');
    const logoText = document.querySelector('.logo-text');
    const loadingStepText = document.getElementById('loading-step-text');

    const stateCapture = document.getElementById('state-capture');
    const stateLoading = document.getElementById('state-loading');
    const stateResolution = document.getElementById('state-resolution');
    const STATE_TRANSITION_MS = 650;
    const LOADING_STEPS = [
        'Receiving form data and activating the session...',
        'Preparing a secure workspace and sanitizing files...',
        'Analyzing architecture, endpoints, and dependencies...',
        'Drafting documentation with Diataxis guidance...',
        'Reviewing quality and applying refinements...',
        'Building the final site and packaging the ZIP...'
    ];
    const LOADING_STEP_INTERVAL_MS = 3200;

    let loadingStepTimer = null;
    let loadingStepIndex = 0;

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

    function resetToStart() {
        form.reset();
        charCounterSpan.textContent = '0';
        btnViewDoc.href = '#';
        repoUrlInput.closest('.form-group').classList.remove('has-error', 'is-valid');
        disableInputs(false);

        if (stateResolution.classList.contains('active')) {
            transitionState(stateResolution, stateCapture);
        } else if (stateLoading.classList.contains('active')) {
            transitionState(stateLoading, stateCapture);
        } else {
            stateCapture.classList.add('active');
            stateLoading.classList.remove('active', 'leaving');
            stateResolution.classList.remove('active', 'leaving');
            if (mainCard) {
                mainCard.classList.remove('is-loading');
            }
        }

        repoUrlInput.focus();
    }

    function setLoadingStep(text) {
        if (!loadingStepText) {
            return;
        }

        loadingStepText.classList.add('is-switching');
        setTimeout(() => {
            loadingStepText.textContent = text;
            loadingStepText.classList.remove('is-switching');
        }, 170);
    }

    function stopLoadingSteps() {
        if (loadingStepTimer) {
            clearInterval(loadingStepTimer);
            loadingStepTimer = null;
        }
    }

    function startLoadingSteps() {
        stopLoadingSteps();
        loadingStepIndex = 0;
        setLoadingStep(LOADING_STEPS[loadingStepIndex]);

        loadingStepTimer = setInterval(() => {
            loadingStepIndex = (loadingStepIndex + 1) % LOADING_STEPS.length;
            setLoadingStep(LOADING_STEPS[loadingStepIndex]);
        }, LOADING_STEP_INTERVAL_MS);
    }

    if (logoText) {
        logoText.addEventListener('click', () => {
            resetToStart();
        });

        logoText.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                resetToStart();
            }
        });
    }

    if (btnGenerateAnother) {
        btnGenerateAnother.addEventListener('click', () => {
            resetToStart();
        });
    }

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
            }, 450);

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
        fromView.classList.add('leaving');

        setTimeout(() => {
            fromView.classList.remove('active', 'leaving');
            toView.classList.add('active');

            if (mainCard) {
                mainCard.classList.toggle('is-loading', toView === stateLoading);
            }

            if (toView === stateLoading) {
                startLoadingSteps();
            } else {
                stopLoadingSteps();
            }
        }, STATE_TRANSITION_MS);
    }

    // Smooth scrolling & active navigation class tracking
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.content-section, main.container');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const targetId = link.getAttribute('href');
            if (targetId.startsWith('#')) {
                e.preventDefault();
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    const offsetTop = targetSection.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    window.addEventListener('scroll', () => {
        let currentSectionId = 'home';
        const scrollPosition = window.scrollY + 120;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            if (scrollPosition >= sectionTop && scrollPosition < (sectionTop + sectionHeight)) {
                currentSectionId = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSectionId}`) {
                link.classList.add('active');
            }
        });
    });

    // Dynamic GitHub Team Members Fetcher
    const teamGrid = document.getElementById('team-grid');

    // Add the GitHub usernames of your team members to this array.
    // The system will automatically fetch their avatars and names from the GitHub API.
    const defaultMembers = [
        'DaveCuc',
        'sourabhDandage'
        // 'username2',
        // 'username3'
    ];

    async function addMemberByUsername(input) {
        let username = input.trim();
        const urlMatch = username.match(/github\.com\/([a-zA-Z0-9_-]+)/);
        if (urlMatch) {
            username = urlMatch[1];
        }

        if (document.getElementById(`member-${username.toLowerCase()}`)) {
            return;
        }

        try {
            const response = await fetch(`https://api.github.com/users/${username}`);
            if (!response.ok) {
                throw new Error('User not found on GitHub');
            }
            const data = await response.json();

            const memberCard = document.createElement('a');
            memberCard.className = 'member-circle';
            memberCard.id = `member-${username.toLowerCase()}`;
            memberCard.href = data.html_url;
            memberCard.target = '_blank';
            memberCard.rel = 'noopener noreferrer';
            memberCard.innerHTML = `
                <div class="member-avatar-wrapper">
                    <img src="${data.avatar_url}" alt="${data.name || data.login}" class="member-avatar" loading="lazy">
                </div>
                <h3 class="member-name">${data.name || data.login}</h3>
                <p class="member-login">@${data.login}</p>
            `;
            teamGrid.appendChild(memberCard);
        } catch (error) {
            console.error('Failed to load GitHub profile:', error);
        }
    }

    // Load default team members
    defaultMembers.forEach(user => addMemberByUsername(user));
});
