import 'package:flutter/material.dart';

class TrendIndicator extends StatelessWidget {
  final double trend;
  final Color? color;
  final double size;

  const TrendIndicator({
    Key? key,
    required this.trend,
    this.color,
    this.size = 16.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isPositive = trend > 0;
    final displayColor = color ?? (isPositive ? Colors.green : Colors.red);
    final arrowIcon = isPositive ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          arrowIcon,
          color: displayColor,
          size: size,
        ),
        const SizedBox(width: 4),
        Text(
          '${trend.abs().toStringAsFixed(1)}%',
          style: TextStyle(
            color: displayColor,
            fontSize: size * 0.75,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}

class AnimatedTrendIndicator extends StatefulWidget {
  final double trend;
  final Color? color;
  final double size;

  const AnimatedTrendIndicator({
    Key? key,
    required this.trend,
    this.color,
    this.size = 16.0,
  }) : super(key: key);

  @override
  State<AnimatedTrendIndicator> createState() => _AnimatedTrendIndicatorState();
}

class _AnimatedTrendIndicatorState extends State<AnimatedTrendIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );

    _animation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.0, end: 1.2),
        weight: 40.0,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.2, end: 0.9),
        weight: 30.0,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.9, end: 1.0),
        weight: 30.0,
      ),
    ]).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(AnimatedTrendIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.trend != widget.trend) {
      _controller.reset();
      _controller.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _animation,
      child: TrendIndicator(
        trend: widget.trend,
        color: widget.color,
        size: widget.size,
      ),
    );
  }
}

class TrendSparkline extends StatelessWidget {
  final List<double> values;
  final Color? color;
  final double height;
  final double width;

  const TrendSparkline({
    Key? key,
    required this.values,
    this.color,
    this.height = 30.0,
    this.width = 80.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (values.isEmpty) return const SizedBox();

    final points = <Offset>[];
    final maxValue = values.reduce((max, value) => value > max ? value : max);
    final minValue = values.reduce((min, value) => value < min ? value : min);
    final range = maxValue - minValue;
    
    for (int i = 0; i < values.length; i++) {
      final x = (width / (values.length - 1)) * i;
      final normalizedValue = range == 0 ? 0.5 : (values[i] - minValue) / range;
      final y = height - (normalizedValue * height);
      points.add(Offset(x, y));
    }

    return SizedBox(
      height: height,
      width: width,
      child: CustomPaint(
        painter: _SparklinePainter(
          points: points,
          color: color ?? Theme.of(context).primaryColor,
        ),
      ),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<Offset> points;
  final Color color;

  _SparklinePainter({
    required this.points,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round
      ..style = PaintingStyle.stroke;

    final path = Path();
    if (points.isNotEmpty) {
      path.moveTo(points.first.dx, points.first.dy);
      for (int i = 1; i < points.length; i++) {
        path.lineTo(points[i].dx, points[i].dy);
      }
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(_SparklinePainter oldDelegate) {
    return oldDelegate.points != points || oldDelegate.color != color;
  }
}