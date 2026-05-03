// Enhanced Citizen Portal - Main JavaScript with Animations (updated)
// - Safer DOM handling (avoid inline onclick with JSON.stringify)
// - Better autosuggest rendering with event handlers (no inner onclick)
// - Debounce & error handling improvements
// - Log engagements to enhanced endpoint
// - Fallbacks for API endpoints where appropriate

const API_FALLBACKS = {
    categories: ["/api/categories", "/api/store/categories"],
    services: ["/api/services"],
    serviceById: (id) => [`/api/service/${id}`],
    ads: ["/api/ads", "/api/announcements"],
    engagement: ["/api/engagement/enhanced", "/api/engagement"],
    profileStep: ["/api/profile/step"],
    aiSearch: ["/api/ai/search"],
    autosuggest: ["/api/search/autosuggest"]
};

let lang = localStorage.getItem('lang') || "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = localStorage.getItem('profile_id') || null;
let suggestTimer = null;
let sessionId = generateSessionId();

let currentCatObj = null;
let currentServiceObj = null;
let currentQuestionObj = null;
let cachedSuggestions = new Map();

// Citizen session
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

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).slice(2, 11);
}

// Small helper for JSON fetch with fallback endpoints
async function fetchJSONWithFallback(urls, options = {}) {
    if (!Array.isArray(urls)) urls = [urls];
    let lastErr = null;
    for (const u of urls) {
        try {
            const res = await fetch(u, options);
            if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
            const text = await res.text();
            // allow endpoints that return empty body
            if (!text) return null;
            return JSON.parse(text);
        } catch (err) {
            lastErr = err;
        }
    }
    throw lastErr;
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// Translations
const TRANSLATIONS = {
    en: {
        "heading_main": "🏛️ Digital Citizen Services",
        "subtitle_main": "Government of Sri Lanka",
        "cat_title": "Categories",
        "quick_title": "Quick Access",
        "btn_profile": "👤 Create Profile",
        "btn_store": "🛒 Public Store",
        "btn_admin": "👨‍💼 Admin Login",
        "ads_title": "Announcements",
        "sub_title_default": "Select Ministry Service",
        "sub_help": "Click on a category to see available services",
        "search_ph": "Search services or ask a question...",
        "btn_ask_ai": "Ask AI Assistant",
        "faq_title": "Frequently Asked Questions",
        "faq_help": "Select a service to see questions and answers",
        "chat_title": "🤖 AI Assistant",
        "chat_welcome": "Hello! I'm your AI assistant. Ask me anything about government services.",
        "chat_ph": "Type your question...",
        "btn_send": "Send",
        "footer_cr": "© 2024 Government of Sri Lanka. All rights reserved.",
        "footer_pow": "Powered by Citizen Services Portal",
        "footer_about_title": "About Citizen Portal",
        "footer_about_text": "The official government services portal of Sri Lanka, providing a unified digital experience for all citizens.",
        "footer_services_title": "Quick Links",
        "footer_contact_title": "Contact Support",
        "footer_hotline": "Hotline: 1919",
        "footer_email": "Email: support@citizen.gov.lk",
        "footer_social_title": "Follow Us",
        "hero_title": "Digital Citizen Services",
        "hero_desc": "Experience secure, intelligent, and instantaneous processing of public services directly from your dashboard.",
        "stat_eservices": "E-Services",
        "stat_ai": "AI Support",
        "stat_secure": "Secure",
        "btn_citizen_login": "🔐 Citizen Login",
        "btn_logout": "Logout",
        "lbl_downloads": "📄 Downloads",
        "lbl_location": "📍 Location",
        "lbl_view_map": "View on Map",
        "lbl_instructions": "📋 Instructions",
        "lbl_answer_loaded": "Answer loaded",
        "lbl_no_questions": "No questions available",
        "lbl_no_services": "No services available",
        "lbl_login_required": "Please login to view details.",
        "lbl_welcome": "Welcome"
    },
    si: {
        "heading_main": "🏛️ ඩිජිටල් පුරවැසි සේවාව",
        "subtitle_main": "ශ්‍රී ලංකා රජය",
        "cat_title": "වර්ගීකරණයන්",
        "quick_title": "කඩිනම් ප්‍රවේශය",
        "btn_profile": "👤 පැතිකඩක් සාදන්න",
        "btn_store": "🛒 පොදු වෙළඳසැල",
        "btn_admin": "👨‍💼 පරිපාලක",
        "ads_title": "නිවේදන",
        "sub_title_default": "සේවාව තෝරන්න",
        "sub_help": "සේවාවන් බැලීමට වර්ගයක් තෝරන්න",
        "search_ph": "සේවාවන් සොයන්න...",
        "btn_ask_ai": "AI සහායක",
        "faq_title": "නිතර අසන ප්‍රශ්න",
        "faq_help": "පිළිතුරු බැලීමට සේවාවක් තෝරන්න",
        "chat_title": "🤖 AI සහායක",
        "chat_welcome": "ආයුබෝවන්! මම ඔබේ AI සහායකයා. ඕනෑම දෙයක් අසන්න.",
        "chat_ph": "ප්‍රශ්නය යොමු කරන්න...",
        "btn_send": "යවන්න",
        "footer_cr": "© 2024 ශ්‍රී ලංකා රජය. සියලුම හිමිකම් ඇවිරිණි.",
        "footer_pow": "පුරවැසි ද්වාරය මගින් බලගන්වා ඇත",
        "footer_about_title": "පුරවැසි ද්වාරය ගැන",
        "footer_about_text": "ශ්‍රී ලංකා රජයේ නිල සේවා ද්වාරය, සියලුම පුරවැසියන් සඳහා ඒකාබද්ධ ඩිජිටල් අත්දැකීමක් ලබා දේ.",
        "footer_services_title": "කඩිනම් සබැඳි",
        "footer_contact_title": "සහාය සඳහා",
        "footer_hotline": "ක්ෂණික ඇමතුම්: 1919",
        "footer_email": "විද්‍යුත් තැපෑල: support@citizen.gov.lk",
        "footer_social_title": "අපව අනුගමනය කරන්න",
        "hero_title": "ඩිජිටල් පුරවැසි සේවා",
        "hero_desc": "රාජ්‍ය සේවා ඉක්මනින්, ආරක්ෂිතව, ඔබේ ඇඟිලි සලකුණෙන් — ඔබ සිටින ඕනෑම තැනකින්.",
        "stat_eservices": "විද්‍යුත් සේවා",
        "stat_ai": "AI සහාය",
        "stat_secure": "ආරක්ෂිතයි",
        "btn_citizen_login": "🔐 පුරවැසි ලෝගින්",
        "btn_logout": "ලොග් අවුට්",
        "lbl_downloads": "📄 බාගතකිරීම්",
        "lbl_location": "📍 ස්ථානය",
        "lbl_view_map": "සිතියමේ බලන්න",
        "lbl_instructions": "📋 උපදෙස්",
        "lbl_answer_loaded": "පිළිතුර පූරණය විය",
        "lbl_no_questions": "ප්‍රශ්න නොමැත",
        "lbl_no_services": "සේවා නොමැත",
        "lbl_login_required": "විස්තර බලන්නට ලෝගින් කරන්න.",
        "lbl_welcome": "පිළිගන්නවා"
    },
    ta: {
        "heading_main": "🏛️ டிஜிட்டல் சிட்டிசன் சேவை",
        "subtitle_main": "இலங்கை அரசாங்கம்",
        "cat_title": "வகைகள்",
        "quick_title": "விரைவு அணுகல்",
        "btn_profile": "👤 சுயவிவரம்",
        "btn_store": "🛒 பொது கடை",
        "btn_admin": "👨‍💼 நிர்வாகி",
        "ads_title": "அறிவிப்புகள்",
        "sub_title_default": "சேவையைத் தேர்வுசெய்க",
        "sub_help": "சேவைகளைப் பார்க்க வகையைத் தேர்ந்தெடுக்கவும்",
        "search_ph": "சேவைகளைத் தேடுங்கள்...",
        "btn_ask_ai": "AI உதவியாளர்",
        "faq_title": "கேள்வி பதில்கள்",
        "faq_help": "கேள்விகளைப் பார்க்க சேவையைத் தேர்ந்தெடுக்கவும்",
        "chat_title": "🤖 AI உதவியாளர்",
        "chat_welcome": "வணக்கம்! நான் AI உதவியாளர். எதையும் கேளுங்கள்.",
        "chat_ph": "கேள்வியைத் தட்டச்சு செய்க...",
        "btn_send": "அனுப்பு",
        "footer_cr": "© 2024 இலங்கை அரசு. உரிமைகள் பாதுகாக்கப்பட்டவை.",
        "footer_pow": "குடிமக்கள் சேவை தளத்தால் இயக்கப்படுகிறது",
        "footer_about_title": "குடிமக்கள் தளம் பற்றி",
        "footer_about_text": "இலங்கை அரசாங்கத்தின் அதிகாரப்பூர்வ சேவைகள் தளம், அனைத்து குடிமக்களுக்கும் ஒரு ஒருங்கிணைந்த டிஜிட்டல் அனுபவத்தை வழங்குகிறது.",
        "footer_services_title": "விரைவு இணைப்புகள்",
        "footer_contact_title": "தொடர்பு கொள்ள",
        "footer_hotline": "ஹாட்லைன்: 1919",
        "footer_email": "மின்னஞ்சல்: support@citizen.gov.lk",
        "footer_social_title": "எங்களைப் பின்தொடரவும்",
        "hero_title": "டிஜிட்டல் குடிமக்கள் சேவைகள்",
        "hero_desc": "பொது சேவைகளை பாதுகாப்பாகவும் உடனடியாகவும் உங்கள் டாஷ்போர்டிலிருந்து பெறுங்கள்.",
        "stat_eservices": "மின் சேவைகள்",
        "stat_ai": "AI ஆதரவு",
        "stat_secure": "பாதுகாப்பானது",
        "btn_citizen_login": "🔐 குடிமக் உள்நுழைவு",
        "btn_logout": "வெளியேறு",
        "lbl_downloads": "📄 பதிவிறக்கங்கள்",
        "lbl_location": "📍 இடம்",
        "lbl_view_map": "வரைபடத்தில் காண்",
        "lbl_instructions": "📋 வழிமுறைகள்",
        "lbl_answer_loaded": "பதில் ஏற்றப்பட்டது",
        "lbl_no_questions": "கேள்விகள் இல்லை",
        "lbl_no_services": "சேவைகள் இல்லை",
        "lbl_login_required": "விவரங்களைக் காண உள்நுழைக.",
        "lbl_welcome": "வரவேற்கிறோம்"
    }
};

// Set Language
function setLang(language) {
    lang = language;
    localStorage.setItem('lang', lang);

    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`lang-${language}`);
    if (activeBtn) activeBtn.classList.add('active');

    // Update all static translated elements immediately
    updateTranslations();

    // Re-render category buttons from cached data
    renderCategories();

    // Refresh current dynamic views with new language
    if (currentCatObj) {
        const savedSubId = currentSub ? currentSub.id : null;
        const savedQIndex = (currentSub && currentQuestionObj) ? currentSub.questions.findIndex(q => q.q.en === currentQuestionObj.q.en) : -1;

        (async () => {
            await loadMinistriesInCategory(currentCatObj);
            
            // Restore sub-service active state
            if (savedSubId) {
                const subList = document.getElementById('sub-list');
                if (subList) {
                    const target = subList.querySelector(`[data-sub-id="${savedSubId}"]`);
                    if (target) {
                        // Mark as active but don't just click if we want to be precise
                        document.querySelectorAll('#sub-list li').forEach(l => l.classList.remove('active'));
                        target.classList.add('active');
                        
                        // Load questions in the new language
                        await loadQuestions(currentSub);
                        
                        // Restore question active state and answer
                        if (savedQIndex !== -1) {
                            const qList = document.getElementById('question-list');
                            if (qList) {
                                const qTarget = qList.querySelector(`[data-q-index="${savedQIndex}"]`);
                                if (qTarget) {
                                    document.querySelectorAll('#question-list li').forEach(l => l.classList.remove('active'));
                                    qTarget.classList.add('active');
                                    showAnswer(currentSub, currentSub, currentQuestionObj);
                                }
                            }
                        }
                    }
                }
            }
        })();
    }

    const langNames = { en: 'English 🇬🇧', si: 'සිංහල 🇱🇰', ta: 'தமிழ் 🇱🇰' };
    showToast(`🌐 ${langNames[language] || language.toUpperCase()}`, 'info');
}

