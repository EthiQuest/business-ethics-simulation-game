import 'package:flutter/material.dart';

class ImpactIndicator extends StatelessWidget {
  final String label;
  final double value;
  final double size;
  final bool showValue;
  final bool animate;

  const ImpactIndicator({
    Key? key,
    required this.label,
    required this.value,
    this.size = 80.0,
    this.showValue = true,
    this.animate = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Background circle
                Container(
                  width: size * 0.9,
                  height: size * 0.9,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Theme.of(context).scaffoldBackgroundColor,
                    border: Border.all(
                      color: _getImpactColor(value).withOpacity(0.2),
                      width: 2,
                    ),
                  ),
                ),
                
                // Impact circle
                if (animate)
                  TweenAnimationBuilder<double>(
                    duration: const Duration(milliseconds: 1000),
                    curve: Curves.easeInOut,
                    tween: Tween<double>(begin: 0, end: value.abs() / 100),
                    builder: (context, progress, child) {
                      return _buildImpactCircle(context, progress);
                    },
                  )
                else
                  _buildImpactCircle(context, value.abs() / 100),
                
                // Impact value
                if (showValue)
                  Text(
                    '${value > 0 ? "+" : ""}${value.toStringAsFixed(0)}',
                    style: TextStyle(
                      color: _getImpactColor(value),
                      fontWeight: FontWeight.bold,
                      fontSize: size * 0.25,
                    ),
                  ),
              ],
            ),
          ),
          
          // Label
          SizedBox(height: size * 0.1),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontSize: size * 0.15,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildImpactCircle(BuildContext context, double progress) {
    return Container(
      width: size * 0.9,
      height: size * 0.9,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: SweepGradient(
          startAngle: -0.5 * 3.14159,
          endAngle: 1.5 * 3.14159,
          stops: [progress, progress],
          colors: [
            _getImpactColor(value).withOpacity(0.4),
            Colors.transparent,
          ],
        ),
      ),
    );
  }

  Color _getImpactColor(double value) {
    if (value > 75) return Colors.green;
    if (value > 25) return Colors.lightGreen;
    if (value > 0) return Colors.lime;
    if (value > -25) return Colors.orange;
    if (value > -75) return Colors.deepOrange;
    return Colors.red;
  }
}

class CompactImpactIndicator extends StatelessWidget {
  final String label;
  final double value;
  final bool showLabel;

  const CompactImpactIndicator({
    Key? key,
    required this.label,
    required this.value,
    this.showLabel = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getImpactColor(value).withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _getImpactColor(value).withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showLabel) ...[
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(width: 4),
          ],
          Text(
            '${value > 0 ? "+" : ""}${value.toStringAsFixed(0)}',
            style: TextStyle(
              color: _getImpactColor(value),
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getImpactColor(double value) {
    if (value > 75) return Colors.green;
    if (value > 25) return Colors.lightGreen;
    if (value > 0) return Colors.lime;
    if (value > -25) return Colors.orange;
    if (value > -75) return Colors.deepOrange;
    return Colors.red;
  }
}

class ImpactChart extends StatelessWidget {
  final Map<String, double> impacts;
  final double width;
  final double height;
  final bool animate;

  const ImpactChart({
    Key? key,
    required this.impacts,
    this.width = 300,
    this.height = 200,
    this.animate = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: CustomPaint(
        painter: _ImpactChartPainter(
          impacts: impacts,
          animate: animate,
        ),
      ),
    );
  }
}

class _ImpactChartPainter extends CustomPainter {
  final Map<String, double> impacts;
  final bool animate;

  _ImpactChartPainter({
    required this.impacts,
    required this.animate,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width < size.height ? size.width / 2 : size.height / 2;
    
    // Draw background circle
    final bgPaint = Paint()
      ..color = Colors.grey.withOpacity(0.1)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;
    
    canvas.drawCircle(center, radius, bgPaint);

    // Draw impact lines
    final count = impacts.length;
    var angle = 0.0;
    final angleStep = (2 * 3.14159) / count;

    impacts.forEach((key, value) {
      final normalized = value / 100;
      final endPoint = Offset(
        center.dx + radius * normalized * cos(angle),
        center.dy + radius * normalized * sin(angle),
      );

      final paint = Paint()
        ..color = _getImpactColor(value)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0;

      canvas.drawLine(center, endPoint, paint);
      angle += angleStep;
    });
  }

  @override
  bool shouldRepaint(_ImpactChartPainter oldDelegate) {
    return oldDelegate.impacts != impacts;
  }

  Color _getImpactColor(double value) {
    if (value > 75) return Colors.green;
    if (value > 25) return Colors.lightGreen;
    if (value > 0) return Colors.lime;
    if (value > -25) return Colors.orange;
    if (value > -75) return Colors.deepOrange;
    return Colors.red;
  }
}