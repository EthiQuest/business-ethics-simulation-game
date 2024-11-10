import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:bloc_test/bloc_test.dart';
import '../../lib/bloc/game/game_bloc.dart';
import '../../lib/services/game_service.dart';
import '../../lib/services/api_service.dart';
import '../../lib/models/game_state.dart';
import '../../lib/models/scenario.dart';
import '../../lib/models/decision.dart';

// Generate mocks
@GenerateMocks([GameService, ApiService])
void main() {
  late GameService gameService;
  late ApiService apiService;
  late GameBloc gameBloc;

  // Sample test data
  final testGameState = GameState(
    id: '1',
    playerId: '1',
    companyName: 'Test Company',
    level: 1,
    financialResources: 1000000,
    reputationPoints: 50,
    stakeholderSatisfaction: {
      'employees': 75.0,
      'customers': 80.0,
      'investors': 70.0,
    },
  );

  final testScenario = Scenario(
    id: '1',
    title: 'Test Scenario',
    description: 'Test Description',
    category: 'ethics',
    difficultyLevel: 0.5,
    stakeholdersAffected: ['employees', 'customers'],
    possibleApproaches: [
      Approach(
        id: 'a1',
        title: 'Approach 1',
        description: 'Description 1',
        impacts: {'employees': 10, 'financial': -5},
      ),
    ],
  );

  final testDecision = Decision(
    scenarioId: '1',
    approachId: 'a1',
    rationale: 'Test rationale',
    timestamp: DateTime.now(),
  );

  setUp(() {
    gameService = MockGameService();
    apiService = MockApiService();
    gameBloc = GameBloc(
      gameService: gameService,
      apiService: apiService,
    );
  });

  tearDown(() {
    gameBloc.close();
  });

  group('GameBloc', () {
    test('initial state is GameLoadingState', () {
      expect(gameBloc.state, isA<GameLoadingState>());
    });

    blocTest<GameBloc, GameState>(
      'emits [GameLoadingState, GameActiveState] when LoadGameEvent is added',
      build: () {
        when(apiService.getGameState())
            .thenAnswer((_) async => testGameState);
        when(apiService.getRecentDecisions())
            .thenAnswer((_) async => []);
        return gameBloc;
      },
      act: (bloc) => bloc.add(LoadGameEvent()),
      expect: () => [
        isA<GameLoadingState>(),
        isA<GameActiveState>(),
      ],
      verify: (_) {
        verify(apiService.getGameState()).called(1);
        verify(apiService.getRecentDecisions()).called(1);
      },
    );

    blocTest<GameBloc, GameState>(
      'emits updated state with scenario when GenerateScenarioEvent is added',
      build: () {
        when(apiService.generateScenario())
            .thenAnswer((_) async => testScenario);
        return gameBloc;
      },
      seed: () => GameActiveState(gameState: testGameState),
      act: (bloc) => bloc.add(GenerateScenarioEvent()),
      expect: () => [
        isA<GameActiveState>()
            .having((state) => state.currentScenario, 'currentScenario', null),
        isA<GameActiveState>()
            .having((state) => state.currentScenario, 'currentScenario', testScenario),
      ],
      verify: (_) {
        verify(apiService.generateScenario()).called(1);
      },
    );

    blocTest<GameBloc, GameState>(
      'processes decision and updates state when MakeDecisionEvent is added',
      build: () {
        when(gameService.processDecision(any, any, any))
            .thenReturn(testGameState);
        when(apiService.submitDecision(any))
            .thenAnswer((_) async => {});
        when(apiService.getGameState())
            .thenAnswer((_) async => testGameState);
        return gameBloc;
      },
      seed: () => GameActiveState(
        gameState: testGameState,
        currentScenario: testScenario,
      ),
      act: (bloc) => bloc.add(MakeDecisionEvent(decision: testDecision)),
      expect: () => [
        isA<GameActiveState>()
            .having((state) => state.currentScenario, 'currentScenario', null)
            .having((state) => state.gameState, 'gameState', testGameState)
            .having((state) => state.recentDecisions.length, 'recentDecisions', 1),
        isA<GameActiveState>()
            .having((state) => state.gameState, 'gameState', testGameState),
      ],
      verify: (_) {
        verify(gameService.processDecision(any, any, any)).called(1);
        verify(apiService.submitDecision(any)).called(1);
        verify(apiService.getGameState()).called(1);
      },
    );

    blocTest<GameBloc, GameState>(
      'emits error state when API calls fail',
      build: () {
        when(apiService.getGameState())
            .thenThrow(Exception('API Error'));
        return gameBloc;
      },
      act: (bloc) => bloc.add(LoadGameEvent()),
      expect: () => [
        isA<GameLoadingState>(),
        isA<GameErrorState>()
            .having((state) => state.message, 'message', contains('API Error')),
      ],
    );

    blocTest<GameBloc, GameState>(
      'updates game state when UpdateGameStateEvent is added',
      build: () => gameBloc,
      seed: () => GameActiveState(gameState: testGameState),
      act: (bloc) => bloc.add(UpdateGameStateEvent(
        gameState: testGameState.copyWith(level: 2),
      )),
      expect: () => [
        isA<GameActiveState>()
            .having((state) => state.gameState.level, 'level', 2),
      ],
    );
  });
}