function updateTranslations() {
    const t = TRANSLATIONS[lang];
    if (!t) return;

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key] !== undefined) {
            if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
                el.placeholder = t[key];
            } else {
                el.textContent = t[key];
            }
        }
    });

    // Update page title
    if (t['heading_main']) document.title = t['heading_main'].replace(/[^\w\s]/gi, '').trim() + ' - Government of Sri Lanka';
}


// Render categories from cached data (no API call, prevents duplicates)
function renderCategories(autoSelectFirst = false) {
    const el = document.getElementById("category-list");
    if (!el || !categories || categories.length === 0) return;

    el.innerHTML = "";
    categories.forEach((c, index) => {
        const btn = document.createElement("div");
        btn.className = "cat-item";
        btn.tabIndex = 0;
        btn.setAttribute("role", "button");
        btn.dataset.catId = c.id || "";
        btn.innerHTML = `<span style="opacity:0.7;margin-right:8px;">🔹</span> ${(c.name && (c.name[lang] || c.name.en)) || c.id || "Category"}`;
        btn.addEventListener("click", () => {
            document.querySelectorAll('.cat-item').forEach(i => i.classList.remove('active'));
            btn.classList.add('active');
            currentCatObj = c;
            loadMinistriesInCategory(c);
            setMobileLevel(2, "Services");
        });
        btn.addEventListener("keypress", (e) => { if (e.key === "Enter") btn.click(); });
        btn.style.animationDelay = `${index * 0.1}s`;
        el.appendChild(btn);
    });

    if (autoSelectFirst) {
        const firstCatBtn = el.querySelector('.cat-item');
        if (firstCatBtn) firstCatBtn.click();
    } else if (currentCatObj) {
        // Re-highlight the active category after language change
        const activeBtn = el.querySelector(`[data-cat-id="${currentCatObj.id}"]`);
        if (activeBtn) activeBtn.classList.add('active');
    }
}

