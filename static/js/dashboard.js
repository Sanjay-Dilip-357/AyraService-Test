// ==================== USER DASHBOARD JS ====================

let allDrafts = [];
let currentFilter = 'all';
let deleteTargetId = null;
let currentEditDraftId = null;

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function () {
    updateDateTime();
    setInterval(updateDateTime, 1000);
    loadDrafts();
    loadStats();
});

function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    const el = document.getElementById('currentDateTime');
    if (el) {
        el.textContent = now.toLocaleDateString('en-US', options);
    }
}

// ==================== TOAST NOTIFICATIONS ====================

function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    const toastIcon = document.getElementById('toastIcon');

    toastTitle.textContent = title;
    toastBody.textContent = message;

    toastIcon.className = 'bi me-2';
    switch (type) {
        case 'success':
            toastIcon.classList.add('bi-check-circle-fill', 'text-success');
            break;
        case 'error':
            toastIcon.classList.add('bi-x-circle-fill', 'text-danger');
            break;
        case 'warning':
            toastIcon.classList.add('bi-exclamation-triangle-fill', 'text-warning');
            break;
        default:
            toastIcon.classList.add('bi-info-circle-fill', 'text-info');
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// ==================== LOAD STATS ====================

async function loadStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        if (data.success) {
            document.getElementById('statsDrafts').textContent = data.stats.drafts || 0;
            document.getElementById('statsPending').textContent = data.stats.pending || 0;
            document.getElementById('statsApproved').textContent = data.stats.approved || 0;
            document.getElementById('statsGenerated').textContent = data.stats.generated || 0;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ==================== LOAD DRAFTS ====================

async function loadDrafts() {
    try {
        const response = await fetch('/api/drafts');
        const data = await response.json();

        if (data.success) {
            allDrafts = data.drafts || [];
            renderDrafts(allDrafts);
            updateDraftsTabCount();
            renderRecentActivity();
        }
    } catch (error) {
        console.error('Error loading drafts:', error);
    }
}

function renderDrafts(drafts) {
    const tbody = document.getElementById('draftsTableBody');
    const emptyState = document.getElementById('draftsEmptyState');

    if (!tbody) return;

    // Apply filter
    let filteredDrafts = drafts;
    if (currentFilter !== 'all') {
        filteredDrafts = drafts.filter(d => d.status === currentFilter);
    }

    if (filteredDrafts.length === 0) {
        tbody.innerHTML = '';
        if (emptyState) emptyState.classList.remove('d-none');
        return;
    }

    if (emptyState) emptyState.classList.add('d-none');

    tbody.innerHTML = filteredDrafts.map(draft => {
        const isPublished = draft.published === true;

        return `
        <tr>
            <td><strong>${draft.old_name || 'Unnamed'}</strong></td>
            <td><span class="badge bg-secondary">${draft.template_name || draft.template_type}</span></td>
            <td>${getStatusBadge(draft.status)}</td>
            <td>
                <span class="badge ${isPublished ? 'badge-published' : 'badge-unpublished'}">
                    <i class="bi bi-${isPublished ? 'check-circle' : 'circle'} me-1"></i>
                    ${isPublished ? 'Published' : 'Unpublished'}
                </span>
            </td>
            <td>${formatDate(draft.modified_at)}</td>
            <td class="action-buttons-cell">
                ${getActionButtons(draft)}
            </td>
        </tr>
    `;
    }).join('');
}

function getStatusBadge(status) {
    const badges = {
        'draft': '<span class="badge bg-warning text-dark">Draft</span>',
        'pending': '<span class="badge bg-info">Pending</span>',
        'approved': '<span class="badge bg-success">Approved</span>',
        'generated': '<span class="badge bg-primary">Generated</span>'
    };
    return badges[status] || `<span class="badge bg-secondary">${status}</span>`;
}

function getPublishedBadge(published) {
    const isPublished = published === true;
    if (isPublished) {
        return '<span class="badge badge-published"><i class="bi bi-check-circle me-1"></i>Published</span>';
    }
    return '<span class="badge badge-unpublished"><i class="bi bi-circle me-1"></i>Unpublished</span>';
}

function getActionButtons(draft) {
    let buttons = `
        <button class="btn btn-view btn-sm" onclick="viewDraft('${draft.id}')" title="View">
            <i class="bi bi-eye"></i>
        </button>
    `;

    // Edit only for draft status
    if (draft.status === 'draft') {
        buttons += `
            <button class="btn btn-edit btn-sm" onclick="editDraft('${draft.id}')" title="Edit">
                <i class="bi bi-pencil"></i>
            </button>
        `;
    }

    // Submit for approval (draft status only)
    if (draft.status === 'draft') {
        buttons += `
            <button class="btn btn-submit btn-sm" onclick="submitForApproval('${draft.id}')" title="Submit for Approval">
                <i class="bi bi-send"></i>
            </button>
        `;
    }

    // Delete only for draft status
    if (draft.status === 'draft') {
        buttons += `
            <button class="btn btn-delete btn-sm" onclick="showDeleteModal('${draft.id}')" title="Delete">
                <i class="bi bi-trash"></i>
            </button>
        `;
    }

    return buttons;
}

function filterDrafts(filter) {
    currentFilter = filter;

    // Update button states
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    renderDrafts(allDrafts);
}

function updateDraftsTabCount() {
    const draftCount = allDrafts.filter(d => d.status === 'draft' || d.status === 'pending').length;
    const countBadge = document.getElementById('draftsTabCount');
    if (countBadge) {
        countBadge.textContent = draftCount;
    }
}

// ==================== RECENT ACTIVITY ====================

function renderRecentActivity() {
    const container = document.getElementById('recentActivityList');
    if (!container) return;

    // Get 5 most recent items
    const recent = allDrafts.slice(0, 5);

    if (recent.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <p>No recent activity</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recent.map(draft => {
        const isPublished = draft.published === true;
        return `
        <div class="activity-item d-flex align-items-center justify-content-between p-3 mb-2 bg-light rounded">
            <div class="d-flex align-items-center">
                <div class="activity-icon me-3">
                    ${getActivityIcon(draft.status)}
                </div>
                <div>
                    <strong>${draft.old_name || 'Unnamed Document'}</strong>
                    <br>
                    <small class="text-muted">${draft.template_name || draft.template_type}</small>
                </div>
            </div>
            <div class="text-end">
                ${getStatusBadge(draft.status)}
                ${isPublished ? '<span class="badge badge-published ms-1">Published</span>' : ''}
                <br>
                <small class="text-muted">${formatDate(draft.modified_at)}</small>
            </div>
        </div>
    `;
    }).join('');
}

function getActivityIcon(status) {
    const icons = {
        'draft': '<i class="bi bi-file-earmark-text text-warning" style="font-size: 1.5rem;"></i>',
        'pending': '<i class="bi bi-hourglass-split text-info" style="font-size: 1.5rem;"></i>',
        'approved': '<i class="bi bi-check-circle text-success" style="font-size: 1.5rem;"></i>',
        'generated': '<i class="bi bi-file-earmark-check text-primary" style="font-size: 1.5rem;"></i>'
    };
    return icons[status] || '<i class="bi bi-file-earmark text-secondary" style="font-size: 1.5rem;"></i>';
}

// ==================== VIEW DRAFT (CD PREVIEW AT TOP) ====================

async function viewDraft(draftId) {
    const draft = allDrafts.find(d => d.id === draftId);
    if (!draft) return;

    const replacements = draft.replacements || {};
    const modalBody = document.getElementById('viewDraftBody');
    const isPublished = draft.published === true;

    // START WITH CD PREVIEW AT TOP
    let html = `
        <div class="view-doc-badge-container">
            ${getStatusBadge(draft.status)}
            <span class="badge ${isPublished ? 'badge-published' : 'badge-unpublished'}">
                <i class="bi bi-${isPublished ? 'check-circle' : 'circle'} me-1"></i>
                ${isPublished ? 'Published' : 'Unpublished'}
            </span>
            <span class="badge bg-secondary">${draft.template_name || draft.template_type}</span>
        </div>
        
        <!-- CD PREVIEW AT TOP -->
        <div class="cd-document-section">
            <div class="cd-document-header">
                <div class="cd-document-icon">
                    <i class="bi bi-file-earmark-text"></i>
                </div>
                <h6 class="cd-document-title">CD Document Preview</h6>
            </div>
            <div class="cd-copy-btn-container">
                <button class="cd-copy-btn" onclick="copyCdContent('viewCdContent')">
                    <i class="bi bi-clipboard"></i> Copy Content
                </button>
            </div>
            <div id="viewCdContent" class="cd-document-content">
                <div class="cd-loading">
                    <i class="bi bi-arrow-repeat"></i>
                    <p>Loading CD preview...</p>
                </div>
            </div>
        </div>
        
        <hr class="my-4">
        <h6 class="text-muted mb-3"><i class="bi bi-list-ul me-2"></i>Document Details</h6>
    `;

    // Personal Section
    html += buildViewSection('Personal Details', 'person-fill', 'personal', [
        { label: 'Old Name', value: replacements.OLD_NAME },
        { label: 'New Name', value: replacements.NEW_NAME },
        { label: 'Relation', value: replacements.UPDATE_RELATION },
        { label: 'Father/Spouse Name', value: replacements['FATHER-SPOUSE_NAME'] },
        { label: 'Wife Of', value: replacements.WIFE_OF ? 'Yes' : '' },
        { label: 'Spouse Name', value: replacements.SPOUSE_NAME1 },
        { label: 'Gender', value: replacements.GENDER_UPDATE },
        { label: 'Cast', value: replacements.CAST_UPDATE }
    ]);

    // Contact Section
    html += buildViewSection('Contact Details', 'telephone-fill', 'contact', [
        { label: 'Phone', value: replacements.PHONE_UPDATE },
        { label: 'Email', value: replacements.EMAIL_UPDATE },
        { label: 'Address', value: replacements.UPDATE_ADDRESS }
    ]);

    // Date Section
    html += buildViewSection('Date Details', 'calendar-event', 'dates', [
        { label: 'Numeric Date', value: replacements.NUM_DATE },
        { label: 'Alpha Date', value: replacements.ALPHA_DATE }
    ]);

    // Witness 1 Section
    html += buildViewSection('Witness 1 Details', 'person-badge', 'witness', [
        { label: 'Name', value: replacements.WITNESS_NAME1 },
        { label: 'Phone', value: replacements.WITNESS_PHONE1 },
        { label: 'Address', value: replacements.WITNESS_ADDRESS1 }
    ]);

    // Witness 2 Section
    html += buildViewSection('Witness 2 Details', 'person-badge-fill', 'witness', [
        { label: 'Name', value: replacements.WITNESS_NAME2 },
        { label: 'Phone', value: replacements.WITNESS_PHONE2 },
        { label: 'Address', value: replacements.WITNESS_ADDRESS2 }
    ]);

    // Minor template fields
    if (draft.template_type === 'minor_template') {
        html += buildViewSection('Child Details', 'emoji-smile', 'child', [
            { label: 'Father/Mother Name', value: replacements['FATHER-MOTHER_NAME'] },
            // ── Display SON-DAUGHTER with first letter capitalized for readability ──
            { label: 'Son/Daughter', value: replacements['SON-DAUGHTER'] ? capitalize(replacements['SON-DAUGHTER']) : '' },
            { label: 'Age', value: replacements.UPDATE_AGE },
            { label: 'DOB', value: replacements.CHILD_DOB },
            { label: 'Birth Place', value: replacements.BIRTH_PLACE }
        ]);
    }

    modalBody.innerHTML = html;

    const modal = new bootstrap.Modal(document.getElementById('viewDraftModal'));
    modal.show();

    // Load CD preview
    loadCDPreview(draftId, 'viewCdContent');
}

function buildViewSection(title, icon, sectionClass, fields) {
    const filledFields = fields.filter(f => f.value && f.value.toString().trim());
    if (filledFields.length === 0) return '';

    return `
        <div class="view-doc-section ${sectionClass}">
            <div class="view-doc-section-header">
                <div class="view-doc-section-icon">
                    <i class="bi bi-${icon}"></i>
                </div>
                <h6 class="view-doc-section-title">${title}</h6>
            </div>
            <div class="row">
                ${filledFields.map(f => `
                    <div class="col-md-6">
                        <div class="view-doc-field">
                            <span class="view-doc-label">${f.label}</span>
                            <span class="view-doc-value">${f.value}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

async function loadCDPreview(draftId, containerId) {
    try {
        const response = await fetch(`/api/drafts/${draftId}/cd-preview`);
        const data = await response.json();

        const container = document.getElementById(containerId);
        if (!container) return;

        if (data.success) {
            container.innerHTML = data.cd_content;
        } else {
            container.innerHTML = `<div class="text-center text-muted py-3">${data.message || 'Could not load preview'}</div>`;
        }
    } catch (error) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="text-center text-danger py-3">Error loading preview</div>`;
        }
    }
}

function copyCdContent(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const text = container.innerText || container.textContent;

    navigator.clipboard.writeText(text).then(() => {
        const btn = container.parentElement.querySelector('.cd-copy-btn');
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="bi bi-check-lg"></i> Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.classList.remove('copied');
            }, 2000);
        }
        showToast('Success', 'Content copied to clipboard', 'success');
    }).catch(() => {
        showToast('Error', 'Failed to copy content', 'error');
    });
}

// ==================== EDIT DRAFT (CD PREVIEW AT TOP - NO AUTO CLOSE) ====================

function editDraft(draftId) {
    currentEditDraftId = draftId;
    const draft = allDrafts.find(d => d.id === draftId);
    if (!draft) return;

    document.getElementById('editDraftTemplateBadge').textContent =
        draft.template_name || draft.template_type;

    const modalBody = document.getElementById('editDraftBody');
    modalBody.innerHTML = buildEditForm(draft);

    // ── Populate existing aliases ──────────────────────────────
    const r = draft.replacements || {};
    const { aliases: parsedAliases } = parseOldNameWithAliases(r.OLD_NAME || '');
    parsedAliases.forEach(function (aliasVal) {
        addDashAliasField(aliasVal);
    });

    if (parsedAliases.length > 0) {
        updateDashAliasPreview();
    }
    // ───────────────────────────────────────────────────────────

    const modal = new bootstrap.Modal(document.getElementById('editDraftModal'));
    modal.show();

    setTimeout(() => {
        loadCDPreview(draftId, 'editCdContent');
    }, 300);
}

function buildEditForm(draft) {
    const r = draft.replacements || {};
    const previewData = draft.preview_data || {};
    const folderType = previewData.folder_type || 'main';
    const relation = r.UPDATE_RELATION || '';
    const hasSpouse = r.WIFE_OF && r.SPOUSE_NAME1;

    const sonDaughterValue = (r['SON-DAUGHTER'] || '').toLowerCase().trim();

    // Parse aliases from OLD_NAME
    const { baseName: parsedBaseName, aliases: parsedAliases } = parseOldNameWithAliases(r.OLD_NAME || '');

    // Reset alias counter
    dashAliasCounter = 0;

    let html = `<input type="hidden" id="editDraftId" value="${draft.id}">`;

    // ── CD Preview (common) ─────────────────────────────────────
    html += `
        <div class="cd-document-section mb-4">
            <div class="cd-document-header">
                <div class="cd-document-icon">
                    <i class="bi bi-file-earmark-text"></i>
                </div>
                <div>
                    <h6 class="cd-document-title mb-0">CD Document Preview (Live)</h6>
                    <small class="text-muted" style="color:#92400e !important;">
                        Updates when you save changes
                    </small>
                </div>
            </div>
            <div class="cd-copy-btn-container">
                <button type="button" class="cd-copy-btn" onclick="copyCdContent('editCdContent')">
                    <i class="bi bi-clipboard"></i> Copy Content
                </button>
                <button type="button" class="btn btn-outline-warning btn-sm ms-2"
                        onclick="refreshCdPreviewFromForm()">
                    <i class="bi bi-arrow-clockwise"></i> Refresh Preview
                </button>
            </div>
            <div id="editCdContent" class="cd-document-content">
                <div class="cd-loading">
                    <i class="bi bi-arrow-repeat"></i>
                    <p>Loading CD preview...</p>
                </div>
            </div>
        </div>

        <hr class="my-4">
        <h6 class="text-primary mb-3">
            <i class="bi bi-pencil-square me-2"></i>Edit Document Details
        </h6>
    `;

    // ============================================================
    // MINOR TEMPLATE - separate layout
    // ============================================================
    if (draft.template_type === 'minor_template') {

        // ── Parent/Guardian Details ─────────────────────────────
        html += `
            <div class="form-section">
                <div class="section-header">
                    <div class="section-icon" style="background:var(--primary-gray,#6c757d);">
                        <i class="bi bi-people-fill"></i>
                    </div>
                    <h6 class="section-title">Parent / Guardian Details</h6>
                </div>
                <div class="row g-3">

                    <div class="col-md-6">
                        <label class="form-label">
                            Father/Mother Name <span class="required-asterisk">*</span>
                        </label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-person-heart"></i></span>
                            <input type="text" class="form-control" id="editFatherMother"
                                   value="${escapeHtml(r['FATHER-MOTHER_NAME'] || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">
                            Relationship <span class="required-asterisk">*</span>
                        </label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-people"></i></span>
                            <select class="form-select" id="editRelation"
                                    onchange="handleMinorRelationChangeDash()">
                                <option value="">Select...</option>
                                <option value="S/o" ${relation === 'S/o' ? 'selected' : ''}>S/o</option>
                                <option value="D/o" ${relation === 'D/o' ? 'selected' : ''}>D/o</option>
                                <option value="W/o" ${relation === 'W/o' ? 'selected' : ''}>W/o</option>
                                <option value="D/o & W/o"
                                    ${relation === 'D/o & W/o' ? 'selected' : ''}>D/o & W/o
                                </option>
                            </select>
                        </div>
                    </div>

                    <!-- Normal Guardian Spouse -->
                    <div class="col-md-6" id="editMinorNormalSpouseField"
                         style="display:${relation === 'D/o & W/o' ? 'none' : 'block'};">
                        <label class="form-label">
                            Guardian Spouse <span class="required-asterisk">*</span>
                        </label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-person"></i></span>
                            <input type="text" class="form-control" id="editFatherSpouse"
                                   value="${escapeHtml(r['FATHER-SPOUSE_NAME'] || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <!-- Dual Relation Fields -->
                    <div class="col-12" id="editMinorDualRelationFields"
                         style="display:${relation === 'D/o & W/o' ? 'block' : 'none'};">
                        <div class="dual-relation-card">
                            <div class="card-header">
                                <i class="bi bi-people-fill me-2"></i>D/o & W/o - Guardian Names
                            </div>
                            <div class="card-body p-3">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">
                                            Guardian's Father <span class="required-asterisk">*</span>
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text"
                                                  style="background:#1a1a1a;color:white;">D/o</span>
                                            <input type="text" class="form-control"
                                                   id="editGuardianFather"
                                                   value="${escapeHtml(r.GUARDIAN_FATHER_NAME || r['FATHER-SPOUSE_NAME'] || '')}"
                                                   style="text-transform:uppercase;"
                                                   oninput="this.value=this.value.toUpperCase();">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <label class="form-label">
                                            Guardian's Husband <span class="required-asterisk">*</span>
                                        </label>
                                        <div class="input-group">
                                            <span class="input-group-text"
                                                  style="background:#6c757d;color:white;">W/o</span>
                                            <input type="text" class="form-control"
                                                   id="editGuardianSpouse"
                                                   value="${escapeHtml(r.GUARDIAN_SPOUSE_NAME || r.SPOUSE_NAME1 || '')}"
                                                   style="text-transform:uppercase;"
                                                   oninput="this.value=this.value.toUpperCase();">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Address <span class="required-asterisk">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-house"></i></span>
                            <input type="text" class="form-control" id="editAddress"
                                   value="${escapeHtml(r.UPDATE_ADDRESS || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Phone <span class="required-asterisk">*</span></label>
                        <input type="tel" class="form-control" id="editPhone"
                               value="${escapeHtml(r.PHONE_UPDATE || '')}" maxlength="10">
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Email <span class="required-asterisk">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                            <input type="text" class="form-control" id="editEmail"
                                   value="${escapeHtml(r.EMAIL_UPDATE || '')}">
                        </div>
                    </div>

                </div>
            </div>
        `;

        // ── Child Details ───────────────────────────────────────
        html += `
            <div class="form-section">
                <div class="section-header">
                    <div class="section-icon" style="background:var(--primary-gray,#6c757d);">
                        <i class="bi bi-emoji-smile"></i>
                    </div>
                    <h6 class="section-title">Child Details</h6>
                </div>
                <div class="row g-3">

                    <!-- Child Old Name with Alias -->
                    <div class="col-md-6">
                        <label class="form-label">
                            Child Old Name <span class="required-asterisk">*</span>
                            <small class="text-muted">(+alias)</small>
                        </label>
                        <div style="display:flex; gap:0.5rem; align-items:flex-start;">
                            <div class="input-group flex-grow-1">
                                <span class="input-group-text"><i class="bi bi-person"></i></span>
                                <input type="text" class="form-control" id="editOldName"
                                       value="${escapeHtml(parsedBaseName)}"
                                       style="text-transform:uppercase;"
                                       oninput="this.value=this.value.toUpperCase();
                                                updateDashAliasPreview();">
                            </div>
                            <button type="button"
                                    title="Add Alias"
                                    onclick="addDashAliasField()"
                                    style="background:linear-gradient(135deg,#1a1a1a 0%,#444 100%);
                                           border:none; color:white; padding:0;
                                           border-radius:8px; width:42px; height:42px;
                                           min-width:42px; display:flex; align-items:center;
                                           justify-content:center; cursor:pointer;
                                           flex-shrink:0; transition:all 0.2s ease;"
                                    onmouseover="this.style.opacity='0.85'"
                                    onmouseout="this.style.opacity='1'">
                                <i class="bi bi-plus-lg"></i>
                            </button>
                        </div>

                        <div id="editAliasContainer" style="margin-top:0.5rem;"></div>

                        <div id="editAliasCounter"
                             style="display:none; margin-top:0.5rem; padding:0.35rem 0.65rem;
                                    background:#f8f9fa; border-radius:6px;
                                    font-size:0.75rem; color:#6c757d;">
                            <i class="bi bi-tags me-1"></i>Aliases: <span class="count">0</span>
                        </div>

                        <div id="editAliasPreview"
                             style="display:none; margin-top:0.75rem; padding:0.75rem;
                                    background:#f8f9fa; border-radius:8px;
                                    border:1px solid #dee2e6;">
                            <div style="font-size:0.75rem; font-weight:600; color:#6c757d;
                                        margin-bottom:0.5rem; text-transform:uppercase;
                                        letter-spacing:0.3px;">
                                <i class="bi bi-eye me-1"></i>Preview:
                            </div>
                            <div id="editAliasPreviewText" style="word-break:break-word;"></div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">
                            Child New Name <span class="required-asterisk">*</span>
                        </label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-person-check"></i></span>
                            <input type="text" class="form-control" id="editNewName"
                                   value="${escapeHtml(r.NEW_NAME || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Gender <span class="required-asterisk">*</span></label>
                        <select class="form-select" id="editGender">
                            <option value="">Select...</option>
                            <option value="MALE"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'MALE' ? 'selected' : ''}>
                                Male
                            </option>
                            <option value="FEMALE"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'FEMALE' ? 'selected' : ''}>
                                Female
                            </option>
                            <option value="OTHER"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'OTHER' ? 'selected' : ''}>
                                Other
                            </option>
                        </select>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Son/Daughter <span class="required-asterisk">*</span></label>
                        <select class="form-select" id="editSonDaughter">
                            <option value="">Select...</option>
                            <option value="son" ${sonDaughterValue === 'son' ? 'selected' : ''}>Son</option>
                            <option value="daughter"
                                ${sonDaughterValue === 'daughter' ? 'selected' : ''}>Daughter
                            </option>
                        </select>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">Date of Birth <span class="required-asterisk">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-calendar"></i></span>
                            <input type="text" class="form-control" id="editChildDob"
                                   value="${escapeHtml(r.CHILD_DOB || '')}"
                                   placeholder="DD/MM/YYYY">
                        </div>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">Age <span class="required-asterisk">*</span></label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-hash"></i></span>
                            <input type="number" class="form-control" id="editAge"
                                   value="${escapeHtml(String(r.UPDATE_AGE || ''))}"
                                   min="0" max="17">
                            <span class="input-group-text">years</span>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <label class="form-label">Birth Place <span class="required-asterisk">*</span></label>
                        <input type="text" class="form-control" id="editBirthPlace"
                               value="${escapeHtml(r.BIRTH_PLACE || '')}"
                               style="text-transform:uppercase;"
                               oninput="this.value=this.value.toUpperCase();">
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Religion/Cast <span class="required-asterisk">*</span></label>
                        <input type="text" class="form-control" id="editCast"
                               value="${escapeHtml(r.CAST_UPDATE || '')}"
                               style="text-transform:uppercase;"
                               oninput="this.value=this.value.toUpperCase();">
                    </div>

                </div>
            </div>
        `;

    } else {
        // ============================================================
        // MAJOR & RELIGION TEMPLATES - Personal Details
        // ============================================================
        html += `
            <div class="form-section">
                <div class="section-header">
                    <div class="section-icon"><i class="bi bi-person-fill"></i></div>
                    <h6 class="section-title">Personal Details</h6>
                </div>
                <div class="row g-3">

                    <!-- Old Name with Alias -->
                    <div class="col-md-6">
                        <label class="form-label">
                            Old Name <span class="required-asterisk">*</span>
                            <small class="text-muted">(+alias)</small>
                        </label>
                        <div style="display:flex; gap:0.5rem; align-items:flex-start;">
                            <div class="input-group flex-grow-1">
                                <span class="input-group-text"><i class="bi bi-person"></i></span>
                                <input type="text" class="form-control" id="editOldName"
                                       value="${escapeHtml(parsedBaseName)}"
                                       style="text-transform:uppercase;"
                                       oninput="this.value=this.value.toUpperCase();
                                                updateDashAliasPreview();">
                            </div>
                            <button type="button"
                                    title="Add Alias"
                                    onclick="addDashAliasField()"
                                    style="background:linear-gradient(135deg,#1a1a1a 0%,#444 100%);
                                           border:none; color:white; padding:0;
                                           border-radius:8px; width:42px; height:42px;
                                           min-width:42px; display:flex; align-items:center;
                                           justify-content:center; cursor:pointer;
                                           flex-shrink:0; transition:all 0.2s ease;"
                                    onmouseover="this.style.opacity='0.85'"
                                    onmouseout="this.style.opacity='1'">
                                <i class="bi bi-plus-lg"></i>
                            </button>
                        </div>

                        <div id="editAliasContainer" style="margin-top:0.5rem;"></div>

                        <div id="editAliasCounter"
                             style="display:none; margin-top:0.5rem; padding:0.35rem 0.65rem;
                                    background:#f8f9fa; border-radius:6px;
                                    font-size:0.75rem; color:#6c757d;">
                            <i class="bi bi-tags me-1"></i>Aliases: <span class="count">0</span>
                        </div>

                        <div id="editAliasPreview"
                             style="display:none; margin-top:0.75rem; padding:0.75rem;
                                    background:#f8f9fa; border-radius:8px;
                                    border:1px solid #dee2e6;">
                            <div style="font-size:0.75rem; font-weight:600; color:#6c757d;
                                        margin-bottom:0.5rem; text-transform:uppercase;
                                        letter-spacing:0.3px;">
                                <i class="bi bi-eye me-1"></i>Preview:
                            </div>
                            <div id="editAliasPreviewText" style="word-break:break-word;"></div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">New Name</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-person-check"></i></span>
                            <input type="text" class="form-control" id="editNewName"
                                   value="${escapeHtml(r.NEW_NAME || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Relation</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-people"></i></span>
                            <select class="form-select" id="editRelation"
                                    onchange="handleEditRelationChange()">
                                <option value="">Select...</option>
                                <option value="S/o" ${relation === 'S/o' ? 'selected' : ''}>
                                    S/o (Son of)
                                </option>
                                <option value="D/o" ${relation === 'D/o' ? 'selected' : ''}>
                                    D/o (Daughter of)
                                </option>
                                <option value="W/o" ${relation === 'W/o' ? 'selected' : ''}>
                                    W/o (Wife of)
                                </option>
                            </select>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Father/Spouse Name</label>
                        <div class="input-group">
                            <span class="input-group-text"><i class="bi bi-person-heart"></i></span>
                            <input type="text" class="form-control" id="editFatherSpouse"
                                   value="${escapeHtml(r['FATHER-SPOUSE_NAME'] || '')}"
                                   style="text-transform:uppercase;"
                                   oninput="this.value=this.value.toUpperCase();">
                        </div>
                    </div>

                    <!-- Dual Relation (D/o & W/o) -->
                    <div class="col-12" id="dualRelationContainer"
                         style="display:${hasSpouse || relation === 'D/o' ? 'block' : 'none'};">
                        <div class="dual-relation-card">
                            <div class="card-header">
                                <i class="bi bi-heart-fill me-2"></i>
                                D/o & W/o - Additional Spouse Details
                            </div>
                            <div class="card-body p-3">
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <label class="form-label">Spouse Name</label>
                                        <input type="text" class="form-control" id="editSpouseName1"
                                               value="${escapeHtml(r.SPOUSE_NAME1 || '')}"
                                               style="text-transform:uppercase;"
                                               oninput="this.value=this.value.toUpperCase();">
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-check mt-4">
                                            <input class="form-check-input" type="checkbox"
                                                   id="editHasSpouse"
                                                   ${hasSpouse ? 'checked' : ''}
                                                   onchange="toggleSpouseFields()">
                                            <label class="form-check-label" for="editHasSpouse">
                                                Include W/o (Wife of) in document
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Gender</label>
                        <select class="form-select" id="editGender">
                            <option value="">Select...</option>
                            <option value="MALE"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'MALE' ? 'selected' : ''}>
                                Male
                            </option>
                            <option value="FEMALE"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'FEMALE' ? 'selected' : ''}>
                                Female
                            </option>
                            <option value="OTHER"
                                ${(r.GENDER_UPDATE || '').toUpperCase() === 'OTHER' ? 'selected' : ''}>
                                Other
                            </option>
                        </select>
                    </div>

                    <div class="col-md-6">
                        <label class="form-label">Religion/Cast</label>
                        <input type="text" class="form-control" id="editCast"
                               value="${escapeHtml(r.CAST_UPDATE || '')}"
                               style="text-transform:uppercase;"
                               oninput="this.value=this.value.toUpperCase();">
                    </div>

                </div>
            </div>
        `;
    }

    // ── Contact Details ─────────────────────────────────────────
    html += `
        <div class="form-section">
            <div class="section-header">
                <div class="section-icon"><i class="bi bi-telephone-fill"></i></div>
                <h6 class="section-title">Contact Details</h6>
            </div>
            <div class="row g-3">
                ${draft.template_type !== 'minor_template' ? `
                <div class="col-md-6">
                    <label class="form-label">Phone Number</label>
                    <input type="tel" class="form-control" id="editPhone"
                           value="${escapeHtml(r.PHONE_UPDATE || '')}" maxlength="10">
                </div>
                <div class="col-md-6">
                    <label class="form-label">Email</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                        <input type="text" class="form-control" id="editEmail"
                               value="${escapeHtml(r.EMAIL_UPDATE || '')}">
                    </div>
                </div>
                <div class="col-12">
                    <label class="form-label">Address</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-house"></i></span>
                        <textarea class="form-control" id="editAddress" rows="2"
                                  style="text-transform:uppercase;"
                                  oninput="this.value=this.value.toUpperCase();"
                        >${escapeHtml(r.UPDATE_ADDRESS || '')}</textarea>
                    </div>
                </div>
                ` : `
                <div class="col-12">
                    <div class="alert alert-info py-2 mb-0">
                        <i class="bi bi-info-circle me-2"></i>
                        Phone, Email and Address are managed in the
                        <strong>Parent / Guardian Details</strong> section above.
                    </div>
                </div>
                `}
            </div>
        </div>
    `;

    // ── Date Details ────────────────────────────────────────────
    html += `
        <div class="form-section">
            <div class="section-header">
                <div class="section-icon"><i class="bi bi-calendar-event"></i></div>
                <h6 class="section-title">Date Details</h6>
            </div>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Numeric Date</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-calendar"></i></span>
                        <input type="text" class="form-control" id="editNumDate"
                               value="${escapeHtml(r.NUM_DATE || '')}"
                               placeholder="DD/MM/YYYY">
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Alpha Date</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-calendar2-check"></i></span>
                        <input type="text" class="form-control" id="editAlphaDate"
                               value="${escapeHtml(r.ALPHA_DATE || '')}"
                               placeholder="1ST JANUARY 2025">
                    </div>
                </div>
            </div>
        </div>
    `;

    // ── Witness 1 ───────────────────────────────────────────────
    html += `
        <div class="form-section">
            <div class="section-header">
                <div class="section-icon"><i class="bi bi-person-badge"></i></div>
                <h6 class="section-title">Witness 1 Details</h6>
            </div>
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-control" id="editWitness1Name"
                           value="${escapeHtml(r.WITNESS_NAME1 || '')}"
                           style="text-transform:uppercase;"
                           oninput="this.value=this.value.toUpperCase();">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-control" id="editWitness1Phone"
                           value="${escapeHtml(r.WITNESS_PHONE1 || '')}" maxlength="10">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Address</label>
                    <input type="text" class="form-control" id="editWitness1Address"
                           value="${escapeHtml(r.WITNESS_ADDRESS1 || '')}"
                           style="text-transform:uppercase;"
                           oninput="this.value=this.value.toUpperCase();">
                </div>
            </div>
        </div>
    `;

    // ── Witness 2 ───────────────────────────────────────────────
    html += `
        <div class="form-section">
            <div class="section-header">
                <div class="section-icon"><i class="bi bi-person-badge-fill"></i></div>
                <h6 class="section-title">Witness 2 Details</h6>
            </div>
            <div class="row g-3">
                <div class="col-md-4">
                    <label class="form-label">Name</label>
                    <input type="text" class="form-control" id="editWitness2Name"
                           value="${escapeHtml(r.WITNESS_NAME2 || '')}"
                           style="text-transform:uppercase;"
                           oninput="this.value=this.value.toUpperCase();">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-control" id="editWitness2Phone"
                           value="${escapeHtml(r.WITNESS_PHONE2 || '')}" maxlength="10">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Address</label>
                    <input type="text" class="form-control" id="editWitness2Address"
                           value="${escapeHtml(r.WITNESS_ADDRESS2 || '')}"
                           style="text-transform:uppercase;"
                           oninput="this.value=this.value.toUpperCase();">
                </div>
            </div>
        </div>
    `;

    // ── Folder Type (major & religion only) ─────────────────────
    if (draft.template_type === 'major_template' ||
        draft.template_type === 'religion_template') {
        html += `
            <div class="form-section">
                <div class="section-header">
                    <div class="section-icon"><i class="bi bi-folder"></i></div>
                    <h6 class="section-title">Template Folder</h6>
                </div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="form-label">Folder Type</label>
                        <select class="form-select" id="editFolderType">
                            <option value="main"
                                ${folderType === 'main' ? 'selected' : ''}>
                                Main Template
                            </option>
                            <option value="unmarried"
                                ${folderType === 'unmarried' ? 'selected' : ''}>
                                Unmarried Template
                            </option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }

    return html;
}

