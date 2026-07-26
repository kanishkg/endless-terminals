"""
SAP CAP task templates and generation logic.
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random


# Task categories for SAP CAP
CAP_TASK_CATEGORIES = [
    "data_modeling",
    "service_definition",
    "database_operations",
    "handler_implementation",
    "file_management",
]


@dataclass
class CAPTaskTemplate:
    """Template for generating SAP CAP tasks."""

    category: str
    complexity: str  # simple, medium, complex
    description_template: str
    required_files: List[str]
    success_criteria: List[str]
    hints: List[str]
    focus_areas: List[str]


# Data Modeling Templates
DATA_MODELING_TEMPLATES = [
    CAPTaskTemplate(
        category="data_modeling",
        complexity="simple",
        description_template=(
            "Create a CDS data model for a {domain} application.\n\n"
            "Requirements:\n"
            "- Define a {entity1} entity with fields: {fields1}\n"
            "- All fields should have appropriate types (String, Integer, Decimal, etc.)\n"
            "- Add a primary key field named 'ID' of type UUID\n"
            "- Save the model in db/schema.cds"
        ),
        required_files=["db/schema.cds"],
        success_criteria=[
            "db/schema.cds exists",
            "Entity is properly defined with all required fields",
            "CDS file compiles without errors",
        ],
        hints=[
            "Use 'cds init' to create project structure",
            "CDS entities use syntax: entity Name { ... }",
            "UUID type is available in CDS",
        ],
        focus_areas=["entity definition", "field types", "primary keys"],
    ),
    CAPTaskTemplate(
        category="data_modeling",
        complexity="medium",
        description_template=(
            "Create a CDS data model for a {domain} application with relationships.\n\n"
            "Requirements:\n"
            "- Define {entity1} entity with fields: {fields1}\n"
            "- Define {entity2} entity with fields: {fields2}\n"
            "- Create a {relationship_type} relationship from {entity1} to {entity2}\n"
            "- Use appropriate association/composition keywords\n"
            "- Save the model in db/schema.cds"
        ),
        required_files=["db/schema.cds"],
        success_criteria=[
            "db/schema.cds exists",
            "Both entities are properly defined",
            "Relationship is correctly established",
            "CDS file compiles without errors",
        ],
        hints=[
            "Use 'Association' for loose relationships",
            "Use 'Composition' for tight parent-child relationships",
            "Relationships use syntax: fieldName : Association to Entity",
        ],
        focus_areas=["entity relationships", "associations", "compositions"],
    ),
    CAPTaskTemplate(
        category="data_modeling",
        complexity="complex",
        description_template=(
            "Create a comprehensive CDS data model for a {domain} application.\n\n"
            "Requirements:\n"
            "- Define {entity1} entity with {num_fields1} fields\n"
            "- Define {entity2} entity with {num_fields2} fields\n"
            "- Define {entity3} entity for many-to-many relationship\n"
            "- Use managed aspects (cuid, managed) for automatic fields\n"
            "- Add @assert.range annotations for numeric fields\n"
            "- Save the model in db/schema.cds"
        ),
        required_files=["db/schema.cds"],
        success_criteria=[
            "db/schema.cds exists",
            "All entities are properly defined",
            "Many-to-many relationship is correctly modeled",
            "Managed aspects are used",
            "Annotations are applied",
            "CDS file compiles without errors",
        ],
        hints=[
            "Managed aspects: `entity Name : cuid, managed { ... }`",
            "Many-to-many needs a junction entity",
            "@assert.range: [min, max] validates numeric fields",
        ],
        focus_areas=["complex relationships", "managed aspects", "annotations"],
    ),
]


# Service Definition Templates
SERVICE_DEFINITION_TEMPLATES = [
    CAPTaskTemplate(
        category="service_definition",
        complexity="simple",
        description_template=(
            "Create a CDS service that exposes entities for a {domain} application.\n\n"
            "Requirements:\n"
            "- Create a service named '{service_name}'\n"
            "- Expose the {entity1} entity with full CRUD access\n"
            "- Save the service definition in srv/catalog-service.cds"
        ),
        required_files=["srv/catalog-service.cds", "db/schema.cds"],
        success_criteria=[
            "srv/catalog-service.cds exists",
            "Service is properly defined",
            "Entity is exposed in the service",
            "Service compiles without errors",
        ],
        hints=[
            "Service syntax: service ServiceName { ... }",
            "Expose entities: entity EntityName as projection on db.EntityName;",
        ],
        focus_areas=["service definition", "entity exposure"],
    ),
]


# Database Operations Templates
DATABASE_OPERATIONS_TEMPLATES = [
    CAPTaskTemplate(
        category="database_operations",
        complexity="medium",
        description_template=(
            "Initialize database and insert seed data for a {domain} application.\n\n"
            "Requirements:\n"
            "- Deploy the CDS model to SQLite database\n"
            "- Insert {num_records} {entity1} records via CSV or direct SQL\n"
            "- Verify data can be queried\n"
            "- Database file should be named 'sqlite.db'"
        ),
        required_files=["sqlite.db", "db/schema.cds"],
        success_criteria=[
            "Database file sqlite.db exists",
            "Tables are created from schema",
            "Required number of records are inserted",
            "Data can be queried successfully",
        ],
        hints=[
            "Use 'cds deploy --to sqlite' to create database",
            "CSV files in db/data/ are auto-loaded",
            "Or use sqlite3 CLI for direct inserts",
        ],
        focus_areas=["database deployment", "data loading", "SQL operations"],
    ),
]


# Business domains for task generation
BUSINESS_DOMAINS = [
    "bookshop", "inventory", "order management", "employee directory",
    "product catalog", "customer management", "invoice system", "travel booking",
    "project management", "warehouse", "library", "rental service",
]


# Entity examples with fields
ENTITY_EXAMPLES = {
    "bookshop": [
        ("Books", ["ID: UUID", "title: String(100)", "stock: Integer", "price: Decimal(10,2)"]),
        ("Authors", ["ID: UUID", "name: String(100)", "birthYear: Integer"]),
        ("Genres", ["ID: UUID", "name: String(50)", "description: String(500)"]),
    ],
    "inventory": [
        ("Products", ["ID: UUID", "name: String(100)", "quantity: Integer", "price: Decimal(10,2)"]),
        ("Warehouses", ["ID: UUID", "name: String(100)", "location: String(200)"]),
        ("Suppliers", ["ID: UUID", "name: String(100)", "contact: String(100)"]),
    ],
    "order management": [
        ("Orders", ["ID: UUID", "orderNumber: String(20)", "orderDate: Date", "total: Decimal(10,2)"]),
        ("OrderItems", ["ID: UUID", "quantity: Integer", "price: Decimal(10,2)"]),
        ("Customers", ["ID: UUID", "name: String(100)", "email: String(100)"]),
    ],
}


def generate_cap_task(
    category: str,
    complexity: str = "medium",
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a SAP CAP task based on category and complexity.

    Args:
        category: Task category (e.g., 'data_modeling', 'service_definition')
        complexity: Task complexity ('simple', 'medium', 'complex')
        domain: Business domain (e.g., 'bookshop', 'inventory'). Random if None.

    Returns:
        Dict containing task description, files, criteria, etc.
    """
    # Select appropriate template
    if category == "data_modeling":
        templates = [t for t in DATA_MODELING_TEMPLATES if t.complexity == complexity]
    elif category == "service_definition":
        templates = [t for t in SERVICE_DEFINITION_TEMPLATES if t.complexity == complexity]
    elif category == "database_operations":
        templates = [t for t in DATABASE_OPERATIONS_TEMPLATES if t.complexity == complexity]
    else:
        raise ValueError(f"Unknown category: {category}")

    if not templates:
        raise ValueError(f"No templates found for {category}/{complexity}")

    template = random.choice(templates)

    # Select business domain
    if domain is None:
        domain = random.choice(BUSINESS_DOMAINS)

    # Get entity examples for domain
    entities = ENTITY_EXAMPLES.get(domain, ENTITY_EXAMPLES["bookshop"])

    # Fill template with concrete values
    entity1_name, entity1_fields = entities[0]
    entity2_name, entity2_fields = entities[1] if len(entities) > 1 else ("Related", ["ID: UUID"])
    entity3_name, entity3_fields = entities[2] if len(entities) > 2 else ("Extra", ["ID: UUID"])

    # Format fields as string
    fields1_str = ", ".join(entity1_fields)
    fields2_str = ", ".join(entity2_fields)

    # Generate task description from template
    description = template.description_template.format(
        domain=domain,
        entity1=entity1_name,
        entity2=entity2_name,
        entity3=entity3_name,
        fields1=fields1_str,
        fields2=fields2_str,
        num_fields1=len(entity1_fields),
        num_fields2=len(entity2_fields),
        relationship_type=random.choice(["one-to-many", "many-to-many"]),
        service_name="CatalogService",
        num_records=random.randint(3, 10),
    )

    return {
        "task_description": description,
        "category": category,
        "complexity": complexity,
        "domain": domain,
        "required_files": template.required_files,
        "success_criteria": template.success_criteria,
        "hints": template.hints,
        "focus_areas": template.focus_areas,
        "entities": [entity1_name, entity2_name],
    }


def get_all_cap_templates() -> List[CAPTaskTemplate]:
    """Get all available CAP task templates."""
    return (
        DATA_MODELING_TEMPLATES +
        SERVICE_DEFINITION_TEMPLATES +
        DATABASE_OPERATIONS_TEMPLATES
    )