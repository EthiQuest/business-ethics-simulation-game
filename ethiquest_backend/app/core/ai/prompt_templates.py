from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ScenarioPrompt:
    """Manages prompt templates for scenario generation"""
    
    @staticmethod
    def build_prompt(context: Dict[str, Any], difficulty: float) -> str:
        """Build a prompt based on context and difficulty"""
        
        base_template = """
        Create a business ethics scenario with the following specifications:
        
        Company Context:
        - Size: {company_size}
        - Industry: {industry}
        - Market Position: {market_position}
        - Current Challenges: {challenges}
        
        Stakeholder Context:
        {stakeholder_details}
        
        Player History:
        - Recent Decisions: {recent_decisions}
        - Learning Patterns: {learning_patterns}
        
        Scenario Requirements:
        1. Difficulty Level: {difficulty}/1.0
        2. Focus Areas: {focus_areas}
        3. Required Stakeholder Involvement: {required_stakeholders}
        4. Learning Objectives: {learning_objectives}
        
        Generate a scenario that:
        - Challenges observed biases in decision-making
        - Creates meaningful tension between stakeholder interests
        - Incorporates realistic business constraints
        - Provides 3-4 distinct approaches with varying risk-reward profiles
        - Includes hidden factors that may emerge during implementation
        
        Response must be in valid JSON format matching the provided schema.
        """
        
        # Format stakeholder details
        stakeholder_details = ScenarioPrompt._format_stakeholder_details(
            context.get('stakeholder_satisfaction', {})
        )
        
        # Identify focus areas based on learning patterns
        focus_areas = ScenarioPrompt._identify_focus_areas(
            context.get('learning_patterns', {})
        )
        
        # Determine required stakeholders based on satisfaction levels
        required_stakeholders = ScenarioPrompt._determine_required_stakeholders(
            context.get('stakeholder_satisfaction', {})
        )
        
        # Generate learning objectives
        learning_objectives = ScenarioPrompt._generate_learning_objectives(
            context.get('learning_patterns', {}),
            difficulty
        )
        
        return base_template.format(
            company_size=context.get('company_size', 'medium'),
            industry=context.get('industry', 'general'),
            market_position=context.get('market_position', 'stable'),
            challenges=", ".join(context.get('current_challenges', [])),
            stakeholder_details=stakeholder_details,
            recent_decisions=ScenarioPrompt._format_recent_decisions(
                context.get('recent_decisions', [])
            ),
            learning_patterns=", ".join(focus_areas),
            difficulty=f"{difficulty:.1f}",
            focus_areas=", ".join(focus_areas),
            required_stakeholders=", ".join(required_stakeholders),
            learning_objectives=", ".join(learning_objectives)
        )

    @staticmethod
    def _format_stakeholder_details(stakeholder_satisfaction: Dict[str, float]) -> str:
        """Format stakeholder satisfaction levels into readable text"""
        details = []
        for stakeholder, satisfaction in stakeholder_satisfaction.items():
            status = "concerned" if satisfaction < 50 else \
                    "neutral" if satisfaction < 75 else "satisfied"
            details.append(f"- {stakeholder.title()}: {satisfaction}% ({status})")
        return "\n".join(details)

    @staticmethod
    def _format_recent_decisions(decisions: list) -> str:
        """Format recent decisions into readable text"""
        if not decisions:
            return "No recent decisions"
        
        formatted = []
        for decision in decisions[-3:]:  # Last 3 decisions
            formatted.append(
                f"- {decision.get('type', 'Unknown')}: "
                f"{decision.get('choice', 'Unknown')} "
                f"(Impact: {decision.get('impact', 'Unknown')})"
            )
        return "\n".join(formatted)

    @staticmethod
    def _identify_focus_areas(learning_patterns: Dict) -> list:
        """Identify areas that need focus based on learning patterns"""
        focus_areas = []
        
        # Check for biases
        if learning_patterns.get('favors_short_term'):
            focus_areas.append('long-term strategic thinking')
        
        # Check for avoided topics
        avoided = learning_patterns.get('avoided_topics', [])
        for topic in avoided:
            focus_areas.append(f'{topic} engagement')
        
        # Check for skill gaps
        gaps = learning_patterns.get('skill_gaps', [])
        focus_areas.extend(gaps)
        
        return focus_areas if focus_areas else ['balanced decision making']

    @staticmethod
    def _determine_required_stakeholders(satisfaction_levels: Dict[str, float]) -> list:
        """Determine which stakeholders should be involved based on satisfaction"""
        required = []
        
        # Include stakeholders with low satisfaction
        for stakeholder, satisfaction in satisfaction_levels.items():
            if satisfaction < 60:
                required.append(stakeholder)
        
        # Always include at least one stakeholder
        if not required and satisfaction_levels:
            required.append(min(satisfaction_levels.items(), key=lambda x: x[1])[0])
        
        return required

    @staticmethod
    def _generate_learning_objectives(patterns: Dict, difficulty: float) -> list:
        """Generate specific learning objectives based on patterns and difficulty"""
        objectives = []
        
        # Basic objectives
        if difficulty < 0.3:
            objectives.append("Understanding stakeholder impacts")
            objectives.append("Identifying ethical considerations")
        
        # Intermediate objectives
        elif difficulty < 0.7:
            objectives.append("Balancing competing interests")
            objectives.append("Managing long-term consequences")
        
        # Advanced objectives
        else:
            objectives.append("Complex stakeholder negotiation")
            objectives.append("Strategic ethical leadership")
        
        # Add specific objectives based on patterns
        if patterns.get('skill_gaps'):
            objectives.extend(f"Develop {skill}" for skill in patterns['skill_gaps'])
        
        return objectives