# Environment Configuration

This project now uses automatic environment detection for API configuration.

## How It Works

The app automatically detects whether it's running in development or production mode:

- **Development Mode** (Debug builds): Uses `http://127.0.0.1:8000` (local development server)
- **Production Mode** (Release builds): Uses AWS Lambda endpoint

## Configuration Files

### `lib/config/app_config.dart`
Central configuration file that handles environment detection and provides:
- API base URL
- Environment name
- Debug settings
- API timeout values

## Visual Indicators

In development mode, you'll see:
- **Orange "DEVELOPMENT" badge** in the app bar
- **Console logs** showing environment and API URL on startup

## Development Workflow

1. **Local Development:**
   ```bash
   flutter run -d web-server
   ```
   - Automatically uses `http://127.0.0.1:8000`
   - Shows development badge in UI
   - Prints debug info to console

2. **Production Build:**
   ```bash
   flutter build web
   ```
   - Automatically uses production AWS endpoint
   - No development badges shown
   - No debug console output

## Customization

### Adding New Environments

To add staging or other environments, modify `lib/config/app_config.dart`:

```dart
static String get apiBaseUrl {
  // Check for custom environment variable
  const customEnv = String.fromEnvironment('API_ENV');
  if (customEnv == 'staging') {
    return _stagingUrl;
  }

  if (kDebugMode) {
    return _localUrl;
  }
  return _productionUrl;
}
```

Then build with:
```bash
flutter build web --dart-define=API_ENV=staging
```

### Force Production in Debug Mode

```bash
flutter run --dart-define=API_ENV=production
```

## Benefits

1. **No Manual URL Switching**: Environment is detected automatically
2. **Developer Friendly**: Local development works out of the box
3. **Production Safe**: Release builds use production URLs automatically
4. **Visual Feedback**: Clear indicators show which environment is active
5. **Easy Testing**: Simple to test against different environments

## Migration from Previous Setup

Previous hardcoded URLs have been replaced with `AppConfig.apiBaseUrl` calls:

- `main.dart`: Feed and card-stack API calls
- `auth_service.dart`: Authentication endpoints

The old commented-out local URL has been removed in favor of the automatic detection system.