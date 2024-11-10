import 'package:flutter/material.dart';

class AnimatedProgressBar extends StatelessWidget {
  final double value;
  final Color? backgroundColor;
  final Color? valueColor;
  final double height;
  final Duration duration;
  final Curve curve;
  final String? label;
  final TextStyle? labelStyle;
  final bool showPercentage;
  final IconData? icon;
  final bool animate;
  final BorderRadius? borderRadius;

  const AnimatedProgressBar({
    Key? key,
    required this.value,
    this.backgroundColor,
    this.valueColor,
    this.height = 4.0,
    this.duration = const Duration(milliseconds: 750),
    this.curve = Curves.easeInOut,
    this.label,
    this.labelStyle,
    this.showPercentage = false,
    this.icon,
    this.animate = true,
    this.borderRadius,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final effectiveBackgroundColor = backgroundColor ?? 
        Theme.of(context).colorScheme.surfaceVariant;
    
    final effectiveValueColor = valueColor ?? 
        Theme.of(context).colorScheme.primary;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null || showPercentage || icon != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (icon != null) ...[
                  Icon(
                    icon,
                    size: 16,
                    color: effectiveValueColor,
                  ),
                  const SizedBox(width: 4),
                ],
                if (label != null)
                  Expanded(
                    child: Text(
                      label!,
                      style: labelStyle ?? Theme.of(context).textTheme.bodySmall,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                if (showPercentage)
                  Padding(
                    padding: EdgeInsets.only(left: label != null ? 8.0 : 0),
                    child: Text(
                      '${(value * 100).toStringAsFixed(1)}%',
                      style: labelStyle ?? Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: effectiveValueColor,
                      ),
                    ),
                  ),
              ],
            ),
          ),

        Stack(
          children: [
            // Background
            Container(
              height: height,
              decoration: BoxDecoration(
                color: effectiveBackgroundColor,
                borderRadius: borderRadius ?? BorderRadius.circular(height / 2),
              ),
            ),

            // Progress
            animate
                ? TweenAnimationBuilder<double>(
                    duration: duration,
                    curve: curve,
                    tween: Tween<double>(
                      begin: 0,
                      end: value.clamp(0.0, 1.0),
                    ),
                    builder: (context, animatedValue, child) {
                      return _buildProgressBar(
                        context,
                        animatedValue,
                        effectiveValueColor,
                      );
                    },
                  )
                : _buildProgressBar(
                    context,
                    value.clamp(0.0, 1.0),
                    effectiveValueColor,
                  ),

            // Shimmer effect for loading state
            if (value < 0)
              _buildShimmerEffect(context),
          ],
        ),
      ],
    );
  }

  Widget _buildProgressBar(
    BuildContext context,
    double progress,
    Color valueColor,
  ) {
    return FractionallySizedBox(
      widthFactor: progress,
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: valueColor,
          borderRadius: borderRadius ?? BorderRadius.circular(height / 2),
          boxShadow: [
            BoxShadow(
              color: valueColor.withOpacity(0.2),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildShimmerEffect(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        borderRadius: borderRadius ?? BorderRadius.circular(height / 2),
      ),
      child: TweenAnimationBuilder<double>(
        duration: const Duration(milliseconds: 1500),
        tween: Tween<double>(begin: 0, end: 1),
        builder: (context, value, child) {
          return FractionallySizedBox(
            widthFactor: 0.6,
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [
                    Colors.transparent,
                    Theme.of(context).colorScheme.primary.withOpacity(0.2),
                    Colors.transparent,
                  ],
                  stops: [
                    0.0,
                    (value % 1.0),
                    1.0,
                  ],
                ),
                borderRadius: borderRadius ?? BorderRadius.circular(height / 2),
              ),
            ),
          );
        },
      ),
    );
  }
}

class SegmentedProgressBar extends StatelessWidget {
  final double value;
  final int segments;
  final Color? backgroundColor;
  final Color? valueColor;
  final double height;
  final Duration duration;
  final double spacing;

  const SegmentedProgressBar({
    Key? key,
    required this.value,
    this.segments = 5,
    this.backgroundColor,
    this.valueColor,
    this.height = 4.0,
    this.duration = const Duration(milliseconds: 750),
    this.spacing = 4.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final effectiveBackgroundColor = backgroundColor ?? 
        Theme.of(context).colorScheme.surfaceVariant;
    
    final effectiveValueColor = valueColor ?? 
        Theme.of(context).colorScheme.primary;

    final segmentWidth = (1.0 - (spacing * (segments - 1))) / segments;
    final filledSegments = (value * segments).floor();
    final partialSegment = (value * segments) % 1;

    return Row(
      children: List.generate(segments * 2 - 1, (index) {
        if (index.isOdd) {
          return SizedBox(width: spacing);
        }

        final segmentIndex = index ~/ 2;
        final isFilledSegment = segmentIndex < filledSegments;
        final isPartialSegment = segmentIndex == filledSegments;

        return Expanded(
          child: AnimatedProgressBar(
            value: isFilledSegment ? 1 : (isPartialSegment ? partialSegment : 0),
            backgroundColor: effectiveBackgroundColor,
            valueColor: effectiveValueColor,
            height: height,
            duration: duration,
            animate: true,
          ),
        );
      }),
    );
  }
}