import 'package:flutter/material.dart';
import '../../models/stakeholder.dart';
import '../common/trend_indicator.dart';
import '../common/animated_progress_bar.dart';

class StakeholderStatus extends StatelessWidget {
  final Map<String, StakeholderInfo> stakeholders;
  final Function(String) onStakeholderTap;

  const StakeholderStatus({
    Key? key,
    required this.stakeholders,
    required this.onStakeholderTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(20),
          topRight: Radius.circular(20),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Stakeholder Relations',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              IconButton(
                icon: const Icon(Icons.info_outline),
                onPressed: () => _showStakeholderInfo(context),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Stakeholder List
          Expanded(
            child: ListView.builder(
              itemCount: stakeholders.length,
              itemBuilder: (context, index) {
                final stakeholder = stakeholders.entries.elementAt(index);
                return _StakeholderCard(
                  stakeholderName: stakeholder.key,
                  info: stakeholder.value,
                  onTap: () => onStakeholderTap(stakeholder.key),
                );
              },
            ),
          ),

          // Overall Relationship Status
          const SizedBox(height: 16),
          _buildOverallStatus(context),
        ],
      ),
    );
  }

  Widget _buildOverallStatus(BuildContext context) {
    final averageSatisfaction = _calculateAverageSatisfaction();
    final relationshipStatus = _getRelationshipStatus(averageSatisfaction);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).dividerColor,
        ),
      ),
      child: Row(
        children: [
          Icon(
            _getStatusIcon(relationshipStatus),
            color: _getStatusColor(relationshipStatus),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Overall Stakeholder Relations',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                Text(
                  relationshipStatus,
                  style: TextStyle(
                    color: _getStatusColor(relationshipStatus),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          CircularProgressIndicator(
            value: averageSatisfaction / 100,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(
              _getStatusColor(relationshipStatus),
            ),
          ),
        ],
      ),
    );
  }

  void _showStakeholderInfo(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Stakeholder Relations'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Understanding stakeholder satisfaction is crucial for sustainable business success.',
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: 16),
              Text(
                'Satisfaction Levels:',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              _buildSatisfactionLegend(context),
              const SizedBox(height: 16),
              Text(
                'Tips:',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              ...stakeholderTips.map((tip) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.tips_and_updates, size: 16),
                    const SizedBox(width: 8),
                    Expanded(child: Text(tip)),
                  ],
                ),
              )),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildSatisfactionLegend(BuildContext context) {
    return Column(
      children: [
        _LegendItem(
          color: Colors.green,
          label: 'Excellent (80-100%)',
          description: 'Strong, positive relationship',
        ),
        _LegendItem(
          color: Colors.blue,
          label: 'Good (60-79%)',
          description: 'Stable, satisfactory relationship',
        ),
        _LegendItem(
          color: Colors.orange,
          label: 'Fair (40-59%)',
          description: 'Needs attention',
        ),
        _LegendItem(
          color: Colors.red,
          label: 'Poor (0-39%)',
          description: 'Immediate action required',
        ),
      ],
    );
  }

  double _calculateAverageSatisfaction() {
    if (stakeholders.isEmpty) return 0;
    final total = stakeholders.values
        .map((info) => info.satisfaction)
        .reduce((a, b) => a + b);
    return total / stakeholders.length;
  }

  String _getRelationshipStatus(double satisfaction) {
    if (satisfaction >= 80) return 'Excellent';
    if (satisfaction >= 60) return 'Good';
    if (satisfaction >= 40) return 'Fair';
    return 'Needs Attention';
  }

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'Excellent':
        return Icons.star;
      case 'Good':
        return Icons.thumb_up;
      case 'Fair':
        return Icons.trending_flat;
      default:
        return Icons.warning;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'Excellent':
        return Colors.green;
      case 'Good':
        return Colors.blue;
      case 'Fair':
        return Colors.orange;
      default:
        return Colors.red;
    }
  }
}

class _StakeholderCard extends StatelessWidget {
  final String stakeholderName;
  final StakeholderInfo info;
  final VoidCallback onTap;

  const _StakeholderCard({
    Key? key,
    required this.stakeholderName,
    required this.info,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  Icon(
                    _getStakeholderIcon(stakeholderName),
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      stakeholderName,
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ),
                  if (info.trend != null)
                    AnimatedTrendIndicator(
                      trend: info.trend!,
                      size: 16,
                    ),
                ],
              ),

              const SizedBox(height: 8),

              // Satisfaction Bar
              AnimatedProgressBar(
                value: info.satisfaction,
                backgroundColor: Colors.grey[200],
                valueColor: _getSatisfactionColor(info.satisfaction),
                height: 8,
              ),

              const SizedBox(height: 4),

              // Status and Recent Event
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${info.satisfaction.toStringAsFixed(1)}% Satisfaction',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  if (info.lastEvent != null)
                    Expanded(
                      child: Text(
                        info.lastEvent!,
                        style: Theme.of(context).textTheme.bodySmall,
                        textAlign: TextAlign.right,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getStakeholderIcon(String stakeholder) {
    switch (stakeholder.toLowerCase()) {
      case 'employees':
        return Icons.people;
      case 'customers':
        return Icons.shopping_cart;
      case 'investors':
        return Icons.trending_up;
      case 'community':
        return Icons.location_city;
      case 'environment':
        return Icons.eco;
      default:
        return Icons.group;
    }
  }

  Color _getSatisfactionColor(double satisfaction) {
    if (satisfaction >= 80) return Colors.green;
    if (satisfaction >= 60) return Colors.blue;
    if (satisfaction >= 40) return Colors.orange;
    return Colors.red;
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final String description;

  const _LegendItem({
    Key? key,
    required this.color,
    required this.label,
    required this.description,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  description,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

const stakeholderTips = [
  'Monitor satisfaction trends to identify potential issues early.',
  'Balance the needs of different stakeholders in decision-making.',
  'Pay special attention to stakeholders with declining satisfaction.',
  'Build long-term relationships through consistent positive actions.',
];