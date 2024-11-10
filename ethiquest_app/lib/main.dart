import 'package:flutter/material.dart';
import 'models/game_state.dart';
import 'widgets/game/company_dashboard.dart';

void main() {
  runApp(const TestApp());
}

class TestApp extends StatelessWidget {
  const TestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EthiQuest Test',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const TestScreen(),
    );
  }
}

class TestScreen extends StatefulWidget {
  const TestScreen({super.key});

  @override
  State<TestScreen> createState() => _TestScreenState();
}

class _TestScreenState extends State<TestScreen> {
  late GameState gameState;

  @override
  void initState() {
    super.initState();
    // Create sample game state
    gameState = GameState(
      id: '1',
      playerId: 'test_player',
      companyName: 'Test Corp',
      companySize: 'medium',
      level: 3,
      experiencePoints: 2500,
      financialResources: 1500000,
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
  }

  void _handleMetricTap(GameMetric metric) {
    // Show metric details in a dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(metric.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Value: ${metric.value}'),
            if (metric.trend != null)
              Text('Trend: ${metric.trend! > 0 ? '+' : ''}${metric.trend}%'),
            const SizedBox(height: 8),
            Text(metric.description),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('EthiQuest Dashboard Test'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Company Dashboard
            Expanded(
              child: CompanyDashboard(
                gameState: gameState,
                onMetricTap: _handleMetricTap,
              ),
            ),
            // Test Controls
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Test Controls',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        ElevatedButton(
                          onPressed: () {
                            setState(() {
                              gameState = gameState.copyWith(
                                financialResources: 
                                    gameState.financialResources + 100000,
                                financialTrend: 10.5,
                              );
                            });
                          },
                          child: const Text('Increase Finances'),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            setState(() {
                              gameState = gameState.copyWith(
                                reputationPoints: 
                                    gameState.reputationPoints + 5,
                                reputationTrend: 5.0,
                              );
                            });
                          },
                          child: const Text('Boost Reputation'),
                        ),
                        ElevatedButton(
                          onPressed: () {
                            // Add a new challenge
                            setState(() {
                              final challenges = 
                                  List<Challenge>.from(gameState.activeChallenges);
                              challenges.add(
                                Challenge(
                                  id: DateTime.now().toString(),
                                  name: 'Market Competition',
                                  type: ChallengeType.financial,
                                  severity: ChallengeSeverity.high,
                                  description: 'New competitor entered market',
                                ),
                              );
                              gameState = gameState.copyWith(
                                activeChallenges: challenges,
                              );
                            });
                          },
                          child: const Text('Add Challenge'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}