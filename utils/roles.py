"""Role-based document access configuration.
Maps 10 organizational roles to 10 documents each.
Only documents assigned to a role are searchable by that role.
"""

# 10 Roles with display names and descriptions
ROLES = {
    "ceo": {"title": "CEO", "description": "Chief Executive Officer — Strategic & Business Intelligence"},
    "director": {"title": "Director", "description": "Director — Technology Leadership & Innovation"},
    "vp": {"title": "VP", "description": "Vice President — Emerging Technologies & Research"},
    "manager": {"title": "Manager", "description": "Manager — Operations, Infrastructure & Processes"},
    "senior_engineer": {"title": "Senior Engineer", "description": "Senior Engineer — Deep Tech & ML Architecture"},
    "engineer": {"title": "Engineer", "description": "Engineer — Programming, Development & Tools"},
    "analyst": {"title": "Analyst", "description": "Analyst — Data, Climate & Environmental Research"},
    "associate": {"title": "Associate", "description": "Associate — Science, Medicine & Health"},
    "assistant": {"title": "Assistant", "description": "Assistant — History & General Knowledge"},
    "intern": {"title": "Intern", "description": "Intern — Space, Astronomy & Foundational Science"},
}

# Map each role to exactly 10 document filenames
ROLE_DOCUMENTS = {
    "ceo": [
        "amazon_company.txt", "apple_company.txt", "google_company.txt",
        "microsoft_corporation.txt", "tesla_company.txt", "global_economy.txt",
        "stock_market.txt", "venture_capital.txt", "supply_chain.txt",
        "digital_payments.txt",
    ],
    "director": [
        "ai_machine_learning.txt", "google_gemini.txt", "openai_gpt.txt",
        "artificial_general_intelligence.txt", "generative_ai.txt",
        "autonomous_vehicles.txt", "electric_vehicles.txt", "robotics.txt",
        "smart_cities.txt", "space_tourism.txt",
    ],
    "vp": [
        "quantum_computing.txt", "blockchain_technology.txt", "nanotechnology.txt",
        "biotechnology.txt", "hydrogen_energy.txt", "3d_printing.txt",
        "augmented_reality.txt", "virtual_reality.txt", "edge_computing.txt",
        "5g_technology.txt",
    ],
    "manager": [
        "cloud_computing.txt", "devops_practices.txt", "microservices.txt",
        "remote_work.txt", "cybersecurity.txt", "data_engineering.txt",
        "fintech_industry.txt", "social_media.txt", "internet_of_things.txt",
        "api_design.txt",
    ],
    "senior_engineer": [
        "transformer_architecture.txt", "neural_networks.txt",
        "natural_language_processing.txt", "computer_vision.txt",
        "reinforcement_learning.txt", "transfer_learning.txt",
        "deep_learning_frameworks.txt", "vector_databases.txt",
        "rag_systems.txt", "embeddings_explained.txt",
    ],
    "engineer": [
        "python_programming.txt", "javascript_ecosystem.txt",
        "database_systems.txt", "linux_operating_system.txt",
        "langchain_framework.txt", "data_privacy_regulations.txt",
        "cryptocurrency_bitcoin.txt", "ai_ethics.txt",
        "satellite_technology.txt", "nuclear_energy.txt",
    ],
    "analyst": [
        "climate_science.txt", "climate_change_effects.txt",
        "renewable_energy.txt", "carbon_capture.txt", "ocean_pollution.txt",
        "deforestation.txt", "biodiversity.txt", "water_scarcity.txt",
        "sustainable_agriculture.txt", "particle_physics.txt",
    ],
    "associate": [
        "genetics_dna.txt", "human_brain.txt", "evolution_biology.txt",
        "vaccination_history.txt", "antibiotics_medicine.txt",
        "mental_health.txt", "nutrition_science.txt",
        "pandemic_preparedness.txt", "telemedicine.txt",
        "quantum_mechanics.txt",
    ],
    "assistant": [
        "world_war_2.txt", "industrial_revolution.txt", "ancient_egypt.txt",
        "roman_empire.txt", "renaissance_period.txt", "french_revolution.txt",
        "cold_war.txt", "silk_road.txt", "magna_carta.txt",
        "moon_landing.txt",
    ],
    "intern": [
        "solar_system.txt", "space_exploration.txt", "black_holes.txt",
        "exoplanets.txt", "big_bang_theory.txt", "hubble_telescope.txt",
        "mars_colonization.txt", "asteroid_mining.txt", "dark_matter.txt",
        "relativity_theory.txt",
    ],
}


def get_role_for_document(filename: str) -> str:
    """Get the role assigned to a document filename."""
    for role, docs in ROLE_DOCUMENTS.items():
        if filename in docs:
            return role
    return "unassigned"


def get_all_roles() -> list[dict]:
    """Return list of all roles with metadata."""
    return [
        {"id": role_id, **info, "doc_count": len(ROLE_DOCUMENTS.get(role_id, []))}
        for role_id, info in ROLES.items()
    ]
