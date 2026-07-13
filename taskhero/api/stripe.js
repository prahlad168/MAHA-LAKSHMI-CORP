/**
 * TaskHero - Stripe Payment Integration
 * 
 * This file handles payment processing via Stripe.
 * In production, replace with your actual Stripe keys.
 * 
 * Setup:
 * 1. Create Stripe account at https://stripe.com
 * 2. Get your API keys from Dashboard > Developers > API keys
 * 3. Replace STRIPE_PUBLIC_KEY and STRIPE_SECRET_KEY below
 * 4. Create a backend endpoint to handle checkout sessions
 */

const STRIPE_PUBLIC_KEY = 'pk_test_YOUR_STRIPE_PUBLIC_KEY';
const STRIPE_SECRET_KEY = 'sk_test_YOUR_STRIPE_SECRET_KEY';
const API_URL = '/api/create-checkout-session';

/**
 * Initialize Stripe
 */
function initStripe() {
    if (typeof Stripe !== 'undefined') {
        return Stripe(STRIPE_PUBLIC_KEY);
    }
    console.warn('Stripe not loaded');
    return null;
}

/**
 * Create a checkout session for booking
 */
async function createCheckoutSession(bookingData) {
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            bookingData,
            success_url: window.location.origin + '/success.html',
            cancel_url: window.location.origin + '/cancel.html',
        }),
    });
    
    if (!response.ok) {
        throw new Error('Failed to create checkout session');
    }
    
    return response.json();
}

/**
 * Redirect to Stripe Checkout
 */
async function checkout(bookingId, amount, currency = 'usd') {
    try {
        const stripe = initStripe();
        if (!stripe) {
            // Demo mode - simulate payment
            simulatePayment(bookingId, amount);
            return;
        }
        
        const { sessionId } = await createCheckoutSession({
            bookingId,
            amount,
            currency,
        });
        
        const { error } = await stripe.redirectToCheckout({ sessionId });
        
        if (error) {
            console.error('Stripe error:', error);
            alert('Payment failed. Please try again.');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        // Fallback to demo payment
        simulatePayment(bookingId, amount);
    }
}

/**
 * Simulate payment for demo purposes
 */
function simulatePayment(bookingId, amount) {
    // Show demo payment modal
    const modal = document.getElementById('paymentModal');
    if (modal) {
        modal.classList.add('active');
        document.getElementById('paymentAmount').textContent = `$${amount.toFixed(2)}`;
    }
}

/**
 * Confirm demo payment
 */
function confirmDemoPayment(bookingId) {
    // Update booking status
    const bookings = JSON.parse(localStorage.getItem('taskhero_bookings') || '[]');
    const booking = bookings.find(b => b.id === bookingId);
    if (booking) {
        booking.status = 'confirmed';
        booking.paid = true;
        booking.paidAt = new Date().toISOString();
        localStorage.setItem('taskhero_bookings', JSON.stringify(bookings));
    }
    
    // Close modal
    const modal = document.getElementById('paymentModal');
    if (modal) {
        modal.classList.remove('active');
    }
    
    // Show success
    UI.toast('Payment successful! Booking confirmed.', 'success');
    
    // Redirect to confirmation
    setTimeout(() => {
        window.location.href = '/dashboard/bookings.html';
    }, 1500);
}

/**
 * Refund a payment
 */
async function refundPayment(paymentIntentId) {
    const response = await fetch('/api/refund', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ paymentIntentId }),
    });
    
    return response.json();
}

/**
 * Get payment history
 */
function getPaymentHistory() {
    const bookings = JSON.parse(localStorage.getItem('taskhero_bookings') || '[]');
    return bookings.filter(b => b.paid).map(b => ({
        id: b.id,
        amount: b.amount,
        status: b.status,
        paidAt: b.paidAt,
        service: b.service,
    }));
}

/**
 * Calculate platform fee
 */
function calculateFee(amount) {
    const platformFee = amount * 0.15; // 15% platform fee
    return {
        gross: amount,
        fee: platformFee,
        net: amount - platformFee,
    };
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initStripe,
        createCheckoutSession,
        checkout,
        refundPayment,
        getPaymentHistory,
        calculateFee,
    };
}