// Load Categories with animation (fetches from API, called only once)
async function loadCategories() {
    try {
        const data = await fetchJSONWithFallback(API_FALLBACKS.categories);
        categories = Array.isArray(data) ? data : (data.categories || []);

        // Deduplicate by id
        const seen = new Set();
        categories = categories.filter(c => {
            if (seen.has(c.id)) return false;
            seen.add(c.id);
            return true;
        });

        if (!categories || categories.length === 0) {
            const el = document.getElementById("category-list");
            if (el) el.innerHTML = '<p style="color: #6b7280; font-size: 12px;">No categories available</p>';
            return;
        }

        // Render without auto-select (user must click)
        renderCategories(false);

        // Load ads concurrently
        loadAds().catch(err => console.warn("Ads load failed", err));

    } catch (error) {
        console.error("Error loading categories:", error);
        showToast("Failed to load categories", "error");
    }
}

// Load Ministries in Category
async function loadMinistriesInCategory(cat) {
    try {
        currentCatObj = cat;
        currentServiceObj = null;
        currentSub = null;
        currentQuestionObj = null;

        const subList = document.getElementById("sub-list");
        const qList = document.getElementById("question-list");
        const answerBox = document.getElementById("answer-box");
        if (subList) subList.innerHTML = "";
        if (qList) qList.innerHTML = "";
        if (answerBox) {
            answerBox.innerHTML = "";
            answerBox.classList.remove('active');
        }

        const subTitle = document.getElementById("sub-title");
        const qTitle = document.getElementById("q-title");
        const qHelp = document.getElementById("q-help");
        const t = TRANSLATIONS[lang] || TRANSLATIONS.en;

        if (subTitle) {
            subTitle.innerHTML = `<span class="title-icon">🎯</span> ${(cat.name && (cat.name[lang] || cat.name.en)) || cat.id}`;
        }
        if (qTitle) {
            qTitle.textContent = t.faq_title || "Frequently Asked Questions";
        }
        if (qHelp) {
            qHelp.textContent = t.faq_help || "Select a service to see questions and answers";
            qHelp.style.display = "block";
        }

        let found = false;
        if (cat.ministry_ids && cat.ministry_ids.length) {
            for (let id of cat.ministry_ids) {
                try {
                    const svc = await fetchJSONWithFallback(API_FALLBACKS.serviceById(id));
                    if (svc && svc.subservices && svc.subservices.length) {
                        svc.subservices.forEach((sub, index) => {
                            appendSubserviceToList(subList, svc, sub, index);
                            found = true;
                        });
                    }
                } catch (err) {
                    console.warn(`Failed to load service ${id}`, err);
                }
            }
        } else {
            // fallback: fetch all services and filter by category
            try {
                const all = await fetchJSONWithFallback(API_FALLBACKS.services);
                if (Array.isArray(all)) {
                    all.filter(s => s.category === cat.id).forEach((s, index) => {
                        s.subservices.forEach((sub, subIndex) => {
                            appendSubserviceToList(subList, s, sub, index + subIndex);
                            found = true;
                        });
                    });
                }
            } catch (err) {
                console.warn("Failed to load services fallback", err);
            }
        }

        if (!found && subList) {
            subList.innerHTML = '<li style="cursor: default;">No services available</li>';
        } else if (subList) {
            // No auto-select, wait for user click
        }

        showToast(`Category: ${(cat.name && (cat.name[lang] || cat.name.en)) || cat.id}`, 'info');
    } catch (error) {
        console.error("Error loading ministries:", error);
        showToast("Failed to load services", "error");
    }
}

