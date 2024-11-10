import 'package:flutter/material.dart';

class TrendIndicator extends StatelessWidget {
  final double trend;
  final double size;

  const TrendIndicator({
    Key? key,
    required this.trend,
    this.size = 16.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isPositive = trend >= 0;
    final color = isPositive ? Colors.green : Colors.red;
    final icon = isPositive ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          color: color,
          size: size,
        ),
        const SizedBox(width: 4),
        Text(
          '${trend.abs().toStringAsFixed(1)}%',
          style: TextStyle(
            color: color,
            fontSize: size * 0.75,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}