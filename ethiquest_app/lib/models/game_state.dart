import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'game_state.g.dart';

enum CompanySize { small, medium, large }

enum ChallengeSeverity { low, medium, high }

enum ChallengeType {
  financial,
  reputation,
  stakeholder,
  environmental,
  operational
}

@JsonSerializable(explicitToJson: true)
class Challenge extends Equatable {
  final String id;
  final String name;
  final ChallengeType type;
  final ChallengeSeverity severity;
  final String description;

  const Challenge({
    required this.id,
    required this.name,
    required this.type,
    required this.severity,
    required this.description,
  });

  factory Challenge.fromJson(Map<String, dynamic> json) => 
      _$ChallengeFromJson(json);

  Map<String, dynamic> toJson() => _$ChallengeToJson(this);

  @override
  List<Object?> get props => [id, name, type, severity, description];
}

@JsonSerializable(explicitToJson: true)
class GameState extends Equatable {
  final String id;
  final String playerId;
  final String companyName;
  final String companySize;
  final int level;
  final int experiencePoints;
  
  // Resources
  final double financialResources;
  final double reputationPoints;
  final double marketShare;
  final String sustainabilityRating;
  
  // Stakeholder Relations
  final Map<String, double> stakeholderSatisfaction;
  
  // Active Challenges
  final List<Challenge> activeChallenges;
  
  // Trends
  final double? financialTrend;
  final double? reputationTrend;
  final double? marketShareTrend;
  final double? sustainabilityTrend;

  const GameState({
    required this.id,
    required this.playerId,
    required this.companyName,
    required this.companySize,
    required this.level,
    required this.experiencePoints,
    required this.financialResources,
    required this.reputationPoints,
    required this.marketShare,
    required this.sustainabilityRating,
    required this.stakeholderSatisfaction,
    this.activeChallenges = const [],
    this.financialTrend,
    this.reputationTrend,
    this.marketShareTrend,
    this.sustainabilityTrend,
  });

  // JSON serialization
  factory GameState.fromJson(Map<String, dynamic> json) => 
      _$GameStateFromJson(json);

  Map<String, dynamic> toJson() => _$GameStateToJson(this);

  // Experience progress calculation
  double get experienceProgress {
    final nextLevelXp = _calculateNextLevelXp(level);
    final currentLevelXp = _calculateNextLevelXp(level - 1);
    final progress = (experiencePoints - currentLevelXp) / 
        (nextLevelXp - currentLevelXp);
    return progress.clamp(0.0, 1.0);
  }

  // Copy with method for immutability
  GameState copyWith({
    String? id,
    String? playerId,
    String? companyName,
    String? companySize,
    int? level,
    int? experiencePoints,
    double? financialResources,
    double? reputationPoints,
    double? marketShare,
    String? sustainabilityRating,
    Map<String, double>? stakeholderSatisfaction,
    List<Challenge>? activeChallenges,
    double? financialTrend,
    double? reputationTrend,
    double? marketShareTrend,
    double? sustainabilityTrend,
  }) {
    return GameState(
      id: id ?? this.id,
      playerId: playerId ?? this.playerId,
      companyName: companyName ?? this.companyName,
      companySize: companySize ?? this.companySize,
      level: level ?? this.level,
      experiencePoints: experiencePoints ?? this.experiencePoints,
      financialResources: financialResources ?? this.financialResources,
      reputationPoints: reputationPoints ?? this.reputationPoints,
      marketShare: marketShare ?? this.marketShare,
      sustainabilityRating: sustainabilityRating ?? this.sustainabilityRating,
      stakeholderSatisfaction: 
          stakeholderSatisfaction ?? Map.from(this.stakeholderSatisfaction),
      activeChallenges: activeChallenges ?? List.from(this.activeChallenges),
      financialTrend: financialTrend ?? this.financialTrend,
      reputationTrend: reputationTrend ?? this.reputationTrend,
      marketShareTrend: marketShareTrend ?? this.marketShareTrend,
      sustainabilityTrend: sustainabilityTrend ?? this.sustainabilityTrend,
    );
  }

  // Helper methods
  static int _calculateNextLevelXp(int level) {
    // Experience points needed for next level using a common game progression formula
    return (1000 * (level * 1.5)).round();
  }

  // For equality comparison
  @override
  List<Object?> get props => [
    id,
    playerId,
    companyName,
    companySize,
    level,
    experiencePoints,
    financialResources,
    reputationPoints,
    marketShare,
    sustainabilityRating,
    stakeholderSatisfaction,
    activeChallenges,
    financialTrend,
    reputationTrend,
    marketShareTrend,
    sustainabilityTrend,
  ];
}

// Initial game state factory
class GameStateFactory {
  static GameState createInitial({
    required String playerId,
    required String companyName,
  }) {
    return GameState(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      playerId: playerId,
      companyName: companyName,
      companySize: CompanySize.small.name,
      level: 1,
      experiencePoints: 0,
      financialResources: 1000000, // Starting with $1M
      reputationPoints: 50.0,      // Neutral reputation
      marketShare: 5.0,            // Starting market share
      sustainabilityRating: 'C',   // Initial rating
      stakeholderSatisfaction: {
        'employees': 50.0,
        'customers': 50.0,
        'investors': 50.0,
        'community': 50.0,
        'environment': 50.0,
      },
      activeChallenges: [],
    );
  }
}