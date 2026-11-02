package io.github.mki002.groschen.i18n

// Built-in category and group names are stored in English on the server (the categorizer looks
// them up by name) and shown translated; names the user typed stay exactly as typed.
// The same list as the web interface (frontend/src/i18n/de.ts, keys "cat.*").
private val CATEGORY_DE = mapOf(
    "Income" to "Einnahmen",
    "Salary" to "Gehalt",
    "Interest & dividends" to "Zinsen & Dividenden",
    "Other income" to "Sonstige Einnahmen",
    "Housing" to "Wohnen",
    "Rent" to "Miete",
    "Energy" to "Energie",
    "Internet & phone" to "Internet & Telefon",
    "Broadcast fee" to "Rundfunkbeitrag",
    "Home & furniture" to "Haushalt & Möbel",
    "Food & Dining" to "Essen & Trinken",
    "Groceries" to "Lebensmittel",
    "Restaurants & cafés" to "Restaurants & Cafés",
    "Food delivery" to "Lieferdienste",
    "Transport" to "Mobilität",
    "Fuel" to "Tanken",
    "Public transport" to "ÖPNV & Bahn",
    "Car costs" to "Autokosten",
    "Parking" to "Parken",
    "Taxi & rides" to "Taxi & Fahrdienste",
    "Shopping" to "Einkaufen",
    "Online shopping" to "Onlineshopping",
    "Clothing" to "Kleidung",
    "Electronics" to "Elektronik",
    "Drugstore" to "Drogerie",
    "Insurance" to "Versicherungen",
    "Subscriptions" to "Abos",
    "Streaming" to "Streaming",
    "Software & cloud" to "Software & Cloud",
    "Fitness" to "Fitness",
    "Health" to "Gesundheit",
    "Pharmacy" to "Apotheke",
    "Doctor & health" to "Arzt & Gesundheit",
    "Leisure & Travel" to "Freizeit & Reisen",
    "Travel" to "Reisen",
    "Hobbies" to "Hobbys",
    "Entertainment" to "Unterhaltung",
    "Gaming" to "Gaming",
    "Personal" to "Persönliches",
    "Cash withdrawal" to "Bargeldabhebung",
    "Gifts & donations" to "Geschenke & Spenden",
    "Education" to "Bildung",
    "Bank fees" to "Bankgebühren",
    "Taxes" to "Steuern",
    "Transfers" to "Umbuchungen",
    "Own transfers" to "Eigene Umbuchungen",
    "Investments" to "Geldanlage",
    "Credit card payment" to "Kreditkartenabrechnung",
    "Uncategorized" to "Ohne Kategorie",
    "Saving & investing" to "Sparen & Anlegen",
    "Savings" to "Sparen",
)

fun categoryName(name: String?, lang: Lang): String {
    if (name.isNullOrBlank()) return ""
    return if (lang == Lang.DE) CATEGORY_DE[name] ?: name else name
}
