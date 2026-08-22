/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

export type Language = 'en' | 'zh' | 'fr'

const messages = {
  en: {
    tagline: "Understand what you're actually ordering.",
    welcomeBack: 'Welcome back', loginHelp: 'Log in to continue to FoodHub.',
    email: 'Email', password: 'Password', login: 'Log in', loggingIn: 'Logging in...',
    noAccount: "Don't have an account?", createAccount: 'Create account',
    createTitle: 'Create your account', name: 'Name', preferredLanguage: 'Preferred language',
    confirmPassword: 'Confirm password', creatingAccount: 'Creating account...', backToLogin: 'Back to login',
    scanTitle: 'Scan your menu', scanSubtitle: 'Upload up to five menu pages. JPG, PNG and WebP are supported.',
    uploadPhotos: 'Upload menu photos', addPage: 'Add another page', page: 'Page', remove: 'Remove',
    scanMenu: 'Scan Menu', loadDemo: 'Load Demo Menu', demoMode: 'Demo mode', liveMode: 'Live scan',
    demoPrivacy: 'Demo mode uses a fixed database menu. Selected images are not uploaded.',
    liveUnavailable: 'Live scanning is disabled for this presentation.',
    processingTitle: 'Reading your menu...', processingText: 'Translating dishes and matching menu information.',
    menuTitle: 'Your Menu', dishesFound: 'dishes found', displayLanguage: 'display language', scanAnother: 'Scan another menu', originalName: 'Original menu name',
    moodTitle: 'What are you in the mood for?', moodText: 'Empty groups use your saved long-term preferences.',
    protein: 'Protein', flavour: 'Flavour', texture: 'Texture', spiceLevel: 'Spice level',
    recommend: 'Recommend dishes', updating: 'Updating recommendations...', topPicks: 'Top Picks',
    disclaimer: 'For reference only. If you have a severe allergy, confirm directly with restaurant staff.',
    referenceImage: 'Reference image', menuIngredients: 'Menu-listed ingredients',
    referenceIngredients: 'Reference recipe ingredients', inferredIngredients: 'AI-inferred ingredients',
    allergenEvidence: 'Possible allergen evidence', details: 'View details', hideDetails: 'Hide details',
    cuisine: 'Cuisine', source: 'Source', confidence: 'Confidence', why: 'Why this result',
    preferenceMatch: 'preference match', good_match: 'Good Match', check_with_staff: 'Check With Staff', avoid: 'Avoid',
    editPreferences: 'Edit preferences', logout: 'Log out', dietaryPreferences: 'Dietary preferences',
    managePreferences: 'Manage allergies, dietary requirements and food preferences.',
    profileTitle: 'Tell us what works for you', profileText: "We'll use this to personalise your recommendations.",
    backToMenu: 'Back to menu', allergies: 'Allergies', dietaryRestrictions: 'Dietary restrictions',
    religiousRequirements: 'Religious dietary requirements', preferredProteins: 'Preferred proteins',
    preferredFlavours: 'Preferred flavours', preferredTextures: 'Preferred textures', disliked: "Ingredients you'd rather avoid",
    dislikedPlaceholder: 'e.g. mushrooms, olives', savePreferences: 'Save preferences',
    saveContinue: 'Save preferences & continue', saving: 'Saving...', skip: 'Skip for now', loadingPreferences: 'Loading saved preferences...',
    selectApplicable: 'Select any that apply to you.', selectEnjoy: 'Select the options you usually enjoy.',
    contains: 'contains', may_contain: 'may contain', unknown: 'unknown',
    menu_evidence: 'menu evidence', reference_recipe: 'reference recipe', inferred: 'AI inference',
    menu_only: 'menu only', themealdb: 'TheMealDB', llm: 'AI analysis', local_fallback: 'local cache', demo_database: 'demo database',
  },
  zh: {
    tagline: '看懂菜单，安心点餐。', welcomeBack: '欢迎回来', loginHelp: '登录后继续使用 FoodHub。',
    email: '邮箱', password: '密码', login: '登录', loggingIn: '正在登录…', noAccount: '还没有账户？', createAccount: '创建账户',
    createTitle: '创建你的账户', name: '姓名', preferredLanguage: '首选语言', confirmPassword: '确认密码', creatingAccount: '正在创建账户…', backToLogin: '返回登录',
    scanTitle: '扫描菜单', scanSubtitle: '最多上传五张菜单图片，支持 JPG、PNG 和 WebP。', uploadPhotos: '上传菜单图片', addPage: '继续添加一页', page: '第', remove: '移除',
    scanMenu: '扫描菜单', loadDemo: '载入演示菜单', demoMode: '演示模式', liveMode: '实时扫描', demoPrivacy: '演示模式使用固定数据库菜单，所选图片不会上传。', liveUnavailable: '当前演示环境已禁用实时扫描。',
    processingTitle: '正在读取菜单…', processingText: '正在翻译菜品并匹配相关信息。', menuTitle: '你的菜单', dishesFound: '道菜', displayLanguage: '显示语言', scanAnother: '扫描另一份菜单', originalName: '菜单原文',
    moodTitle: '这一餐想吃什么？', moodText: '未选择的项目会沿用你的长期偏好。', protein: '蛋白质', flavour: '风味', texture: '口感', spiceLevel: '辣度', recommend: '生成推荐', updating: '正在更新推荐…', topPicks: '推荐结果',
    disclaimer: '结果仅供参考；如有严重过敏，请务必向餐厅工作人员确认。', referenceImage: '参考图片', menuIngredients: '菜单明确成分', referenceIngredients: '参考食谱成分', inferredIngredients: 'AI 推断成分', allergenEvidence: '可能的过敏原证据', details: '查看详情', hideDetails: '收起详情', cuisine: '菜系', source: '信息来源', confidence: '可信度', why: '判断原因', preferenceMatch: '偏好匹配度', good_match: '适合', check_with_staff: '请向餐厅确认', avoid: '建议避开',
    editPreferences: '编辑偏好', logout: '退出登录', dietaryPreferences: '饮食偏好', managePreferences: '管理过敏原、饮食要求和口味偏好。', profileTitle: '告诉我们你的饮食需求', profileText: '这些信息将用于生成个性化推荐。', backToMenu: '返回菜单', allergies: '过敏原', dietaryRestrictions: '饮食限制', religiousRequirements: '宗教饮食要求', preferredProteins: '偏好的蛋白质', preferredFlavours: '偏好的风味', preferredTextures: '偏好的口感', disliked: '不喜欢的成分', dislikedPlaceholder: '例如：蘑菇、橄榄', savePreferences: '保存偏好', saveContinue: '保存并继续', saving: '正在保存…', skip: '暂时跳过', loadingPreferences: '正在加载偏好…', selectApplicable: '请选择适用于你的选项。', selectEnjoy: '请选择你通常喜欢的选项。',
    contains: '明确含有', may_contain: '可能含有', unknown: '未知', menu_evidence: '菜单证据', reference_recipe: '参考食谱', inferred: 'AI 推断', menu_only: '仅菜单信息', themealdb: 'TheMealDB', llm: 'AI 分析', local_fallback: '本地缓存', demo_database: '演示数据库',
  },
  fr: {
    tagline: 'Comprenez vraiment ce que vous commandez.', welcomeBack: 'Bon retour', loginHelp: 'Connectez-vous pour continuer sur FoodHub.',
    email: 'E-mail', password: 'Mot de passe', login: 'Se connecter', loggingIn: 'Connexion…', noAccount: 'Pas encore de compte ?', createAccount: 'Créer un compte',
    createTitle: 'Créez votre compte', name: 'Nom', preferredLanguage: 'Langue préférée', confirmPassword: 'Confirmer le mot de passe', creatingAccount: 'Création du compte…', backToLogin: 'Retour à la connexion',
    scanTitle: 'Scannez votre menu', scanSubtitle: "Ajoutez jusqu'à cinq pages en JPG, PNG ou WebP.", uploadPhotos: 'Ajouter des photos du menu', addPage: 'Ajouter une page', page: 'Page', remove: 'Supprimer',
    scanMenu: 'Scanner le menu', loadDemo: 'Charger le menu démo', demoMode: 'Mode démo', liveMode: 'Scan réel', demoPrivacy: "Le mode démo utilise un menu fixe en base. Les images sélectionnées ne sont pas envoyées.", liveUnavailable: 'Le scan réel est désactivé pour cette présentation.',
    processingTitle: 'Lecture du menu…', processingText: 'Traduction des plats et recherche des informations.', menuTitle: 'Votre menu', dishesFound: 'plats trouvés', displayLanguage: "langue d'affichage", scanAnother: 'Scanner un autre menu', originalName: "Nom d'origine du menu",
    moodTitle: "Qu'avez-vous envie de manger ?", moodText: 'Les groupes vides utilisent vos préférences enregistrées.', protein: 'Protéines', flavour: 'Saveurs', texture: 'Texture', spiceLevel: 'Niveau épicé', recommend: 'Recommander des plats', updating: 'Mise à jour…', topPicks: 'Meilleurs choix',
    disclaimer: "À titre indicatif uniquement. En cas d'allergie sévère, confirmez auprès du restaurant.", referenceImage: 'Image de référence', menuIngredients: 'Ingrédients indiqués au menu', referenceIngredients: "Ingrédients d'une recette de référence", inferredIngredients: "Ingrédients déduits par l'IA", allergenEvidence: "Indices d'allergènes possibles", details: 'Voir les détails', hideDetails: 'Masquer les détails', cuisine: 'Cuisine', source: 'Source', confidence: 'Confiance', why: 'Pourquoi ce résultat', preferenceMatch: 'compatibilité', good_match: 'Bon choix', check_with_staff: 'À confirmer', avoid: 'À éviter',
    editPreferences: 'Modifier les préférences', logout: 'Se déconnecter', dietaryPreferences: 'Préférences alimentaires', managePreferences: 'Gérez les allergies, exigences et préférences alimentaires.', profileTitle: 'Parlez-nous de vos besoins', profileText: 'Ces informations personnalisent vos recommandations.', backToMenu: 'Retour au menu', allergies: 'Allergies', dietaryRestrictions: 'Régimes alimentaires', religiousRequirements: 'Exigences religieuses', preferredProteins: 'Protéines préférées', preferredFlavours: 'Saveurs préférées', preferredTextures: 'Textures préférées', disliked: 'Ingrédients à éviter', dislikedPlaceholder: 'ex. champignons, olives', savePreferences: 'Enregistrer', saveContinue: 'Enregistrer et continuer', saving: 'Enregistrement…', skip: 'Passer pour le moment', loadingPreferences: 'Chargement des préférences…', selectApplicable: 'Sélectionnez les options qui vous concernent.', selectEnjoy: 'Sélectionnez ce que vous appréciez habituellement.',
    contains: 'contient', may_contain: 'peut contenir', unknown: 'inconnu', menu_evidence: 'preuve du menu', reference_recipe: 'recette de référence', inferred: 'inférence IA', menu_only: 'menu uniquement', themealdb: 'TheMealDB', llm: 'analyse IA', local_fallback: 'cache local', demo_database: 'base de démonstration',
  },
} as const

