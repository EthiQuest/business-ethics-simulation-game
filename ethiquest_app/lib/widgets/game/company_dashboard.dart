import 'package:flutter/material.dart';
import '../../models/game_state.dart';
import '../../models/game_metric.dart';
import '../common/animated_metric_card.dart';
import '../common/trend_indicator.dart';
import 'package:intl/intl.dart';

class CompanyDashboard extends StatelessWidget {
  final GameState gameState;
  final Function(GameMetric) onMetricTap;
  final currencyFormatter = NumberFormat.currency(symbol: '\$');

  CompanyDashboard({
    Key? key,
    required this.gameState,
    required this.onMetricTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Company Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  gameState.companyName,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                Chip(
                  label: Text(
                    gameState.companySize.toUpperCase(),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Level and Experience
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Theme.of(context).primaryColor,
                    shape: BoxShape.circle,
                  ),
                  child: Text(
                    '${gameState.level}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Level ${gameState.level}',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      LinearProgressIndicator(
                        value: gameState.experienceProgress,
                        backgroundColor: Colors.grey[200],
                      ),
                    ],
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Metrics Grid
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 1.5,
                children: [
                  // Financial Resources
                  AnimatedMetricCard(
                    title: 'Financial Resources',
                    value: currencyFormatter.format(gameState.financialResources),
                    trend: gameState.financialTrend,
                    icon: Icons.attach_money,
                    onTap: () => onMetricTap(GameMetric(
                      name: 'Financial Resources',
                      value: gameState.financialResources,
                      trend: gameState.financialTrend,
                      description: 'Available capital for company operations',
                    )),
                  ),

                  // Reputation
                  AnimatedMetricCard(
                    title: 'Reputation',
                    value: gameState.reputationPoints.toString(),
                    trend: gameState.reputationTrend,
                    icon: Icons.star,
                    onTap: () => onMetricTap(GameMetric(
                      name: 'Reputation',
                      value: gameState.reputationPoints,
                      trend: gameState.reputationTrend,
                      description: 'Company reputation and standing',
                    )),
                  ),

                  // Market Share
                  AnimatedMetricCard(
                    title: 'Market Share',
                    value: '${gameState.marketShare}%',
                    trend: gameState.marketShareTrend,
                    icon: Icons.pie_chart,
                    onTap: () => onMetricTap(GameMetric(
                      name: 'Market Share',
                      value: gameState.marketShare,
                      trend: gameState.marketShareTrend,
                      description: 'Current market share percentage',
                    )),
                  ),

                  // Sustainability
                  AnimatedMetricCard(
                    title: 'Sustainability',
                    value: gameState.sustainabilityRating,
                    trend: gameState.sustainabilityTrend,
                    icon: Icons.eco,
                    onTap: () => onMetricTap(GameMetric(
                      name: 'Sustainability',
                      value: gameState.sustainabilityRating,
                      trend: gameState.sustainabilityTrend,
                      description: 'Environmental sustainability rating',
                    )),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}