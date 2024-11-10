import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../models/player.dart';
import '../models/scenario.dart';
import '../models/game_state.dart';

part 'api_service.g.dart';

@RestApi(baseUrl: "http://localhost:8000")
abstract class ApiService {
  factory ApiService() {
    final dio = Dio()
      ..options = BaseOptions(
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 3),
        headers: {
          'Content-Type': 'application/json',
        },
      )
      ..interceptors.add(LogInterceptor(
        requestBody: true,
        responseBody: true,
      ));

    return _ApiService(dio);
  }

  // Player Endpoints
  @POST("/players")
  Future<Player> createPlayer(@Body() Player player);

  @GET("/players/{playerId}")
  Future<Player> getPlayer(@Path("playerId") String playerId);

  @PUT("/players/{playerId}")
  Future<Player> updatePlayer(
    @Path("playerId") String playerId,
    @Body() Player player,
  );

  // Game State Endpoints
  @GET("/players/{playerId}/state")
  Future<GameState> getGameState(@Path("playerId") String playerId);

  @PUT("/players/{playerId}/state")
  Future<GameState> updateGameState(
    @Path("playerId") String playerId,
    @Body() GameState state,
  );

  // Scenario Endpoints
  @GET("/scenarios/generate")
  Future<Scenario> generateScenario(@Query("playerId") String playerId);

  @POST("/players/{playerId}/decisions")
  Future<Map<String, dynamic>> submitDecision(
    @Path("playerId") String playerId,
    @Query("scenarioId") String scenarioId,
    @Body() Map<String, dynamic> decision,
  );

  // Analytics Endpoints
  @GET("/players/{playerId}/analytics")
  Future<Map<String, dynamic>> getPlayerAnalytics(
    @Path("playerId") String playerId,
  );
}

// Error handling
class ApiError implements Exception {
  final String message;
  final int? statusCode;

  ApiError(this.message, [this.statusCode]);

  @override
  String toString() => 'ApiError: $message (Status: $statusCode)';
}

// Helper class for handling API responses
class ApiResponse<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResponse.success(this.data)
      : error = null,
        isSuccess = true;

  ApiResponse.error(this.error)
      : data = null,
        isSuccess = false;

  bool get hasData => data != null;
}

// Extension methods for API service
extension ApiServiceExtension on ApiService {
  Future<ApiResponse<T>> safeCall<T>(Future<T> Function() call) async {
    try {
      final response = await call();
      return ApiResponse.success(response);
    } on DioException catch (e) {
      final message = _handleDioError(e);
      return ApiResponse.error(message);
    } catch (e) {
      return ApiResponse.error(e.toString());
    }
  }

  String _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return 'Connection timeout. Please check your internet connection.';
      case DioExceptionType.badResponse:
        return _handleErrorResponse(error.response);
      case DioExceptionType.cancel:
        return 'Request cancelled';
      default:
        return 'Something went wrong. Please try again.';
    }
  }

  String _handleErrorResponse(Response? response) {
    if (response == null) return 'No response from server';

    try {
      final data = response.data;
      if (data is Map && data.containsKey('detail')) {
        return data['detail'];
      }
      return 'Server error: ${response.statusCode}';
    } catch (_) {
      return 'Server error: ${response.statusCode}';
    }
  }
}

// Mock API service for testing
class MockApiService implements ApiService {
  @override
  Future<Player> createPlayer(Player player) async {
    // Implement mock behavior
    await Future.delayed(const Duration(milliseconds: 500));
    return player;
  }

  @override
  Future<Player> getPlayer(String playerId) async {
    // Implement mock behavior
    await Future.delayed(const Duration(milliseconds: 500));
    return Player(id: playerId, name: 'Test Player');
  }

  // Implement other methods with mock behavior
  // ...
}