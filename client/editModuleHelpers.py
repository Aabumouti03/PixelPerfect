from .models import Section

def get_or_create_general_section(module):
    general_section_title = f"{module.title} - General Exercises"
    section, created = Section.objects.get_or_create(
        title=general_section_title,
        defaults={"description": "Auto-generated section for ungrouped exercises."}
    )
    if created:
        module.sections.add(section)
    return section
