# Agent Configuration File
# Add new agents here without modifying code

# Default system agents
SYSTEM_AGENTS = [
    {
        "agent_uuid": "english_teacher_001",
        "agent_type": "english_teacher",
        "description": "English language teacher specialized in grammar, vocabulary, writing, and literature analysis",
        "topic": "english_teacher",
        "module_path": "src.agents.english_teacher",
        "class_name": "EnglishTeacherAgent",
    },
    {
        "agent_uuid": "chinese_teacher_001",
        "agent_type": "chinese_teacher",
        "description": "Chinese language teacher specialized in literature, writing, poetry, and cultural context",
        "topic": "chinese_teacher",
        "module_path": "src.agents.chinese_teacher",
        "class_name": "ChineseTeacherAgent",
    },
]

# Example: How to add new agents
# {
#     "agent_uuid": "math_teacher_001",
#     "agent_type": "math_teacher",
#     "description": "Mathematics teacher specialized in algebra, calculus, and problem solving",
#     "topic": "math_teacher",
#     "module_path": "src.agents.math_teacher",
#     "class_name": "MathTeacherAgent"
# },
# {
#     "agent_uuid": "science_teacher_001",
#     "agent_type": "science_teacher",
#     "description": "Science teacher specialized in physics, chemistry, and biology",
#     "topic": "science_teacher",
#     "module_path": "src.agents.science_teacher",
#     "class_name": "ScienceTeacherAgent"
# }

# Agent configuration validation rules
AGENT_CONFIG_SCHEMA = {
    "required_fields": [
        "agent_uuid",
        "agent_type",
        "description",
        "topic",
        "module_path",
        "class_name",
    ],
    "uuid_pattern": r"^[a-zA-Z_][a-zA-Z0-9_]*_\d{3}$",
    "type_pattern": r"^[a-z_]+$",
    "topic_pattern": r"^[a-z_]+$",
}