function handleEditRelationChange() {
    const relation = document.getElementById('editRelation').value;
    const container = document.getElementById('dualRelationContainer');

    if (relation === 'D/o' && container) {
        container.style.display = 'block';
    } else if (container) {
        container.style.display = 'none';
        // Clear spouse fields when hiding
        const spouseInput = document.getElementById('editSpouseName1');
        const hasSpouseCheck = document.getElementById('editHasSpouse');
        if (spouseInput) spouseInput.value = '';
        if (hasSpouseCheck) hasSpouseCheck.checked = false;
    }
}

function handleMinorRelationChangeDash() {
    const relation = document.getElementById('editRelation')?.value;
    const normalField = document.getElementById('editMinorNormalSpouseField');
    const dualField = document.getElementById('editMinorDualRelationFields');
    const spouseInput = document.getElementById('editFatherSpouse');

    if (relation === 'D/o & W/o') {
        if (normalField) normalField.style.display = 'none';
        if (dualField) dualField.style.display = 'block';
        if (spouseInput) spouseInput.value = '';
    } else {
        if (normalField) normalField.style.display = 'block';
        if (dualField) dualField.style.display = 'none';
        const guardianFather = document.getElementById('editGuardianFather');
        const guardianSpouse = document.getElementById('editGuardianSpouse');
        if (guardianFather) guardianFather.value = '';
        if (guardianSpouse) guardianSpouse.value = '';
    }
}

