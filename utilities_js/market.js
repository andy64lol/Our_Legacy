/**
 * Market API for accessing the Elite Market with 10-minute cooldown
 * Ported from utilities/market.py
 */

const MARKET_API_URLS = [
    "https://our-legacy.vercel.app/api/market",
    "https://our-legacy-api.replit.app/api/market",
    "http://localhost:5000/api/market"
];
const MARKET_COOLDOWN_MINUTES = 10;

/**
 * API for accessing the Elite Market with 10-minute cooldown
 */
export class MarketAPI {
    /**
     * @param {Object} lang - Language manager instance
     * @param {Object} colors - Colors class for styling
     */
    constructor(lang = null, colors = null) {
        this.cache = null;
        this.lastFetch = null;
        this.cooldownMinutes = MARKET_COOLDOWN_MINUTES;
        
        this.Colors = colors || {
            CYAN: '',
            GREEN: '',
            RED: '',
            END: ''
        };
        
        this.lang = lang || { 
            get: (key, defaultValue = null, params = {}) => defaultValue || key 
        };
    }

    /**
     * Check if cache is still valid (within cooldown period)
     * @returns {boolean} True if cache is valid
     */
    isCacheValid() {
        if (!this.lastFetch || !this.cache) return false;
        const elapsed = (new Date() - this.lastFetch) / 1000 / 60;
        return elapsed < this.cooldownMinutes;
    }

    /**
     * Fetch market data from the API with caching, cooldown, and fallback endpoints
     * @param {boolean} forceRefresh - Force refresh even if cache is valid
     * @returns {Promise<Object|null>} Market data or null if failed
     */
    async fetchMarketData(forceRefresh = false) {
        // Check cache validity
        if (!forceRefresh && this.isCacheValid()) {
            this.game?.print(this.lang.get('visiting_market'));
            return this.cache;
        }

        // Check cooldown
        if (this.lastFetch && !this.isCacheValid()) {
            const elapsed = (new Date() - this.lastFetch) / 1000 / 60;
            const remaining = this.cooldownMinutes - elapsed;
            const mins = Math.floor(remaining);
            const secs = Math.floor((remaining - mins) * 60);
            this.game?.print(
                this.lang.get(
                    "market_closed_msg",
                    "Merchants have left and the market is closed! Please come back in {mins}m {secs}s",
                    { mins, secs }
                )
            );
            return null;
        }

        this.game?.print(
            this.lang.get('checking_merchants_msg', 'Checking if merchants are in the market...')
        );

        // Try each endpoint in order
        for (const url of MARKET_API_URLS) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const data = await response.json();
                    this.cache = data;
                    this.lastFetch = new Date();
                    this.game?.print(
                        this.lang.get('market_open_msg', 'Market is open!')
                    );
                    return data;
                }
            } catch (e) {
                continue;
            }
        }

        this.game?.print(
            this.lang.get('market_reach_error', 'Failed to reach any market merchants at this time.')
        );
        return null;
    }

    /**
     * Get remaining cooldown time
     * @returns {number|null} Remaining minutes or null if no cooldown
     */
    getCooldownRemaining() {
        if (!this.lastFetch) return null;
        const elapsed = (new Date() - this.lastFetch) / 1000 / 60;
        const remaining = this.cooldownMinutes - elapsed;
        return remaining > 0 ? remaining : null;
    }

    /**
     * Get all market items
     * @returns {Promise<Array>} Array of market items
     */
    async getAllItems() {
        const data = await this.fetchMarketData();
        return (data && data.ok) ? (data.items || []) : [];
    }

    /**
     * Get items grouped by type
     * @returns {Promise<Object>} Object with items grouped by type
     */
    async getItemsByType() {
        const data = await this.fetchMarketData();
        return (data && data.ok) ? (data.itemsByType || {}) : {};
    }

    /**
     * Get filtered market items
     * @param {Object} filters - Filter options
     * @param {string} filters.itemType - Item type to filter by
     * @param {string} filters.rarity - Rarity to filter by
     * @param {string} filters.classReq - Class requirement to filter by
     * @param {number} filters.maxPrice - Maximum price
     * @returns {Promise<Array>} Filtered array of items
     */
    async filterItems(filters = {}) {
        const data = await this.fetchMarketData();
        if (!data || !data.ok) return [];

        let items = data.items || [];
        
        if (filters.itemType) {
            items = items.filter(i => i.type && i.type.toLowerCase() === filters.itemType.toLowerCase());
        }
        if (filters.rarity) {
            items = items.filter(i => i.rarity && i.rarity.toLowerCase() === filters.rarity.toLowerCase());
        }
        if (filters.classReq) {
            items = items.filter(i => {
                const req = i.requirements || {};
                return req.class && req.class.toLowerCase() === filters.classReq.toLowerCase();
            });
        }
        if (filters.maxPrice) {
            items = items.filter(i => (i.marketPrice || 0) <= filters.maxPrice);
        }
        return items;
    }
}

export { MarketAPI };
export default MarketAPI;
