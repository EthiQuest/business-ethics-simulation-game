import 'package:flutter_test/flutter_test.dart';
import 'package:ethiquest/bloc/game/game_bloc.dart';
import 'package:ethiquest/models/game_state.dart';

void main() {
  group('GameBloc Tests', () {
    test('initial state should be GameLoadingState', () {
      final gameState = GameState(
        id: '1',
        playerId: 'test_player',
        companyName: 'Test Corp',
        companySize: 'medium',
        level: 1,
        experiencePoints: 0,
        financialResources: 1000000,
        reputationPoints: 50.0,
        marketShare: 10.0,
        sustainabilityRating: 'B',
        stakeholderSatisfaction: {
          'employees': 70.0,
          'customers': 75.0,
          'investors': 65.0,
          'community': 60.0,
          'environment': 80.0,
        },
      );

      expect(gameState.id, equals('1'));
      expect(gameState.companyName, equals('Test Corp'));
      expect(gameState.financialResources, equals(1000000));
    });
  });
}