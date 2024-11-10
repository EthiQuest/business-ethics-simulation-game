import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part 'scenario.g.dart';

@JsonSerializable(explicitToJson: true)
class Approach extends Equatable {
  final String id;
  final String title;
  final String description;
  final Map<String, double> impacts;
  
  // Optional fields for more detailed information
  final List<String>? risks;
  final List<String>? opportunities;
  final Map<String, double>? longTermImpacts;

  const Approach({
    required this.id,
    required this.title,
    required this.description,
    required this.impacts,
    this.risks,
    this.opportunities,
    this.longTermImpacts,
  });

  factory Approach.fromJson(Map<String, dynamic> json) => 
      _$ApproachFromJson(json);

  Map<String, dynamic> toJson() => _$ApproachToJson(this);

  @override
  List<Object?> get props => [
    id,
    title,
    description,
    impacts,
    risks,
    opportunities,
    longTermImpacts,
  ];
}

@JsonSerializable(explicitToJson: true)
class Scenario extends Equatable {
  final String id;
  final String title;
  final String description;
  final String category;
  final double difficultyLevel;
  final List<String> stakeholdersAffected;
  final List<Approach> possibleApproaches;
  final List<String>? hiddenFactors;
  final int? timeConstraint;  // Time limit in seconds
  
  // Additional context and analysis
  final Map<String, String>? stakeholderAnalysis;
  final List<String>? keyConsiderations;
  final Map<String, double>? marketConditions;
  
  // Timestamp for scenario creation
  @JsonKey(fromJson: _dateTimeFromJson, toJson: _dateTimeToJson)
  final DateTime createdAt;

  const Scenario({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.difficultyLevel,
    required this.stakeholdersAffected,
    required this.possibleApproaches,
    this.hiddenFactors,
    this.timeConstraint,
    this.stakeholderAnalysis,
    this.keyConsiderations,
    this.marketConditions,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  // JSON serialization
  factory Scenario.fromJson(Map<String, dynamic> json) => 
      _$ScenarioFromJson(json);

  Map<String, dynamic> toJson() => _$ScenarioToJson(this);

  // Helper methods
  static DateTime _dateTimeFromJson(String date) => DateTime.parse(date);
  static String _dateTimeToJson(DateTime date) => date.toIso8601String();

  // Get elapsed time since scenario creation
  int getElapsedTime() {
    return DateTime.now().difference(createdAt).inSeconds;
  }

  // Check if scenario is still valid (within time constraint)
  bool isValid() {
    if (timeConstraint == null) return true;
    return getElapsedTime() < timeConstraint!;
  }

  // Get remaining time in seconds
  int? getRemainingTime() {
    if (timeConstraint == null) return null;
    return timeConstraint! - getElapsedTime();
  }

  // Copy with method
  Scenario copyWith({
    String? id,
    String? title,
    String? description,
    String? category,
    double? difficultyLevel,
    List<String>? stakeholdersAffected,
    List<Approach>? possibleApproaches,
    List<String>? hiddenFactors,
    int? timeConstraint,
    Map<String, String>? stakeholderAnalysis,
    List<String>? keyConsiderations,
    Map<String, double>? marketConditions,
    DateTime? createdAt,
  }) {
    return Scenario(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      difficultyLevel: difficultyLevel ?? this.difficultyLevel,
      stakeholdersAffected: stakeholdersAffected ?? this.stakeholdersAffected,
      possibleApproaches: possibleApproaches ?? this.possibleApproaches,
      hiddenFactors: hiddenFactors ?? this.hiddenFactors,
      timeConstraint: timeConstraint ?? this.timeConstraint,
      stakeholderAnalysis: stakeholderAnalysis ?? this.stakeholderAnalysis,
      keyConsiderations: keyConsiderations ?? this.keyConsiderations,
      marketConditions: marketConditions ?? this.marketConditions,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
    id,
    title,
    description,
    category,
    difficultyLevel,
    stakeholdersAffected,
    possibleApproaches,
    hiddenFactors,
    timeConstraint,
    stakeholderAnalysis,
    keyConsiderations,
    marketConditions,
    createdAt,
  ];
}

// Factory for creating test scenarios
class ScenarioFactory {
  static Scenario createSample({
    required String id,
    String? title,
    double difficultyLevel = 0.5,
  }) {
    return Scenario(
      id: id,
      title: title ?? 'Sample Scenario',
      description: 'This is a sample scenario for testing purposes.',
      category: 'ethics',
      difficultyLevel: difficultyLevel,
      stakeholdersAffected: ['employees', 'community'],
      possibleApproaches: [
        Approach(
          id: 'approach_1',
          title: 'Conservative Approach',
          description: 'A safer, more measured approach.',
          impacts: {
            'financial': -10,
            'reputation': 5,
            'employees': 10,
          },
        ),
        Approach(
          id: 'approach_2',
          title: 'Aggressive Approach',
          description: 'A riskier approach with higher potential rewards.',
          impacts: {
            'financial': 20,
            'reputation': -5,
            'employees': -15,
          },
        ),
      ],
      hiddenFactors: ['market_conditions', 'employee_morale'],
      timeConstraint: 300, // 5 minutes
    );
  }
}