const optionLabels: Record<Language, Record<string, string>> = {
  en: {},
  zh: { peanut: '花生', tree_nuts: '树坚果', milk: '牛奶/乳制品', egg: '鸡蛋', fish: '鱼类', shellfish: '甲壳类海鲜', molluscs: '软体动物', gluten: '小麦/麸质', soy: '大豆', sesame: '芝麻', mustard: '芥末', celery: '芹菜', lupin: '羽扇豆', sulfites: '亚硫酸盐', vegetarian: '素食', vegan: '纯素', pescatarian: '鱼素', gluten_free: '无麸质', dairy_free: '无乳制品', lactose_free: '无乳糖', egg_free: '无蛋', halal_required: '清真', no_pork: '不吃猪肉', kosher_required: '犹太洁食', no_beef: '不吃牛肉', no_alcohol: '不含酒精', beef: '牛肉', lamb: '羊肉', chicken: '鸡肉', duck: '鸭肉', pork: '猪肉', plant_based: '植物蛋白', savoury: '咸香', rich: '浓郁', light: '清爽', creamy: '奶油感', herby: '香草味', smoky: '烟熏味', tangy: '酸香', sweet: '甜味', crispy: '酥脆', tender: '软嫩', crunchy: '爽脆', soft: '柔软', chewy: '有嚼劲', brothy: '汤汁感', mild: '微辣', medium: '中辣', hot: '辣' },
  fr: { peanut: 'Cacahuètes', tree_nuts: 'Fruits à coque', milk: 'Lait / produits laitiers', egg: 'Œufs', fish: 'Poisson', shellfish: 'Crustacés', molluscs: 'Mollusques', gluten: 'Blé / gluten', soy: 'Soja', sesame: 'Sésame', mustard: 'Moutarde', celery: 'Céleri', lupin: 'Lupin', sulfites: 'Sulfites', vegetarian: 'Végétarien', vegan: 'Végane', pescatarian: 'Pescétarien', gluten_free: 'Sans gluten', dairy_free: 'Sans produits laitiers', lactose_free: 'Sans lactose', egg_free: 'Sans œufs', halal_required: 'Halal', no_pork: 'Sans porc', kosher_required: 'Casher', no_beef: 'Sans bœuf', no_alcohol: 'Sans alcool', beef: 'Bœuf', lamb: 'Agneau', chicken: 'Poulet', duck: 'Canard', pork: 'Porc', plant_based: 'Végétal', savoury: 'Savoureux', rich: 'Riche', light: 'Léger', creamy: 'Crémeux', herby: 'Aux herbes', smoky: 'Fumé', tangy: 'Acidulé', sweet: 'Sucré', crispy: 'Croustillant', tender: 'Tendre', crunchy: 'Croquant', soft: 'Fondant', chewy: 'Moelleux', brothy: 'En bouillon', mild: 'Doux', medium: 'Moyen', hot: 'Fort' },
}

type MessageKey = keyof typeof messages.en
interface I18nValue { language: Language; setLanguage: (language: Language) => void; t: (key: MessageKey) => string; optionLabel: (code: string, fallback?: string) => string }
const I18nContext = createContext<I18nValue | null>(null)

function initialLanguage(): Language {
  const saved = window.localStorage.getItem('foodhub_ui_language')
  if (saved === 'zh' || saved === 'fr' || saved === 'en') return saved
  const browser = window.navigator.language.toLowerCase()
  return browser.startsWith('zh') ? 'zh' : browser.startsWith('fr') ? 'fr' : 'en'
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, updateLanguage] = useState<Language>(initialLanguage)
  const setLanguage = useCallback((next: Language) => {
    window.localStorage.setItem('foodhub_ui_language', next)
    updateLanguage(next)
  }, [])
  const value = useMemo<I18nValue>(() => ({
    language,
    setLanguage,
    t: (key) => messages[language][key] ?? messages.en[key],
    optionLabel: (code, fallback) => optionLabels[language][code] ?? fallback ?? code.replaceAll('_', ' '),
  }), [language, setLanguage])
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const value = useContext(I18nContext)
  if (!value) throw new Error('useI18n must be used inside I18nProvider')
  return value
}
