USER_BRANCH_FAMILIES = {
    "Computer & IT": [
        "Computer Engineering",
        "Computer Engineering (Regional Language)",
        "Computer Engineering (Software Engineering)",
        "Computer Science",
        "Computer Science and Business Systems",
        "Computer Science and Design",
        "Computer Science and Engineering",
        "Computer Science and Engineering (Artificial Intelligence and Data Science)",
        "Computer Science and Engineering (Artificial Intelligence)",
        "Computer Science and Engineering (Cyber Security)",
        "Computer Science and Engineering (Internet of Things and Cyber Security Including Block Chain",
        "Computer Science and Engineering (IoT)",
        "Computer Science and Engineering(Artificial Intelligence and Machine Learning)",
        "Computer Science and Engineering(Cyber Security)",
        "Computer Science and Engineering(Data Science)",
        "Computer Science and Information Technology",
        "Computer Science and Technology",
        "Computer Technology",
        "Cyber Security",
        "Data Engineering",
        "Data Science",
        "Electrical and Computer",
        "Electrical and Computer Engineering",
        "Electrical and ComputerEngineering",
        "Electronics and Computer Engineering",
        "Electronics and Computer Science",
        "Information Technology",
    ],
    "Artificial Intelligence": [
        "Artificial Intelligence",
        "Artificial Intelligence (AI) and Data Science",
        "Artificial Intelligence and Data Science",
        "Artificial Intelligence and Machine Learning",
        "Robotics and Artificial Intelligence",
    ],
    "Electronics & Telecom": [
        "5G",
        "ELECTRONICS AND COMMUNICATION ENGINEERING (BIO-MEDICAL ENGINEERING)",
        "Electrical Engg[Electronics and Power]",
        "Electrical and Electronics Engineering",
        "Electrical, Electronics and Power",
        "Electronics Engineering",
        "Electronics Engineering ( VLSI Design and Technology)",
        "Electronics and Biomedical Engineering",
        "Electronics and Communication (Advanced Communication Technology)",
        "Electronics and Communication Engineering",
        "Electronics and Communication(Advanced Communication Technology)",
        "Electronics & Telecommunication Engineering",
        "Electronics and Telecommunication Engg",
        "Instrumentation Engineering",
        "Instrumentation and Control Engineering",
        "VLSI",
    ],
    "Mechanical": [
        "Automobile Engineering",
        "Automotive Technology",
        "MECHANICAL AND RAIL ENGINEERING",
        "Mechanical & Automation Engineering",
        "Mechanical Engineering",
        "Mechanical Engineering Automobile",
        "Mechanical Engineering[Sandwich]",
        "Mechanical and Automation Engineering",
        "Mechanical and Mechatronics Engineering (Additive Manufacturing)",
        "Mechatronics Engineering",
    ],
    "Civil": [
        "Architectural Assistantship",
        "Civil Engineering",
        "Civil Engineering (Structural Engineering)",
        "Civil Engineering with Computer Application",
        "Civil Engineering and Planning",
        "Civil and Environmental Engineering",
        "Civil and infrastructure Engineering",
        "Structural Engineering",
    ],
    "Chemical": [
        "Bio Medical Engineering",
        "Bio Technology",
        "Chemical Engineering",
        "Dyestuff Technology",
        "Food Engineering",
        "Food Engineering and Technology",
        "Food Technology",
        "Food Technology And Management",
        "Oil Fats and Waxes Technology",
        "Oil Technology",
        "Oil and Paints Technology",
        "Oil,Oleochemicals and Surfactants Technology",
        "Paints Technology",
        "Petro Chemical Engineering",
        "Petro Chemical Technology",
        "Pharmaceutical and Fine Chemical Technology",
        "Pharmaceuticals Chemistry and Technology",
        "Surface Coating Technology",
    ],
    "Robotics & Automation": [
        "Automation and Robotics",
        "Industrial IoT",
        "Internet of Things (IoT)",
        "Robotics",
        "Robotics and Automation",
    ],
    "Textile": [
        "Fashion Technology",
        "Fibres and Textile Processing Technology",
        "Man Made Textile Technology",
        "Technical Textiles",
        "Textile Chemistry",
        "Textile Engineering / Technology",
        "Textile Plant Engineering",
        "Textile Technology",
    ],
    "Production & Manufacturing": [
        "Manufacturing Science and Engineering",
        "Paper and Pulp Technology",
        "Printing Technology",
        "Printing and Packing Technology",
        "Production Engineering",
        "Production Engineering[Sandwich]",
    ],
    "Others": [
        "Aeronautical Engineering",
        "Agricultural Engineering",
        "Agriculture Engineering",
        "Electrical Engg [Electrical and Power]",
        "Electrical Engineering",
        "Fire Engineering",
        "Logistics",
        "Metallurgy and Material Technology",
        "Mining Engineering",
        "Plastic Technology",
        "Plastic and Polymer Engineering",
        "Plastic and Polymer Technology",
        "Polymer Engineering and Technology",
        "Safety and Fire Engineering",
    ],
}


USER_BRANCH_ALIASES = {
    "COMPUTER": "Computer & IT",
    "COMPUTER_IT": "Computer & IT",
    "COMPUTER_&_IT": "Computer & IT",
    "CS": "Computer & IT",
    "CSE": "Computer & IT",
    "IT": "Computer & IT",
    "AI": "Artificial Intelligence",
    "AIDS": "Artificial Intelligence",
    "AI_DS": "Artificial Intelligence",
    "AIML": "Artificial Intelligence",
    "AI_ML": "Artificial Intelligence",
    "ENTC": "Electronics & Telecom",
    "EXTC": "Electronics & Telecom",
    "ELECTRONICS": "Electronics & Telecom",
    "CIVIL": "Civil",
    "MECHANICAL": "Mechanical",
    "CHEMICAL": "Chemical",
    "ROBOTICS": "Robotics & Automation",
    "TEXTILE": "Textile",
    "PRODUCTION": "Production & Manufacturing",
    "MANUFACTURING": "Production & Manufacturing",
}


DISPLAY_BRANCH_FAMILIES = list(USER_BRANCH_FAMILIES.keys())


AI_SEARCH_BRANCHES = [
    "Artificial Intelligence",
    "Artificial Intelligence (AI) and Data Science",
    "Artificial Intelligence and Data Science",
    "Artificial Intelligence and Machine Learning",
    "Computer Science and Engineering (Artificial Intelligence and Data Science)",
    "Computer Science and Engineering (Artificial Intelligence)",
    "Computer Science and Engineering(Artificial Intelligence and Machine Learning)",
    "Computer Science and Engineering(Data Science)",
    "Data Science",
    "Robotics and Artificial Intelligence",
]


def build_search_tags():
    search_tags = {}
    for family, branches in USER_BRANCH_FAMILIES.items():
        for branch in branches:
            search_tags.setdefault(branch, set()).add(family)

    for branch in AI_SEARCH_BRANCHES:
        search_tags.setdefault(branch, set()).add("Artificial Intelligence")

    return search_tags


USER_BRANCH_SEARCH_TAGS = build_search_tags()


def normalize_family_input(branch_input):
    branch_key = branch_input.strip()
    upper_key = branch_key.upper().replace(" ", "_")

    if branch_key in USER_BRANCH_FAMILIES:
        return branch_key

    return USER_BRANCH_ALIASES.get(upper_key)


def get_user_family_branches(branch_input):
    family = normalize_family_input(branch_input)
    if not family:
        return []

    branches = [
        branch
        for branch, tags in USER_BRANCH_SEARCH_TAGS.items()
        if family in tags
    ]

    return sorted(branches)
