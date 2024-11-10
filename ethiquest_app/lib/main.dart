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
      activeChallenges: [],
      financialTrend: 5.2,
      reputationTrend: 2.8,
      marketShareTrend: -1.5,
      sustainabilityTrend: 3.0,
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
            Expanded(
              child: CompanyDashboard(
                gameState: gameState,
                onMetricTap: (metric) {
                  // Show a simple snackbar for now
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Tapped metric: ${metric.name}'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}