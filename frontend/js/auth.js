// Authentication Manager
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            this.loadCurrentUser();
        }

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login button
        document.getElementById('loginBtn')?.addEventListener('click', () => {
            this.showAuthModal('login');
        });

        // Register button
        document.getElementById('registerBtn')?.addEventListener('click', () => {
            this.showAuthModal('register');
        });

        // Logout button
        document.getElementById('logoutBtn')?.addEventListener('click', () => {
            this.logout();
        });

        // Modal close
        const modal = document.getElementById('authModal');
        const closeBtn = modal?.querySelector('.close');
        closeBtn?.addEventListener('click', () => {
            this.hideAuthModal();
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hideAuthModal();
            }
        });

        // Form switchers
        document.getElementById('showRegister')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showAuthModal('register');
        });

        document.getElementById('showLogin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showAuthModal('login');
        });

        // Login form
        document.getElementById('loginFormElement')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Register form
        document.getElementById('registerFormElement')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }

    showAuthModal(type = 'login') {
        const modal = document.getElementById('authModal');
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (type === 'login') {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
        } else {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        }

        modal.style.display = 'block';
        this.clearErrors();
    }

    hideAuthModal() {
        const modal = document.getElementById('authModal');
        modal.style.display = 'none';
        this.clearErrors();
    }

    clearErrors() {
        document.getElementById('loginError').textContent = '';
        document.getElementById('registerError').textContent = '';
    }

    async handleLogin() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const errorElement = document.getElementById('loginError');

        try {
            showLoading();
            const response = await api.login({ email, password });

            if (response.access_token) {
                await this.loadCurrentUser();
                this.hideAuthModal();
                showToast('Login successful!', 'success');

                // Reload page to refresh data
                window.location.reload();
            }
        } catch (error) {
            errorElement.textContent = error.message || 'Login failed. Please try again.';
        } finally {
            hideLoading();
        }
    }

    async handleRegister() {
        const name = document.getElementById('registerName').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const balance = parseFloat(document.getElementById('registerBalance').value);
        const errorElement = document.getElementById('registerError');

        console.log('Starting registration...', { name, email });

        try {
            showLoading();
            const user = await api.register({ name, email, password, balance });
            console.log('Registration successful:', user);

            if (user.id) {
                console.log('Attempting auto-login...');
                // Auto-login after registration using the same credentials
                const loginResponse = await api.login({ email, password });
                console.log('Login response:', loginResponse);

                if (loginResponse.access_token) {
                    console.log('Login successful, loading user...');
                    await this.loadCurrentUser();

                    console.log('Hiding modal...');
                    this.hideAuthModal();

                    console.log('Showing success toast...');
                    showToast('Registration successful! Welcome!', 'success');

                    console.log('Reloading page...');
                    // Small delay before reload to show the toast
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                }
            }
        } catch (error) {
            console.error('Registration error:', error);
            errorElement.textContent = error.message || 'Registration failed. Please try again.';
        } finally {
            hideLoading();
        }
    }

    async loadCurrentUser() {
        try {
            const user = await api.getCurrentUser();
            this.currentUser = user;
            localStorage.setItem('current_user', JSON.stringify(user));
            this.updateUI();
            return user;
        } catch (error) {
            console.error('Failed to load current user:', error);
            this.logout();
            return null;
        }
    }

    logout() {
        this.currentUser = null;
        api.logout();
        this.updateUI();
        showToast('Logged out successfully', 'info');
    }

    updateUI() {
        const userInfo = document.getElementById('userInfo');
        const authButtons = document.getElementById('authButtons');
        const userName = document.getElementById('userName');

        if (this.currentUser) {
            userInfo.style.display = 'flex';
            authButtons.style.display = 'none';
            userName.textContent = `${this.currentUser.name} ($${parseFloat(this.currentUser.balance).toLocaleString('en-US', CONFIG.CURRENCY_FORMAT)})`;
        } else {
            userInfo.style.display = 'none';
            authButtons.style.display = 'flex';
        }
    }

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    getCurrentUser() {
        return this.currentUser;
    }

    getUserId() {
        return this.currentUser?.id || localStorage.getItem('user_id');
    }
}

// Create global auth manager
const authManager = new AuthManager();
