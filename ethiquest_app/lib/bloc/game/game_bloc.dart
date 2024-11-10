import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/game_state.dart';
import '../../models/scenario.dart';
import '../../models/decision.dart';
import '../../services/game_service.dart';
import '../../services/api_service.dart';

// Events
abstract class GameEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class LoadGameEvent extends GameEvent {}

class GenerateScenarioEvent extends GameEvent {}

class MakeDecisionEvent extends GameEvent {
  final Decision decision;

  MakeDecisionEvent({required this.decision});

  @override
  List<Object?> get props => [decision];
}

class UpdateGameStateEvent extends GameEvent {
  final GameState gameState;

  UpdateGameStateEvent({required this.gameState});

  @override
  List<Object?> get props => [gameState];
}

// States
abstract class GameState extends Equatable {
  @override
  List<Object?> get props => [];
}

class GameLoadingState extends GameState {}

class GameErrorState extends GameState {
  final String message;

  GameErrorState({required this.message});

  @override
  List<Object?> get props => [message];
}

class GameActiveState extends GameState {
  final GameState gameState;
  final Scenario? currentScenario;
  final List<Decision> recentDecisions;

  GameActiveState({
    required this.gameState,
    this.currentScenario,
    this.recentDecisions = const [],
  });

  @override
  List<Object?> get props => [gameState, currentScenario, recentDecisions];

  GameActiveState copyWith({
    GameState? gameState,
    Scenario? currentScenario,
    List<Decision>? recentDecisions,
  }) {
    return GameActiveState(
      gameState: gameState ?? this.gameState,
      currentScenario: currentScenario ?? this.currentScenario,
      recentDecisions: recentDecisions ?? this.recentDecisions,
    );
  }
}

// BLoC
class GameBloc extends Bloc<GameEvent, GameState> {
  final GameService gameService;
  final ApiService apiService;

  GameBloc({
    required this.gameService,
    required this.apiService,
  }) : super(GameLoadingState()) {
    on<LoadGameEvent>(_onLoadGame);
    on<GenerateScenarioEvent>(_onGenerateScenario);
    on<MakeDecisionEvent>(_onMakeDecision);
    on<UpdateGameStateEvent>(_onUpdateGameState);
  }

  Future<void> _onLoadGame(
    LoadGameEvent event,
    Emitter<GameState> emit,
  ) async {
    try {
      emit(GameLoadingState());

      // Load game state from server
      final gameState = await apiService.getGameState();
      final recentDecisions = await apiService.getRecentDecisions();

      emit(GameActiveState(
        gameState: gameState,
        recentDecisions: recentDecisions,
      ));
    } catch (e) {
      emit(GameErrorState(message: 'Failed to load game: $e'));
    }
  }

  Future<void> _onGenerateScenario(
    GenerateScenarioEvent event,
    Emitter<GameState> emit,
  ) async {
    try {
      if (state is! GameActiveState) return;
      final currentState = state as GameActiveState;

      // Show loading state while keeping current game state
      emit(currentState.copyWith(currentScenario: null));

      // Generate new scenario
      final scenario = await apiService.generateScenario();

      emit(currentState.copyWith(currentScenario: scenario));
    } catch (e) {
      emit(GameErrorState(message: 'Failed to generate scenario: $e'));
    }
  }

  Future<void> _onMakeDecision(
    MakeDecisionEvent event,
    Emitter<GameState> emit,
  ) async {
    try {
      if (state is! GameActiveState) return;
      final currentState = state as GameActiveState;

      // Process decision locally first
      final processedState = gameService.processDecision(
        currentState.gameState,
        currentState.currentScenario!,
        event.decision,
      );

      // Update local state immediately
      emit(currentState.copyWith(
        gameState: processedState,
        currentScenario: null, // Clear current scenario
        recentDecisions: [
          event.decision,
          ...currentState.recentDecisions,
        ].take(10).toList(), // Keep last 10 decisions
      ));

      // Send decision to server
      await apiService.submitDecision(event.decision);

      // Get updated game state from server
      final updatedState = await apiService.getGameState();
      
      emit(currentState.copyWith(gameState: updatedState));
    } catch (e) {
      emit(GameErrorState(message: 'Failed to process decision: $e'));
    }
  }

  Future<void> _onUpdateGameState(
    UpdateGameStateEvent event,
    Emitter<GameState> emit,
  ) async {
    try {
      if (state is! GameActiveState) return;
      final currentState = state as GameActiveState;

      emit(currentState.copyWith(gameState: event.gameState));
    } catch (e) {
      emit(GameErrorState(message: 'Failed to update game state: $e'));
    }
  }
}