function appendSubserviceToList(container, service, sub, index = 0) {
    if (!container) return;
    const li = document.createElement("li");
    li.dataset.subId = sub.id;
    li.innerHTML = `<span style="opacity:0.7;margin-right:8px;color:var(--primary-color);">🔸</span> ${(sub.name && (sub.name[lang] || sub.name.en)) || sub.id}`;
    li.tabIndex = 0;
    li.style.animationDelay = `${index * 0.05}s`;
    li.addEventListener('click', () => {
        container.querySelectorAll('li').forEach(el => {
            el.style.borderColor = 'var(--border-glass)';
            el.style.background = '';
        });
        li.style.borderColor = 'var(--primary-color)';
        li.style.background = 'rgba(59, 130, 246, 0.1)';
        loadQuestions(service, sub);
        setMobileLevel(3, "Q&A");

        // Mobile: Scroll to questions section
        if (window.innerWidth <= 1024) {
            const qSection = document.getElementById('q-title');
            if (qSection) qSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
    li.addEventListener('keypress', (e) => { if (e.key === "Enter") li.click(); });
    container.appendChild(li);
}

// Load Questions
async function loadQuestions(service, sub) {
    currentServiceObj = service;
    currentSub = sub;
    currentQuestionObj = null;
    currentServiceName = (service.name && (service.name[lang] || service.name.en)) || service.name || "";

    const qList = document.getElementById("question-list");
    if (!qList) return;
    qList.innerHTML = "";

    const qTitle = document.getElementById("q-title");
    if (qTitle) {
        qTitle.innerHTML = `<span class="title-icon">❓</span> ${(sub.name && (sub.name[lang] || sub.name.en)) || sub.id}`;
    }

    const qHelp = document.getElementById("q-help");
    if (qHelp) qHelp.style.display = "none";

    const questions = sub.questions || [];
    if (questions.length === 0) {
        qList.innerHTML = '<li style="cursor: default;">No questions available</li>';
        return;
    }

    questions.forEach((q, index) => {
        const li = document.createElement("li");
        li.dataset.qIndex = index;
        li.innerHTML = `<span style="color:var(--primary-color);margin-right:8px;">❓</span> ${(q.q && (q.q[lang] || q.q.en)) || q.q || "Question"}`;
        li.style.animationDelay = `${index * 0.05}s`;
        li.tabIndex = 0;
        li.addEventListener('click', () => {
            qList.querySelectorAll('li').forEach(el => {
                el.style.borderColor = 'var(--border-glass)';
                el.style.background = 'rgba(255, 255, 255, 0.02)';
            });
            li.style.borderColor = 'var(--primary-color)';
            li.style.background = 'rgba(59, 130, 246, 0.1)';
            showAnswer(service, sub, q);
        });
        li.addEventListener('keypress', (e) => { if (e.key === "Enter") li.click(); });
        qList.appendChild(li);
    });
}

// Show Answer with animation
function showAnswer(service, sub, q) {
    currentQuestionObj = q;
    const t = TRANSLATIONS[lang] || TRANSLATIONS.en;
    if (!isCitizenLoggedIn()) {
        showToast(t.lbl_login_required || "Please login or register to view details and instructions.", "error");
        setTimeout(() => window.location.href = '/citizen/login', 1500);
        return;
    }
    const answerBox = document.getElementById("answer-box");
    if (!answerBox) return;

    // Build DOM safely
    answerBox.innerHTML = "";
    const h = document.createElement("h3");
    h.textContent = (q.q && (q.q[lang] || q.q.en)) || q.q || "";
    answerBox.appendChild(h);

    const p = document.createElement("p");
    p.textContent = (q.answer && (q.answer[lang] || q.answer.en)) || q.answer || "";
    answerBox.appendChild(p);

    if (q.downloads && q.downloads.length) {
        const dlp = document.createElement("p");
        const strong = document.createElement("b");
        strong.textContent = t.lbl_downloads + ":";
        dlp.appendChild(strong);
        dlp.appendChild(document.createElement("br"));
        q.downloads.forEach(d => {
            const a = document.createElement("a");
            a.href = d;
            a.target = "_blank";
            a.rel = "noopener";
            a.download = "";
            a.textContent = d.split("/").pop();
            dlp.appendChild(a);
            dlp.appendChild(document.createElement("br"));
        });
        answerBox.appendChild(dlp);
    }

    if (q.location) {
        const loc = document.createElement("p");
        loc.innerHTML = `<b>${t.lbl_location}:</b> <a href="${q.location}" target="_blank" rel="noopener">${t.lbl_view_map}</a>`;
        answerBox.appendChild(loc);
    }

    if (q.instructions) {
        const inst = document.createElement("p");
        // Check if instructions are localized (dictionary) or string
        const instText = (typeof q.instructions === 'object') ? (q.instructions[lang] || q.instructions.en) : q.instructions;
        inst.innerHTML = `<b>${t.lbl_instructions}:</b> ${escapeHtml(instText)}`;
        answerBox.appendChild(inst);
    }

    answerBox.classList.add('active');
    answerBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Log engagement (use enhanced endpoint)
    logEngagement({
        user_id: profile_id,
        session_id: sessionId,
        question_clicked: (q.q && (q.q[lang] || q.q.en)) || q.q || "",
        service: currentServiceName,
        timestamp: new Date().toISOString()
    }).catch(err => console.warn("Engagement log failed", err));

    showToast("Answer loaded successfully", "success");
}

// Escape simple HTML (for safe insertion where necessary)
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Log Engagement (posts to enhanced endpoint)
async function logEngagement(data) {
    if (!isCitizenLoggedIn()) return; // Don't log if not logged in
    try {
        await fetchJSONWithFallback(API_FALLBACKS.engagement, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify(data)
        });
    } catch (error) {
        // Do not surface to user; just log
        console.debug("Error logging engagement:", error);
    }
}

// Chat Functions
function openChat() {
    if (!isCitizenLoggedIn()) {
        showToast("Please login or register to use the AI Assistant.", "error");
        setTimeout(() => window.location.href = '/citizen/login', 1500);
        return;
    }
    const chatPanel = document.getElementById("chat-panel");
    if (!chatPanel) return;
    chatPanel.classList.add('show');
    chatPanel.style.display = "flex";

    // Transfer any text already typed in the search box into the chat input
    const searchInput = document.getElementById("search-input");
    const chatInput = document.getElementById("chat-text");
    if (searchInput && chatInput && searchInput.value.trim()) {
        chatInput.value = searchInput.value.trim();
        // Clear the search box so it doesn't confuse the user
        searchInput.value = "";
        const suggestions = document.getElementById("suggestions");
        if (suggestions) {
            suggestions.innerHTML = "";
            suggestions.classList.remove('active');
        }
    }

    setTimeout(() => {
        const input = document.getElementById("chat-text");
        if (input) input.focus();
    }, 300);
}

function closeChat() {
    const chatPanel = document.getElementById("chat-panel");
    if (!chatPanel) return;
    chatPanel.classList.remove('show');
    setTimeout(() => chatPanel.style.display = "none", 300);
}

async function sendChat() {
    const input = document.getElementById("chat-text");
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    appendChat("user", text);
    input.value = "";

    showTypingIndicator();

    try {
        const data = await fetchJSONWithFallback(API_FALLBACKS.aiSearch, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify({ query: text, top_k: 5 })
        });

        hideTypingIndicator();

        const answer = (data && (data.answer || data.text)) || "No answer found.";
        const downloads = (data && data.downloads) || [];
        const location = (data && data.location) || "";
        const instructions = (data && data.instructions) || "";

        appendBotMessage(answer, downloads, location, instructions);

        // Log engagement
        logEngagement({
            user_id: profile_id,
            session_id: sessionId,
            question_clicked: text,
            service: "AI Chat",
            source: "chat",
            timestamp: new Date().toISOString()
        }).catch(() => { });
    } catch (error) {
        hideTypingIndicator();
        appendChat("bot", "Sorry, I encountered an error. Please try again.");
        console.error("Chat error:", error);
        showToast("Failed to get AI response", "error");
    }
}

function sendPredefinedQuery(query) {
    const input = document.getElementById("chat-text");
    if (input) {
        input.value = query;
        sendChat();
    }
}

function showTypingIndicator() {
    const typing = document.getElementById("chat-typing");
    if (typing) typing.classList.add('show');
}

function hideTypingIndicator() {
    const typing = document.getElementById("chat-typing");
    if (typing) typing.classList.remove('show');
}

function appendChat(sender, text) {
    const body = document.getElementById("chat-body");
    if (!body) return;

    const welcome = body.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    const div = document.createElement("div");
    div.className = "chat-msg " + (sender === "user" ? "user-msg" : "bot-msg");

    // Plain text rendering (safe for both user and simple bot messages)
    String(text).split("\n").forEach((p, idx, arr) => {
        const pEl = document.createElement("div");
        pEl.textContent = p;
        if (idx < arr.length - 1) pEl.style.marginBottom = "6px";
        div.appendChild(pEl);
    });

    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// Rich bot message: renders answer text + download links + location + instructions
function appendBotMessage(answer, downloads, location, instructions) {
    const body = document.getElementById("chat-body");
    if (!body) return;

    const welcome = body.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    const div = document.createElement("div");
    div.className = "chat-msg bot-msg";

    // Answer text
    String(answer).split("\n").forEach((p, idx, arr) => {
        const pEl = document.createElement("div");
        pEl.textContent = p;
        if (idx < arr.length - 1) pEl.style.marginBottom = "6px";
        div.appendChild(pEl);
    });

    // Instructions
    if (instructions && instructions.trim()) {
        const instBox = document.createElement("div");
        instBox.style.cssText = "margin-top:10px;padding:8px 10px;background:rgba(59,130,246,0.08);border-left:3px solid #3b82f6;border-radius:4px;font-size:13px;";
        const instLabel = document.createElement("b");
        instLabel.textContent = "📋 Instructions: ";
        instBox.appendChild(instLabel);
        const instText = document.createTextNode(instructions);
        instBox.appendChild(instText);
        div.appendChild(instBox);
    }

    // Location link
    if (location && location.trim()) {
        const locDiv = document.createElement("div");
        locDiv.style.cssText = "margin-top:10px;";
        const locLabel = document.createElement("b");
        locLabel.textContent = "📍 Location: ";
        locDiv.appendChild(locLabel);
        const locLink = document.createElement("a");
        locLink.href = location;
        locLink.target = "_blank";
        locLink.rel = "noopener noreferrer";
        locLink.textContent = "View on Map / Visit Website";
        locLink.style.cssText = "color:#1e40af;font-weight:600;text-decoration:underline;";
        locDiv.appendChild(locLink);
        div.appendChild(locDiv);
    }

    // Download links
    if (downloads && downloads.length > 0) {
        const dlDiv = document.createElement("div");
        dlDiv.style.cssText = "margin-top:10px;";
        const dlLabel = document.createElement("b");
        dlLabel.textContent = "📄 Download Forms:";
        dlDiv.appendChild(dlLabel);
        downloads.forEach(url => {
            if (!url) return;
            const br = document.createElement("br");
            dlDiv.appendChild(br);
            const a = document.createElement("a");
            a.href = url;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.download = url.split("/").pop();
            // Display only the filename nicely
            const fname = url.split("/").pop().replace(/_/g, " ").replace(/\.pdf$/i, "");
            a.textContent = "⬇ " + fname + " (.pdf)";
            a.style.cssText = "display:inline-block;margin-top:6px;padding:4px 10px;background:#1e40af;color:white;border-radius:5px;text-decoration:none;font-size:13px;font-weight:600;";
            dlDiv.appendChild(a);
        });
        div.appendChild(dlDiv);
    }

    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// Autosuggest (debounced)
async function autosuggest(q) {
    clearTimeout(suggestTimer);
    const suggestionsEl = document.getElementById("suggestions");
    if (!suggestionsEl) return;

    if (!q || q.length < 2) {
        suggestionsEl.innerHTML = "";
        suggestionsEl.classList.remove('active');
        return;
    }

    suggestTimer = setTimeout(async () => {
        try {
            const url = `${API_FALLBACKS.autosuggest[0]}?q=${encodeURIComponent(q)}`;
            const items = await fetchJSONWithFallback([url]);

            if (!items || items.length === 0) {
                suggestionsEl.innerHTML = "";
                suggestionsEl.classList.remove('active');
                return;
            }

            // Clear first
            suggestionsEl.innerHTML = "";
            items.forEach(it => {
                const div = document.createElement("div");
                div.className = "s-item";
                const name = (it.name && (it.name[lang] || it.name.en)) || it.name || it.id || "Suggestion";
                div.textContent = name;
                div.tabIndex = 0;
                // store in cache in case needed
                const key = `sug_${Math.random().toString(36).slice(2, 9)}`;
                cachedSuggestions.set(key, it);
                div.dataset.sugKey = key;
                div.addEventListener('click', () => {
                    const item = cachedSuggestions.get(div.dataset.sugKey);
                    if (item) pickSuggestion(item);
                });
                div.addEventListener('keypress', (e) => { if (e.key === "Enter") div.click(); });
                suggestionsEl.appendChild(div);
            });

            suggestionsEl.classList.add('active');
        } catch (error) {
            console.error("Autosuggest error:", error);
        }
    }, 250);
}

function pickSuggestion(item) {
    if (!item) return;
    // If the suggestion contains subservices directly, open first one
    if (item.subservices && item.subservices.length) {
        loadQuestions(item, item.subservices[0]);
    } else if (item.id) {
        // If it's a service id or similar, try to fetch the service details then open
        (async () => {
            try {
                const svc = await fetchJSONWithFallback(API_FALLBACKS.serviceById(item.id));
                if (svc && svc.subservices && svc.subservices.length) {
                    loadQuestions(svc, svc.subservices[0]);
                }
            } catch (err) {
                console.warn("Failed to fetch suggested service details", err);
            }
        })();
    }
    const suggestionsEl = document.getElementById("suggestions");
    if (suggestionsEl) {
        suggestionsEl.innerHTML = "";
        suggestionsEl.classList.remove('active');
    }
    const searchInput = document.getElementById("search-input");
    if (searchInput) searchInput.value = "";
}

// Profile Modal Functions
function showProfileModal() {
    if (!isCitizenLoggedIn()) {
        showToast("Please login or register to create your profile.", "error");
        setTimeout(() => window.location.href = '/citizen/login', 1500);
        return;
    }
    const modal = document.getElementById("profile-modal");
    if (!modal) return;
    modal.style.display = "flex";
    modal.classList.add('show');
    setTimeout(() => {
        const el = document.getElementById("p_name");
        if (el) el.focus();
    }, 300);
}

function closeProfileModal() {
    const modal = document.getElementById("profile-modal");
    if (!modal) return;
    modal.classList.remove('show');
    setTimeout(() => modal.style.display = "none", 300);
}

function profileNext(step) {
    document.querySelectorAll('.step').forEach(s => {
        const stepNum = parseInt(s.getAttribute('data-step'), 10);
        if (stepNum <= step + 1) s.classList.add('active'); else s.classList.remove('active');
    });
    const cur = document.getElementById(`profile-step-${step}`);
    const nxt = document.getElementById(`profile-step-${step + 1}`);
    if (cur) cur.style.display = "none";
    if (nxt) nxt.style.display = "block";
    setTimeout(() => {
        const firstInput = nxt ? nxt.querySelector('input, select') : null;
        if (firstInput) firstInput.focus();
    }, 100);
}

function profileBack(step) {
    document.querySelectorAll('.step').forEach(s => {
        const stepNum = parseInt(s.getAttribute('data-step'), 10);
        if (stepNum <= step - 1) s.classList.add('active'); else s.classList.remove('active');
    });
    const cur = document.getElementById(`profile-step-${step}`);
    const prev = document.getElementById(`profile-step-${step - 1}`);
    if (cur) cur.style.display = "none";
    if (prev) prev.style.display = "block";
}

async function profileSubmit() {
    const data1 = {
        name: document.getElementById("p_name")?.value || "",
        age: document.getElementById("p_age")?.value || ""
    };

    const data2 = {
        email: document.getElementById("p_email")?.value || "",
        phone: document.getElementById("p_phone")?.value || ""
    };

    const data3 = {
        job: document.getElementById("p_job")?.value || "",
        education: document.getElementById("p_education")?.value || ""
    };

    const interests = Array.from(document.querySelectorAll('input[name="interest"]:checked')).map(cb => cb.value);
    const data4 = {
        marital_status: document.getElementById("p_marital")?.value || "",
        children: document.getElementById("p_children")?.value || "0",
        interests: interests
    };

    try {
        // Step 1 - create or update basic profile
        const res1 = await fetchJSONWithFallback(API_FALLBACKS.profileStep, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify({ email: data2.email, step: "basic", data: data1 })
        });
        profile_id = res1?.profile_id || profile_id;
        if (profile_id) localStorage.setItem('profile_id', profile_id);

        // Step 2 - contact
        await fetchJSONWithFallback(API_FALLBACKS.profileStep, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify({ profile_id: profile_id, step: "contact", data: data2 })
        });

        // Step 3 - employment
        await fetchJSONWithFallback(API_FALLBACKS.profileStep, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify({ profile_id: profile_id, step: "employment", data: data3 })
        });

        // Step 4 - family & interests
        await fetchJSONWithFallback(API_FALLBACKS.profileStep, {
            method: "POST",
            headers: citizenAuthHeaders(),
            body: JSON.stringify({ profile_id: profile_id, step: "family_interests", data: data4 })
        });

        closeProfileModal();
        showToast("✓ Profile created successfully! You'll now receive personalized recommendations.", "success");

        const badge = document.getElementById("profile-badge");
        if (badge) badge.style.display = "inline-block";
    } catch (error) {
        console.error("Profile submission error:", error);
        showToast("Error creating profile. Please try again.", "error");
    }
}

