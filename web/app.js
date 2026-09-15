// ==========================================================================
// AGENT SKILLS HUB — APPLICATION LOGIC
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  const skillsData = window.SKILLS_DATA || [];
  
  // State
  let searchQuery = '';
  let selectedBranch = 'all';
  let filterUserInvoked = true;
  let filterModelInvoked = true;
  let activePhaseTab = '1. Discovery & Planning';

  // DOM Elements
  const searchInput = document.getElementById('globalSearchInput');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const categoryPills = document.getElementById('categoryFilterPills');
  const checkboxUser = document.getElementById('filterUserInvoked');
  const checkboxModel = document.getElementById('filterModelInvoked');
  const skillsGrid = document.getElementById('skillsGrid');
  const skillsCountTag = document.getElementById('skillsCountTag');
  const noResultsBox = document.getElementById('noResultsBox');
  const resetFiltersBtn = document.getElementById('resetFiltersBtn');
  
  const workflowTabs = document.getElementById('workflowTabs');
  const workflowDetailBox = document.getElementById('workflowDetailBox');
  const scenariosGrid = document.getElementById('scenariosGrid');
  const recommendationResult = document.getElementById('recommendationResult');

  const modalBackdrop = document.getElementById('modalBackdrop');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalFooterCloseBtn = document.getElementById('modalFooterCloseBtn');
  const modalTitle = document.getElementById('modalTitle');
  const modalDesc = document.getElementById('modalDesc');
  const modalCategoryBadge = document.getElementById('modalCategoryBadge');
  const modalTypeBadge = document.getElementById('modalTypeBadge');
  const modalPhaseBadge = document.getElementById('modalPhaseBadge');
  const modalTriggerCode = document.getElementById('modalTriggerCode');
  const modalCopyTriggerBtn = document.getElementById('modalCopyTriggerBtn');
  const modalFilePath = document.getElementById('modalFilePath');
  const modalMarkdownContent = document.getElementById('modalMarkdownContent');
  const modalCopyFullBtn = document.getElementById('modalCopyFullBtn');
  const toastContainer = document.getElementById('toastContainer');

  let currentModalSkill = null;

  // 1. PHASES CONFIGURATION DATA
  const phasesMeta = {
    '1. Discovery & Planning': {
      title: 'Giai đoạn 1: Làm Rõ Ý Tưởng & Đặc Tả Kỹ Thuật',
      desc: 'Ngăn chặn sai lầm phổ biến nhất trong phát triển AI: hiểu nhầm yêu cầu và bịa đặt tính năng. Ép agent phỏng vấn bạn chi tiết trước khi code.',
      combo: 'Combo Khuyên Dùng: /grill-with-docs ➔ /to-spec ➔ /to-tickets',
      keySkills: ['grill-with-docs', 'to-spec', 'to-tickets', 'wayfinder', 'domain-modeling', 'ask-matt', 'project-blueprint-loop-architect']
    },
    '2. Architecture & Design': {
      title: 'Giai đoạn 2: Thiết Kế Kiến Trúc & Tạo Bộ Khung',
      desc: 'Xây dựng các module sâu (Deep Modules) với giao diện tối giản nhưng xử lý nghiệp vụ mạnh mẽ, tránh tình trạng code biến thành "đống bùn lầy".',
      combo: 'Combo Khuyên Dùng: fullstack-boilerplate-architect ➔ codebase-design ➔ prototype',
      keySkills: ['codebase-design', 'fullstack-boilerplate-architect', 'workflow-node-studio', 'prototype', 'improve-codebase-architecture']
    },
    '3. Implementation & TDD': {
      title: 'Giai đoạn 3: Lập Trình & Kiểm Thử TDD',
      desc: 'Vòng lặp đỏ-xanh-tối ưu (Red-Green-Refactor). Ép agent viết test thất bại trước khi viết code, giúp từng lát cắt tính năng đạt độ tin cậy tuyệt đối.',
      combo: 'Combo Khuyên Dùng: implement ➔ tdd ➔ claude-task-runner',
      keySkills: ['implement', 'tdd', 'claude-task-runner', 'implement-spec', 'writing-for-agents']
    },
    '4. Review & Quality Guardrails': {
      title: 'Giai đoạn 4: Rà Soát & Kiểm Soát Ngân Sách Mã Nguồn',
      desc: 'Bảo vệ mã nguồn khỏi tình trạng phình to mất kiểm soát. Hai agent độc lập song song kiểm tra Chuẩn Coding và Tính Đúng Đắn.',
      combo: 'Combo Khuyên Dùng: codebase-line-budget-guard ➔ code-review ➔ resolving-merge-conflicts',
      keySkills: ['codebase-line-budget-guard', 'code-review', 'resolving-merge-conflicts', 'setup-pre-commit', 'handoff']
    },
    '5. Debugging & Recovery': {
      title: 'Giai đoạn 5: Cứu Hộ Agent & Gỡ Lỗi Chuyên Sâu',
      desc: 'Cứu hộ khẩn cấp khi agent bị lặp vòng vô tận, mất phương hướng sau khi context bị nén, hoặc gỡ các ca bug hệ thống nan giải.',
      combo: 'Combo Khuyên Dùng: agent-disorientation-recovery ➔ diagnosing-bugs ➔ code-bug-inspector',
      keySkills: ['agent-disorientation-recovery', 'code-bug-inspector', 'diagnosing-bugs', 'system-logs-and-diagnostics', 'triage']
    },
    '6. Setup & Operations': {
      title: 'Giai đoạn 6: Thiết Lập Môi Trường & Đóng Gói Vận Hành',
      desc: 'Cấu hình hệ thống Multi-Agent AI tối ưu cho Apple Silicon (M1/M2/M3/M4) hoặc đa nền tảng, tạo wizard tự động và đóng gói Chrome Extension.',
      combo: 'Combo Khuyên Dùng: macos-m1-multiagent-setup ➔ wizard ➔ chrome-web-store-prep',
      keySkills: ['macos-m1-multiagent-setup', 'multiagent-setup-crossplatform', 'chrome-web-store-prep', 'wizard', 'setup-matt-pocock-skills']
    }
  };

  // 2. SCENARIO RECOMMENDER DATA
  const scenarios = [
    {
      icon: '💡',
      text: 'Tôi có ý tưởng mới, muốn Agent tra hỏi làm rõ mọi khía cạnh',
      skillId: 'grill-with-docs',
      prompt: '/grill-with-docs Hãy phỏng vấn tôi về tính năng mới này'
    },
    {
      icon: '📋',
      text: 'Chuyển toàn bộ cuộc hội thoại vừa rồi thành file Spec kỹ thuật',
      skillId: 'to-spec',
      prompt: '/to-spec'
    },
    {
      icon: '🎯',
      text: 'Cắt nhỏ kế hoạch thành các ticket độc lập có thứ tự ưu tiên',
      skillId: 'to-tickets',
      prompt: '/to-tickets'
    },
    {
      icon: '🏗️',
      text: 'Khởi tạo dự án Fullstack Web chuẩn kiến trúc Clean Architecture',
      skillId: 'fullstack-boilerplate-architect',
      prompt: 'Áp dụng skill fullstack-boilerplate-architect để dựng khung dự án'
    },
    {
      icon: '🧪',
      text: 'Muốn viết code chất lượng cao theo phương pháp TDD (Test-First)',
      skillId: 'tdd',
      prompt: 'Áp dụng quy trình tdd: viết test đỏ trước rồi mới implement'
    },
    {
      icon: '📏',
      text: 'File code dài quá (trên 300-500 dòng), cần kiểm soát độ phình',
      skillId: 'codebase-line-budget-guard',
      prompt: 'Kích hoạt codebase-line-budget-guard rà soát và chia nhỏ file'
    },
    {
      icon: '🔍',
      text: 'Rà soát kỹ lưỡng (Review) toàn bộ code vừa viết trước khi commit',
      skillId: 'code-review',
      prompt: '/code-review Soát xét các thay đổi so với nhánh main'
    },
    {
      icon: '🚨',
      text: 'Agent bị lú / ngáo / lặp vòng xoáy sửa chỗ này hỏng chỗ kia',
      skillId: 'agent-disorientation-recovery',
      prompt: 'Kích hoạt agent-disorientation-recovery: dừng lại, kiểm tra trạng thái và lập kế hoạch phẫu thuật'
    },
    {
      icon: '🎛️',
      text: 'Thiết kế giao diện Studio dạng canvas và kéo thả Node với React Flow',
      skillId: 'workflow-node-studio',
      prompt: 'Áp dụng workflow-node-studio hướng dẫn thiết kế custom node trên React Flow'
    },
    {
      icon: '🚀',
      text: 'Chuẩn bị nộp extension lên Chrome Web Store duyệt lần đầu ăn ngay',
      skillId: 'chrome-web-store-prep',
      prompt: 'Kích hoạt chrome-web-store-prep rà soát manifest, icon, quyền hạn và privacy policy'
    }
  ];

  // 3. TOAST HELPER
  function showToast(message, icon = '✓') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 2400);
  }

  // 4. RENDER WORKFLOW DETAIL BOX
  function renderWorkflowDetail(phaseKey) {
    const meta = phasesMeta[phaseKey];
    if (!meta) return;

    const skillsInPhase = skillsData.filter(s => meta.keySkills.includes(s.id));

    workflowDetailBox.innerHTML = `
      <div class="wf-box-header">
        <div>
          <h3 class="wf-box-title">${meta.title}</h3>
          <p class="wf-box-sub">${meta.desc}</p>
        </div>
        <span class="wf-combo-tag">${meta.combo}</span>
      </div>
      <div>
        <div style="font-size: 12px; font-weight: 700; color: var(--text-dim); text-transform: uppercase;">
          Các kỹ năng then chốt trong giai đoạn này:
        </div>
        <div class="wf-skills-chips">
          ${skillsInPhase.map(s => `
            <div class="wf-skill-chip" data-skill-id="${s.id}">
              <span>⚡ ${s.name}</span>
              <span class="chip-type">${s.userInvoked ? 'User' : 'Model'}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    workflowDetailBox.querySelectorAll('.wf-skill-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const id = chip.getAttribute('data-skill-id');
        openSkillModal(id);
      });
    });
  }

  // 5. RENDER RECOMMENDER SCENARIOS
  function renderScenarios() {
    scenariosGrid.innerHTML = scenarios.map((sc, index) => `
      <button class="scenario-btn" data-index="${index}">
        <span class="scenario-icon">${sc.icon}</span>
        <span>${sc.text}</span>
      </button>
    `).join('');

    scenariosGrid.querySelectorAll('.scenario-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        scenariosGrid.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const index = parseInt(btn.getAttribute('data-index'), 10);
        showRecommendation(scenarios[index]);
      });
    });
  }

  function showRecommendation(scenario) {
    const targetSkill = skillsData.find(s => s.id === scenario.skillId);
    recommendationResult.style.display = 'flex';
    recommendationResult.innerHTML = `
      <div class="rec-title-row">
        <div>
          <span style="font-size: 12px; color: var(--text-dim); text-transform: uppercase; font-weight: 700;">Đề xuất tối ưu:</span>
          <div class="rec-skill-name">⚡ ${targetSkill ? targetSkill.name : scenario.skillId}</div>
        </div>
        <button class="btn btn-secondary" id="recViewSkillBtn">Xem chi tiết skill</button>
      </div>
      <p style="font-size: 14px; color: var(--text-muted);">${targetSkill ? targetSkill.description : ''}</p>
      <div>
        <div style="font-size: 12px; font-weight: 700; color: var(--text-dim); margin-bottom: 6px;">Câu lệnh / Prompt gợi ý copy vào Chat:</div>
        <div class="rec-prompt-box">
          <code>${scenario.prompt}</code>
          <button class="btn-copy-code" id="recCopyPromptBtn">Sao chép</button>
        </div>
      </div>
    `;

    document.getElementById('recCopyPromptBtn').addEventListener('click', () => {
      navigator.clipboard.writeText(scenario.prompt);
      showToast('Đã sao chép prompt gợi ý!');
    });

    document.getElementById('recViewSkillBtn').addEventListener('click', () => {
      openSkillModal(scenario.skillId);
    });
  }

  // 6. FILTER AND RENDER SKILLS GRID
  function filterAndRenderSkills() {
    const q = searchQuery.toLowerCase().trim();

    const filtered = skillsData.filter(s => {
      // Branch filter
      if (selectedBranch !== 'all' && s.branch !== selectedBranch) {
        return false;
      }

      // Invocation filter
      if (s.userInvoked && !filterUserInvoked) return false;
      if (!s.userInvoked && !filterModelInvoked) return false;

      // Search query
      if (q) {
        const matchName = s.name.toLowerCase().includes(q);
        const matchId = s.id.toLowerCase().includes(q);
        const matchDesc = s.description.toLowerCase().includes(q);
        const matchBranch = (s.branch || '').toLowerCase().includes(q);
        const matchViWhat = s.vi && s.vi.what ? s.vi.what.toLowerCase().includes(q) : false;
        const matchViWhen = s.vi && s.vi.when ? s.vi.when.toLowerCase().includes(q) : false;
        if (!matchName && !matchId && !matchDesc && !matchBranch && !matchViWhat && !matchViWhen) return false;
      }

      return true;
    });

    skillsCountTag.textContent = `Đang hiển thị ${filtered.length} / ${skillsData.length} skills`;

    if (filtered.length === 0) {
      skillsGrid.style.display = 'none';
      noResultsBox.style.display = 'block';
    } else {
      skillsGrid.style.display = 'grid';
      noResultsBox.style.display = 'none';

      skillsGrid.innerHTML = filtered.map(s => {
        const triggerText = s.userInvoked ? `/${s.id}` : `Áp dụng skill ${s.id}`;
        const viWhat = s.vi && s.vi.what ? s.vi.what : s.description;
        return `
          <div class="skill-card" data-skill-id="${s.id}">
            <div class="card-top">
              <div class="card-badges">
                <span class="badge badge-category">${s.branch}</span>
                <span class="badge ${s.userInvoked ? 'badge-user-invoked' : 'badge-model-invoked'}">
                  ${s.userInvoked ? '⚡ User-invoked' : '🤖 Model-invoked'}
                </span>
              </div>
              <h3 class="card-title">${s.name}</h3>
              <p class="card-desc">${s.description}</p>
              
              <!-- Vietnamese Plain Explanation -->
              <div class="card-vi-box">
                <div class="card-vi-label">
                  <span>🇻🇳 Dễ hiểu:</span>
                </div>
                <div class="card-vi-text">${viWhat}</div>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn-card-copy" data-copy="${triggerText}" title="Copy lệnh kích hoạt">
                Sao chép lệnh
              </button>
              <button class="btn-card-view" data-view="${s.id}">
                Chi tiết ➔
              </button>
            </div>
          </div>
        `;
      }).join('');

      // Attach card listeners
      skillsGrid.querySelectorAll('.btn-card-copy').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const text = btn.getAttribute('data-copy');
          navigator.clipboard.writeText(text);
          showToast(`Đã sao chép: ${text}`);
        });
      });

      skillsGrid.querySelectorAll('.btn-card-view, .skill-card').forEach(el => {
        el.addEventListener('click', (e) => {
          if (e.target.classList.contains('btn-card-copy')) return;
          const card = el.closest('.skill-card');
          if (card) {
            const id = card.getAttribute('data-skill-id');
            openSkillModal(id);
          }
        });
      });
    }
  }

  // 7. MODAL DRAWER LOGIC
  function openSkillModal(skillId) {
    const skill = skillsData.find(s => s.id === skillId);
    if (!skill) return;

    currentModalSkill = skill;
    modalTitle.textContent = skill.name;
    modalDesc.textContent = skill.description;
    modalCategoryBadge.textContent = skill.category.toUpperCase();
    modalTypeBadge.textContent = skill.userInvoked ? 'User-invoked (Lệnh gõ tay)' : 'Model-invoked (Tự động)';
    modalPhaseBadge.textContent = skill.branch || 'Chung';

    // Populate Vietnamese explanation
    if (skill.vi) {
      document.getElementById('modalViWhat').textContent = skill.vi.what;
      document.getElementById('modalViWhen').textContent = skill.vi.when;
      document.getElementById('modalViBenefit').textContent = skill.vi.benefit;
    } else {
      document.getElementById('modalViWhat').textContent = skill.description;
      document.getElementById('modalViWhen').textContent = 'Dùng khi cần.';
      document.getElementById('modalViBenefit').textContent = 'Nâng cao chất lượng dự án.';
    }

    const trigger = skill.userInvoked ? `/${skill.id}` : `Áp dụng skill ${skill.id}`;
    modalTriggerCode.textContent = trigger;
    modalFilePath.textContent = skill.path;
    modalMarkdownContent.textContent = skill.content || 'Không có mô tả chi tiết.';

    modalBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modalBackdrop.classList.remove('open');
    document.body.style.overflow = '';
  }

  modalCloseBtn.addEventListener('click', closeModal);
  modalFooterCloseBtn.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
  });

  modalCopyTriggerBtn.addEventListener('click', () => {
    if (currentModalSkill) {
      const trigger = currentModalSkill.userInvoked ? `/${currentModalSkill.id}` : `Áp dụng skill ${currentModalSkill.id}`;
      navigator.clipboard.writeText(trigger);
      showToast('Đã sao chép lệnh kích hoạt!');
    }
  });

  modalCopyFullBtn.addEventListener('click', () => {
    if (currentModalSkill) {
      navigator.clipboard.writeText(currentModalSkill.content);
      showToast('Đã sao chép toàn bộ nội dung SKILL.md!');
    }
  });

  // 8. EVENT LISTENERS
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    clearSearchBtn.style.display = searchQuery ? 'block' : 'none';
    filterAndRenderSkills();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearchBtn.style.display = 'none';
    filterAndRenderSkills();
    searchInput.focus();
  });

  categoryPills.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      categoryPills.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      selectedBranch = pill.getAttribute('data-branch') || 'all';
      filterAndRenderSkills();
    });
  });

  checkboxUser.addEventListener('change', (e) => {
    filterUserInvoked = e.target.checked;
    filterAndRenderSkills();
  });

  checkboxModel.addEventListener('change', (e) => {
    filterModelInvoked = e.target.checked;
    filterAndRenderSkills();
  });

  resetFiltersBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearchBtn.style.display = 'none';
    selectedBranch = 'all';
    categoryPills.querySelectorAll('.filter-pill').forEach(p => {
      p.classList.toggle('active', p.getAttribute('data-branch') === 'all');
    });
    checkboxUser.checked = true;
    checkboxModel.checked = true;
    filterUserInvoked = true;
    filterModelInvoked = true;
    filterAndRenderSkills();
  });

  workflowTabs.querySelectorAll('.workflow-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      workflowTabs.querySelectorAll('.workflow-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activePhaseTab = tab.getAttribute('data-phase');
      renderWorkflowDetail(activePhaseTab);
    });
  });

  // 9. INITIALIZE
  renderWorkflowDetail(activePhaseTab);
  renderScenarios();
  filterAndRenderSkills();
});
