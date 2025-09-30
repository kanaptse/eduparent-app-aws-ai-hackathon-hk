import 'package:flutter/foundation.dart';

class AppConfig {
  static const String _localUrl = 'http://localhost:8001';
  static const String _stagingUrl = 'https://staging-api-url.com'; // Placeholder for future staging environment
  static const String _productionUrl = 'https://k7lgv1ds9c.execute-api.ap-northeast-1.amazonaws.com/Prod';

  /// Returns the appropriate API base URL based on the current environment
  /// - Debug builds (development): uses local server
  /// - Release builds (production): uses AWS Lambda
  /// - Can be overridden with --dart-define=USE_PRODUCTION_API=true
  static String get apiBaseUrl {
    // Allow forcing production API in debug mode
    const useProductionApi = String.fromEnvironment('USE_PRODUCTION_API');
    if (useProductionApi == 'true') {
      return _productionUrl;
    }

    if (kDebugMode) {
      return _localUrl;
    }
    return _productionUrl;
  }

  /// Returns the current environment name for debugging/logging purposes
  static String get environmentName {
    const useProductionApi = String.fromEnvironment('USE_PRODUCTION_API');
    if (useProductionApi == 'true') {
      return 'Dev+Prod API';
    }
    if (kDebugMode) {
      return 'Development';
    }
    return 'Production';
  }

  /// Whether to show debug information in the UI
  static bool get showDebugInfo => kDebugMode;

  /// API timeout in milliseconds
  static int get apiTimeout => kDebugMode ? 10000 : 30000; // Longer timeout for local development
}