// Load Ads
async function loadAds() {
    try {
        let adsUrls = [...API_FALLBACKS.ads];
        if (citizenId()) {
            adsUrls = [`${API_FALLBACKS.ads[0]}?user_id=${citizenId()}`, ...adsUrls];
        }
        const ads = await fetchJSONWithFallback(adsUrls);
        const el = document.getElementById("ads-area");
        if (!el) return;

        if (!ads || ads.length === 0) {
            el.innerHTML = '<p style="font-size: 12px; color: var(--text-muted); text-align: center;">No announcements</p>';
            return;
        }

        el.innerHTML = "";
        ads.slice(0, 4).forEach((a, index) => {
            const card = document.createElement("div");
            card.className = "ad-card";
            card.style.animationDelay = `${index * 0.1}s`;
            
            const isRecommended = a.relevance_score && a.relevance_score > 10;
            const badge = isRecommended 
                ? `<span style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.65rem; font-weight: bold; position: absolute; top: -10px; right: -10px; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4); z-index: 10;">✨ For You</span>` 
                : '';
            
            card.style.position = "relative";
            card.style.padding = "16px";
            card.style.marginBottom = "20px";
            card.style.borderRadius = "16px";
            card.style.background = isRecommended 
                ? "linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95))"
                : "linear-gradient(145deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01))";
            card.style.border = isRecommended 
                ? "1px solid rgba(16, 185, 129, 0.3)" 
                : "1px solid rgba(255, 255, 255, 0.05)";
            card.style.boxShadow = isRecommended ? "0 8px 25px rgba(0, 0, 0, 0.3)" : "none";
            card.style.transition = "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)";
            card.style.cursor = "pointer";
            
            card.onmouseenter = () => {
                card.style.transform = "translateY(-4px)";
                card.style.boxShadow = "0 12px 30px rgba(59, 130, 246, 0.2)";
                card.style.borderColor = "rgba(96, 165, 250, 0.3)";
            };
            card.onmouseleave = () => {
                card.style.transform = "translateY(0)";
                card.style.boxShadow = isRecommended ? "0 8px 25px rgba(0, 0, 0, 0.3)" : "none";
                card.style.borderColor = isRecommended ? "rgba(16, 185, 129, 0.3)" : "rgba(255, 255, 255, 0.05)";
            };
            
            const link = document.createElement("a");
            link.href = a.link || "#";
            link.target = "_blank";
            link.rel = "noopener";
            link.style.textDecoration = "none";
            link.style.display = "block";
            
            const h = document.createElement("h4");
            h.innerHTML = `📢 ${a.title || ""}`;
            h.style.margin = "0 0 8px 0";
            h.style.color = isRecommended ? "#34d399" : "#60a5fa";
            h.style.fontSize = "0.95rem";
            h.style.fontWeight = "700";
            
            const p = document.createElement("p");
            p.textContent = a.content || a.body || "";
            p.style.margin = "0";
            p.style.fontSize = "0.85rem";
            p.style.color = "#cbd5e1";
            p.style.lineHeight = "1.5";
            
            link.innerHTML = badge;
            link.appendChild(h);
            link.appendChild(p);
            card.appendChild(link);
            el.appendChild(card);
        });
    } catch (error) {
        console.error("Error loading ads:", error);
    }
}

