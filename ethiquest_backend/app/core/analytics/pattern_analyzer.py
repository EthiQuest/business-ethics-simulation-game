from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

@dataclass
class Decision:
    id: str
    timestamp: datetime
    scenario_type: str
    choice: str
    stakeholders_affected: List[str]
    impacts: Dict[str, float]
    rationale: str
    time_spent: int  # seconds
    difficulty_level: float

@dataclass
class LearningPattern:
    bias_score: float  # -1 to 1, where 0 is balanced
    confidence: float  # 0 to 1
    stakeholder_preferences: Dict[str, float]
    avoided_topics: List[str]
    skill_levels: Dict[str, float]
    learning_rate: float
    decision_speed: float  # relative to average
    consistency_score: float  # 0 to 1

class PatternAnalyzer:
    """Analyzes player decision patterns and learning behavior"""

    def __init__(self, min_decisions: int = 5):
        self.min_decisions = min_decisions
        self.skill_categories = {
            'stakeholder_management': [
                'employee_relations',
                'community_engagement',
                'investor_relations'
            ],
            'ethical_reasoning': [
                'principle_application',
                'consequence_analysis',
                'moral_judgment'
            ],
            'strategic_thinking': [
                'long_term_planning',
                'risk_assessment',
                'resource_allocation'
            ],
            'leadership': [
                'decision_making',
                'crisis_management',
                'change_management'
            ]
        }

    def analyze_patterns(
        self,
        decisions: List[Decision],
        current_level: int
    ) -> LearningPattern:
        """Analyze player's decision patterns and learning behavior"""
        
        if len(decisions) < self.min_decisions:
            return self._generate_initial_pattern()

        try:
            return LearningPattern(
                bias_score=self._calculate_bias_score(decisions),
                confidence=self._calculate_confidence(decisions),
                stakeholder_preferences=self._analyze_stakeholder_preferences(decisions),
                avoided_topics=self._identify_avoided_topics(decisions),
                skill_levels=self._assess_skill_levels(decisions),
                learning_rate=self._calculate_learning_rate(decisions),
                decision_speed=self._analyze_decision_speed(decisions),
                consistency_score=self._calculate_consistency(decisions)
            )
        except Exception as e:
            print(f"Error in pattern analysis: {str(e)}")
            return self._generate_initial_pattern()

    def _calculate_bias_score(self, decisions: List[Decision]) -> float:
        """Calculate bias in decision making"""
        biases = {
            'short_term': 0,
            'financial': 0,
            'stakeholder': 0
        }
        
        for decision in decisions:
            # Short-term vs long-term bias
            impacts = decision.impacts
            short_term_impact = impacts.get('immediate', 0)
            long_term_impact = impacts.get('long_term', 0)
            biases['short_term'] += (short_term_impact - long_term_impact) / 100

            # Financial vs stakeholder bias
            financial_impact = impacts.get('financial', 0)
            stakeholder_impact = np.mean([
                impacts.get(s, 0) for s in decision.stakeholders_affected
            ])
            biases['financial'] += (financial_impact - stakeholder_impact) / 100

        # Normalize biases
        return np.mean(list(biases.values()))

    def _calculate_confidence(self, decisions: List[Decision]) -> float:
        """Calculate player's decision-making confidence"""
        recent_decisions = sorted(decisions, key=lambda x: x.timestamp)[-5:]
        
        factors = {
            'time_spent': [],  # Normalized decision time
            'changes': 0,      # Number of decision changes
            'consistency': []  # Consistency with previous similar decisions
        }
        
        for i, decision in enumerate(recent_decisions):
            # Analyze decision time
            avg_time = np.mean([d.time_spent for d in recent_decisions])
            normalized_time = min(decision.time_spent / avg_time, 2)
            factors['time_spent'].append(normalized_time)
            
            # Check for decision changes
            if i > 0:
                prev_decision = recent_decisions[i-1]
                if decision.scenario_type == prev_decision.scenario_type:
                    similarity = self._calculate_decision_similarity(
                        decision, prev_decision
                    )
                    factors['consistency'].append(similarity)

        confidence_score = np.mean([
            1 - np.std(factors['time_spent']),  # Time consistency
            np.mean(factors['consistency']) if factors['consistency'] else 0.5,
            1 - (factors['changes'] / len(recent_decisions))
        ])
        
        return max(0, min(1, confidence_score))

    def _analyze_stakeholder_preferences(
        self,
        decisions: List[Decision]
    ) -> Dict[str, float]:
        """Analyze preferences toward different stakeholders"""
        stakeholder_impacts = defaultdict(list)
        
        for decision in decisions:
            for stakeholder in decision.stakeholders_affected:
                impact = decision.impacts.get(stakeholder, 0)
                stakeholder_impacts[stakeholder].append(impact)
        
        preferences = {}
        for stakeholder, impacts in stakeholder_impacts.items():
            avg_impact = np.mean(impacts)
            preferences[stakeholder] = (avg_impact + 100) / 200  # Normalize to 0-1
            
        return preferences

    def _identify_avoided_topics(self, decisions: List[Decision]) -> List[str]:
        """Identify topics the player tends to avoid"""
        topic_counts = defaultdict(int)
        topic_avoidance = defaultdict(int)
        
        for decision in decisions:
            topic_counts[decision.scenario_type] += 1
            if self._is_avoidance_behavior(decision):
                topic_avoidance[decision.scenario_type] += 1
        
        avoided_topics = []
        for topic, count in topic_counts.items():
            avoidance_rate = topic_avoidance[topic] / count
            if avoidance_rate > 0.7:  # High avoidance threshold
                avoided_topics.append(topic)
                
        return avoided_topics

    def _assess_skill_levels(self, decisions: List[Decision]) -> Dict[str, float]:
        """Assess player's skill levels in different areas"""
        skills = defaultdict(list)
        
        for decision in decisions:
            # Evaluate each skill category
            for category, subcategories in self.skill_categories.items():
                skill_score = self._calculate_skill_score(decision, subcategories)
                skills[category].append(skill_score)
        
        return {
            category: np.mean(scores)
            for category, scores in skills.items()
        }

    def _calculate_learning_rate(self, decisions: List[Decision]) -> float:
        """Calculate player's learning rate"""
        if len(decisions) < 10:
            return 0.5  # Default for insufficient data
            
        # Sort decisions by time
        sorted_decisions = sorted(decisions, key=lambda x: x.timestamp)
        
        # Calculate performance improvement over time
        performance_trend = []
        window_size = 5
        
        for i in range(len(sorted_decisions) - window_size):
            window = sorted_decisions[i:i+window_size]
            performance = self._calculate_window_performance(window)
            performance_trend.append(performance)
        
        if not performance_trend:
            return 0.5
            
        # Calculate learning rate from trend
        learning_rate = np.polyfit(
            range(len(performance_trend)),
            performance_trend,
            1
        )[0]
        
        # Normalize to 0-1 range
        return max(0, min(1, (learning_rate + 1) / 2))

    def _analyze_decision_speed(self, decisions: List[Decision]) -> float:
        """Analyze decision-making speed relative to difficulty"""
        if not decisions:
            return 0.5
            
        speed_scores = []
        for decision in decisions:
            expected_time = 30 + (90 * decision.difficulty_level)  # seconds
            actual_time = decision.time_spent
            
            speed_ratio = expected_time / actual_time
            speed_scores.append(speed_ratio)
        
        avg_speed = np.mean(speed_scores)
        return max(0, min(1, avg_speed))

    def _calculate_consistency(self, decisions: List[Decision]) -> float:
        """Calculate decision-making consistency"""
        if len(decisions) < 3:
            return 0.5
            
        consistency_scores = []
        scenario_decisions = defaultdict(list)
        
        # Group decisions by scenario type
        for decision in decisions:
            scenario_decisions[decision.scenario_type].append(decision)
        
        # Calculate consistency within each scenario type
        for scenario_type, type_decisions in scenario_decisions.items():
            if len(type_decisions) < 2:
                continue
                
            similarities = []
            for i in range(len(type_decisions)-1):
                for j in range(i+1, len(type_decisions)):
                    similarity = self._calculate_decision_similarity(
                        type_decisions[i],
                        type_decisions[j]
                    )
                    similarities.append(similarity)
            
            if similarities:
                consistency_scores.append(np.mean(similarities))
        
        return np.mean(consistency_scores) if consistency_scores else 0.5

    def _calculate_decision_similarity(
        self,
        decision1: Decision,
        decision2: Decision
    ) -> float:
        """Calculate similarity between two decisions"""
        impact_similarity = self._calculate_impact_similarity(
            decision1.impacts,
            decision2.impacts
        )
        
        stakeholder_similarity = len(
            set(decision1.stakeholders_affected) &
            set(decision2.stakeholders_affected)
        ) / len(
            set(decision1.stakeholders_affected) |
            set(decision2.stakeholders_affected)
        )
        
        return (impact_similarity + stakeholder_similarity) / 2

    def _calculate_impact_similarity(
        self,
        impacts1: Dict[str, float],
        impacts2: Dict[str, float]
    ) -> float:
        """Calculate similarity between impact patterns"""
        all_keys = set(impacts1.keys()) | set(impacts2.keys())
        differences = []
        
        for key in all_keys:
            val1 = impacts1.get(key, 0)
            val2 = impacts2.get(key, 0)
            differences.append(abs(val1 - val2) / 200)  # Normalize by max range
            
        return 1 - np.mean(differences)

    def _calculate_window_performance(self, decisions: List[Decision]) -> float:
        """Calculate performance score for a window of decisions"""
        scores = []
        for decision in decisions:
            impact_score = np.mean(list(decision.impacts.values()))
            difficulty_adj = decision.difficulty_level
            scores.append((impact_score + 100) / 200 * difficulty_adj)
        return np.mean(scores)

    def _is_avoidance_behavior(self, decision: Decision) -> bool:
        """Detect if a decision shows avoidance behavior"""
        # Consider it avoidance if the player:
        # 1. Chose the safest option
        # 2. Spent very little time
        # 3. Had minimal impact
        
        avg_impact = np.mean(list(decision.impacts.values()))
        quick_decision = decision.time_spent < 15  # Less than 15 seconds
        minimal_impact = abs(avg_impact) < 10
        
        return quick_decision and minimal_impact

    def _generate_initial_pattern(self) -> LearningPattern:
        """Generate initial pattern for new players"""
        return LearningPattern(
            bias_score=0.0,
            confidence=0.5,
            stakeholder_preferences={
                'employees': 0.5,
                'community': 0.5,
                'investors': 0.5,
                'environment': 0.5
            },
            avoided_topics=[],
            skill_levels={
                category: 0.3
                for category in self.skill_categories.keys()
            },
            learning_rate=0.5,
            decision_speed=0.5,
            consistency_score=0.5
        )