// ChurnGuide Dynamic Client-Side Interactions

// Project Dropdown Toggle
function toggleProjectDropdown(event) {
  if (event) {
    event.stopPropagation();
  }
  const dropdown = document.getElementById('project-dropdown');
  if (dropdown) {
    dropdown.classList.toggle('open');
  }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
  const dropdown = document.getElementById('project-dropdown');
  const toggleBtn = document.getElementById('project-toggle-btn');
  if (dropdown && dropdown.classList.contains('open')) {
    if (!dropdown.contains(e.target) && !toggleBtn.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  }
});

// Step 1: File Upload & Demo Selection
function triggerUploadClick() {
  const fileInput = document.getElementById('csv_file_input');
  if (fileInput) {
    fileInput.click();
  }
}

function selectDemoProject(demoId, cardId) {
  document.getElementById('dataset_choice').value = 'demo';
  document.getElementById('demo_project_id').value = demoId;
  
  // Highlight selected card
  document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
  const card = document.getElementById(cardId);
  if (card) {
    card.classList.add('selected');
  }

  // Update dropzone UI
  const title = document.getElementById('dropzone-title');
  const sub = document.getElementById('dropzone-sub');
  if (title) title.innerText = `Selected demo: ${demoId}`;
  if (sub) sub.innerText = "Click 'Continue' below to activate and view results.";
}

// Drag & Drop and File Input Handler on Step 1
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('csv_file_input');
  const dropzone = document.getElementById('dropzone-area');
  
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        document.getElementById('dataset_choice').value = 'upload';
        document.getElementById('demo_project_id').value = '';
        document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));

        const title = document.getElementById('dropzone-title');
        const sub = document.getElementById('dropzone-sub');
        if (title) title.innerText = `Selected: ${file.name}`;
        if (sub) sub.innerText = `Size: ${(file.size / 1024).toFixed(1)} KB (Ready to proceed to Step 2)`;
      }
    });
  }

  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.style.borderColor = '#0fa37f';
        dropzone.style.background = '#f0fdf4';
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.style.borderColor = '#6ee7b7';
        dropzone.style.background = '#fcfdfd';
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files && files.length > 0) {
        if (fileInput) {
          fileInput.files = files;
          const evt = new Event('change');
          fileInput.dispatchEvent(evt);
        }
      }
    });
  }
});
