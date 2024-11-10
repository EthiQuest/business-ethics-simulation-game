import 'package:flutter/material.dart';
import 'trend_indicator.dart';

class AnimatedMetricCard extends StatelessWidget {
  final String title;
  final String value;
  final double? trend;
  final IconData icon;
  final VoidCallback onTap;

  const AnimatedMetricCard({
    Key? key,
    required this.title,
    required this.value,
    this.trend,
    required this.icon,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Title and Icon
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  Icon(
                    icon,
                    color: Theme.of(context).primaryColor,
                  ),
                ],
              ),

              // Value and Trend
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Expanded(
                    child: Text(
                      value,
                      style: Theme.of(context).textTheme.headlineSmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (trend != null)
                    TrendIndicator(trend: trend!),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}