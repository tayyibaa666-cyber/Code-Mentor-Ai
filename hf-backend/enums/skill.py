from enum import Enum

# Define allowed skill levels
class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    all = "all"
