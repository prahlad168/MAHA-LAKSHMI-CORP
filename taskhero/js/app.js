// TaskHero - Main JavaScript

// API Base URL
const API_BASE = '/api';

// ============ USER AUTH ============
class Auth {
    static isLoggedIn() {
        return !!localStorage.getItem('taskhero_user');
    }
    
    static getUser() {
        const user = localStorage.getItem('taskhero_user');
        return user ? JSON.parse(user) : null;
    }
    
    static login(email, password) {
        // Simulate login
        const user = {
            id: Date.now(),
            email,
            name: email.split('@')[0],
            type: 'customer',
            created: new Date().toISOString()
        };
        localStorage.setItem('taskhero_user', JSON.stringify(user));
        return user;
    }
    
    static register(data) {
        const user = {
            id: Date.now(),
            ...data,
            created: new Date().toISOString()
        };
        localStorage.setItem('taskhero_user', JSON.stringify(user));
        return user;
    }
    
    static logout() {
        localStorage.removeItem('taskhero_user');
        window.location.href = '/';
    }
}

// ============ BOOKING ============
class Booking {
    static create(bookingData) {
        const bookings = this.getAll();
        const newBooking = {
            id: Date.now(),
            ...bookingData,
            status: 'pending',
            created: new Date().toISOString()
        };
        bookings.push(newBooking);
        localStorage.setItem('taskhero_bookings', JSON.stringify(bookings));
        return newBooking;
    }
    
    static getAll() {
        const bookings = localStorage.getItem('taskhero_bookings');
        return bookings ? JSON.parse(bookings) : [];
    }
    
    static getById(id) {
        const bookings = this.getAll();
        return bookings.find(b => b.id === parseInt(id));
    }
    
    static update(id, data) {
        const bookings = this.getAll();
        const index = bookings.findIndex(b => b.id === parseInt(id));
        if (index !== -1) {
            bookings[index] = { ...bookings[index], ...data };
            localStorage.setItem('taskhero_bookings', JSON.stringify(bookings));
            return bookings[index];
        }
        return null;
    }
}

// ============ PROFESSIONALS ============
class Professionals {
    static getAll() {
        // Sample data
        return [
            { id: 1, name: 'John Smith', service: 'plumbing', rating: 4.9, reviews: 234, city: 'New York', price: 60, image: '👨‍🔧', verified: true },
            { id: 2, name: 'Sarah Johnson', service: 'electrical', rating: 4.8, reviews: 189, city: 'Los Angeles', price: 75, image: '👩‍🔧', verified: true },
            { id: 3, name: 'Mike Wilson', service: 'carpentry', rating: 4.7, reviews: 156, city: 'Chicago', price: 55, image: '👨‍🔧', verified: true },
            { id: 4, name: 'Emily Brown', service: 'painting', rating: 4.9, reviews: 298, city: 'Houston', price: 45, image: '👩‍🎨', verified: true },
            { id: 5, name: 'David Lee', service: 'ac', rating: 4.8, reviews: 167, city: 'Phoenix', price: 80, image: '👨‍🔧', verified: true },
            { id: 6, name: 'Lisa Chen', service: 'cleaning', rating: 4.9, reviews: 412, city: 'San Francisco', price: 40, image: '👩‍💼', verified: true },
        ];
    }
    
    static search(service, city) {
        let pros = this.getAll();
        if (service) pros = pros.filter(p => p.service === service);
        if (city) pros = pros.filter(p => p.city.toLowerCase().includes(city.toLowerCase()));
        return pros;
    }
}

// ============ UI HELPERS ============
const UI = {
    toast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },
    
    modal(id, show = true) {
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.toggle('active', show);
        }
    },
    
    loading(show = true) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = show ? 'flex' : 'none';
        }
    },
    
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency
        }).format(amount);
    },
    
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }
};

// ============ PAYMENT (STRIPE INTEGRATION) ============
class Payment {
    static async createCheckoutSession(bookingId, amount) {
        // In production, this calls your backend
        // For demo, simulate success
        return {
            sessionId: 'demo_' + Date.now(),
            url: '#checkout-demo'
        };
    }
    
    static async confirmPayment(sessionId) {
        // Simulate payment confirmation
        return { success: true };
    }
}

// ============ ANALYTICS ============
class Analytics {
    static track(event, data) {
        console.log('Analytics:', event, data);
        // In production, send to analytics service
    }
}

// ============ SPEECH ============
function speak(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = 'en-US';
        msg.rate = 1;
        msg.pitch = 1;
        speechSynthesis.speak(msg);
    }
}

// ============ FORM HANDLING ============
document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss toasts
    setTimeout(() => {
        document.querySelectorAll('.toast').forEach(t => t.remove());
    }, 5000);
    
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Auth, Booking, Professionals, Payment, UI, Analytics };
}
