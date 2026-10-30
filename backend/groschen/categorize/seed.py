"""Built-in categories, German merchant list and example phrases.

This is the offline knowledge the categorizer starts with. It is extended by
the user's own rules and corrections, which always win over anything here.
"""

# (group, color, kind, [category names])
CATEGORY_TREE = [
    ("Income", "green", "income", ["Salary", "Interest & dividends", "Other income"]),
    ("Housing", "blue", "expense", ["Rent", "Energy", "Internet & phone", "Broadcast fee", "Home & furniture"]),
    ("Food & Dining", "amber", "expense", ["Groceries", "Restaurants & cafés", "Food delivery"]),
    ("Transport", "pink", "expense", ["Fuel", "Public transport", "Car costs", "Parking", "Taxi & rides"]),
    ("Shopping", "gray", "expense", ["Online shopping", "Clothing", "Electronics", "Drugstore"]),
    ("Insurance", "forest", "expense", ["Insurance"]),
    ("Subscriptions", "teal", "expense", ["Streaming", "Software & cloud", "Fitness"]),
    ("Health", "red", "expense", ["Pharmacy", "Doctor & health"]),
    ("Leisure & Travel", "violet", "expense", ["Travel", "Hobbies", "Entertainment", "Gaming"]),
    ("Personal", "sand", "expense", ["Cash withdrawal", "Gifts & donations", "Education", "Bank fees", "Taxes"]),
    ("Saving & investing", "forest", "transfer", ["Savings", "Investments"]),
    ("Transfers", "slate", "transfer", ["Own transfers", "Credit card payment"]),
]

# Every spending and income group also has a category named like the group itself. It is the
# "general" choice for bookings that fit the group but none of its subcategories.
GENERAL_KINDS = ("expense", "income")


# Categories added after the first release. Existing installs get them on the next start:
# (name, group, kind, color, name of the category they are sorted in front of or None)
ADDED_LATER = [
    ("Savings", "Saving & investing", "transfer", "forest", "Investments"),
]
# Built-in categories that moved to another group: name -> (old group, new group, color)
MOVED_LATER = {"Investments": ("Transfers", "Saving & investing", "forest")}

# Brokers, robo-advisors and crypto exchanges: money sent there is invested.
BROKERS = (
    r"\bTRADE ?REPUBLIC\b|\bSCALABLE\b|\bBAADER ?BANK\b|\bFLATEX|\bSMARTBROKER\b|\bDAB BNP\b|\bJUSTTRADE\b|\bSUTOR BANK\b"
    r"|\bFINANZEN\.NET ZERO\b|\bONVISTA\b|\bMAXBLUE\b|\bLYNX\b|\bINTERACTIVE BROKERS\b|\bDEGIRO\b|\bBITPANDA\b|\bCOINBASE\b"
    r"|\bBISON APP\b|\bQUIRION\b|\bGINMON\b|\bWHITEBOX\b|\bGROWNEY\b|\bVISUALVEST\b|\bLIQID\b|\bEXTRAETF\b|\bFONDSDEPOT BANK\b"
    r"|\bUNION INVESTMENT\b|\bDEKABANK\b"
)
# Overnight-money platforms: money sent there is put aside.
SAVERS = r"\bWELTSPAREN\b|\bRAISIN\b|\bZINSPILOT\b|\bSAVEDO\b|\bZINSPORTAL\b"
# Words that say what a transfer to the user's own name is for.
INVEST_WORDS = BROKERS + r"|\bWERTPAPIER|\bSPARPLAN\b|\bDEPOT\b|\bWP-KAUF|\bETF\b|\bAKTIEN?\b|\bFONDS\b|\bKRYPTO|\bBITCOIN\b"
SAVE_WORDS = (
    SAVERS + r"|\bSPAREN\b|\bSPARRATE\b|\bSPARBETRAG\b|\bTAGESGELD\b|\bFESTGELD\b|\bSPARKONTO\b|\bEXTRA.?KONTO\b"
    r"|\bRUECKLAGE|\bRÜCKLAGE|\bNOTGROSCHEN\b"
)

