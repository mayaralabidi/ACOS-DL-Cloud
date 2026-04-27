"""Product prices in TND. One entry per detectable class."""
"""
Product prices in TND (Tunisian Dinar). Maps each YOLO class name to its unit price.

**Maintenance notes:**
- One entry per detectable class (must match YOLO model class names exactly)
- Used by receipt calculation to compute totals
- Single source of truth for pricing (shared between pipeline and API)
- Update here when prices change; rebuild product database if using multi-tenancy

**Price verification:**
Run this after updating prices to verify all classes are priced:
    from pipeline.checkout import StaticSceneCheckout
    from pipeline.prices import PRICES
    model = YOLO(cfg.model_path)
    missing = set(model.names.values()) - set(PRICES.keys())
    if missing:
        print(f"WARNING: Missing prices for {missing}")
"""

PRICES: dict[str, float] = {
    "choco_esprit_de_fete": 25, 
    "milk_delice": 1.35, 
    "juice_diva": 3.5,
    "soapbar_dove_shea": 4.9, 
    "butter_jadida": 3.8, 
    "vanillinatedsugar": 1.5,
    "disinfectant_cnett": 7.5, 
    "cocoapowder": 2.76, 
    "pril": 3.0,
    "conditioner_avilea": 6.0, 
    "showergel": 5.5, 
    "riso_scotti": 18,
    "flour": 1.4, 
    "yogurt_danette": 0.9, 
    "choc": 3.7,
    "pasta_spaghetti": 0.41, 
    "rice": 1.6, 
    "bathfoam_malizia": 10.9,
    "soapbar_dove_lavender": 3.5, 
    "dryyeast_smartchef": 0.8,
    "butter_delice": 7.59, 
    "judy": 6.2, 
    "carolin": 10.69,
    "vinegar": 2.59, 
    "dryyeast_lapatissiere": 0.9, 
    "choco_coating": 2.3,
    "toothpaste_colgate": 3.8, 
    "shampoo_elseve_hya": 25.59,
    "bakingpowder": 1.1, 
    "pasta_fell": 0.41, 
    "teabags_camomilia": 7.39,
    "chocoline": 7.29, 
    "pasta_canelloni": 1.39, 
    "yogurt_delice": 0.85,
    "coffee_bondin": 4.8, 
    "chantilly_vanoise": 3.3,
    "shampoo_elseve_gly": 25.59, 
    "shampoo_elvive": 6.8,
    "orzo": 0.41, 
    "soap_lilas": 10.2, 
    "mustard": 6.5,
    "harissa": 2.2, 
    "liquidsoap_naya": 3.8,
    "chocospread_vanoise": 8.7, 
    "canned_peas": 1.9,
}