function toggleSpouseFields() {
    const hasSpouse = document.getElementById('editHasSpouse').checked;
    const spouseInput = document.getElementById('editSpouseName1');

    if (!hasSpouse && spouseInput) {
        spouseInput.value = '';
    }
}

function refreshCdPreviewFromForm() {
    if (currentEditDraftId) {
        loadCDPreview(currentEditDraftId, 'editCdContent');
        showToast('Info', 'Preview refreshed. Save changes first to see updates.', 'info');
    }
}

// ==================== SAVE DRAFT (NO AUTO CLOSE - REFRESH PREVIEW) ====================

async function saveDraftChanges() {
    const draftId = document.getElementById('editDraftId').value;
    const draft = allDrafts.find(d => d.id === draftId);
    if (!draft) return;

    const saveBtn = document.querySelector('#editDraftModal .modal-footer .btn-primary');
    const originalBtnText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
    saveBtn.disabled = true;

    // ── Build OLD_NAME with aliases ────────────────────────────
    const replacements = {
        OLD_NAME: buildDashboardOldNameWithAliases(),
        NEW_NAME: document.getElementById('editNewName')?.value.toUpperCase().trim() || '',
        UPDATE_RELATION: document.getElementById('editRelation')?.value || '',
        GENDER_UPDATE: document.getElementById('editGender')?.value || '',
        PHONE_UPDATE: document.getElementById('editPhone')?.value.trim() || '',
        EMAIL_UPDATE: document.getElementById('editEmail')?.value.trim() || '',
        UPDATE_ADDRESS: document.getElementById('editAddress')?.value.toUpperCase().trim() || '',
        NUM_DATE: document.getElementById('editNumDate')?.value.trim() || '',
        ALPHA_DATE: document.getElementById('editAlphaDate')?.value.trim() || '',
        WITNESS_NAME1: document.getElementById('editWitness1Name')?.value.toUpperCase().trim() || '',
        WITNESS_PHONE1: document.getElementById('editWitness1Phone')?.value.trim() || '',
        WITNESS_ADDRESS1: document.getElementById('editWitness1Address')?.value.toUpperCase().trim() || '',
        WITNESS_NAME2: document.getElementById('editWitness2Name')?.value.toUpperCase().trim() || '',
        WITNESS_PHONE2: document.getElementById('editWitness2Phone')?.value.trim() || '',
        WITNESS_ADDRESS2: document.getElementById('editWitness2Address')?.value.toUpperCase().trim() || ''
    };

    // ── Minor template ─────────────────────────────────────────
    if (draft.template_type === 'minor_template') {
        // Guardian fields
        replacements['FATHER-MOTHER_NAME'] =
            document.getElementById('editFatherMother')?.value.toUpperCase().trim() || '';

        const minorRelation = document.getElementById('editRelation')?.value || '';
        replacements.UPDATE_RELATION = minorRelation;

        if (minorRelation === 'D/o & W/o') {
            replacements.GUARDIAN_FATHER_NAME =
                document.getElementById('editGuardianFather')?.value.toUpperCase().trim() || '';
            replacements.GUARDIAN_SPOUSE_NAME =
                document.getElementById('editGuardianSpouse')?.value.toUpperCase().trim() || '';
            replacements['FATHER-SPOUSE_NAME'] = '';
        } else {
            replacements['FATHER-SPOUSE_NAME'] =
                document.getElementById('editFatherSpouse')?.value.toUpperCase().trim() || '';
        }

        // Child fields
        replacements['SON-DAUGHTER'] =
            (document.getElementById('editSonDaughter')?.value || '').toLowerCase().trim();
        replacements.UPDATE_AGE =
            document.getElementById('editAge')?.value || '';
        replacements.CHILD_DOB =
            document.getElementById('editChildDob')?.value || '';
        replacements.BIRTH_PLACE =
            document.getElementById('editBirthPlace')?.value.toUpperCase().trim() || '';
        replacements.CAST_UPDATE =
            document.getElementById('editCast')?.value.toUpperCase().trim() || '';

        // HE_SHE
        const sd = replacements['SON-DAUGHTER'];
        replacements.HE_SHE = sd === 'son' ? 'he' : sd === 'daughter' ? 'she' : 'he/she';

        // Clear spouse for non D/o & W/o
        if (minorRelation !== 'D/o & W/o') {
            replacements.WIFE_OF = '';
            replacements.SPOUSE_NAME1 = '';
        }

    } else {
        // ── Major & Religion ───────────────────────────────────
        replacements['FATHER-SPOUSE_NAME'] =
            document.getElementById('editFatherSpouse')?.value.toUpperCase().trim() || '';
        replacements.CAST_UPDATE =
            document.getElementById('editCast')?.value.toUpperCase().trim() || '';

        // Spouse fields
        const hasSpouseCheck = document.getElementById('editHasSpouse');
        const spouseName1El = document.getElementById('editSpouseName1');

        if (hasSpouseCheck?.checked && spouseName1El?.value.trim()) {
            replacements.WIFE_OF = ' W/o ';
            replacements.SPOUSE_NAME1 = spouseName1El.value.toUpperCase().trim();
        } else {
            replacements.WIFE_OF = '';
            replacements.SPOUSE_NAME1 = '';
        }

        // HE_SHE
        const gender = (replacements.GENDER_UPDATE || '').toUpperCase();
        replacements.HE_SHE = gender === 'MALE' ? 'he' : gender === 'FEMALE' ? 'she' : 'he/she';
    }

    const folderTypeEl = document.getElementById('editFolderType');
    const folderType = folderTypeEl ? folderTypeEl.value : 'main';

    try {
        const response = await fetch(`/api/drafts/${draftId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ replacements, folder_type: folderType })
        });

        const data = await response.json();

        saveBtn.innerHTML = originalBtnText;
        saveBtn.disabled = false;

        if (data.success) {
            showToast('Success', 'Draft saved! Preview updated.', 'success');

            // Update local data
            const draftIndex = allDrafts.findIndex(d => d.id === draftId);
            if (draftIndex !== -1) {
                allDrafts[draftIndex].replacements = replacements;
                allDrafts[draftIndex].old_name = replacements.OLD_NAME;
            }

            // Refresh CD preview WITHOUT closing modal
            loadCDPreview(draftId, 'editCdContent');
            loadDrafts();
            loadStats();

        } else {
            showToast('Error', data.message || 'Failed to save draft', 'error');
        }
    } catch (error) {
        saveBtn.innerHTML = originalBtnText;
        saveBtn.disabled = false;
        showToast('Error', 'Network error', 'error');
    }
}

// ==================== SUBMIT FOR APPROVAL ====================

async function submitForApproval(draftId) {
    if (!confirm('Submit this document for admin approval?')) return;

    try {
        const response = await fetch(`/api/drafts/${draftId}/submit-approval`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showToast('Success', 'Document submitted for approval!', 'success');
            loadDrafts();
            loadStats();
        } else {
            showToast('Error', data.message || 'Failed to submit', 'error');
        }
    } catch (error) {
        showToast('Error', 'Network error', 'error');
    }
}

// ==================== DELETE DRAFT ====================

function showDeleteModal(draftId) {
    deleteTargetId = draftId;
    const draft = allDrafts.find(d => d.id === draftId);

    document.getElementById('deleteDraftName').textContent = draft ? draft.old_name || 'Unnamed' : '';

    const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    modal.show();
}

async function confirmDelete() {
    if (!deleteTargetId) return;

    try {
        const response = await fetch(`/api/drafts/${deleteTargetId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Success', 'Draft deleted successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
            loadDrafts();
            loadStats();
        } else {
            showToast('Error', data.message || 'Failed to delete', 'error');
        }
    } catch (error) {
        showToast('Error', 'Network error', 'error');
    }

    deleteTargetId = null;
}

// ==================== EDIT PROFILE ====================

async function openEditProfile() {
    try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();

        if (data.success) {
            document.getElementById('profileName').value = data.user.name || '';
            document.getElementById('profileEmail').value = data.user.email || '';
            document.getElementById('profilePhone').value = data.user.phone || '';
            document.getElementById('profilePassword').value = '';

            const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            modal.show();
        } else {
            showToast('Error', 'Failed to load profile', 'error');
        }
    } catch (error) {
        showToast('Error', 'Network error', 'error');
    }
}