# Regular expressions matched against the upper-cased text of a transaction
# (counterparty, purpose and booking text). Sign: "+" income only, "-" spending only, None both.
# Bump KNOWLEDGE when this list changes: existing installs then sort their bookings again on the next
# start (never the ones the user sorted).
KNOWLEDGE = 2
MERCHANTS: list[tuple[str, str, str | None]] = [
    # Groceries
    (r"\bREWE\b", "Groceries", "-"),
    (r"\bEDEKA\b", "Groceries", "-"),
    (r"\bALDI\b", "Groceries", "-"),
    (r"\bLIDL\b", "Groceries", "-"),
    (r"\bNETTO\b", "Groceries", "-"),
    (r"\bPENNY\b", "Groceries", "-"),
    (r"\bKAUFLAND\b", "Groceries", "-"),
    (r"\bTEGUT\b", "Groceries", "-"),
    (r"\bGLOBUS\b", "Groceries", "-"),
    (r"\bNORMA\b", "Groceries", "-"),
    (r"\bMARKTKAUF\b", "Groceries", "-"),
    (r"\bDENN'?S\b", "Groceries", "-"),
    (r"\bALNATURA\b", "Groceries", "-"),
    (r"\bBIOMARKT\b", "Groceries", "-"),
    (r"\bE CENTER\b|\bE-CENTER\b", "Groceries", "-"),
    (r"\bHIT MARKT\b|\bHIT \d", "Groceries", "-"),
    (r"\bNAHKAUF\b", "Groceries", "-"),
    (r"\bFLINK\b", "Groceries", "-"),
    (r"\bPICNIC\b", "Groceries", "-"),
    (r"\bGETIR\b", "Groceries", "-"),
    (r"\bBAECKEREI\b|\bBÄCKEREI\b", "Groceries", "-"),
    (r"\bMETRO\b", "Groceries", "-"),
    (r"\bSPAR\b", "Groceries", "-"),
    # Drugstores
    (r"\bDM[- ]?DROGERIE|\bDM FIL|\bDM-MARKT", "Drugstore", "-"),
    (r"\bROSSMANN\b", "Drugstore", "-"),
    (r"\bMUELLER\b|\bMÜLLER DROG", "Drugstore", "-"),
    (r"\bBUDNI", "Drugstore", "-"),
    # Fuel
    (r"\bARAL\b", "Fuel", "-"),
    (r"\bSHELL\b", "Fuel", "-"),
    (r"\bESSO\b", "Fuel", "-"),
    (r"\bTOTAL(ENERGIES)?\b", "Fuel", "-"),
    (r"\bJET TANK|\bJET\b", "Fuel", "-"),
    (r"\bAGIP\b|\bENI\b", "Fuel", "-"),
    (r"\bOMV\b", "Fuel", "-"),
    (r"\bAVIA\b", "Fuel", "-"),
    (r"\bORLEN\b|\bSTAR TANK", "Fuel", "-"),
    (r"\bHEM TANK|\bHEM\b", "Fuel", "-"),
    (r"\bTANKSTELLE\b", "Fuel", "-"),
    (r"\bIONITY\b|\bENBW MOBILITY|\bEWE GO\b|\bTESLA SUPERCHARG", "Fuel", "-"),
    # Public transport
    (r"\bDB VERTRIEB|\bDEUTSCHE BAHN|\bDB FERNVERKEHR|\bBAHN\.DE", "Public transport", "-"),
    (r"\bDEUTSCHLANDTICKET|\bD-TICKET", "Public transport", "-"),
    (
        r"\bMVG\b|\bMVV\b|\bBVG\b|\bHVV\b|\bRMV\b|\bVBB\b|\bKVB\b|\bVRR\b|\bVVS\b|\bVGN\b|\bRHEINBAHN\b|\bUESTRA\b",
        "Public transport",
        "-",
    ),
    (r"\bFLIXBUS\b|\bFLIXTRAIN\b", "Public transport", "-"),
    # Taxi, parking, car
    (r"\bUBER\b(?!.*EATS)", "Taxi & rides", "-"),
    (r"\bFREE ?NOW\b", "Taxi & rides", "-"),
    (r"\bBOLT\.EU|\bBOLT\b", "Taxi & rides", "-"),
    (r"\bTIER\b|\bLIME\b|\bVOI\b|\bSHARE NOW\b|\bMILES MOBILITY", "Taxi & rides", "-"),
    (r"\bPARKHAUS\b|\bPARKEN\b|\bEASYPARK\b|\bPARK ?NOW\b|\bAPCOA\b|\bCONTIPARK\b|\bPAYBYPHONE\b", "Parking", "-"),
    (
        r"\bATU\b|\bA\.T\.U\b|\bTUEV\b|\bTÜV\b|\bDEKRA\b|\bKFZ[- ]?STEUER|\bAUTOHAUS\b|\bWERKSTATT\b|\bCARGLASS\b|\bWASCHSTRASSE",
        "Car costs",
        "-",
    ),
    # Online shopping & retail
    (r"\bAMAZON WEB SERVICES|\bAWS EMEA\b|\bAWS\b", "Software & cloud", "-"),
    (r"\bAMAZON\b(?!.*PRIME)|\bAMZN\b(?!.*PRIME)|\bAMZ\*", "Online shopping", "-"),
    (r"\bEBAY\b", "Online shopping", "-"),
    (r"\bOTTO\b", "Online shopping", "-"),
    (r"\bTEMU\b", "Online shopping", "-"),
    (r"\bSHEIN\b", "Clothing", "-"),
    (r"\bALIEXPRESS\b", "Online shopping", "-"),
    (r"\bKLEINANZEIGEN\b", "Online shopping", None),
    (r"\bKLARNA\b|\bSECUPAY\b|\bRATEPAY\b|\bRIVERTY\b|\bAFTERPAY\b|\bBILLPAY\b", "Online shopping", "-"),
    (r"\bZALANDO\b", "Clothing", "-"),
    (r"\bH ?& ?M\b|\bH\+M\b|\bHENNES", "Clothing", "-"),
    (r"\bZARA\b", "Clothing", "-"),
    (r"\bPRIMARK\b", "Clothing", "-"),
    (r"\bC ?& ?A\b", "Clothing", "-"),
    (r"\bABOUT YOU\b", "Clothing", "-"),
    (r"\bDEICHMANN\b", "Clothing", "-"),
    (r"\bSNIPES\b", "Clothing", "-"),
    (r"\bUNIQLO\b", "Clothing", "-"),
    (r"\bDECATHLON\b", "Hobbies", "-"),
    (r"\bMEDIA ?MARKT\b", "Electronics", "-"),
    (r"\bSATURN\b", "Electronics", "-"),
    (r"\bCYBERPORT\b", "Electronics", "-"),
    (r"\bNOTEBOOKSBILLIGER\b", "Electronics", "-"),
    (r"\bALTERNATE\b", "Electronics", "-"),
    (r"\bMINDFACTORY\b", "Electronics", "-"),
    (r"\bCONRAD\b", "Electronics", "-"),
    (r"\bGALAXUS\b", "Electronics", "-"),
    (r"\bIKEA\b", "Home & furniture", "-"),
    (r"\bOBI\b", "Home & furniture", "-"),
    (r"\bBAUHAUS\b", "Home & furniture", "-"),
    (r"\bHORNBACH\b", "Home & furniture", "-"),
    (r"\bTOOM\b", "Home & furniture", "-"),
    (r"\bHAGEBAU", "Home & furniture", "-"),
    (r"\bXXXLUTZ\b|\bPOCO\b|\bROLLER\b|\bSEGMUELLER\b|\bHOEFFNER\b|\bHÖFFNER\b|\bJYSK\b", "Home & furniture", "-"),
    (r"\bACTION\b|\bTEDI\b|\bWOOLWORTH\b|\bNANU[- ]NANA\b", "Home & furniture", "-"),
    # Streaming & software
    (r"\bNETFLIX\b", "Streaming", "-"),
    (r"\bSPOTIFY\b", "Streaming", "-"),
    (r"\bDISNEY\s?\+|\bDISNEY PLUS\b|\bDISNEYPLUS", "Streaming", "-"),
    (r"\bDAZN\b", "Streaming", "-"),
    (r"\bSKY DEUTSCHLAND|\bWOW TV\b", "Streaming", "-"),
    (r"\bAMAZON PRIME|\bPRIME VIDEO|\bAMZN DIGITAL", "Streaming", "-"),
    (r"\bAUDIBLE\b", "Streaming", "-"),
    (r"\bYOUTUBE\b", "Streaming", "-"),
    (r"\bJOYN\b", "Streaming", "-"),
    (r"\bRTL ?\+", "Streaming", "-"),
    (r"\bPARAMOUNT\b", "Streaming", "-"),
    (r"\bCRUNCHYROLL\b", "Streaming", "-"),
    (r"\bDEEZER\b", "Streaming", "-"),
    (r"\bAPPLE\.COM/BILL|\bAPPLE SERVICES|\bITUNES", "Software & cloud", "-"),
    (r"\bGOOGLE \*|\bGOOGLE PLAY|\bGOOGLE ONE|\bGOOGLE STORAGE|\bGOOGLE ?CLOUD|\bGOOGLE WORKSPACE", "Software & cloud", "-"),
    (r"\bMICROSOFT\b|\bMSFT\b", "Software & cloud", "-"),
    (r"\bADOBE\b", "Software & cloud", "-"),
    (r"\bDROPBOX\b", "Software & cloud", "-"),
    (r"\bICLOUD\b", "Software & cloud", "-"),
    (r"\bOPENAI\b|\bCHATGPT\b|\bANTHROPIC\b|\bCLAUDE\.AI\b", "Software & cloud", "-"),
    (r"\bGITHUB\b", "Software & cloud", "-"),
    (r"\bNORDVPN\b|\bPROTON\b|\bSURFSHARK\b|\b1PASSWORD\b|\bBITWARDEN\b", "Software & cloud", "-"),
    (r"\bLIME ?TECHNOLOGY|\bUNRAID\b|\bHETZNER\b|\bSTRATO\b|\bIONOS\b|\bNETCUP\b|\bALL-INKL", "Software & cloud", "-"),
    (
        r"\bNZB|\bUSENET|\bNEWSHOSTING\b|\bEWEKA\b|\bTWEAKNEWS\b|\bGIGANEWS\b|\bEASYNEWS\b|\bNEWSDEMON\b",
        "Software & cloud",
        "-",
    ),
    (
        r"\bPLEX\b|\bTAILSCALE\b|\bCLOUDFLARE\b|\bBACKBLAZE\b|\bSYNOLOGY\b|\bN8N\b|\bJETBRAINS\b|\bNOTION\b",
        "Software & cloud",
        "-",
    ),
    # Fitness
    (r"\bMC ?FIT\b", "Fitness", "-"),
    (r"\bFITNESS FIRST\b", "Fitness", "-"),
    (r"\bURBAN ?SPORTS", "Fitness", "-"),
    (r"\bCLEVER ?FIT\b", "Fitness", "-"),
    (r"\bJOHN REED\b", "Fitness", "-"),
    (r"\bEASY ?FIT\b", "Fitness", "-"),
    (r"\bFITX\b", "Fitness", "-"),
    (r"\bEGYM\b|\bWELLPASS\b", "Fitness", "-"),
    (r"\bFITNESS\b|\bGYM\b", "Fitness", "-"),
    # Food
    (r"\bLIEFERANDO\b", "Food delivery", "-"),
    (r"\bWOLT\b", "Food delivery", "-"),
    (r"\bUBER ?EATS\b", "Food delivery", "-"),
    (r"\bMC ?DONALD'?S\b", "Restaurants & cafés", "-"),
    (r"\bBURGER KING\b", "Restaurants & cafés", "-"),
    (r"\bSTARBUCKS\b", "Restaurants & cafés", "-"),
    (r"\bSUBWAY\b", "Restaurants & cafés", "-"),
    (r"\bKFC\b", "Restaurants & cafés", "-"),
    (r"\bVAPIANO\b", "Restaurants & cafés", "-"),
    (r"\bDOMINO'?S\b", "Restaurants & cafés", "-"),
    (r"\bPIZZA\b|\bPIZZERIA\b|\bRISTORANTE\b|\bTRATTORIA\b|\bOSTERIA\b", "Restaurants & cafés", "-"),
    (
        r"\bRESTAURANT\b|\bGASTHAUS\b|\bGASTSTAETTE\b|\bGASTSTÄTTE\b|\bWIRTSHAUS\b|\bBRAUHAUS\b|\bBIERGARTEN\b",
        "Restaurants & cafés",
        "-",
    ),
    (r"\bCAFE\b|\bCAFÉ\b|\bKAFFEE\b|\bCOFFEE\b|\bESPRESSO\b|\bTCHIBO\b", "Restaurants & cafés", "-"),
    (
        r"\bDITSCH\b|\bBACKWERK\b|\bKAMPS\b|\bBACKSHOP\b|\bSCHOKOLADE|\bCHOCOLAT|\bCONFISERIE\b|\bKONDITOREI\b|\bEISCAFE\b|\bEISDIELE\b|\bGELATERIA\b",
        "Restaurants & cafés",
        "-",
    ),
    (
        r"\bDOENER\b|\bDÖNER\b|\bKEBAB\b|\bIMBISS\b|\bSUSHI\b|\bBURGER\b|\bBISTRO\b|\bKANTINE\b|\bMENSA\b",
        "Restaurants & cafés",
        "-",
    ),
    # Health
    (r"\bAPOTHEKE\b|\bDOCMORRIS\b|\bSHOP ?APOTHEKE\b|\bMEDPEX\b|\bAPO\b", "Pharmacy", "-"),
    (
        r"\bPRAXIS\b|\bZAHNARZT\b|\bDR\. MED\b|\bKLINIK\b|\bKRANKENHAUS\b|\bPHYSIO|\bOPTIK\b|\bFIELMANN\b|\bAPOLLO OPTIK\b|\bLABOR\b",
        "Doctor & health",
        "-",
    ),
    # Housing and utilities
    (
        r"\bMIETE\b|\bKALTMIETE\b|\bWARMMIETE\b|\bNEBENKOSTEN\b|\bHAUSVERWALTUNG\b|\bWOHNUNGSBAU|\bVONOVIA\b|\bLEG IMMOBILIEN\b|\bDEUTSCHE WOHNEN\b",
        "Rent",
        "-",
    ),
    (
        r"\bSTADTWERKE\b|\bE\.ON\b|\bEON\b|\bVATTENFALL\b|\bENBW\b|\bRWE\b|\bLICHTBLICK\b|\bOSTROM\b|\bTIBBER\b|\bNATURSTROM\b|\bSTROM\b|\bGASAG\b|\bEWE\b|\bMAINOVA\b|\bRHEINENERGIE\b|\bN-ERGIE\b|\bFERNWAERME|\bFERNWÄRME|\bABSCHLAG",
        "Energy",
        "-",
    ),
    (
        r"\bTELEKOM\b|\bVODAFONE\b|\bO2\b|\bTELEFONICA\b|\b1 ?& ?1\b|\b1UND1\b|\bCONGSTAR\b|\bFREENET\b|\bKABEL DEUTSCHLAND|\bUNITYMEDIA|\bDEUTSCHE GLASFASER\b|\bM-NET\b|\bNETCOLOGNE\b|\bALDI TALK\b|\bFRAENK\b|\bWINSIM\b|\bPYUR\b"
        r"|\bKLARMOBIL\b|\bMOBILCOM\b|\bSIMPLYTEL\b|\bSMARTMOBIL\b|\bPREMIUMSIM\b|\bDRILLISCH\b|\bLIDL CONNECT\b|\bNETZCLUB\b"
        r"|\bBLAU\.DE\b|\bOTELO\b|\bLEBARA\b|\bLYCAMOBILE\b|\bHIGH ?MOBILE\b|\bSIPGATE\b",
        "Internet & phone",
        "-",
    ),
    (r"\bBEITRAGSSERVICE\b|\bARD ZDF\b|\bRUNDFUNK", "Broadcast fee", "-"),
    # Insurance
    (
        r"\bALLIANZ\b|\bHUK\b|\bHUK-COBURG|\bAXA\b|\bERGO\b|\bDEVK\b|\bGENERALI\b|\bR\+V\b|\bZURICH\b|\bSIGNAL IDUNA\b|\bHANSEMERKUR\b|\bDEBEKA\b|\bGOTHAER\b|\bWUERTTEMBERGISCHE|\bVHV\b|\bHDI\b|\bCOSMOS ?DIREKT\b|\bLVM\b|\bPROVINZIAL\b|\bADAC\b|\bVERSICHERUNG|\bGETSAFE\b|\bWERTGARANTIE\b"
        r"|\bRHION\b|\bBARMENIA\b|\bCONTINENTALE\b|\bNUERNBERGER\b|\bNÜRNBERGER\b|\bALTE LEIPZIGER\b|\bWGV\b|\bDA DIREKT\b"
        r"|\bVERTI\b|\bJANITOS\b|\bHELVETIA\b|\bBASLER\b|\bARAG\b|\bAUXILIA\b|\bROLAND RECHTSSCHUTZ|\bMECKLENBURGISCHE\b"
        r"|\bDIE BAYERISCHE\b|\bVKB\b|\bCONCORDIA\b|\bHANNOVERSCHE\b|\bKRANKENKASSE\b|\bAOK\b|\bBARMER\b|\bTECHNIKER KRANKENKASSE"
        r"|\bDAK\b|\bIKK\b|\bBKK\b|\bKKH\b|\bHKK\b",
        "Insurance",
        "-",
    ),
    # Leisure
    (
        r"\bSTEAM\b|\bVALVE\b|\bPLAYSTATION\b|\bSONY INTERACTIVE|\bNINTENDO\b|\bXBOX\b|\bEPIC GAMES\b|\bBLIZZARD\b|\bRIOT GAMES\b|\bEA\.COM|\bUBISOFT\b|\bGOG\.COM|\bINSTANT GAMING",
        "Gaming",
        "-",
    ),
    (
        r"\bBOOKING\.COM\b|\bAIRBNB\b|\bLUFTHANSA\b|\bEUROWINGS\b|\bRYANAIR\b|\bEASYJET\b|\bCONDOR\b|\bTUI\b|\bHOTEL\b|\bEXPEDIA\b|\bHOLIDAYCHECK\b|\bCHECK24 REISE|\bOPODO\b|\bHOSTEL\b|\bSIXT\b|\bEUROPCAR\b|\bHERTZ\b|\bAVIS\b|\bRENTALCARS",
        "Travel",
        "-",
    ),
    (
        r"\bCINEMAXX\b|\bUCI\b|\bCINESTAR\b|\bKINO\b|\bEVENTIM\b|\bTICKETMASTER\b|\bRESERVIX\b|\bMUSEUM\b|\bTHEATER\b|\bKONZERT\b|\bFREIZEITPARK\b|\bEUROPA-PARK\b|\bSCHWIMMBAD\b|\bTHERME\b",
        "Entertainment",
        "-",
    ),
    (
        r"\bTHALIA\b|\bHUGENDUBEL\b|\bBUCHHANDLUNG\b|\bWELTBILD\b|\bMUSIC STORE\b|\bTHOMANN\b|\bFRESSNAPF\b|\bZOOPLUS\b|\bLEGO\b|\bSMYTHS\b",
        "Hobbies",
        "-",
    ),
    (
        r"\bUDEMY\b|\bCOURSERA\b|\bVOLKSHOCHSCHULE\b|\bVHS\b|\bFAHRSCHULE\b|\bHOCHSCHULE\b|\bUNIVERSITAET\b|\bUNIVERSITÄT\b|\bSTUDIENGEB",
        "Education",
        "-",
    ),
    (
        r"\bSPENDE\b|\bUNICEF\b|\bWIKIMEDIA\b|\bRED CROSS\b|\bROTES KREUZ\b|\bARZTE OHNE|\bÄRZTE OHNE|\bGREENPEACE\b|\bWWF\b|\bBETTERPLACE\b",
        "Gifts & donations",
        "-",
    ),
    (r"\bFINANZAMT\b|\bBUNDESKASSE\b|\bSTEUERVERWALTUNG|\bKFZ-STEUER|\bGRUNDSTEUER\b|\bHUNDESTEUER\b", "Taxes", None),
    # Church tax and its refunds, unless it is the salary of someone working for the church.
    (
        r"^(?!.*\b(GEHALT|LOHN|BEZUEGE|BEZÜGE|RENTE)\b).*(\bKIRCHENSTEUER|\bDIOEZESE\b|\bDIOZESE\b|\bDIÖZESE\b|\bERZBISTUM\b|\bBISTUM\b)",
        "Taxes",
        None,
    ),
    # Workshops, tyres and car parts. After insurance and taxes, so "Kfz-Versicherung" stays insurance.
    (
        r"\bKFZ\b|\bAUTOSERVICE|\bREIFEN|\bKAROSSERIE|\bLACKIER|\bABSCHLEPP|\bAUTOTEILE\b|\bPITSTOP\b|\bVERGOELST\b|\bVERGÖLST\b"
        r"|\bEUROMASTER\b|\bAUTOGLAS\b|\bAUTOWERKSTATT\b|\bKFZ-WERKSTATT|\bAUTOPFLEGE\b",
        "Car costs",
        "-",
    ),
    # Cash and bank
    (
        r"\bBARGELDAUSZAHLUNG|\bBARGELDABHEBUNG|\bGELDAUTOMAT|\bAUSZAHLUNG GAA|\bGA NR|\bCASH ?GROUP|\bATM\b|\bBARGELD\b",
        "Cash withdrawal",
        "-",
    ),
    (r"\bENTGELT\b|\bKONTOFUEHRUNG|\bKONTOFÜHRUNG|\bGEBUEHR\b|\bGEBÜHR\b|\bDISPOZINS|\bSOLLZINS", "Bank fees", "-"),
    # Income
    (
        r"\bGEHALT\b|\bLOHN\b|\bBEZUEGE\b|\bBEZÜGE\b|\bGEHALT/RENTE\b|\bLOHN/GEHALT\b|\bRENTE\b|\bVERSORGUNGSBEZ",
        "Salary",
        "+",
    ),
    (
        r"\bZINSEN\b|\bZINSGUTSCHRIFT\b|\bABSCHLUSS\b|\bHABENZINS|\bERTRAGSGUTSCHRIFT|\bDIVIDENDE|\bAUSSCHUETTUNG|\bAUSSCHÜTTUNG",
        "Interest & dividends",
        "+",
    ),
    (
        r"\bFAMILIENKASSE\b|\bKINDERGELD\b|\bELTERNGELD\b|\bERSTATTUNG\b|\bRUECKERSTATTUNG|\bRÜCKERSTATTUNG",
        "Other income",
        "+",
    ),
    # Saving & investing. ING's round-up saving "Kleingeld-Plus" goes into the Extra-Konto
    # ("Kleingeld Plus - Sparen") or into a fund savings plan; the destination account decides
    # when both sides of the booking are known (see engine.pair_own_transfers).
    (r"\bKLEINGELD.?PLUS\b.*\b(INVEST|ANLEGEN|ANLAGE|SPARPLAN|DEPOT|ETF|FONDS)", "Investments", None),
    (r"\bKLEINGELD.?PLUS\b|\bAUFRUNDUNG\b|\bAUFGERUNDET", "Savings", None),
    (BROKERS, "Investments", None),
    (SAVERS, "Savings", None),
    (r"\bSPAREN\b|\bSPARRATE\b|\bSPARBETRAG\b|\bTAGESGELD\b|\bFESTGELD\b|\bSPARKONTO\b|\bEXTRA.?KONTO\b", "Savings", None),
    (r"\bWERTPAPIER|\bSPARPLAN\b|\bDEPOT\b|\bWP-KAUF|\bETF\b", "Investments", "-"),
    (
        r"\bKREDITKARTE\b|\bKREDITKARTENABRECHNUNG|\bVISA ABRECHNUNG|\bMASTERCARD ABRECHNUNG|\bAMEX\b|\bAMERICAN EXPRESS\b|\bBARCLAYCARD\b|\bADVANZIA\b",
        "Credit card payment",
        "-",
    ),
    # Banks call money moved between the same customer's accounts "Übertrag" or "Umbuchung".
    (r"\bUEBERTRAG\b|\bÜBERTRAG\b|\bUMBUCHUNG\b", "Own transfers", None),
]

