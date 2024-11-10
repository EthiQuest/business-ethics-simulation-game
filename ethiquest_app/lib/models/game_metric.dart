class GameMetric {
  final String name;
  final dynamic value;
  final double? trend;
  final String description;

  const GameMetric({
    required this.name,
    required this.value,
    this.trend,
    required this.description,
  });
}