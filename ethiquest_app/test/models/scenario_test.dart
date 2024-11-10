import 'package:flutter_test/flutter_test.dart';
import 'package:ethiquest/models/scenario.dart';

void main() {
  group('Scenario Model Tests', () {
    test('Create sample scenario', () {
      final scenario = ScenarioFactory.createSample(id: 'test_id');
      
      expect(scenario.id, equals('test_id'));
      expect(scenario.possibleApproaches.length, equals(2));
      expect(scenario.difficultyLevel, equals(0.5));
    });

    test('Scenario JSON serialization', () {
      final originalScenario = ScenarioFactory.createSample(
        id: 'test_id',
        title: 'Test Scenario',
      );
      
      // Convert to JSON and back
      final json = originalScenario.toJson();
      final reconstructedScenario = Scenario.fromJson(json);
      
      // Verify equality
      expect(reconstructedScenario, equals(originalScenario));
    });

    test('Time constraint validation', () {
      final scenario = ScenarioFactory.createSample(id: 'test_id');
      
      // New scenario should be valid
      expect(scenario.isValid(), isTrue);
      
      // Create an expired scenario
      final expiredScenario = scenario.copyWith(
        createdAt: DateTime.now().subtract(const Duration(minutes: 10)),
        timeConstraint: 300, // 5 minutes
      );
      
      expect(expiredScenario.isValid(), isFalse);
    });

    test('Approach impact calculations', () {
      final scenario = ScenarioFactory.createSample(id: 'test_id');
      final conservativeApproach = scenario.possibleApproaches[0];
      
      expect(conservativeApproach.impacts['financial'], equals(-10));
      expect(conservativeApproach.impacts['reputation'], equals(5));
      expect(conservativeApproach.impacts['employees'], equals(10));
    });

    test('Scenario copyWith', () {
      final original = ScenarioFactory.createSample(id: 'test_id');
      final modified = original.copyWith(
        title: 'New Title',
        difficultyLevel: 0.8,
      );
      
      expect(modified.id, equals(original.id));
      expect(modified.title, equals('New Title'));
      expect(modified.difficultyLevel, equals(0.8));
      expect(modified.possibleApproaches, equals(original.possibleApproaches));
    });

    test('Remaining time calculation', () {
      final scenario = ScenarioFactory.createSample(id: 'test_id');
      
      final remainingTime = scenario.getRemainingTime();
      expect(remainingTime, isNotNull);
      expect(remainingTime! <= 300, isTrue); // Should be less than initial time
      expect(remainingTime >= 0, isTrue); // Should not be negative
    });
  });
}