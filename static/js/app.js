// 全局变量
let currentProjectId = null;
let currentProjectPath = null;
let currentFile = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    loadProjects();
    checkCurrentProject();
});

// 导航功能
function initNavigation() {
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            showPage(page);
            
            // 更新活动状态
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showPage(pageName) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示目标页面
    const targetPage = document.getElementById(pageName + 'Page');
    if (targetPage) {
        targetPage.classList.add('active');
        
        // 根据页面加载数据
        switch(pageName) {
            case 'projects':
                loadProjects();
                break;
            case 'settings':
                if (currentProjectId) {
                    loadMemoryFiles();
                }
                break;
            case 'outlines':
                if (currentProjectId) {
                    loadGeneralOutline();
                    loadVolumes();
                    loadVolumeSelect(); // 加载卷列表到细纲下拉框
                } else {
                    showNotification('请先选择项目', 'error');
                }
                break;
            case 'chapters':
                if (currentProjectId) {
                    loadVolumesForGenerate();
                    // 重置选择状态
                    window.selectedVolumeForGenerate = null;
                    window.selectedChapterForGenerate = null;
                    const selectedDisplay = document.getElementById('selectedChapterDisplay');
                    const generateBtn = document.getElementById('generateChapterBtn');
                    if (selectedDisplay) selectedDisplay.textContent = '未选择';
                    if (generateBtn) generateBtn.disabled = true;
                    // 隐藏内容，显示列表
                    const contentContainer = document.getElementById('chapterContent');
                    const listContainer = document.getElementById('generateChaptersList');
                    if (contentContainer) contentContainer.style.display = 'none';
                    if (listContainer) listContainer.style.display = 'block';
                } else {
                    showNotification('请先选择项目', 'error');
                }
                break;
            case 'config':
                loadAIConfig();
                break;
        }
    }
}

// API调用函数
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: '未知错误' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success && data.error) {
            console.error('API错误:', data.error);
            if (data.traceback) {
                console.error('Traceback:', data.traceback);
            }
            showNotification('错误: ' + data.error, 'error');
        }
        
        return data;
    } catch (error) {
        console.error('API调用错误:', error);
        showNotification('错误: ' + error.message, 'error');
        return { success: false, error: error.message };
    }
}

// 项目管理
async function loadProjects() {
    const result = await apiCall('/api/projects');
    if (result.success) {
        displayProjects(result.projects);
    }
}

function displayProjects(projects) {
    const container = document.getElementById('projectsList');
    if (projects.length === 0) {
        container.innerHTML = '<div class="loading">暂无项目，请创建新项目</div>';
        return;
    }
    
    container.innerHTML = projects.map(project => `
        <div class="project-card" onclick="selectProject('${project.id}')">
            <h3>${project.name}</h3>
            <div class="meta">
                <div>题材: ${project.genre}</div>
                <div>最后修改: ${project.last_modified}</div>
            </div>
            <div class="actions">
                <button class="btn btn-primary" onclick="event.stopPropagation(); selectProject('${project.id}')">
                    <i class="fas fa-folder-open"></i> 打开
                </button>
            </div>
        </div>
    `).join('');
}

async function selectProject(projectId) {
    const result = await apiCall(`/api/projects/${projectId}/select`, {
        method: 'POST'
    });
    
    if (result.success) {
        currentProjectId = projectId;
        currentProjectPath = result.project_path;
        updateCurrentProjectDisplay(result.project_info);
        showNotification('项目已选择', 'success');
        
        // 切换到设定编辑页面
        showPage('settings');
    }
}

async function checkCurrentProject() {
    const result = await apiCall('/api/projects/current');
    if (result.success && result.project_id) {
        currentProjectId = result.project_id;
        currentProjectPath = result.project_path;
        updateCurrentProjectDisplay(result.project_info);
    } else {
        // 没有选择项目，静默处理，不显示错误
        currentProjectId = null;
        currentProjectPath = null;
    }
}

function updateCurrentProjectDisplay(projectInfo) {
    const display = document.getElementById('currentProject');
    if (projectInfo) {
        display.innerHTML = `
            <i class="fas fa-folder-open"></i> ${projectInfo.name}<br>
            <small>${projectInfo.genre}</small>
        `;
    }
}

