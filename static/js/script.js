// Protokolant - JavaScript utilities

// Web Speech API - rozpoznawanie mowy w przeglądarce
let recognition = null;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'pl-PL';
} else if ('SpeechRecognition' in window) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'pl-PL';
}

document.addEventListener('DOMContentLoaded', function() {
    // Set default date to now for datetime-local input
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        dateInput.value = now.toISOString().slice(0, 16);
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Sprawdź czy przeglądarka wspiera Web Speech API
    if (!recognition) {
        console.warn('Przeglądarka nie wspiera Web Speech API');
    }
});

// Function to add participant field
function addParticipant() {
    const container = document.getElementById('participants-container');
    const div = document.createElement('div');
    div.className = 'mb-2';
    div.innerHTML = '<input type="text" class="form-control" name="participants[]" placeholder="Imię i nazwisko uczestnika">';
    container.appendChild(div);
}

// Function to add agenda item
function addAgendaItem() {
    const container = document.getElementById('agenda-container');
    const div = document.createElement('div');
    div.className = 'mb-3 agenda-item';
    div.innerHTML = `
        <label class="form-label">Punkt agendy</label>
        <input type="text" class="form-control mb-2" name="agenda_title[]" placeholder="Tytuł punktu">
        <textarea class="form-control" name="agenda_discussion[]" rows="3" placeholder="Omówienie / dyskusja"></textarea>
    `;
    container.appendChild(div);
}

// Function to add action item
function addActionItem() {
    const container = document.getElementById('actions-container');
    const div = document.createElement('div');
    div.className = 'mb-3 action-item row';
    div.innerHTML = `
        <div class="col-md-6">
            <label class="form-label">Opis zadania</label>
            <textarea class="form-control" name="action_description[]" rows="2" placeholder="Co należy zrobić?"></textarea>
        </div>
        <div class="col-md-3">
            <label class="form-label">Odpowiedzialny</label>
            <input type="text" class="form-control" name="action_assignee[]" placeholder="Imię i nazwisko">
        </div>
        <div class="col-md-3">
            <label class="form-label">Termin</label>
            <input type="date" class="form-control" name="action_deadline[]">
        </div>
    `;
    container.appendChild(div);
}

// Function to toggle action item status
function toggleActionStatus(actionId) {
    // This would be implemented when adding AJAX functionality
    console.log('Toggle status for action:', actionId);
}

// Export to PDF functionality (placeholder)
function exportToPDF(protocolId) {
    // This would trigger PDF generation endpoint
    window.location.href = `/protocol/${protocolId}/pdf`;
}

// Search functionality
function searchProtocols(searchTerm) {
    const rows = document.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(term)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    form.classList.add('was-validated');
}