# Short descriptions the built-in model compares new transactions against.
EXAMPLES: dict[str, list[str]] = {
    "Salary": ["Gehalt", "Lohn", "Monatsgehalt", "Arbeitgeber Gehaltszahlung", "salary payment"],
    "Interest & dividends": ["Zinsen Tagesgeld", "Dividende", "Ertragsgutschrift", "interest"],
    "Other income": ["Erstattung", "Rückzahlung", "Kindergeld Familienkasse", "Verkauf Kleinanzeigen", "refund"],
    "Rent": ["Miete Wohnung", "Kaltmiete", "Vermieter", "Hausverwaltung Nebenkosten", "rent"],
    "Energy": ["Stromabschlag", "Gas Abschlag", "Stadtwerke Energie", "Fernwärme", "electricity bill"],
    "Internet & phone": ["Mobilfunk Rechnung", "DSL Internet", "Handyvertrag", "Glasfaser", "phone bill"],
    "Broadcast fee": ["Rundfunkbeitrag", "Beitragsservice ARD ZDF"],
    "Home & furniture": ["Baumarkt", "Möbelhaus", "Einrichtung", "Gartencenter", "Haushaltswaren"],
    "Groceries": [
        "Supermarkt",
        "Lebensmittel",
        "Bäckerei",
        "Metzgerei",
        "Getränkemarkt",
        "Wochenmarkt",
        "Hofladen",
        "Biomarkt",
        "grocery store",
    ],
    "Restaurants & cafés": [
        "Restaurant",
        "Café",
        "Pizzeria",
        "Gaststätte",
        "Bistro",
        "Imbiss",
        "Döner",
        "Sushi",
        "Bar",
        "Kneipe",
        "Eisdiele",
        "coffee shop",
    ],
    "Food delivery": ["Essen bestellen Lieferdienst", "food delivery"],
    "Fuel": ["Tankstelle", "Benzin", "Diesel", "Laden E-Auto Ladesäule", "petrol station"],
    "Public transport": ["Bahnticket", "Fahrkarte", "ÖPNV", "Monatskarte", "Busticket", "train ticket"],
    "Car costs": ["Autowerkstatt", "Kfz Reparatur", "Reifenwechsel", "Autowäsche", "Hauptuntersuchung"],
    "Parking": ["Parkhaus", "Parkgebühr", "Parkticket"],
    "Taxi & rides": ["Taxi", "Fahrdienst", "E-Scooter", "Carsharing"],
    "Online shopping": ["Onlineshop Bestellung", "Versandhandel", "Marketplace", "online order"],
    "Clothing": ["Mode", "Bekleidung", "Schuhe", "Fashion Store"],
    "Electronics": ["Elektronikmarkt", "Computer Hardware", "Smartphone Zubehör"],
    "Drugstore": ["Drogerie", "Drogeriemarkt", "Kosmetik"],
    "Insurance": [
        "Versicherung Beitrag",
        "Haftpflichtversicherung",
        "Kfz-Versicherung",
        "Hausratversicherung",
        "insurance premium",
    ],
    "Streaming": ["Streaming Abo", "Musik Abo", "Video on demand"],
    "Software & cloud": ["Software Abo", "Cloud Speicher", "App Store", "Webhosting", "VPN"],
    "Fitness": ["Fitnessstudio", "Sportverein Beitrag", "gym membership"],
    "Pharmacy": ["Apotheke", "Medikamente", "Online Apotheke"],
    "Doctor & health": ["Arztpraxis", "Zahnarzt", "Physiotherapie", "Optiker", "Krankenhaus"],
    "Travel": ["Hotel", "Flug", "Ferienwohnung", "Reise", "Mietwagen", "flight booking"],
    "Hobbies": ["Hobby", "Bücher", "Musikinstrument", "Sportartikel", "Tierbedarf", "Spielwaren"],
    "Entertainment": ["Kino", "Konzert Tickets", "Theater", "Museum", "Freizeitpark", "Schwimmbad"],
    "Gaming": ["Videospiel", "Spiele Store", "Gaming", "video game"],
    "Cash withdrawal": ["Bargeldabhebung Geldautomat", "cash withdrawal"],
    "Gifts & donations": ["Spende", "Geschenk", "donation"],
    "Education": ["Kursgebühr", "Weiterbildung", "Fahrschule", "Studiengebühr"],
    "Bank fees": ["Kontoführungsgebühr", "Bankentgelt"],
    "Taxes": ["Finanzamt Steuer", "Steuerzahlung"],
    "Own transfers": ["Umbuchung eigenes Konto", "Übertrag zwischen eigenen Konten"],
    "Savings": [
        "Kleingeld Plus Sparen",
        "Übertrag Sparkonto",
        "Sparen Extra-Konto",
        "Tagesgeld Einzahlung",
        "Sparrate",
        "savings transfer",
    ],
    "Investments": ["Wertpapierkauf Sparplan", "ETF Sparplan Depot", "Kleingeld Plus Investieren"],
    "Credit card payment": ["Kreditkartenabrechnung"],
}

