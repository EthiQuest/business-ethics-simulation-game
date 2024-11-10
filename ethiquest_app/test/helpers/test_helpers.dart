import 'package:flutter/material.dart';
import '../../lib/models/game_state.dart';
import '../../lib/models/scenario.dart';
import '../../lib/models/decision.dart';

/// Helper class to wrap widgets for testing with necessary providers
class TestWrapper extends StatelessWidget {
  final Widget child;
  final ThemeData? theme;

  const TestWrapper({
    Key? key,
    required this.child,
    this.theme,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: theme ?? ThemeData.light(),
      home: Scaffold(body: child),
    );
  }
}

/// Mock data generators for testing
class MockData {
  /// Generate a sample game state for testing
  static GameState getSampleGameState({
    String id = 'test_id',
    String playerId = 'test_player',
    String companyName = 'Test Company',
    String companySize = 'small',
    int level = 1,
    double? financialResources,
    double? reputationPoints,
  }) {
    return GameState(
      id: id,
      playerId: playerId,
      companyName: companyName,
      companySize: companySize,
      level: level,
      experiencePoints: 1000,
      financialResources: financialResources ?? 1000000,
      reputationPoints: reputationPoints ?? 50.0,
      marketShare: 10.0,
      sustainabilityRating: 'B',
      stakeholderSatisfaction: {
        'employees': 70.0,
        'customers': 75.0,
        'investors': 65.0,
        'community': 60.0,
        'environment': 80.0,
      },
      activeChallenges: [],
      financialTrend: 2.5,
      reputationTrend: 1.5,
      marketShareTrend: 0.5,
      sustainabilityTrend: 3.0,
    );
  }

  /// Generate a sample scenario for testing
  static Scenario getSampleScenario({
    String id = 'test_scenario',
    String title = 'Test Scenario',
    String category = 'ethics',
    double difficultyLevel = 0.5,
  }) {
    return Scenario(
      id: id,
      title: title,
      description: 'Test scenario description',
      category: category,
      difficultyLevel: difficultyLevel,
      stakeholdersAffected: ['employees', 'customers'],
      possibleApproaches: [
        Approach(
          id: 'approach_1',
          title: 'Conservative Approach',
          description: 'A safe but slow approach',
          impacts: {
            'financial': -10,
            'employees': 15,
            'reputation': 5,
          },
        ),
        Approach(
          id: 'approach_2',
          title: 'Aggressive Approach',
          description: 'A risky but potentially rewarding approach',
          impacts: {
            'financial': 20,
            'employees': -10,
            'reputation': -5,
          },
        ),
      ],
      hiddenFactors: ['market_conditions', 'employee_morale'],
      timeConstraint: 60,
    );
  }

  /// Generate a sample decision for testing
  static Decision getSampleDecision({
    String scenarioId = 'test_scenario',
    String approachId = 'approach_1',
    DateTime? timestamp,
  }) {
    return Decision(
      scenarioId: scenarioId,
      approachId: approachId,
      rationale: 'Test decision rationale',
      timestamp: timestamp ?? DateTime.now(),
    );
  }

  /// Generate a list of sample decisions for testing
  static List<Decision> getSampleDecisions({
    int count = 5,
    String scenarioId = 'test_scenario',
  }) {
    return List.generate(
      count,
      (index) => getSampleDecision(
        scenarioId: '${scenarioId}_$index',
        approachId: 'approach_${index % 2 + 1}',
        timestamp: DateTime.now().subtract(Duration(days: index)),
      ),
    );
  }

  /// Create a pumped widget tester helper
  static Future<void> pumpWidget(
    WidgetTester tester,
    Widget widget, {
    ThemeData? theme,
  }) async {
    await tester.pumpWidget(
      TestWrapper(
        theme: theme,
        child: widget,
      ),
    );
    await tester.pumpAndSettle();
  }

  /// Helper to find widgets by type and text
  static Finder findWidgetByTypeAndText(
    Type widgetType,
    String text,
  ) {
    return find.ancestor(
      of: find.text(text),
      matching: find.byType(widgetType),
    );
  }

  /// Helper to verify color of a widget
  static bool hasColor(Widget widget, Color color) {
    if (widget is Material) {
      return widget.color == color;
    } else if (widget is Container) {
      return widget.color == color;
    } else if (widget is DecoratedBox) {
      final decoration = widget.decoration;
      if (decoration is BoxDecoration) {
        return decoration.color == color;
      }
    }
    return false;
  }

  /// Helper to find all text in a widget
  static List<String> getAllText(WidgetTester tester) {
    return tester
        .widgetList<Text>(find.byType(Text))
        .map((widget) => widget.data ?? '')
        .where((text) => text.isNotEmpty)
        .toList();
  }

  /// Helper to simulate user interaction
  static Future<void> simulateUserInteraction(
    WidgetTester tester,
    Finder finder,
  ) async {
    await tester.tap(finder);
    await tester.pump();
    await tester.pumpAndSettle();
  }
}