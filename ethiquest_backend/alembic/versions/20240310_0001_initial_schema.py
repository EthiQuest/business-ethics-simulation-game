"""initial schema

Revision ID: 20240310_0001
Revises: 
Create Date: 2024-03-10 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

# revision identifiers, used by Alembic.
revision = '20240310_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Players table
    op.create_table(
        'players',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('last_active', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('current_level', sa.Integer, default=1),
        sa.Column('experience_points', sa.BigInteger, default=0),
        sa.Column('total_decisions', sa.Integer, default=0),
        sa.Column('company_name', sa.String(100)),
        sa.Column('company_size', sa.String(20)),
        sa.Column('industry', sa.String(50)),
        sa.Column('learning_patterns', JSONB, default=dict),
        sa.Column('skill_levels', JSONB, default=dict),
        sa.Column('achievement_stats', JSONB, default=dict)
    )

    # Game States table
    op.create_table(
        'game_states',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('financial_resources', sa.BigInteger, nullable=False),
        sa.Column('human_resources', sa.Integer, nullable=False),
        sa.Column('reputation_points', sa.Float, nullable=False),
        sa.Column('sustainability_rating', sa.String(2), nullable=False),
        sa.Column('stakeholder_satisfaction', JSONB, nullable=False),
        sa.Column('active_challenges', JSONB, default=list),
        sa.Column('ongoing_events', JSONB, default=list),
        sa.Column('market_share', sa.Float, default=0.0),
        sa.Column('competitor_relations', JSONB, default=dict),
        sa.Column('operational_efficiency', sa.Float, default=50.0),
        sa.Column('innovation_score', sa.Float, default=0.0)
    )

    # Scenarios table
    op.create_table(
        'scenarios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('difficulty_level', sa.Float, nullable=False),
        sa.Column('stakeholders_affected', JSONB, nullable=False),
        sa.Column('possible_approaches', JSONB, nullable=False),
        sa.Column('hidden_factors', JSONB),
        sa.Column('time_pressure', sa.Integer),
        sa.Column('success_metrics', JSONB),
        sa.Column('learning_objectives', JSONB),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('times_used', sa.Integer, default=0),
        sa.Column('average_success', sa.Float)
    )

    # Decisions table
    op.create_table(
        'decisions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('scenario_id', UUID(as_uuid=True), sa.ForeignKey('scenarios.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('choice_made', sa.String(100), nullable=False),
        sa.Column('rationale', sa.Text),
        sa.Column('time_spent', sa.Integer),
        sa.Column('immediate_impacts', JSONB),
        sa.Column('long_term_impacts', JSONB),
        sa.Column('stakeholder_reactions', JSONB),
        sa.Column('ethical_alignment', sa.Float),
        sa.Column('risk_level', sa.Float),
        sa.Column('success_rating', sa.Float)
    )

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('achievement_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('criteria_met', JSONB),
        sa.Column('date_earned', sa.DateTime, nullable=False),
        sa.Column('associated_stats', JSONB)
    )

    # Analytics Logs table
    op.create_table(
        'analytics_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('player_id', UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False),
        sa.Column('decision_patterns', JSONB),
        sa.Column('learning_progress', JSONB),
        sa.Column('skill_development', JSONB),
        sa.Column('engagement_metrics', JSONB),
        sa.Column('feature_vector', JSONB),
        sa.Column('labels', JSONB)
    )

    # Create indexes
    op.create_index('idx_players_username', 'players', ['username'])
    op.create_index('idx_players_email', 'players', ['email'])
    op.create_index('idx_game_states_player_timestamp', 'game_states', ['player_id', 'timestamp'])
    op.create_index('idx_decisions_player_timestamp', 'decisions', ['player_id', 'timestamp'])
    op.create_index('idx_decisions_scenario', 'decisions', ['scenario_id'])
    op.create_index('idx_achievements_player_type', 'achievements', ['player_id', 'achievement_type'])
    op.create_index('idx_analytics_player_timestamp', 'analytics_logs', ['player_id', 'timestamp'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('analytics_logs')
    op.drop_table('achievements')
    op.drop_table('decisions')
    op.drop_table('scenarios')
    op.drop_table('game_states')
    op.drop_table('players')