async function saveProfile() {
    const name = document.getElementById('profileName').value.trim();
    const email = document.getElementById('profileEmail').value.trim();
    const phone = document.getElementById('profilePhone').value.trim();
    const password = document.getElementById('profilePassword').value;

    if (!name || !email) {
        showToast('Error', 'Name and email are required', 'error');
        return;
    }

    try {
        const response = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password: password || undefined })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Success', 'Profile updated successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editProfileModal')).hide();

            // Update displayed name if changed
            const userNameEls = document.querySelectorAll('.user-dropdown .d-none.d-md-inline');
            userNameEls.forEach(el => el.textContent = name);
        } else {
            showToast('Error', data.message || 'Failed to update profile', 'error');
        }
    } catch (error) {
        showToast('Error', 'Network error', 'error');
    }
}

// ==================== TAB SWITCHING ====================

function switchTab(tabName) {
    const tabEl = document.getElementById(`${tabName}-tab`);
    if (tabEl) {
        const tab = new bootstrap.Tab(tabEl);
        tab.show();
    }
}

// ==================== UTILITY FUNCTIONS ====================

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// ==================== ALIAS HELPERS (DASHBOARD EDIT) ====================

function parseOldNameWithAliases(oldName) {
    if (!oldName) return { baseName: '', aliases: [] };
    const parts = oldName.split(/\s+alias\s+/i);
    return {
        baseName: parts[0].trim(),
        aliases: parts.slice(1).map(a => a.trim()).filter(Boolean)
    };
}