_COLORS_BY_GROUP = {group: color for group, color, _, _ in CATEGORY_TREE}


def seed_categories(conn) -> None:
    """Create the built-in categories on first start."""
    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]:
        return
    sort = 0
    for group, color, kind, names in CATEGORY_TREE:
        if kind in GENERAL_KINDS and group not in names:
            names = [group, *names]
        for name in names:
            sort += 1
            conn.execute(
                "INSERT INTO categories (name, grp, kind, color, sort) VALUES (?, ?, ?, ?, ?)",
                (name, group, kind, color, sort),
            )


def upgrade_categories(conn) -> bool:
    """Bring the built-in categories of an existing install up to date. Returns True if anything changed.

    Only touches categories that are still named and grouped the way Groschen created them,
    so anything the user renamed or moved stays as it is.
    """
    changed = False
    for name, (old_group, new_group, color) in MOVED_LATER.items():
        cur = conn.execute(
            "UPDATE categories SET grp = ?, color = ? WHERE name = ? AND grp = ?", (new_group, color, name, old_group)
        )
        changed = changed or cur.rowcount > 0
    for name, group, kind, color, before in ADDED_LATER:
        if conn.execute("SELECT 1 FROM categories WHERE name = ?", (name,)).fetchone():
            continue
        row = conn.execute("SELECT sort FROM categories WHERE name = ?", (before,)).fetchone() if before else None
        if row:
            sort = row[0]
            conn.execute("UPDATE categories SET sort = sort + 1 WHERE sort >= ?", (sort,))
        else:
            sort = (conn.execute("SELECT COALESCE(MAX(sort), 0) FROM categories").fetchone()[0]) + 1
        conn.execute(
            "INSERT INTO categories (name, grp, kind, color, sort) VALUES (?, ?, ?, ?, ?)", (name, group, kind, color, sort)
        )
        changed = True
    for group, color, kind, _ in CATEGORY_TREE:
        if kind not in GENERAL_KINDS:
            continue
        first = conn.execute("SELECT MIN(sort) FROM categories WHERE grp = ?", (group,)).fetchone()[0]
        if first is None or conn.execute("SELECT 1 FROM categories WHERE name = ? AND grp = ?", (group, group)).fetchone():
            continue
        conn.execute("UPDATE categories SET sort = sort + 1 WHERE sort >= ?", (first,))
        conn.execute(
            "INSERT INTO categories (name, grp, kind, color, sort) VALUES (?, ?, ?, ?, ?)",
            (group, group, kind, color, first),
        )
        changed = True
    return changed


def group_color(group: str) -> str:
    return _COLORS_BY_GROUP.get(group, "gray")
