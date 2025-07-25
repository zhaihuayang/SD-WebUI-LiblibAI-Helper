// liblibAI Helper 插件 - 前端脚本
// 负责增强 WebUI 的模型卡片和提示词输入框

// 等待 DOM 加载完成
document.addEventListener("DOMContentLoaded", function() {
    // 初始化插件
    initLiblibAIHelper();
});

// 初始化插件
function initLiblibAIHelper() {
    console.log("LiblibAI Helper 插件初始化中...");
    
    // 监听 WebUI 中的元素变化
    observeElementChanges();
    
    // 添加模型卡片功能
    enhanceModelCards();
    
    // 添加提示词输入框功能
    enhancePromptTextarea();
}

// 监听元素变化
function observeElementChanges() {
    // 创建 MutationObserver 实例
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            // 检查是否有新的模型卡片添加
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 检查是否是模型卡片
                        const modelCards = node.querySelectorAll('.model-card');
                        if (modelCards.length > 0) {
                            modelCards.forEach(card => {
                                enhanceModelCard(card);
                            });
                        }
                    }
                }
            }
        });
    });
    
    // 配置 observer
    const config = { childList: true, subtree: true };
    
    // 开始观察
    observer.observe(document.body, config);
}

// 增强模型卡片
function enhanceModelCards() {
    // 查找所有现有的模型卡片
    const modelCards = document.querySelectorAll('.model-card');
    modelCards.forEach(card => {
        enhanceModelCard(card);
    });
}

// 增强单个模型卡片
function enhanceModelCard(card) {
    // 检查是否已经增强
    if (card.dataset.liblibaiEnhanced === 'true') {
        return;
    }
    
    // 标记为已增强
    card.dataset.liblibaiEnhanced = 'true';
    
    // 创建 LiblibAI 按钮
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'liblibai-buttons';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.justifyContent = 'space-around';
    buttonContainer.style.marginTop = '8px';
    
    // 添加 "使用 LiblibAI" 按钮
    const useLiblibAIButton = document.createElement('button');
    useLiblibAIButton.textContent = '使用 LiblibAI';
    useLiblibAIButton.className = 'liblibai-button';
    useLiblibAIButton.style.padding = '4px 8px';
    useLiblibAIButton.style.backgroundColor = '#4b6fff';
    useLiblibAIButton.style.color = 'white';
    useLiblibAIButton.style.border = 'none';
    useLiblibAIButton.style.borderRadius = '4px';
    useLiblibAIButton.style.cursor = 'pointer';
    
    // 添加点击事件
    useLiblibAIButton.addEventListener('click', function() {
        // 获取模型名称
        const modelName = card.querySelector('.model-name')?.textContent;
        if (modelName) {
            // 切换到 LiblibAI 选项卡
            switchToLiblibAITab();
            
            // 搜索并选择模型
            searchAndSelectModel(modelName);
        }
    });
    
    // 添加按钮到容器
    buttonContainer.appendChild(useLiblibAIButton);
    
    // 添加按钮容器到卡片
    card.appendChild(buttonContainer);
}

// 切换到 LiblibAI 选项卡
function switchToLiblibAITab() {
    // 查找 LiblibAI 选项卡
    const tabs = document.querySelectorAll('#tabs button');
    for (let i = 0; i < tabs.length; i++) {
        if (tabs[i].textContent.includes('LiblibAI')) {
            tabs[i].click();
            break;
        }
    }
}

// 搜索并选择模型
function searchAndSelectModel(modelName) {
    // 等待选项卡加载完成
    setTimeout(function() {
        // 查找模型搜索输入框
        const searchInput = document.querySelector('#liblibai_interface input[placeholder*="搜索"]');
        if (searchInput) {
            // 设置搜索值
            searchInput.value = modelName;
            
            // 触发 change 事件
            const event = new Event('change', { bubbles: true });
            searchInput.dispatchEvent(event);
            
            // 触发 input 事件
            const inputEvent = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(inputEvent);
        }
    }, 500);
}

// 增强提示词输入框
function enhancePromptTextarea() {
    // 查找所有提示词输入框
    const promptTextareas = document.querySelectorAll('#txt2img_prompt, #img2img_prompt');
    promptTextareas.forEach(textarea => {
        // 检查是否已经增强
        if (textarea.dataset.liblibaiEnhanced === 'true') {
            return;
        }
        
        // 标记为已增强
        textarea.dataset.liblibaiEnhanced = 'true';
        
        // 创建 LiblibAI 按钮
        const button = document.createElement('button');
        button.textContent = '发送到 LiblibAI';
        button.className = 'liblibai-prompt-button';
        button.style.position = 'absolute';
        button.style.right = '10px';
        button.style.top = '10px';
        button.style.padding = '4px 8px';
        button.style.backgroundColor = '#4b6fff';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '4px';
        button.style.cursor = 'pointer';
        button.style.zIndex = '100';
        
        // 添加点击事件
        button.addEventListener('click', function() {
            // 获取提示词
            const prompt = textarea.value;
            
            // 获取负面提示词
            let negativePrompt = '';
            const textareaId = textarea.id;
            if (textareaId === 'txt2img_prompt') {
                negativePrompt = document.querySelector('#txt2img_neg_prompt')?.value || '';
            } else if (textareaId === 'img2img_prompt') {
                negativePrompt = document.querySelector('#img2img_neg_prompt')?.value || '';
            }
            
            // 切换到 LiblibAI 选项卡
            switchToLiblibAITab();
            
            // 设置提示词和负面提示词
            setTimeout(function() {
                // 查找 LiblibAI 提示词输入框
                const liblibaiPrompt = document.querySelector('#liblibai_interface textarea[placeholder*="提示词"]');
                if (liblibaiPrompt) {
                    liblibaiPrompt.value = prompt;
                    
                    // 触发 change 事件
                    const event = new Event('change', { bubbles: true });
                    liblibaiPrompt.dispatchEvent(event);
                }
                
                // 查找 LiblibAI 负面提示词输入框
                const liblibaiNegPrompt = document.querySelector('#liblibai_interface textarea[placeholder*="负面提示词"]');
                if (liblibaiNegPrompt) {
                    liblibaiNegPrompt.value = negativePrompt;
                    
                    // 触发 change 事件
                    const event = new Event('change', { bubbles: true });
                    liblibaiNegPrompt.dispatchEvent(event);
                }
            }, 500);
        });
        
        // 获取父元素
        const parent = textarea.parentElement;
        
        // 设置父元素为相对定位，以便按钮定位
        if (parent) {
            if (window.getComputedStyle(parent).position === 'static') {
                parent.style.position = 'relative';
            }
            
            // 添加按钮到父元素
            parent.appendChild(button);
        }
    });
}