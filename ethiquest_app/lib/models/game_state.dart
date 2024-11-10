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

@JsonSerializable()
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

@JsonSerializable()
class GameState extends Equatable {
  final String id;
  final String playerId;
  final String companyName;
  final String companySize;
  final int level;
  final int experiencePoints;
  final double financialResources;
  final double reputationPoints;
  final double marketShare;
  final String sustainabilityRating;
  final Map<String, double> stakeholderSatisfaction;
  @JsonKey(defaultValue: [])
  final List<Challenge> activeChallenges;
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

  factory GameState.fromJson(Map<String, dynamic> json) => 
      _$GameStateFromJson(json);

  Map<String, dynamic> toJson() => _$GameStateToJson(this);

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
          stakeholderSatisfaction ?? this.stakeholderSatisfaction,
      activeChallenges: activeChallenges ?? this.activeChallenges,
      financialTrend: financialTrend ?? this.financialTrend,
      reputationTrend: reputationTrend ?? this.reputationTrend,
      marketShareTrend: marketShareTrend ?? this.marketShareTrend,
      sustainabilityTrend: sustainabilityTrend ?? this.sustainabilityTrend,
    );
  }

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