// Check if profile exists and show badge
function checkProfile() {
    if (profile_id) {
        const badge = document.getElementById("profile-badge");
        if (badge) badge.style.display = "inline-block";
    }
}

// Citizen login state on main portal page
function initCitizenState() {
    const greeting = document.getElementById('citizen-greeting');
    const logoutBtn = document.getElementById('citizen-logout-btn');
    if (!greeting) return;
    if (isCitizenLoggedIn()) {
        const name = citizenName();
        greeting.innerHTML = `✅ <strong style="color:white;">${name}</strong>`;
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
        greeting.innerHTML = `👤 <a href="/citizen/login" style="color:white;font-weight:600;text-decoration:underline;" data-i18n="btn_citizen_login">Login / Register</a>`;
        if (logoutBtn) logoutBtn.style.display = 'none';
    }
}

async function citizenLogout() {
    try {
        await fetch('/api/citizen/logout', {
            method: 'POST',
            headers: citizenAuthHeaders()
        });
    } catch (e) { /* ignore network errors on logout */ }
    localStorage.removeItem('citizen_token');
    localStorage.removeItem('citizen_id');
    localStorage.removeItem('citizen_name');
    initCitizenState();
    showToast('You have been logged out.', 'info');
}

// Initialize on page load
window.addEventListener("load", async () => {
    try {
        // Restore saved language and apply
        lang = localStorage.getItem('lang') || 'en';
        updateTranslations();
        // Highlight saved language button
        document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
        const savedLangBtn = document.getElementById(`lang-${lang}`);
        if (savedLangBtn) savedLangBtn.classList.add('active');

        initCitizenState();
        await loadCategories();
        // Load services for fallback, but don't block UI
        try {
            const svcRes = await fetchJSONWithFallback(API_FALLBACKS.services);
            services = Array.isArray(svcRes) ? svcRes : [];
        } catch (e) {
            console.debug("Services fallback load failed", e);
        }
        checkProfile();
        const welcomeName = isCitizenLoggedIn() ? `, ${citizenName()}` : '';
        showToast(`Welcome${welcomeName} to Citizen Services Portal! 🏛️`, "info");
    } catch (error) {
        console.error("Initialization error:", error);
        showToast("Failed to load portal data", "error");
    }
});

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    // Mobile Level Navigation Logic
    const backBtn = document.getElementById('mobile-back-btn');
    const mobileTitle = document.getElementById('mobile-current-title');
    
    window.setMobileLevel = function(level, title = "Categories") {
        if (window.innerWidth <= 1024) {
            document.body.setAttribute('data-mobile-level', level);
            if (mobileTitle) mobileTitle.textContent = title;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    // Set initial level
    setMobileLevel(1);

    if (backBtn) {
        backBtn.addEventListener('click', () => {
            const currentLevel = parseInt(document.body.getAttribute('data-mobile-level') || "1");
            if (currentLevel === 3) {
                setMobileLevel(2, "Services");
            } else if (currentLevel === 2) {
                setMobileLevel(1, "Categories");
            }
        });
    }

    // Bottom Nav Logic
    const navHome = document.getElementById('nav-home');
    const navServices = document.getElementById('nav-services');
    const navChat = document.getElementById('nav-chat');
    const navLang = document.getElementById('nav-lang');
    const langModal = document.getElementById('langModal');
    const closeLang = document.getElementById('closeLang');

    function setActiveNav(el) {
        document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
        if (el) el.classList.add('active');
    }

    if (navHome) {
        navHome.addEventListener('click', () => {
            setMobileLevel(1);
            document.querySelector('.chat-panel').classList.remove('show');
        });
    }

    if (navServices) {
        navServices.addEventListener('click', () => {
            setMobileLevel(2, "Services");
        });
    }

    if (navChat) {
        navChat.addEventListener('click', () => {
            setActiveNav(navChat);
            document.querySelector('.chat-panel').classList.toggle('show');
        });
    }

    if (navLang) {
        navLang.addEventListener('click', () => {
            langModal.style.display = 'flex';
        });
    }

    if (closeLang) {
        closeLang.onclick = () => langModal.style.display = 'none';
    }

    window.closeLangModal = () => {
        langModal.style.display = 'none';
    };

    if (closeLang) {
        closeLang.onclick = () => langModal.style.display = 'none';
    }

    window.closeLangModal = () => {
        langModal.style.display = 'none';
    };

    // Close mobile menu when clicking a category
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 1024 && e.target.closest('.cat-item')) {
            mobileMenu.classList.remove('show');
        }
    });

    const chatInput = document.getElementById('chat-text');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }

    // Smooth anchor scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
});

// Add loading animation
function showLoading(element) {
    if (element) element.innerHTML = '<div class="loading">Loading</div>';
}
function hideLoading(element) {
    if (element) {
        const loading = element.querySelector('.loading');
        if (loading) loading.remove();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        openChat();
    }
    if (e.key === 'Escape') {
        closeChat();
        closeProfileModal();
    }
});