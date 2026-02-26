const MARKET_API_URLS = [
    "https://our-legacy.vercel.app/api/market",
    "https://our-legacy-api.replit.app/api/market",
    "http://localhost:5000/api/market"
];
const MARKET_COOLDOWN_MINUTES = 10;

class MarketAPI {
    constructor(lang = null) {
        this.cache = null;
        this.lastFetch = null;
        this.cooldownMinutes = MARKET_COOLDOWN_MINUTES;
        this.lang = lang || { get: (key, def) => def || key };
    }

    isCacheValid() {
        if (!this.lastFetch || !this.cache) return false;
        const elapsed = (new Date() - this.lastFetch) / 1000 / 60;
        return elapsed < this.cooldownMinutes;
    }

    async fetchMarketData(forceRefresh = false) {
        if (!forceRefresh && this.isCacheValid()) {
            return this.cache;
        }

        if (this.lastFetch && !this.isCacheValid()) {
            // Cooldown logic could go here
            return null;
        }

        for (const url of MARKET_API_URLS) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const data = await response.json();
                    this.cache = data;
                    this.lastFetch = new Date();
                    return data;
                }
            } catch (e) {
                continue;
            }
        }
        return null;
    }

    async getAllItems() {
        const data = await this.fetchMarketData();
        return (data && data.ok) ? data.items : [];
    }

    async filterItems(filters = {}) {
        const data = await this.fetchMarketData();
        if (!data || !data.ok) return [];

        let items = data.items || [];
        if (filters.itemType) {
            items = items.filter(i => i.type.toLowerCase() === filters.itemType.toLowerCase());
        }
        if (filters.rarity) {
            items = items.filter(i => i.rarity.toLowerCase() === filters.rarity.toLowerCase());
        }
        if (filters.maxPrice) {
            items = items.filter(i => i.marketPrice <= filters.maxPrice);
        }
        return items;
    }
}

export default MarketAPI;
