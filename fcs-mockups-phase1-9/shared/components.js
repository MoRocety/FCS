/**
 * FCS V3 Shared Components
 * Reusable JS utilities for all mockup phases
 */

const FCS = {
    // Color palette
    colors: {
        brand: '#2563eb',
        success: '#16a34a',
        warning: '#d97706',
        danger: '#dc2626',
        gray: '#6b7280'
    },

    // Department colors
    deptColors: {
        BIOL: 'emerald',
        CHEM: 'blue',
        MATH: 'amber',
        CS: 'purple',
        ENGL: 'rose',
        PHYS: 'teal',
        HIST: 'orange'
    },

    // Format seat count with color coding
    formatSeats(remaining, total) {
        const pct = remaining / total;
        let colorClass = 'text-emerald-600';
        if (pct <= 0.15) colorClass = 'text-red-600';
        else if (pct <= 0.35) colorClass = 'text-amber-600';
        return `<span class="font-semibold ${colorClass}">${remaining}/${total}</span>`;
    },

    // Format star rating
    formatRating(rating) {
        return `
            <div class="flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-amber-400 fill-current" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <span class="text-sm font-medium text-gray-700">${rating}</span>
            </div>`;
    },

    // Calculate health score (mock)
    calcHealthScore(schedule) {
        let score = 70;
        if (schedule.credits >= 12 && schedule.credits <= 16) score += 10;
        if (schedule.courses <= 5) score += 5;
        if (schedule.instructorAvg >= 4.0) score += 10;
        if (schedule.commuteAvg <= 5) score += 5;
        return Math.min(100, score);
    },

    // Format credit range
    formatCredits(min, max) {
        return `${min}-${max} credits`;
    },

    // Time formatting
    formatTime(hour, minute = 0) {
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const h = hour > 12 ? hour - 12 : hour;
        return `${h}:${minute.toString().padStart(2, '0')} ${ampm}`;
    },

    // Day abbreviations
    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],

    // Generate color class for department
    deptColorClass(dept) {
        const color = this.deptColors[dept] || 'gray';
        return {
            bg: `bg-${color}-100`,
            text: `text-${color}-700`,
            border: `border-${color}-200`,
            dot: `bg-${color}-400`
        };
    },

    // Debounce utility
    debounce(fn, delay = 300) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), delay);
        };
    },

    // Local storage helpers
    storage: {
        get(key) {
            try { return JSON.parse(localStorage.getItem(`fcs_${key}`)); }
            catch { return null; }
        },
        set(key, value) {
            localStorage.setItem(`fcs_${key}`, JSON.stringify(value));
        },
        remove(key) {
            localStorage.removeItem(`fcs_${key}`);
        }
    },

    // Toast notification
    showToast(message, type = 'info') {
        const colors = {
            info: 'bg-brand-600',
            success: 'bg-emerald-600',
            warning: 'bg-amber-600',
            error: 'bg-red-600'
        };
        const toast = document.createElement('div');
        toast.className = `fixed bottom-20 right-6 ${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg z-50 text-sm font-medium`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }
};

// Export for use in phases
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FCS;
}