function showCreateProjectModal() {
    document.getElementById('createProjectModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

async function createProject() {
    const name = document.getElementById('projectNameInput').value;
    const genre = document.getElementById('projectGenreInput').value;
    const wordCount = parseInt(document.getElementById('projectWordCountInput').value);
    
    if (!name) {
        showNotification('请输入项目名称', 'error');
        return;
    }
    
    const result = await apiCall('/api/projects', {
        method: 'POST',
        body: JSON.stringify({
            name: name,
            genre: genre,
            target_word_count: wordCount
        })
    });
    
    if (result.success) {
        closeModal('createProjectModal');
        showNotification('项目创建成功', 'success');
        selectProject(result.project_id);
    }
}

// 设定文件管理
async function loadMemoryFiles() {
    const result = await apiCall('/api/memory/files');
    if (result.success) {
        displayMemoryFiles(result.files);
    }
}

function displayMemoryFiles(files) {
    const container = document.getElementById('memoryFilesList');
    if (!container) return;
    
    container.innerHTML = files.map(file => `
        <li onclick="loadMemoryFile('${file.name}')" class="${file.exists ? '' : 'text-muted'}">
            <i class="fas fa-file-alt"></i> ${file.name}
            ${file.exists ? `<span class="badge">${file.size}字</span>` : '<span class="badge badge-warning">空</span>'}
        </li>
    `).join('');
}

async function loadMemoryFile(filename) {
    currentFile = filename;
    const result = await apiCall(`/api/memory/files/${filename}`);
    
    if (result.success) {
        const placeholder = document.getElementById('editorPlaceholder');
        const container = document.getElementById('editorContainer');
        const title = document.getElementById('editorTitle');
        const editor = document.getElementById('fileEditor');
        
        if (placeholder) placeholder.style.display = 'none';
        if (container) container.style.display = 'flex';
        if (title) title.textContent = filename;
        if (editor) editor.value = result.content || '';
        
        // 更新活动状态
        document.querySelectorAll('#memoryFilesList li').forEach(li => {
            li.classList.remove('active');
            if (li.textContent.includes(filename)) {
                li.classList.add('active');
            }
        });
    }
}

async function saveCurrentFile() {
    if (!currentFile) {
        showNotification('请先选择文件', 'error');
        return;
    }
    
    const content = document.getElementById('fileEditor').value;
    const result = await apiCall(`/api/memory/files/${currentFile}`, {
        method: 'POST',
        body: JSON.stringify({ content: content })
    });
    
    if (result.success) {
        showNotification('文件已保存', 'success');
        loadMemoryFiles(); // 刷新列表
    }
}

async function saveAllMemoryFiles() {
    showNotification('批量保存功能开发中', 'info');
}

function refreshMemoryFiles() {
    loadMemoryFiles();
}

// 大纲管理
async function loadGeneralOutline() {
    const result = await apiCall('/api/outlines/general');
    if (result.success) {
        const container = document.getElementById('generalOutlineContent');
        const editor = document.getElementById('generalOutlineEditor');
        const saveBtn = document.getElementById('saveGeneralBtn');
        
        if (result.exists && result.content) {
            // 显示可编辑模式
            container.style.display = 'none';
            editor.style.display = 'block';
            editor.value = result.content;
            if (saveBtn) saveBtn.style.display = 'inline-flex';
        } else {
            container.style.display = 'block';
            editor.style.display = 'none';
            container.innerHTML = '<div class="placeholder"><i class="fas fa-file-alt"></i><p>总纲尚未生成</p></div>';
            if (saveBtn) saveBtn.style.display = 'none';
        }
    }
}

async function saveGeneralOutline() {
    const editor = document.getElementById('generalOutlineEditor');
    if (!editor) return;
    
    const content = editor.value.trim();
    if (!content) {
        showNotification('总纲内容不能为空', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('saveGeneralBtn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
    }
    
    const result = await apiCall('/api/outlines/general/save', {
        method: 'POST',
        body: JSON.stringify({ content: content })
    });
    
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> 保存总纲';
    }
    
    if (result.success) {
        showNotification('总纲已保存', 'success');
    } else {
        showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
    }
}

async function generateGeneralOutline() {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    const wordCount = prompt('请输入目标总字数（默认: 1000000）:', '1000000');
    if (!wordCount) return;
    
    showNotification('正在生成总纲，请稍候...', 'info');
    
    const result = await apiCall('/api/outlines/general', {
        method: 'POST',
        body: JSON.stringify({
            target_word_count: parseInt(wordCount),
            project_name: '项目名称', // TODO: 从项目信息获取
            genre: '玄幻' // TODO: 从项目信息获取
        })
    });
    
    if (result.success) {
        showNotification('总纲生成成功', 'success');
        loadGeneralOutline();
    }
}

async function loadVolumes() {
    const result = await apiCall('/api/outlines/volumes');
    if (result.success) {
        displayVolumes(result.volumes);
    }
    
    // 确保内容容器隐藏
    const contentContainer = document.getElementById('volumeOutlineContent');
    if (contentContainer) {
        contentContainer.style.display = 'none';
    }
}

function displayVolumes(volumes) {
    const listContainer = document.getElementById('volumesList');
    const contentContainer = document.getElementById('volumeOutlineContent');
    const editor = document.getElementById('volumeOutlineEditor');
    const saveBtn = document.getElementById('saveVolumeBtn');
    
    if (!listContainer) return;
    
    // 隐藏内容容器和编辑器，显示列表
    if (contentContainer) {
        contentContainer.style.display = 'none';
    }
    if (editor) {
        editor.style.display = 'none';
    }
    if (saveBtn) {
        saveBtn.style.display = 'none';
    }
    listContainer.style.display = 'grid';
    
    if (volumes.length === 0) {
        listContainer.innerHTML = '<div class="loading">暂无卷纲</div>';
        return;
    }
    
    listContainer.innerHTML = volumes.map(vol => `
        <div class="volume-card" onclick="loadVolumeOutline(${vol.volume_num})">
            <h4>第${vol.volume_num}卷</h4>
            <p class="meta">${vol.size}字</p>
        </div>
    `).join('');
}

async function loadVolumeOutline(volumeNum) {
    const result = await apiCall(`/api/outlines/volumes/${volumeNum}`);
    if (result.success) {
        // 显示卷纲内容，和总纲一样的显示方式
        const listContainer = document.getElementById('volumesList');
        const contentContainer = document.getElementById('volumeOutlineContent');
        const editor = document.getElementById('volumeOutlineEditor');
        const saveBtn = document.getElementById('saveVolumeBtn');
        
        if (!listContainer || !contentContainer || !editor) return;
        
        // 隐藏列表，显示编辑器
        listContainer.style.display = 'none';
        contentContainer.style.display = 'none';
        editor.style.display = 'block';
        
        // 保存当前卷号到编辑器
        editor.dataset.volumeNum = volumeNum;
        
        if (result.exists && result.content) {
            editor.value = result.content;
            if (saveBtn) saveBtn.style.display = 'inline-flex';
        } else {
            editor.value = '';
            editor.placeholder = '卷纲不存在，请输入内容';
            if (saveBtn) saveBtn.style.display = 'inline-flex';
        }
    }
}

async function saveVolumeOutline() {
    const editor = document.getElementById('volumeOutlineEditor');
    if (!editor) return;
    
    const volumeNum = editor.dataset.volumeNum;
    if (!volumeNum) {
        showNotification('请先选择卷纲', 'error');
        return;
    }
    
    const content = editor.value.trim();
    if (!content) {
        showNotification('卷纲内容不能为空', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('saveVolumeBtn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
    }
    
    const result = await apiCall(`/api/outlines/volumes/${volumeNum}/save`, {
        method: 'POST',
        body: JSON.stringify({ content: content })
    });
    
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> 保存卷纲';
    }
    
    if (result.success) {
        showNotification(`第${volumeNum}卷卷纲已保存`, 'success');
    } else {
        showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
    }
}

async function loadChapters() {
    const volumeNum = document.getElementById('volumeSelect').value;
    const listContainer = document.getElementById('chaptersList');
    const contentContainer = document.getElementById('chapterOutlineContent');
    
    if (!volumeNum) {
        if (listContainer) {
            listContainer.innerHTML = '<div class="loading">请先选择卷号</div>';
            listContainer.style.display = 'block';
        }
        if (contentContainer) {
            contentContainer.style.display = 'none';
        }
        return;
    }
    
    const result = await apiCall(`/api/outlines/chapters/${volumeNum}`);
    if (result.success) {
        displayChapters(result.chapters);
    }
    
    // 确保内容容器隐藏
    if (contentContainer) {
        contentContainer.style.display = 'none';
    }
}

async function loadVolumeSelect() {
    // 加载卷列表到下拉框
    const result = await apiCall('/api/outlines/volumes');
    if (result.success) {
        const select = document.getElementById('volumeSelect');
        if (select) {
            select.innerHTML = '<option value="">选择卷号</option>' + 
                result.volumes.map(vol => 
                    `<option value="${vol.volume_num}">第${vol.volume_num}卷</option>`
                ).join('');
        }
    }
}

function displayChapters(chapters) {
    const listContainer = document.getElementById('chaptersList');
    const contentContainer = document.getElementById('chapterOutlineContent');
    const editor = document.getElementById('chapterOutlineEditor');
    const saveBtn = document.getElementById('saveChapterBtn');
    
    if (!listContainer) return;
    
    // 隐藏内容容器和编辑器，显示列表
    if (contentContainer) {
        contentContainer.style.display = 'none';
    }
    if (editor) {
        editor.style.display = 'none';
    }
    if (saveBtn) {
        saveBtn.style.display = 'none';
    }
    listContainer.style.display = 'grid';
    
    if (chapters.length === 0) {
        listContainer.innerHTML = '<div class="loading">暂无细纲</div>';
        return;
    }
    
    listContainer.innerHTML = chapters.map(ch => `
        <div class="chapter-card" onclick="loadChapterOutline(${ch.chapter_num})">
            <h4>第${ch.chapter_num}章</h4>
            <p class="meta">${ch.size}字</p>
        </div>
    `).join('');
}

async function loadChapterOutline(chapterNum) {
    const volumeNum = document.getElementById('volumeSelect').value;
    if (!volumeNum) {
        showNotification('请先选择卷号', 'error');
        return;
    }
    
    const result = await apiCall(`/api/outlines/chapters/${volumeNum}/${chapterNum}`);
    if (result.success) {
        // 显示细纲内容，和总纲、卷纲一样的显示方式
        const listContainer = document.getElementById('chaptersList');
        const contentContainer = document.getElementById('chapterOutlineContent');
        const editor = document.getElementById('chapterOutlineEditor');
        const saveBtn = document.getElementById('saveChapterBtn');
        
        if (!listContainer || !contentContainer || !editor) return;
        
        // 隐藏列表，显示编辑器
        listContainer.style.display = 'none';
        contentContainer.style.display = 'none';
        editor.style.display = 'block';
        
        // 保存当前卷号和章节号到编辑器
        editor.dataset.volumeNum = volumeNum;
        editor.dataset.chapterNum = chapterNum;
        
        if (result.exists && result.content) {
            editor.value = result.content;
            if (saveBtn) saveBtn.style.display = 'inline-flex';
        } else {
            editor.value = '';
            editor.placeholder = '细纲不存在，请输入内容';
            if (saveBtn) saveBtn.style.display = 'inline-flex';
        }
    }
}

async function saveChapterOutline() {
    const editor = document.getElementById('chapterOutlineEditor');
    if (!editor) return;
    
    const volumeNum = editor.dataset.volumeNum;
    const chapterNum = editor.dataset.chapterNum;
    
    if (!volumeNum || !chapterNum) {
        showNotification('请先选择细纲', 'error');
        return;
    }
    
    const content = editor.value.trim();
    if (!content) {
        showNotification('细纲内容不能为空', 'error');
        return;
    }
    
    const saveBtn = document.getElementById('saveChapterBtn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 保存中...';
    }
    
    const result = await apiCall(`/api/outlines/chapters/${volumeNum}/${chapterNum}/save`, {
        method: 'POST',
        body: JSON.stringify({ content: content })
    });
    
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-save"></i> 保存细纲';
    }
    
    if (result.success) {
        showNotification(`第${volumeNum}卷第${chapterNum}章细纲已保存`, 'success');
    } else {
        showNotification('保存失败: ' + (result.error || '未知错误'), 'error');
    }
}

async function loadVolumesForGenerate() {
    const result = await apiCall('/api/outlines/volumes');
    if (result.success) {
        const select = document.getElementById('generateVolumeSelect');
        if (select) {
            select.innerHTML = '<option value="">选择卷号</option>' + 
                result.volumes.map(vol => 
                    `<option value="${vol.volume_num}">第${vol.volume_num}卷</option>`
                ).join('');
        }
    }
}

async function loadChaptersForGenerate() {
    const volumeNum = document.getElementById('generateVolumeSelect').value;
    const listContainer = document.getElementById('generateChaptersList');
    const contentContainer = document.getElementById('chapterContent');
    const selectedDisplay = document.getElementById('selectedChapterDisplay');
    const generateBtn = document.getElementById('generateChapterBtn');
    
    // 重置选择状态
    if (selectedDisplay) {
        selectedDisplay.textContent = '未选择';
    }
    if (generateBtn) {
        generateBtn.disabled = true;
    }
    if (contentContainer) {
        contentContainer.style.display = 'none';
    }
    
    if (!volumeNum) {
        if (listContainer) {
            listContainer.innerHTML = '<div class="placeholder"><i class="fas fa-list"></i><p>请先选择卷号</p></div>';
        }
        return;
    }
    
    const result = await apiCall(`/api/outlines/chapters/${volumeNum}`);
    if (result.success) {
        displayChaptersForGenerate(result.chapters, volumeNum);
    } else {
        if (listContainer) {
            listContainer.innerHTML = '<div class="error">加载章节列表失败</div>';
        }
    }
}

function displayChaptersForGenerate(chapters, volumeNum) {
    const listContainer = document.getElementById('generateChaptersList');
    if (!listContainer) return;
    
    if (chapters.length === 0) {
        listContainer.innerHTML = '<div class="placeholder"><i class="fas fa-file-alt"></i><p>该卷暂无细纲，请先生成细纲</p></div>';
        return;
    }
    
    listContainer.innerHTML = `
        <div class="chapters-list-header">
            <h3>第${volumeNum}卷 - 已有细纲的章节</h3>
            <p class="hint">点击章节卡片选择要生成的章节</p>
        </div>
        <div class="chapters-grid">
            ${chapters.map(ch => `
                <div class="chapter-card-selectable" onclick="selectChapterForGenerate(${volumeNum}, ${ch.chapter_num})" data-volume="${volumeNum}" data-chapter="${ch.chapter_num}">
                    <h4>第${ch.chapter_num}章</h4>
                    <p class="meta">${ch.size}字</p>
                </div>
            `).join('')}
        </div>
    `;
}

function selectChapterForGenerate(volumeNum, chapterNum) {
    // 更新选中状态显示
    const selectedDisplay = document.getElementById('selectedChapterDisplay');
    const generateBtn = document.getElementById('generateChapterBtn');
    
    if (selectedDisplay) {
        selectedDisplay.textContent = `第${volumeNum}卷 第${chapterNum}章`;
    }
    
    if (generateBtn) {
        generateBtn.disabled = false;
    }
    
    // 更新卡片选中状态
    document.querySelectorAll('.chapter-card-selectable').forEach(card => {
        card.classList.remove('selected');
        if (card.dataset.volume == volumeNum && card.dataset.chapter == chapterNum) {
            card.classList.add('selected');
        }
    });
    
    // 保存选中的章节信息到全局变量
    window.selectedVolumeForGenerate = volumeNum;
    window.selectedChapterForGenerate = chapterNum;
}

// 章节生成
async function generateChapter() {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    const volumeNum = window.selectedVolumeForGenerate;
    const chapterNum = window.selectedChapterForGenerate;
    
    if (!volumeNum || !chapterNum) {
        showNotification('请先选择要生成的章节', 'error');
        return;
    }
    
    // 禁用生成按钮，防止重复点击
    const generateBtn = document.getElementById('generateChapterBtn');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
    }
    
    showNotification(`正在生成第${volumeNum}卷第${chapterNum}章，请稍候...`, 'info');
    
    try {
        const result = await apiCall('/api/chapters/generate', {
            method: 'POST',
            body: JSON.stringify({
                project_id: currentProjectId,
                volume_num: volumeNum,
                chapter_num: chapterNum,
                genre: '玄幻' // TODO: 从项目信息获取
            })
        });
        
        if (result.success) {
            showNotification('章节生成成功', 'success');
            loadChapterContent(chapterNum);
        } else {
            showNotification('章节生成失败: ' + (result.error || '未知错误'), 'error');
            // 恢复按钮
            if (generateBtn) {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-magic"></i> 生成章节';
            }
        }
    } catch (error) {
        showNotification('章节生成失败: ' + error.message, 'error');
        // 恢复按钮
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic"></i> 生成章节';
        }
    }
}

async function loadChapterContent(chapterNum) {
    const contentContainer = document.getElementById('chapterContent');
    const listContainer = document.getElementById('generateChaptersList');
    
    if (!contentContainer) return;
    
    const result = await apiCall(`/api/chapters/${chapterNum}`);
    if (result.success && result.content) {
        // 隐藏列表，显示内容
        if (listContainer) {
            listContainer.style.display = 'none';
        }
        contentContainer.style.display = 'block';
        contentContainer.textContent = result.content;
    } else {
        showNotification('章节内容加载失败', 'error');
    }
}

// 标签页切换
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const tab = this.getAttribute('data-tab');
        
        // 更新按钮状态
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // 更新内容
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(tab + 'Tab').classList.add('active');
        
        // 加载数据
        if (tab === 'volumes') {
            loadVolumes();
        } else if (tab === 'chapters') {
            loadVolumeSelect(); // 先加载卷列表
            loadChapters();
        }
    });
});

