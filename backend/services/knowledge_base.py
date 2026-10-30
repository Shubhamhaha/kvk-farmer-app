"""Small local retrieval index for the app's curated West Bengal farm data."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.data_service import CROP_DATA, SCHEMES, get_advisory


REFERENCE_NOTES = [
    ("Rice pest management", "For brown plant hopper (BPH) in rice, scout the base of plants and avoid excessive nitrogen and standing water. Preserve spiders and other beneficial insects. Use only a locally approved pesticide when the economic threshold is reached, following its label and KVK guidance."),
    ("Potato disease management", "Late blight risk in potato rises in cool, humid, wet weather. Scout leaves and stems frequently, remove badly affected plants where practical, and seek local KVK advice before choosing a fungicide. Follow the product label and pre-harvest interval."),
    ("Soil health", "Use a soil test to guide nutrient and lime application. The Soil Health Card Scheme provides soil testing and fertilizer recommendations through local agriculture offices and KVKs. Do not apply lime without checking soil pH and local recommendations."),
    ("Safe pesticide use", "Identify the pest before treatment, monitor crop damage, and consult the local KVK or Block Agriculture Office. Use only products registered for that crop and pest, follow the label dose and protective equipment instructions, and observe the pre-harvest interval."),
    ("West Bengal crop seasons", "Kharif crops are generally sown with the monsoon, Rabi crops are grown in the cooler months, and Zaid is the intervening summer season. Planting dates vary by district, water availability, and variety; check the current local advisory."),
]


def _documents(district):
    documents = []
    for crop, info in CROP_DATA.items():
        content = (
            f"{crop}. Season: {info['season']}. Sowing: {info['sow_month']}. "
            f"Harvest: {info['harvest_month']}. Average yield: {info['avg_yield_qtl_per_ha']} quintal/ha. "
            f"MSP: {info['msp_per_qtl']} rupees/quintal. Key pests: {', '.join(info['key_pests'])}. "
            f"Fertilizer kg/ha: {info['fertilizer_kg_per_ha']}. Relevant districts: {', '.join(info['districts'])}."
        )
        documents.append({"source": f"Crop guide: {crop}", "content": content})

    for scheme in SCHEMES:
        documents.append({
            "source": f"Government scheme: {scheme['name']}",
            "content": (f"{scheme['name']}. {scheme['description']} Eligibility: {scheme['eligibility']} "
                        f"Benefit: {scheme['benefit']} Apply at: {scheme['apply_at']}."),
        })

    for source, content in REFERENCE_NOTES:
        documents.append({"source": source, "content": content})

    advisory = get_advisory(district)
    documents.append({
        "source": f"Current advisory: {district}",
        "content": (f"Current {advisory['season']} advisory for {district}: "
                    + " ".join(advisory['advisories'])
                    + f" Contact: {advisory['kvk_contact']}"),
    })
    return documents


def retrieve_context(question, district="Bardhaman", limit=4):
    """Return the closest curated references and their labels for citations."""
    docs = _documents(district)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1, sublinear_tf=True)
    matrix = vectorizer.fit_transform([doc["content"] for doc in docs] + [question])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    selected = [
        {**docs[index], "score": float(score)}
        for index, score in ranked[:limit]
        if score > 0.015
    ]
    return selected
