import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../bloc/game/game_bloc.dart';
import '../../bloc/game/game_state.dart';
import '../../widgets/game/company_dashboard.dart';
import '../../widgets/game/decision_panel.dart';
import '../../widgets/game/stakeholder_status.dart';
import '../../widgets/common/loading_overlay.dart';
import '../../models/game_state.dart';

class MainGameScreen extends StatelessWidget {
  const MainGameScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<GameBloc, GameState>(
      builder: (context, state) {
        if (state is GameLoadingState) {
          return const LoadingOverlay();
        }

        if (state is GameErrorState) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Error: ${state.message}',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.red,
                  ),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    context.read<GameBloc>().add(LoadGameEvent());
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }

        if (state is GameActiveState) {
          return Scaffold(
            appBar: AppBar(
              title: Text(state.gameState.companyName),
              actions: [
                IconButton(
                  icon: const Icon(Icons.person),
                  onPressed: () {
                    // Navigate to profile
                    Navigator.pushNamed(context, '/profile');
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.analytics),
                  onPressed: () {
                    // Navigate to analytics
                    Navigator.pushNamed(context, '/analytics');
                  },
                ),
              ],
            ),
            body: SafeArea(
              child: Column(
                children: [
                  // Company Dashboard showing key metrics
                  Expanded(
                    flex: 2,
                    child: CompanyDashboard(
                      gameState: state.gameState,
                      onMetricTap: (metric) {
                        // Show detailed metric information
                        _showMetricDetails(context, metric);
                      },
                    ),
                  ),
                  
                  // Current Scenario/Decision Panel
                  if (state.currentScenario != null)
                    Expanded(
                      flex: 3,
                      child: DecisionPanel(
                        scenario: state.currentScenario!,
                        onDecisionMade: (decision) {
                          context.read<GameBloc>().add(
                            MakeDecisionEvent(decision: decision),
                          );
                        },
                      ),
                    ),

                  // Stakeholder Status Panel
                  Expanded(
                    flex: 2,
                    child: StakeholderStatus(
                      stakeholders: state.gameState.stakeholderSatisfaction,
                      onStakeholderTap: (stakeholder) {
                        // Show stakeholder details
                        _showStakeholderDetails(context, stakeholder);
                      },
                    ),
                  ),
                ],
              ),
            ),
            floatingActionButton: state.currentScenario == null
                ? FloatingActionButton(
                    onPressed: () {
                      context.read<GameBloc>().add(GenerateScenarioEvent());
                    },
                    child: const Icon(Icons.play_arrow),
                  )
                : null,
          );
        }

        // Default loading state
        return const LoadingOverlay();
      },
    );
  }

  void _showMetricDetails(BuildContext context, GameMetric metric) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              metric.name,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(metric.description),
            const SizedBox(height: 16),
            Text(
              'Current Value: ${metric.formattedValue}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (metric.trend != null) ...[
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    metric.trend! > 0
                        ? Icons.trending_up
                        : Icons.trending_down,
                    color: metric.trend! > 0 ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '${metric.trend!.abs()}%',
                    style: TextStyle(
                      color: metric.trend! > 0 ? Colors.green : Colors.red,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _showStakeholderDetails(BuildContext context, Stakeholder stakeholder) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              stakeholder.name,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(stakeholder.description),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: stakeholder.satisfaction / 100,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                stakeholder.satisfaction > 70
                    ? Colors.green
                    : stakeholder.satisfaction > 40
                        ? Colors.orange
                        : Colors.red,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Satisfaction: ${stakeholder.satisfaction}%',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 16),
            if (stakeholder.recentEvents.isNotEmpty) ...[
              Text(
                'Recent Events',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Expanded(
                child: ListView.builder(
                  itemCount: stakeholder.recentEvents.length,
                  itemBuilder: (context, index) {
                    final event = stakeholder.recentEvents[index];
                    return ListTile(
                      leading: Icon(
                        event.impact > 0
                            ? Icons.arrow_upward
                            : Icons.arrow_downward,
                        color: event.impact > 0 ? Colors.green : Colors.red,
                      ),
                      title: Text(event.description),
                      subtitle: Text(event.formattedDate),
                    );
                  },
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}