function buildDashboardOldNameWithAliases() {
    const baseInput = document.getElementById('editOldName');
    const container = document.getElementById('editAliasContainer');
    if (!baseInput) return '';

    const baseName = baseInput.value.trim().toUpperCase();
    if (!container) return baseName;

    const aliasInputs = container.querySelectorAll('.dash-alias-input');
    const aliases = [];
    aliasInputs.forEach(function (inp) {
        const v = inp.value.trim().toUpperCase();
        if (v) aliases.push(v);
    });

    if (aliases.length === 0) return baseName;
    return baseName + ' alias ' + aliases.join(' alias ');
}

let dashAliasCounter = 0;

function addDashAliasField(existingValue) {
    dashAliasCounter++;
    const container = document.getElementById('editAliasContainer');
    if (!container) return;

    const n = dashAliasCounter;
    const wrapper = document.createElement('div');
    wrapper.className = 'alias-field-wrapper';
    wrapper.id = 'dash_alias_item_' + n;
    wrapper.style.cssText = 'display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; animation: slideDown 0.3s ease;';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control dash-alias-input';
    input.placeholder = 'Alias ' + n;
    input.value = existingValue ? existingValue.toUpperCase() : '';
    input.style.textTransform = 'uppercase';
    input.setAttribute('oninput', 'this.value=this.value.toUpperCase(); updateDashAliasPreview();');

    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.title = 'Remove Alias';
    deleteBtn.style.cssText = `
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        border: none;
        color: white;
        padding: 0;
        border-radius: 8px;
        width: 38px;
        height: 38px;
        min-width: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        flex-shrink: 0;
    `;
    deleteBtn.innerHTML = '<i class="bi bi-trash3"></i>';
    deleteBtn.setAttribute('onclick', 'removeDashAliasField(' + n + ')');

    wrapper.appendChild(input);
    wrapper.appendChild(deleteBtn);
    container.appendChild(wrapper);

    updateDashAliasCounter();
    updateDashAliasPreview();

    if (!existingValue) input.focus();
}