// 通知功能
function showNotification(message, type = 'info') {
    // 简单的通知实现
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// AI配置管理
async function loadAIConfig() {
    const container = document.querySelector('.config-container');
    if (!container) return;
    
    container.innerHTML = '<div class="loading">加载配置中...</div>';
    
    const result = await apiCall('/api/config/ai');
    if (result.success) {
        displayAIConfig(result.current_platform, result.platforms);
    } else {
        container.innerHTML = `<div class="error">加载配置失败: ${result.error || '未知错误'}</div>`;
    }
}

function displayAIConfig(currentPlatform, platforms) {
    const container = document.querySelector('.config-container');
    if (!container) return;
    
    let html = `
        <div class="config-section">
            <h3>当前AI平台</h3>
            <div class="config-item">
                <label>平台:</label>
                <select id="currentPlatformSelect" onchange="changePlatform()">
    `;
    
    for (const [platform, config] of Object.entries(platforms)) {
        const selected = platform === currentPlatform ? 'selected' : '';
        html += `<option value="${platform}" ${selected}>${platform.toUpperCase()}</option>`;
    }
    
    html += `
                </select>
            </div>
        </div>
    `;
    
    for (const [platform, config] of Object.entries(platforms)) {
        const isCurrent = platform === currentPlatform;
        html += `
            <div class="config-section platform-config" data-platform="${platform}" style="${isCurrent ? '' : 'display: none;'}">
                <h3>${platform.toUpperCase()} 配置</h3>
                <div class="config-item">
                    <label>启用:</label>
                    <input type="checkbox" id="${platform}_enabled" ${config.enabled ? 'checked' : ''} onchange="updatePlatformConfig('${platform}')">
                </div>
                <div class="config-item">
                    <label>API地址:</label>
                    <input type="text" id="${platform}_base_url" value="${config.base_url || ''}" onchange="updatePlatformConfig('${platform}')">
                </div>
                <div class="config-item">
                    <label>模型:</label>
                    <input type="text" id="${platform}_model" value="${config.model || ''}" onchange="updatePlatformConfig('${platform}')">
                </div>
    `;
        
        if (platform !== 'ollama') {
            html += `
                <div class="config-item">
                    <label>API Key:</label>
                    <input type="password" id="${platform}_api_key" value="${config.api_key || ''}" onchange="updatePlatformConfig('${platform}')" placeholder="输入API密钥">
                </div>
            `;
        }
        
        html += `
                <div class="config-item">
                    <label>超时时间(秒):</label>
                    <input type="number" id="${platform}_timeout" value="${config.timeout || 60}" onchange="updatePlatformConfig('${platform}')">
                </div>
                <div class="config-item">
                    <label>温度:</label>
                    <input type="number" id="${platform}_temperature" value="${config.temperature || 0.7}" step="0.1" min="0" max="2" onchange="updatePlatformConfig('${platform}')">
                </div>
                <div class="config-item">
                    <label>最大Token:</label>
                    <input type="number" id="${platform}_max_tokens" value="${config.max_tokens || 4000}" onchange="updatePlatformConfig('${platform}')">
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function changePlatform() {
    const platform = document.getElementById('currentPlatformSelect').value;
    
    // 隐藏所有平台配置
    document.querySelectorAll('.platform-config').forEach(el => {
        el.style.display = 'none';
    });
    
    // 显示当前平台配置
    const currentConfig = document.querySelector(`[data-platform="${platform}"]`);
    if (currentConfig) {
        currentConfig.style.display = 'block';
    }
    
    // 更新后端配置
    const result = await apiCall('/api/config/ai', {
        method: 'POST',
        body: JSON.stringify({
            current_platform: platform
        })
    });
    
    if (result.success) {
        showNotification('平台已切换', 'success');
    }
}

async function updatePlatformConfig(platform) {
    const config = {
        enabled: document.getElementById(`${platform}_enabled`).checked,
        base_url: document.getElementById(`${platform}_base_url`).value,
        model: document.getElementById(`${platform}_model`).value,
        timeout: parseInt(document.getElementById(`${platform}_timeout`).value),
        temperature: parseFloat(document.getElementById(`${platform}_temperature`).value),
        max_tokens: parseInt(document.getElementById(`${platform}_max_tokens`).value)
    };
    
    if (platform !== 'ollama') {
        config.api_key = document.getElementById(`${platform}_api_key`).value;
    }
    
    const result = await apiCall('/api/config/ai', {
        method: 'POST',
        body: JSON.stringify({
            platforms: {
                [platform]: config
            }
        })
    });
    
    if (result.success) {
        showNotification(`${platform}配置已更新`, 'success');
    }
}

// 生成卷纲模态框
function showGenerateVolumeModal() {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    const volumeNum = prompt('请输入要生成的卷号:', '1');
    if (!volumeNum || isNaN(volumeNum)) {
        return;
    }
    
    generateVolumeOutline(parseInt(volumeNum));
}

async function generateVolumeOutline(volumeNum) {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    showNotification(`正在生成第${volumeNum}卷卷纲，请稍候...`, 'info');
    
    try {
        const result = await apiCall('/api/outlines/volumes', {
            method: 'POST',
            body: JSON.stringify({
                volume_num: volumeNum
            })
        });
        
        if (result.success) {
            showNotification(`第${volumeNum}卷卷纲生成成功`, 'success');
            loadVolumes();
        } else {
            showNotification('卷纲生成失败: ' + (result.error || '未知错误'), 'error');
        }
    } catch (error) {
        showNotification('卷纲生成失败: ' + error.message, 'error');
    }
}

// 生成细纲模态框
function showGenerateChapterModal() {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    const volumeNum = document.getElementById('volumeSelect').value;
    if (!volumeNum) {
        showNotification('请先选择卷号', 'error');
        return;
    }
    
    const chapterNum = prompt(`请输入要生成的章节编号（第${volumeNum}卷）:`, '1');
    if (!chapterNum || isNaN(chapterNum)) {
        return;
    }
    
    generateChapterOutline(parseInt(volumeNum), parseInt(chapterNum));
}

async function generateChapterOutline(volumeNum, chapterNum) {
    if (!currentProjectId) {
        showNotification('请先选择项目', 'error');
        return;
    }
    
    showNotification(`正在生成第${volumeNum}卷第${chapterNum}章细纲，请稍候...`, 'info');
    
    try {
        const result = await apiCall(`/api/outlines/chapters/${volumeNum}/${chapterNum}`, {
            method: 'POST',
            body: JSON.stringify({
                volume_num: volumeNum,
                chapter_num: chapterNum
            })
        });
        
        if (result.success) {
            showNotification(`第${chapterNum}章细纲生成成功`, 'success');
            loadChapters();
        } else {
            showNotification('细纲生成失败: ' + (result.error || '未知错误'), 'error');
        }
    } catch (error) {
        showNotification('细纲生成失败: ' + error.message, 'error');
    }
}

// 模态框点击外部关闭
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.classList.remove('active');
        }
    });
}
