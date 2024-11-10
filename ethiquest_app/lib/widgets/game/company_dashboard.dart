import 'package:flutter/material.dart';
import '../../models/game_state.dart';
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
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Company Level and XP
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
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
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Level ${gameState.level}',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      LinearProgressIndicator(
                        value: gameState.experienceProgress,
                        backgroundColor: Colors.grey[200],
                        valueColor: AlwaysStoppedAnimation<Color>(
                          Theme.of(context).primaryColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Chip(
                label: Text(gameState.companySize.toUpperCase()),
                backgroundColor: Theme.of(context).primaryColorLight,
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Key Metrics Grid
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
                  value: '${gameState.reputationPoints.toStringAsFixed(1)}',
                  trend: gameState.reputationTrend,
                  icon: Icons.star,
                  color: _getReputationColor(gameState.reputationPoints),
                  onTap: () => onMetricTap(GameMetric(
                    name: 'Reputation',
                    value: gameState.reputationPoints,
                    trend: gameState.reputationTrend,
                    description: 'Overall company reputation and standing',
                  )),
                ),

                // Market Share
                AnimatedMetricCard(
                  title: 'Market Share',
                  value: '${gameState.marketShare.toStringAsFixed(1)}%',
                  trend: gameState.marketShareTrend,
                  icon: Icons.pie_chart,
                  onTap: () => onMetricTap(GameMetric(
                    name: 'Market Share',
                    value: gameState.marketShare,
                    trend: gameState.marketShareTrend,
                    description: 'Company\'s share of the target market',
                  )),
                ),

                // Sustainability
                AnimatedMetricCard(
                  title: 'Sustainability',
                  value: gameState.sustainabilityRating,
                  trend: gameState.sustainabilityTrend,
                  icon: Icons.eco,
                  color: _getSustainabilityColor(gameState.sustainabilityRating),
                  onTap: () => onMetricTap(GameMetric(
                    name: 'Sustainability',
                    value: gameState.sustainabilityRating,
                    trend: gameState.sustainabilityTrend,
                    description: 'Environmental and social sustainability rating',
                  )),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // Active Challenges
          if (gameState.activeChallenges.isNotEmpty) ...[
            Text(
              'Active Challenges',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 60,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: gameState.activeChallenges.length,
                itemBuilder: (context, index) {
                  final challenge = gameState.activeChallenges[index];
                  return Card(
                    margin: const EdgeInsets.only(right: 8),
                    color: _getChallengeColor(challenge.severity),
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Row(
                        children: [
                          Icon(
                            _getChallengeIcon(challenge.type),
                            color: Colors.white,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            challenge.name,
                            style: const TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getReputationColor(double reputation) {
    if (reputation >= 80) return Colors.green;
    if (reputation >= 60) return Colors.blue;
    if (reputation >= 40) return Colors.orange;
    return Colors.red;
  }

  Color _getSustainabilityColor(String rating) {
    switch (rating[0]) {
      case 'A':
        return Colors.green;
      case 'B':
        return Colors.blue;
      case 'C':
        return Colors.orange;
      default:
        return Colors.red;
    }
  }

  Color _getChallengeColor(ChallengeSeverity severity) {
    switch (severity) {
      case ChallengeSeverity.low:
        return Colors.blue;
      case ChallengeSeverity.medium:
        return Colors.orange;
      case ChallengeSeverity.high:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getChallengeIcon(ChallengeType type) {
    switch (type) {
      case ChallengeType.financial:
        return Icons.attach_money;
      case ChallengeType.reputation:
        return Icons.star;
      case ChallengeType.stakeholder:
        return Icons.people;
      case ChallengeType.environmental:
        return Icons.eco;
      default:
        return Icons.warning;
    }
  }
}