function removeDashAliasField(n) {
    const el = document.getElementById('dash_alias_item_' + n);
    if (el) {
        el.remove();
        updateDashAliasCounter();
        updateDashAliasPreview();
    }
}

function updateDashAliasCounter() {
    const container = document.getElementById('editAliasContainer');
    const counter = document.getElementById('editAliasCounter');
    if (!container || !counter) return;

    const count = container.querySelectorAll('.alias-field-wrapper').length;
    if (count > 0) {
        counter.style.display = 'inline-block';
        const span = counter.querySelector('.count');
        if (span) span.textContent = count;
    } else {
        counter.style.display = 'none';
    }
}

function updateDashAliasPreview() {
    const baseInput = document.getElementById('editOldName');
    const container = document.getElementById('editAliasContainer');
    const preview = document.getElementById('editAliasPreview');
    const previewText = document.getElementById('editAliasPreviewText');

    if (!baseInput || !container || !preview || !previewText) return;

    const baseName = baseInput.value.trim().toUpperCase();
    const aliasInputs = container.querySelectorAll('.dash-alias-input');

    let html = '<span style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:0.25rem 0.5rem;border-radius:6px;display:inline-block;margin:0.25rem;font-weight:600;">'
        + (escapeHtml(baseName) || 'NAME') + '</span>';

    let hasAlias = false;
    aliasInputs.forEach(function (inp) {
        const v = inp.value.trim().toUpperCase();
        if (v) {
            hasAlias = true;
            html += '<span style="color:#6c757d;font-style:italic;font-weight:500;margin:0 0.25rem;">alias</span>'
                + '<span style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:0.25rem 0.5rem;border-radius:6px;display:inline-block;margin:0.25rem;font-weight:600;">'
                + escapeHtml(v) + '</span>';
        }
    });

    if (baseName || hasAlias) {
        preview.style.display = 'block';
        previewText.innerHTML = html;
    } else {
        preview.style.display = 'none';
    }
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return dateString;
    }
}

function logout() {
    fetch('/api/auth/logout', { method: 'POST' })
        .then(() => {
            window.location.href = '/';
        })
        .catch(() => {
            window.location.href = '/';
        });
}
