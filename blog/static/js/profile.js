// 1. 选项卡平滑切换（简化动画时长）
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
        setTimeout(() => {
            el.style.display = 'none';
        }, 200); // 简化延迟
    });
    const activeTab = document.getElementById(tabId);
    activeTab.style.display = 'block';
    setTimeout(() => {
        activeTab.classList.remove('hidden');
    }, 10);
    document.querySelectorAll('.tab-item').forEach(el => {
        el.classList.remove('active');
    });
    if (event) {
        event.target.classList.add('active');
    }
}

// 2. 头像上传实时预览（优化性能，减少渲染）
const avatarInput = document.getElementById('avatar-input');
const avatarPreview = document.getElementById('avatar-preview');
const currentAvatar = document.getElementById('current-avatar');
const defaultAvatar = document.getElementById('default-avatar');

if (avatarInput) {
    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                showAlert('请选择图片文件！', 'error');
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                showAlert('图片大小不能超过5MB！', 'error');
                return;
            }
            // 优化：使用URL.createObjectURL，比FileReader更快
            const imgUrl = URL.createObjectURL(file);
            avatarPreview.src = imgUrl;
            avatarPreview.style.display = 'block';
            if (currentAvatar) currentAvatar.style.display = 'none';
            if (defaultAvatar) defaultAvatar.style.display = 'none';
            showAlert('图片预览成功！', 'success');
        }
    });
}

// 3. 用户名实时验证（保留功能，简化逻辑）
const newUsername = document.getElementById('new-username');
const usernameTip = document.getElementById('username-tip');
const usernameSubmit = document.getElementById('username-submit');

if (newUsername) {
    newUsername.addEventListener('input', function() {
        const value = this.value.trim();
        const reg = /^[a-zA-Z0-9_]{3,15}$/;
        if (value === '') {
            usernameTip.textContent = '请输入用户名';
            usernameTip.className = 'validation-tip tip-error';
            usernameSubmit.disabled = true;
        } else if (!reg.test(value)) {
            usernameTip.textContent = '用户名需3-15位，仅含字母/数字/下划线';
            usernameTip.className = 'validation-tip tip-error';
            usernameSubmit.disabled = true;
        } else {
            usernameTip.textContent = '用户名格式正确';
            usernameTip.className = 'validation-tip tip-success';
            usernameSubmit.disabled = false;
        }
    });
}

// 4. 密码实时验证（保留功能，简化逻辑）
const newPassword1 = document.getElementById('new-password1');
const newPassword2 = document.getElementById('new-password2');
const password1Tip = document.getElementById('password1-tip');
const password2Tip = document.getElementById('password2-tip');
const passwordSubmit = document.getElementById('password-submit');

if (newPassword1 && newPassword2) {
    newPassword1.addEventListener('input', validatePassword);
    newPassword2.addEventListener('input', validatePassword);

    function validatePassword() {
        const pwd1 = newPassword1.value;
        const pwd2 = newPassword2.value;
        let canSubmit = true;

        const pwdReg = /^(?=.*[a-zA-Z])(?=.*\d).{6,}$/;
        if (pwd1 === '') {
            password1Tip.textContent = '请输入新密码';
            password1Tip.className = 'validation-tip tip-error';
            canSubmit = false;
        } else if (!pwdReg.test(pwd1)) {
            password1Tip.textContent = '密码需6位以上，含字母+数字';
            password1Tip.className = 'validation-tip tip-error';
            canSubmit = false;
        } else {
            password1Tip.textContent = '密码格式正确';
            password1Tip.className = 'validation-tip tip-success';
        }

        if (pwd2 === '') {
            password2Tip.textContent = '请确认新密码';
            password2Tip.className = 'validation-tip tip-error';
            canSubmit = false;
        } else if (pwd2 !== pwd1) {
            password2Tip.textContent = '两次密码不一致';
            password2Tip.className = 'validation-tip tip-error';
            canSubmit = false;
        } else {
            password2Tip.textContent = '两次密码一致';
            password2Tip.className = 'validation-tip tip-success';
        }

        passwordSubmit.disabled = !canSubmit;
    }
}

// 5. 按钮防抖（保留功能，简化延迟）
function debounceSubmit(formId, btnId) {
    const form = document.getElementById(formId);
    const btn = document.getElementById(btnId);
    if (form && btn) {
        form.addEventListener('submit', function(e) {
            if (btn.disabled) return;
            btn.disabled = true;
            btn.textContent = '提交中...';
            setTimeout(() => {
                btn.disabled = false;
                btn.textContent = btnId === 'follow-btn' ? (btn.classList.contains('unfollow') ? '取消关注' : '关注') :
                                           (btnId === 'avatar-submit' ? '上传头像' : '保存修改');
            }, 2000); // 缩短防抖时间
        });
    }
}

debounceSubmit('follow-form', 'follow-btn');
debounceSubmit('avatar-form', 'avatar-submit');
debounceSubmit('username-form', 'username-submit');
debounceSubmit('password-form', 'password-submit');

// 6. 自定义提示框（保留功能）
function showAlert(message, type) {
    const alertBox = document.getElementById('custom-alert');
    alertBox.textContent = message;
    alertBox.className = `custom-alert alert-${type}`;
    alertBox.classList.add('alert-show');
    setTimeout(() => {
        alertBox.classList.remove('alert-show');
    }, 2000); // 缩短提示框显示时间
}

// 7. 美化删除确认框
function confirmDelete() {
    showAlert('确定要删除这篇文章吗？', 'error');
    return confirm('确定要删除这篇文章吗？');
}

// 初始化
window.onload = function() {
    showTab('my-articles');
    document.querySelector('.tab-item').classList.add('active');
    window.scrollTo({top: 0, behavior: 'smooth'});
}