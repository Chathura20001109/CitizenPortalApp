// Store JavaScript (updated)
// - Avoids inline onclick with JSON.stringify
// - Renders DOM nodes safely and attaches event listeners
// - Handles missing fields and provides fallbacks
// - Uses product ID to look up product object when opening modal
// - Small UX improvements: button disable during actions, graceful errors

let cart = JSON.parse(localStorage.getItem('cart')) || [];
let currentProducts = [];
let currentFilters = {};
const CURRENCY_FORMATTER = new Intl.NumberFormat('en-LK');
let lang = localStorage.getItem('lang') || 'en';
let profile_id = localStorage.getItem('profile_id') || null;

// Citizen session helpers
const citizenToken = () => localStorage.getItem('citizen_token') || '';
const citizenId = () => localStorage.getItem('citizen_id') || '';
const citizenName = () => localStorage.getItem('citizen_name') || '';
const isCitizenLoggedIn = () => !!(citizenToken() && citizenId());

function citizenAuthHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${citizenToken()}`,
        'X-Citizen-Id': citizenId()
    };
}

const STORE_TRANSLATIONS = {
    en: {
        "store_title": "🛒 Public Store",
        "back_link": "← Back to Portal",
        "cart_btn": "🛒 Cart",
        "filters_heading": "Filters",
        "cat_heading": "Categories",
        "price_heading": "Price Range",
        "delivery_heading": "Delivery Options",
        "del_home": "Home Delivery",
        "del_pickup": "Store Pickup",
        "del_online": "Online",
        "btn_apply": "Apply Filters",
        "btn_clear": "Clear All",
        "prod_title": "Featured Products",
        "sort_feat": "Featured",
        "sort_low": "Price: Low to High",
        "sort_high": "Price: High to Low",
        "sort_rate": "Highest Rated",
        "sort_new": "Newest First",
        "loading": "Loading products...",
        "cart_title": "Shopping Cart",
        "total": "Total:",
        "checkout": "Proceed to Checkout",
        "close": "Close",
        "hero_title1": "Premium Citizen Services,",
        "hero_title2": "Direct to your door.",
        "hero_desc": "Access the official marketplace for fast track logistics, secure processing, and guaranteed public assurance.",
        "search_placeholder": "Search by name...",
        "mock_secure": "Secure Checkout",
        "mock_test": "TEST MODE",
        "mock_card": "Card Number",
        "mock_exp": "Expiry Date",
        "mock_cvv": "CVV",
        "mock_name": "Cardholder Name",
        "mock_secured": "Secured by Mock Gateway API",
        "cat_education": "Education",
        "cat_visa_services": "Visa Services",
        "cat_electronics": "Electronics",
        "cat_fashion": "Fashion",
        "cat_professional_services": "Professional Services",
        "cat_training": "Training",
        "cat_jobs": "Jobs",
        "cat_agriculture": "Agriculture",
        "trust_fast_title": "Fast Delivery",
        "trust_fast_desc": "Nationwide coverage",
        "trust_gov_title": "Gov Verified",
        "trust_gov_desc": "100% Authentic Services",
        "trust_247_title": "24/7 Support",
        "trust_247_desc": "Dedicated citizen helpline"
    },
    si: {
        "store_title": "🛒 පොදු වෙළඳසැල",
        "back_link": "← ප්‍රධාන පිටුවට",
        "cart_btn": "🛒 කූඩය",
        "filters_heading": "පෙරහන්",
        "cat_heading": "වර්ගීකරණය",
        "price_heading": "මිල පරාසය",
        "delivery_heading": "බෙදා හැරීමේ විකල්ප",
        "del_home": "නිවසටම ගෙනැවිත් දීම",
        "del_pickup": "වෙළඳසැලෙන් ලබාගැනීම",
        "del_online": "මාර්ගගත තහවුරුකිරීම",
        "btn_apply": "පෙරහන් යොදන්න",
        "btn_clear": "සියල්ල ඉවත් කරන්න",
        "prod_title": "විශේෂිත නිෂ්පාදන",
        "sort_feat": "විශේෂිත",
        "sort_low": "මිල: අඩුවේ සිට වැඩියට",
        "sort_high": "මිල: වැඩියේ සිට අඩුවට",
        "sort_rate": "ඉහළම ශ්‍රේණිගත කිරීම්",
        "sort_new": "නවීනතම",
        "loading": "නිෂ්පාදන පූරණය වෙමින්...",
        "cart_title": "ඔබේ කූඩය",
        "total": "මුළු එකතුව:",
        "checkout": "මුදල් ගෙවීම සඳහා",
        "close": "වසා දමන්න",
        "hero_title1": "උසස් පුරවැසි සේවා,",
        "hero_title2": "ඔබේ නිවසටම.",
        "hero_desc": "වේගවත් සැපයුම්, ආරක්ෂිත සැකසුම්, සහ සහතික කළ මහජන විශ්වාසය සඳහා නිල වෙළඳපොළට පිවිසෙන්න.",
        "search_placeholder": "නමින් සොයන්න...",
        "mock_secure": "ආරක්ෂිත ගෙවීමක්",
        "mock_test": "පරීක්ෂණ මාදිලිය",
        "mock_card": "කාඩ්පත් අංකය",
        "mock_exp": "කල් ඉකුත්වන දිනය",
        "mock_cvv": "CVV",
        "mock_name": "කාඩ්පතේ ඇති නම",
        "mock_secured": "Mock Gateway API මගින් ආරක්ෂිතයි",
        "cat_education": "අධ්‍යාපන",
        "cat_visa_services": "වීසා සේවා",
        "cat_electronics": "විද්‍යුත් උපකරණ",
        "cat_fashion": "විලාසිතා",
        "cat_professional_services": "වෘත්තීය සේවා",
        "cat_training": "පුහුණු කටයුතු",
        "cat_jobs": "රැකියා",
        "cat_agriculture": "කෘෂිකර්මය",
        "trust_fast_title": "වේගවත් බෙදාහැරීම",
        "trust_fast_desc": "දිවයින පුරා ආවරණය",
        "trust_gov_title": "රජය තහවුරු කළ",
        "trust_gov_desc": "100% අව්‍යාජ සේවා",
        "trust_247_title": "24/7 සහාය",
        "trust_247_desc": "කැපවූ පුරවැසි උපකාරක සේවාව"
    },
    ta: {
        "store_title": "🛒 பொது கடை",
        "back_link": "← பின்னால்",
        "cart_btn": "🛒 கூடை",
        "filters_heading": "வடிப்பான்கள்",
        "cat_heading": "வகைகள்",
        "price_heading": "விலை",
        "delivery_heading": "டெலிவரி",
        "del_home": "வீடு",
        "del_pickup": "கடை",
        "del_online": "ஆன்லைன்",
        "btn_apply": "பயன்படுத்துக",
        "btn_clear": "அழிக்கவும்",
        "prod_title": "சிறப்பு",
        "sort_feat": "சிறப்பு",
        "sort_low": "விலை: குறைவானது",
        "sort_high": "விலை: அதிகமானது",
        "sort_rate": "அதிக மதிப்பீடு",
        "sort_new": "புதியது",
        "loading": "ஏற்றுகிறது...",
        "cart_title": "கூடை",
        "total": "மொத்தம்:",
        "checkout": "செக்அவுட்",
        "close": "மூடு",
        "hero_title1": "பிரீமியம் குடிமக்கள் சேவைகள்,",
        "hero_title2": "உங்கள் வீட்டு வாசலுக்கு.",
        "hero_desc": "துரித தளவாடங்கள், பாதுகாப்பான செயலாக்கங்கள் மற்றும் உறுதிப்படுத்தப்பட்ட பொது நம்பகத்தன்மைக்கான அதிகாரப்பூர்வ சந்தையை அணுகவும்.",
        "search_placeholder": "பெயரால் தேடுக...",
        "mock_secure": "பாதுகாப்பான கட்டணம்",
        "mock_test": "சோதனை முறை",
        "mock_card": "அட்டை எண்",
        "mock_exp": "காலாவதி தேதி",
        "mock_cvv": "CVV",
        "mock_name": "அட்டைதாரரின் பெயர்",
        "mock_secured": "Mock Gateway API மூலம் பாதுகாக்கப்படுகிறது",
        "cat_education": "கல்வி",
        "cat_visa_services": "விசா சேவைகள்",
        "cat_electronics": "மின்னணுவியல்",
        "cat_fashion": "பேஷன்",
        "cat_professional_services": "தொழில்முறை சேவைகள்",
        "cat_training": "பயிற்சி",
        "cat_jobs": "வேலைகள்",
        "cat_agriculture": "வேளாண்மை",
        "trust_fast_title": "விரைவான விநியோகம்",
        "trust_fast_desc": "நாடு தழுவிய கவரேஜ்",
        "trust_gov_title": "அரசு சரிபார்க்கப்பட்டது",
        "trust_gov_desc": "100% உண்மையான சேவைகள்",
        "trust_247_title": "24/7 ஆதரவு",
        "trust_247_desc": "அர்ப்பணிப்பு குடிமக்கள் உதவி எண்"
    }
};

let cachedStoreCategories = [];

function setStoreLang(language) {
    lang = language;
    localStorage.setItem('lang', lang);
    updateStoreTranslations();
    // Re-render category filters from cache (no duplicate re-fetch)
    renderStoreCategories();
    // Re-render products with new language (product names etc.)
    renderProducts(currentProducts);
}

function updateStoreTranslations() {
    const t = STORE_TRANSLATIONS[lang] || STORE_TRANSLATIONS['en'];
    if (!t) return;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key] !== undefined) {
            if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                el.placeholder = t[key];
            } else if (key === 'cart_btn') {
                // Special case: preserve cart count span
                const count = document.getElementById('cart-count');
                const countVal = count ? count.textContent : '0';
                el.innerHTML = `${t[key]} (<span id="cart-count">${countVal}</span>)`;
            } else {
                el.textContent = t[key];
            }
        }
    });
}

function renderStoreCategories() {
    const container = document.getElementById('category-filters');
    if (!container || !cachedStoreCategories.length) return;
    container.innerHTML = '';
    const t = STORE_TRANSLATIONS[lang] || STORE_TRANSLATIONS['en'];
    cachedStoreCategories.forEach(category => {
        const label = document.createElement('label');
        label.className = 'category-label';
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.name = 'category';
        input.value = category;
        const catKey = 'cat_' + category;
        const displayStr = t[catKey] ? t[catKey] : (category.charAt(0).toUpperCase() + category.slice(1)).replace(/_/g, ' ');
        const text = document.createTextNode(' ' + displayStr);
        label.appendChild(input);
        label.appendChild(text);
        container.appendChild(label);
    });
}

// Initialize store
async function initStore() {
    updateStoreTranslations();
    await loadCategories();
    await loadProducts();
    updateCartCount();
}

// Load categories (fetch once, cache, then render)
async function loadCategories() {
    try {
        const res = await fetch('/api/store/categories');
        const data = await res.json();
        // Deduplicate categories
        const seen = new Set();
        cachedStoreCategories = (data.categories || []).filter(c => {
            if (seen.has(c)) return false;
            seen.add(c);
            return true;
        });
        renderStoreCategories();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load products
async function loadProducts() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'block';

    const params = new URLSearchParams();

    if (citizenId()) {
        params.append('user_id', citizenId());
    }

    // Add filters
    if (currentFilters.category) {
        params.append('category', currentFilters.category);
    }
    if (currentFilters.minPrice) {
        params.append('min_price', currentFilters.minPrice);
    }
    if (currentFilters.maxPrice) {
        params.append('max_price', currentFilters.maxPrice);
    }

    try {
        const res = await fetch(`/api/store/products?${params}`);
        currentProducts = await res.json() || [];

        // Normalize product ids (accept both db _id-based and explicit id)
        currentProducts = currentProducts.map(p => {
            // ensure id exists
            if (!p.id) {
                if (p._id) p.id = (typeof p._id === 'object' ? p._id.$oid || String(p._id) : String(p._id));
            }
            return p;
        });

        // Sort products
        const sortBy = document.getElementById('sort-by')?.value || 'featured';
        sortProducts(sortBy);

        displayProducts(currentProducts);
    } catch (error) {
        console.error('Error loading products:', error);
        showNotification('Error loading products', 'error');
    } finally {
        if (loading) loading.style.display = 'none';
    }
}

function sortProducts(sortBy) {
    switch (sortBy) {
        case 'price_low':
            currentProducts.sort((a, b) => (a.price || 0) - (b.price || 0));
            break;
        case 'price_high':
            currentProducts.sort((a, b) => (b.price || 0) - (a.price || 0));
            break;
        case 'rating':
            currentProducts.sort((a, b) => (b.rating || 0) - (a.rating || 0));
            break;
        case 'newest':
            currentProducts.sort((a, b) => {
                const da = new Date(a.created || 0).getTime();
                const db = new Date(b.created || 0).getTime();
                return db - da;
            });
            break;
        default:
            // featured - keep original order
            break;
    }
}

// Display products (creates elements and attaches listeners)
function displayProducts(products) {
    const container = document.getElementById('products-container');
    const suggSection = document.getElementById('suggested-section');
    const suggContainer = document.getElementById('suggested-container');
    
    if (!container) return;

    if (!Array.isArray(products) || products.length === 0) {
        container.innerHTML = '<div class="no-products">No products found matching your criteria.</div>';
        if (suggSection) suggSection.style.display = 'none';
        return;
    }

    let mainProducts = products;
    let suggestedProducts = [];

    const noFilters = (!currentFilters.category || currentFilters.category === '') && 
                      (!currentFilters.minPrice || currentFilters.minPrice === 0) && 
                      (!currentFilters.maxPrice || currentFilters.maxPrice === 500000);
                      
    if (citizenId() && noFilters) {
        suggestedProducts = products.filter(p => p.recommendation_score > 0).slice(0, 4);
        if (suggestedProducts.length > 0) {
            const suggIds = suggestedProducts.map(p => p.id);
            mainProducts = products.filter(p => !suggIds.includes(p.id));
        }
    }

    if (suggSection && suggContainer) {
        if (suggestedProducts.length > 0) {
            suggSection.style.display = 'block';
            suggContainer.innerHTML = '';
            suggestedProducts.forEach(prod => renderProductCard(prod, suggContainer));
        } else {
            suggSection.style.display = 'none';
        }
    }

    // Clear container
    container.innerHTML = '';
    mainProducts.forEach(prod => renderProductCard(prod, container));
}

// Alias used by setStoreLang for re-rendering with new language
const renderProducts = displayProducts;

function renderProductCard(product, container) {
    const prod = product || {};
    const price = Number(prod.price || 0);
    const original = Number(prod.original_price || 0);
    const discount = original > 0 ? Math.round((1 - price / original) * 100) : 0;
    const rating = Math.max(0, Math.min(5, Math.floor(Number(prod.rating || 0))));

    const card = document.createElement('div');
    card.className = 'product-card';
    card.tabIndex = 0;
    card.dataset.productId = prod.id || '';

    // Wishlist setup
    let wishlistIds = JSON.parse(localStorage.getItem('wishlist') || '[]');

    // Click opens modal for that product id
    card.addEventListener('click', () => openProductModal(prod.id));
    card.addEventListener('keypress', (e) => { if (e.key === 'Enter') openProductModal(prod.id); });

    const imageWrap = document.createElement('div');
    imageWrap.className = 'product-image';
    const imgPlaceholder = document.createElement('div');
    imgPlaceholder.style.cssText = 'width:100%;height:140px;background:#e5e7eb;display:flex;align-items:center;justify-content:center;font-size:40px;border-radius:8px;';
    imgPlaceholder.textContent = prod.images && prod.images[0] ? '' : '📦';
    // Proper fallback images per product id or category
    const PRODUCT_IMAGE_MAP = {
        'prod_bit':         'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400&auto=format&fit=crop',
        'prod_ielts':       'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&auto=format&fit=crop',
        'prod_japan_visa':  'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&auto=format&fit=crop',
        'prod_dell_laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&auto=format&fit=crop',
        'prod_saree':       'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=400&auto=format&fit=crop',
        'prod_ol_tuition':  'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&auto=format&fit=crop',
        'prod_slas':        'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&auto=format&fit=crop',
        'prod_data_entry':  'https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=400&auto=format&fit=crop',
        'prod_coding_camp': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=400&auto=format&fit=crop',
        'prod_leadership':  'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=400&auto=format&fit=crop',
        'prod_solar_panel': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400&auto=format&fit=crop',
        'prod_tax_consultation': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&auto=format&fit=crop',
        'prod_organic_fert': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&auto=format&fit=crop',
        'prod_driver_training': 'https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400&auto=format&fit=crop',
    };
    const CATEGORY_IMAGE_MAP = {
        'education':    'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&auto=format&fit=crop',
        'electronics':  'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&auto=format&fit=crop',
        'fashion':      'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&auto=format&fit=crop',
        'visa_services':'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=400&auto=format&fit=crop',
        'professional_services': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&auto=format&fit=crop',
        'training':     'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&auto=format&fit=crop',
        'jobs':         'https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=400&auto=format&fit=crop',
        'agriculture':  'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&auto=format&fit=crop',
    };
    
    const resolvedImage = (prod.images && prod.images[0])
        || PRODUCT_IMAGE_MAP[prod.id]
        || CATEGORY_IMAGE_MAP[prod.category]
        || 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400&auto=format&fit=crop';

    if (resolvedImage) {
        const img = document.createElement('img');
        img.src = resolvedImage;
        img.alt = prod.name || 'Product';
        img.style.cssText = 'width:100%;height:100%;object-fit:cover;transition:transform 0.5s ease;';
        img.onerror = () => {
            img.src = 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400&auto=format&fit=crop';
        };
        imageWrap.appendChild(img);
    }
    if (discount > 0) {
        const disc = document.createElement('div');
        disc.className = 'discount-badge';
        disc.textContent = `-${discount}%`;
        imageWrap.appendChild(disc);
    }

    // --- Further Features for Public Store ---
    imageWrap.style.position = 'relative';
    imageWrap.style.overflow = 'hidden';

    // 1. Wishlist Button Feature
    const wishBtn = document.createElement('button');
    wishBtn.className = 'wishlist-btn';
    wishBtn.innerHTML = wishlistIds.includes(prod.id) ? '❤️' : '🤍';
    if (wishlistIds.includes(prod.id)) wishBtn.classList.add('active');
    wishBtn.onclick = (e) => {
        e.stopPropagation(); // Avoid triggering card click
        let wIds = JSON.parse(localStorage.getItem('wishlist') || '[]');
        if (wIds.includes(prod.id)) {
            wIds = wIds.filter(x => x !== prod.id);
            wishBtn.innerHTML = '🤍';
            wishBtn.style.transform = 'scale(1)';
        } else {
            wIds.push(prod.id);
            wishBtn.innerHTML = '❤️';
            wishBtn.style.transform = 'scale(1.2)';
            setTimeout(() => wishBtn.style.transform = 'scale(1)', 200);
        }
        localStorage.setItem('wishlist', JSON.stringify(wIds));
    };
    wishBtn.style.cssText = 'position: absolute; top: 12px; right: 12px; border: none; background: rgba(255,255,255,0.25); backdrop-filter: blur(8px); border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 3; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 4px 6px rgba(0,0,0,0.1);';
    wishBtn.onmouseover = () => wishBtn.style.background = 'rgba(255,255,255,0.7)';
    wishBtn.onmouseout = () => wishBtn.style.background = 'rgba(255,255,255,0.25)';
    imageWrap.appendChild(wishBtn);

    // 2. Quick View Overlay Feature
    const quickViewBtn = document.createElement('button');
    quickViewBtn.className = 'quick-view-btn';
    quickViewBtn.innerHTML = '👁️ Quick View';
    quickViewBtn.style.cssText = 'position: absolute; bottom: -40px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; border: none; border-radius: 20px; padding: 6px 14px; font-weight: 600; font-size: 12px; cursor: pointer; transition: all 0.3s ease; opacity: 0; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4); z-index: 2; pointer-events: none;';
    quickViewBtn.onclick = (e) => { e.stopPropagation(); openProductModal(prod.id); };
    imageWrap.appendChild(quickViewBtn);

    card.onmouseenter = () => {
        quickViewBtn.style.bottom = '12px';
        quickViewBtn.style.opacity = '1';
        quickViewBtn.style.pointerEvents = 'auto';
    };
    card.onmouseleave = () => {
        quickViewBtn.style.bottom = '-40px';
        quickViewBtn.style.opacity = '0';
        quickViewBtn.style.pointerEvents = 'none';
    };

    card.appendChild(imageWrap);

    const info = document.createElement('div');
    info.className = 'product-info';

    const h3 = document.createElement('h3');
    h3.className = 'product-name';
    h3.textContent = prod.name || 'Unnamed product';
    info.appendChild(h3);

    const priceDiv = document.createElement('div');
    priceDiv.className = 'product-price';
    if (original > 0) {
        const origSpan = document.createElement('span');
        origSpan.className = 'original-price';
        origSpan.textContent = `LKR ${CURRENCY_FORMATTER.format(original)}`;
        priceDiv.appendChild(origSpan);
    }
    const currSpan = document.createElement('span');
    currSpan.className = 'current-price';
    currSpan.textContent = `LKR ${CURRENCY_FORMATTER.format(price)}`;
    priceDiv.appendChild(currSpan);
    info.appendChild(priceDiv);

    const ratingDiv = document.createElement('div');
    ratingDiv.className = 'product-rating';
    ratingDiv.textContent = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    const rc = document.createElement('span');
    rc.className = 'rating-count';
    rc.textContent = ` (${prod.reviews_count || 0})`;
    ratingDiv.appendChild(rc);
    info.appendChild(ratingDiv);

    const btn = document.createElement('button');
    btn.className = 'add-to-cart-btn';
    btn.type = 'button';
    btn.textContent = 'Add to Cart';
    // Stop card click from triggering when clicking button
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        btn.disabled = true;

        // Advanced visual confirmation logic (Fly to cart framework)
        const imgToFly = imageWrap.querySelector('img');
        if (imgToFly) {
            const flyImg = imgToFly.cloneNode(true);
            const rect = imgToFly.getBoundingClientRect();
            flyImg.style.position = 'fixed';
            flyImg.style.left = rect.left + 'px';
            flyImg.style.top = rect.top + 'px';
            flyImg.style.width = rect.width + 'px';
            flyImg.style.height = rect.height + 'px';
            flyImg.style.zIndex = '9999';
            flyImg.style.transition = 'all 0.8s cubic-bezier(0.25, 1, 0.5, 1)';
            flyImg.style.borderRadius = '8px';
            flyImg.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
            document.body.appendChild(flyImg);

            const cartBtn = document.getElementById('cart-btn');
            const cartRect = cartBtn.getBoundingClientRect();

            requestAnimationFrame(() => {
                flyImg.style.left = (cartRect.left + cartRect.width / 2 - 20) + 'px';
                flyImg.style.top = (cartRect.top + cartRect.height / 2 - 20) + 'px';
                flyImg.style.width = '40px';
                flyImg.style.height = '40px';
                flyImg.style.opacity = '0';
                flyImg.style.transform = 'scale(0.1) rotate(15deg)';
            });

            setTimeout(() => {
                flyImg.remove();
                cartBtn.style.transform = 'scale(1.2)';
                cartBtn.style.transition = 'transform 0.2s';
                setTimeout(() => cartBtn.style.transform = 'scale(1)', 200);
            }, 800);
        }

        addToCart(prod.id);
        btn.innerHTML = '✔ Added';
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = 'Add to Cart';
        }, 1000);
    });
    info.appendChild(btn);

    card.appendChild(info);
    container.appendChild(card);
}

// Cart management
function addToCart(productId) {
    const product = currentProducts.find(p => p.id === productId);
    if (!product) {
        showNotification('Product not found', 'error');
        return;
    }

    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: product.name || 'Unnamed product',
            price: Number(product.price || 0),
            quantity: 1
        });
    }

    updateCart();
    showNotification(`${product.name} added to cart!`);
}

function updateCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    updateCartModal(); // keep modal in sync if open
}

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const el = document.getElementById('cart-count');
    if (el) el.textContent = count;
}

function viewCart() {
    const modal = document.getElementById('cart-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    updateCartModal();
}

function closeCart() {
    const modal = document.getElementById('cart-modal');
    if (modal) modal.style.display = 'none';
}

function updateCartModal() {
    const container = document.getElementById('cart-items');
    const total = document.getElementById('cart-total');

    if (!container || !total) return;

    if (cart.length === 0) {
        container.innerHTML = '<p style="text-align:center;padding:40px;color:#6b7280;">Your cart is empty</p>';
        total.textContent = '0';
        return;
    }

    container.innerHTML = '';
    cart.forEach(item => {
        const itemEl = document.createElement('div');
        itemEl.className = 'cart-item';

        const imgBox = document.createElement('div');
        imgBox.style.cssText = 'width:80px;height:80px;background:#e5e7eb;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:30px;';
        imgBox.textContent = '📦';
        itemEl.appendChild(imgBox);

        const info = document.createElement('div');
        info.className = 'cart-item-info';
        const h4 = document.createElement('h4');
        h4.textContent = item.name;
        const p = document.createElement('div');
        p.className = 'cart-item-price';
        p.textContent = `LKR ${CURRENCY_FORMATTER.format(item.price)}`;
        info.appendChild(h4);
        info.appendChild(p);
        itemEl.appendChild(info);

        const controls = document.createElement('div');
        controls.className = 'cart-item-controls';

        const btnDec = document.createElement('button');
        btnDec.type = 'button';
        btnDec.textContent = '-';
        btnDec.addEventListener('click', () => updateQuantity(item.id, -1));
        controls.appendChild(btnDec);

        const qtySpan = document.createElement('span');
        qtySpan.textContent = item.quantity;
        controls.appendChild(qtySpan);

        const btnInc = document.createElement('button');
        btnInc.type = 'button';
        btnInc.textContent = '+';
        btnInc.addEventListener('click', () => updateQuantity(item.id, 1));
        controls.appendChild(btnInc);

        const btnRemove = document.createElement('button');
        btnRemove.type = 'button';
        btnRemove.textContent = 'Remove';
        btnRemove.style.color = '#ef4444';
        btnRemove.addEventListener('click', () => removeFromCart(item.id));
        controls.appendChild(btnRemove);

        itemEl.appendChild(controls);
        container.appendChild(itemEl);
    });

    const cartTotal = cart.reduce((t, item) => t + (item.price * item.quantity), 0);
    total.textContent = CURRENCY_FORMATTER.format(cartTotal);
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(productId);
        } else {
            updateCart();
        }
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    updateCart();
}

// Product modal (lookup by id)
function openProductModal(productId) {
    const product = currentProducts.find(p => p.id === productId);
    if (!product) return;
    const modal = document.getElementById('product-modal');
    const content = document.getElementById('modal-content');

    if (!modal || !content) return;

    const price = Number(product.price || 0);
    const original = Number(product.original_price || 0);
    const discount = original > 0 ? Math.round((1 - price / original) * 100) : 0;
    const rating = Math.max(0, Math.min(5, Math.floor(Number(product.rating || 0))));

    // Build modal content safely
    content.innerHTML = '';
    const grid = document.createElement('div');
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = '1fr 1fr';
    grid.style.gap = '30px';

    const left = document.createElement('div');
    const imgBox = document.createElement('div');
    imgBox.style.cssText = 'width:100%;height:400px;background:#e5e7eb;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:80px;';
    const resolvedImage = (product.images && product.images[0])
        || PRODUCT_IMAGE_MAP[product.id]
        || CATEGORY_IMAGE_MAP[product.category]
        || 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=400&auto=format&fit=crop';

    if (resolvedImage) {
        const img = document.createElement('img');
        img.src = resolvedImage;
        img.alt = product.name || 'Product';
        img.onerror = () => { imgBox.textContent = '📦'; img.remove(); };
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.borderRadius = '12px';
        imgBox.appendChild(img);
    } else {
        imgBox.textContent = '📦';
    }
    left.appendChild(imgBox);
    grid.appendChild(left);

    const right = document.createElement('div');
    const title = document.createElement('h2');
    title.style.marginBottom = '15px';
    title.textContent = product.name || '';
    right.appendChild(title);

    const priceWrap = document.createElement('div');
    priceWrap.style.marginBottom = '15px';
    if (original > 0) {
        const origSpan = document.createElement('span');
        origSpan.style.textDecoration = 'line-through';
        origSpan.style.color = '#6b7280';
        origSpan.style.marginRight = '10px';
        origSpan.textContent = `LKR ${CURRENCY_FORMATTER.format(original)}`;
        priceWrap.appendChild(origSpan);
    }
    const currSpan = document.createElement('span');
    currSpan.style.color = '#1e40af';
    currSpan.style.fontSize = '28px';
    currSpan.style.fontWeight = '700';
    currSpan.textContent = `LKR ${CURRENCY_FORMATTER.format(price)}`;
    priceWrap.appendChild(currSpan);
    if (discount > 0) {
        const discBadge = document.createElement('span');
        discBadge.style.background = '#ef4444';
        discBadge.style.color = 'white';
        discBadge.style.padding = '4px 8px';
        discBadge.style.borderRadius = '4px';
        discBadge.style.fontSize = '12px';
        discBadge.style.marginLeft = '10px';
        discBadge.textContent = `-${discount}%`;
        priceWrap.appendChild(discBadge);
    }
    right.appendChild(priceWrap);

    const ratingDiv = document.createElement('div');
    ratingDiv.style.marginBottom = '20px';
    ratingDiv.style.color = '#fbbf24';
    ratingDiv.textContent = '★'.repeat(rating) + '☆'.repeat(5 - rating);
    const rc = document.createElement('span');
    rc.style.color = '#6b7280';
    rc.textContent = ` (${product.reviews_count || 0} reviews)`;
    ratingDiv.appendChild(rc);
    right.appendChild(ratingDiv);

    const desc = document.createElement('p');
    desc.style.marginBottom = '20px';
    desc.style.lineHeight = '1.6';
    desc.textContent = product.description || '';
    right.appendChild(desc);

    if (Array.isArray(product.features) && product.features.length) {
        const featuresWrap = document.createElement('div');
        featuresWrap.style.marginBottom = '20px';
        const hf = document.createElement('h4');
        hf.style.marginBottom = '10px';
        hf.textContent = 'Features:';
        featuresWrap.appendChild(hf);
        const ul = document.createElement('ul');
        ul.style.listStyle = 'none';
        ul.style.padding = '0';
        product.features.forEach(f => {
            const li = document.createElement('li');
            li.style.padding = '5px 0';
            li.textContent = `✓ ${f}`;
            ul.appendChild(li);
        });
        featuresWrap.appendChild(ul);
        right.appendChild(featuresWrap);
    }

    const actions = document.createElement('div');
    actions.style.display = 'flex';
    actions.style.gap = '10px';

    const btnAdd = document.createElement('button');
    btnAdd.type = 'button';
    btnAdd.style.cssText = 'flex:1;background:#1e40af;color:white;border:none;padding:15px;border-radius:8px;font-weight:600;cursor:pointer;';
    btnAdd.textContent = 'Add to Cart';
    btnAdd.addEventListener('click', () => {
        addToCart(product.id);
        closeModal();
    });

    const btnBuy = document.createElement('button');
    btnBuy.type = 'button';
    btnBuy.style.cssText = 'flex:1;background:#10b981;color:white;border:none;padding:15px;border-radius:8px;font-weight:600;cursor:pointer;';
    btnBuy.textContent = 'Buy Now';
    btnBuy.addEventListener('click', () => {
        addToCart(product.id);
        closeModal();
        viewCart();
    });

    actions.appendChild(btnAdd);
    actions.appendChild(btnBuy);
    right.appendChild(actions);

    grid.appendChild(right);
    content.appendChild(grid);

    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('product-modal');
    if (modal) modal.style.display = 'none';
}

// Filter functions
function applyFilters() {
    const categoryCheckboxes = document.querySelectorAll('input[name="category"]:checked');
    const deliveryCheckboxes = document.querySelectorAll('input[name="delivery"]:checked');
    const maxPrice = document.getElementById('price-range')?.value || 500000;

    currentFilters = {
        category: Array.from(categoryCheckboxes).map(cb => cb.value).join(','),
        delivery: Array.from(deliveryCheckboxes).map(cb => cb.value),
        minPrice: 0,
        maxPrice: parseInt(maxPrice)
    };

    loadProducts();
}

function clearFilters() {
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    const priceRange = document.getElementById('price-range');
    if (priceRange) priceRange.value = 500000;
    updatePriceDisplay();
    currentFilters = {};
    loadProducts();
}

function updatePriceDisplay() {
    const range = document.getElementById('price-range');
    const display = document.getElementById('max-price-display') || document.getElementById('max-price');
    if (range && display) {
        display.textContent = parseInt(range.value).toLocaleString();
    }
}

// Checkout
let currentOrderId = null;

async function checkout() {
    if (!isCitizenLoggedIn()) {
        showNotification('Please login or register to place an order.', 'error');
        setTimeout(() => window.location.href = '/citizen/login', 1500);
        return;
    }

    if (cart.length === 0) {
        showNotification('Your cart is empty', 'error');
        return;
    }

    const orderData = {
        user_id: profile_id,
        items: cart,
        total: cart.reduce((total, item) => total + (item.price * item.quantity), 0),
        payment_method: 'card'
    };

    try {
        const res = await fetch('/api/store/order', {
            method: 'POST',
            headers: citizenAuthHeaders(),
            body: JSON.stringify(orderData)
        });

        const result = await res.json();

        if (result.status === 'ok') {
            currentOrderId = result.order_id;
            openPaymentModal();
        } else {
            showNotification('Order creation failed', 'error');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showNotification('Checkout failed. Please try again.', 'error');
    }
}

function openPaymentModal() {
    const modal = document.getElementById('payment-modal');
    const amountEl = document.getElementById('sandbox-amount');

    const total = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
    if (amountEl) {
        amountEl.textContent = `Pay LKR ${CURRENCY_FORMATTER.format(total)}`;
    }

    if (modal) {
        modal.style.display = 'flex';
    }
}

function closePaymentModal() {
    const modal = document.getElementById('payment-modal');
    if (modal) modal.style.display = 'none';
}

function confirmPayment() {
    const card = document.getElementById('sandbox-card')?.value;
    const expiry = document.getElementById('sandbox-expiry')?.value;
    const cvv = document.getElementById('sandbox-cvv')?.value;
    const btn = document.getElementById('btn-pay-now');

    if (!card || !expiry || !cvv) {
        showNotification('Please fill in mock card details to test sandbox', 'error');
        return;
    }

    if (btn) {
        btn.innerHTML = '<span style="display:inline-block; margin-right:8px;">⏳</span> Processing...';
        btn.disabled = true;
    }

    // Simulate API delay
    setTimeout(() => {
        processPayment(currentOrderId).then(() => {
            closePaymentModal();
            if (btn) {
                btn.innerHTML = '<strong id="sandbox-amount">Pay Now</strong>';
                btn.disabled = false;
            }
        });
    }, 1500);
}

async function processPayment(orderId) {
    const paymentData = {
        order_id: orderId,
        user_id: localStorage.getItem('profile_id'),
        amount: cart.reduce((total, item) => total + (item.price * item.quantity), 0),
        method: 'card',
        items: cart,
        transaction_id: 'TXN' + Date.now()
    };

    try {
        const res = await fetch('/api/store/payment', {
            method: 'POST',
            headers: citizenAuthHeaders(),
            body: JSON.stringify(paymentData)
        });

        const result = await res.json();

        if (result.status === 'ok') {
            showNotification('Order placed successfully! Thank you for your purchase.');
            cart = [];
            updateCart();
            closeCart();
        } else {
            showNotification('Payment failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Payment error:', error);
        showNotification('Payment failed. Please try again.', 'error');
    }
}

// Notification
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    if (!notification) {
        // fallback to alert
        if (type === 'error') console.error(message);
        else console.info(message);
        return;
    }

    notification.textContent = message;
    notification.style.background = type === 'error' ? '#ef4444' : '#10b981';
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', initStore);