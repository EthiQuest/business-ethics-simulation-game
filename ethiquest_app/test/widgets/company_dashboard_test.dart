import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import '../../lib/widgets/game/company_dashboard.dart';
import '../../lib/models/game_state.dart';
import '../../lib/models/game_metric.dart';

void main() {
  late GameState testGameState;

  setUp(() {
    testGameState = GameState(
      id: '1',
      playerId: 'test_player',
      companyName: 'Test Corp',
      companySize: 'medium',
      level: 3,
      experiencePoints: 2500,
      financialResources: 1000000,
      reputationPoints: 75.5,
      marketShare: 23.4,
      sustainabilityRating: 'A-',
      stakeholderSatisfaction: {
        'employees': 82.0,
        'customers': 78.5,
        'investors': 70.0,
        'community': 65.0,
        'environment': 85.0,
      },
      activeChallenges: [
        Challenge(
          id: '1',
          name: 'Employee Retention',
          type: ChallengeType.stakeholder,
          severity: ChallengeSeverity.medium,
          description: 'Address declining employee satisfaction',
        ),
      ],
      financialTrend: 5.2,
      reputationTrend: 2.8,
      marketShareTrend: -1.5,
      sustainabilityTrend: 3.0,
    );
  });

  testWidgets('CompanyDashboard displays basic company info', (WidgetTester tester) async {
    // Build widget
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: testGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify company name is displayed
    expect(find.text('Test Corp'), findsOneWidget);
    
    // Verify level is displayed
    expect(find.text('Level 3'), findsOneWidget);
    
    // Verify company size is displayed
    expect(find.text('MEDIUM'), findsOneWidget);
  });

  testWidgets('CompanyDashboard displays all metrics correctly', (WidgetTester tester) async {
    // Track metrics that were tapped
    final tappedMetrics = <GameMetric>[];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: testGameState,
            onMetricTap: (metric) => tappedMetrics.add(metric),
          ),
        ),
      ),
    );

    // Verify financial resources are displayed and formatted
    expect(find.text('\$1,000,000'), findsOneWidget);
    
    // Verify reputation points
    expect(find.text('75.5'), findsOneWidget);
    
    // Verify market share
    expect(find.text('23.4%'), findsOneWidget);
    
    // Verify sustainability rating
    expect(find.text('A-'), findsOneWidget);

    // Test metric card taps
    await tester.tap(find.text('\$1,000,000'));
    await tester.pumpAndSettle();
    expect(tappedMetrics.length, 1);
    expect(tappedMetrics.first.name, 'Financial Resources');

    await tester.tap(find.text('75.5'));
    await tester.pumpAndSettle();
    expect(tappedMetrics.length, 2);
    expect(tappedMetrics.last.name, 'Reputation');
  });

  testWidgets('CompanyDashboard displays trends correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: testGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify positive trends
    expect(find.text('+5.2%'), findsOneWidget);  // Financial trend
    expect(find.text('+2.8%'), findsOneWidget);  // Reputation trend
    
    // Verify negative trends
    expect(find.text('-1.5%'), findsOneWidget);  // Market share trend
    
    // Verify trend icons
    expect(
      find.byIcon(Icons.trending_up),
      findsNWidgets(3),  // Financial, Reputation, and Sustainability trends
    );
    expect(
      find.byIcon(Icons.trending_down),
      findsOneWidget,    // Market share trend
    );
  });

  testWidgets('CompanyDashboard displays active challenges', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: testGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify challenge section exists
    expect(find.text('Active Challenges'), findsOneWidget);
    
    // Verify challenge details
    expect(find.text('Employee Retention'), findsOneWidget);
    
    // Verify challenge icon based on type
    expect(find.byIcon(Icons.people), findsOneWidget);
    
    // Verify challenge severity indicator
    final challengeCard = find.ancestor(
      of: find.text('Employee Retention'),
      matching: find.byType(Card),
    );
    expect(challengeCard, findsOneWidget);
    
    // Verify color based on severity
    final card = tester.widget<Card>(challengeCard);
    expect(
      card.color,
      equals(Colors.orange),  // Medium severity color
    );
  });

  testWidgets('CompanyDashboard handles empty challenges gracefully', (WidgetTester tester) async {
    // Create game state with no challenges
    final emptyGameState = testGameState.copyWith(
      activeChallenges: [],
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: emptyGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify no challenges section is shown
    expect(find.text('Active Challenges'), findsNothing);
  });

  testWidgets('CompanyDashboard updates when game state changes', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: testGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify initial state
    expect(find.text('Level 3'), findsOneWidget);

    // Update game state
    final updatedGameState = testGameState.copyWith(
      level: 4,
      financialResources: 1200000,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: CompanyDashboard(
            gameState: updatedGameState,
            onMetricTap: (_) {},
          ),
        ),
      ),
    );

    // Verify updated values are displayed
    expect(find.text('Level 4'), findsOneWidget);
    expect(find.text('\$1,200,000'), findsOneWidget);
  });
}