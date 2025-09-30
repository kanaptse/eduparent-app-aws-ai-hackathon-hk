import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../config/app_config.dart';

class AuthService extends ChangeNotifier {
  static const _storage = FlutterSecureStorage();
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  static const String _guestKey = 'guest_mode';
  static const String _guestUserKey = 'guest_user_data';

  User? _currentUser;
  String? _token;
  bool _isLoading = false;
  String? _lastError;
  bool _isGuest = false;

  User? get currentUser => _currentUser;
  String? get token => _token;
  bool get isAuthenticated => _currentUser != null && (_token != null || _isGuest);
  bool get isGuest => _isGuest;
  bool get isLoading => _isLoading;
  String? get lastError => _lastError;

  AuthService() {
    _loadStoredAuth();
  }

  Future<void> _loadStoredAuth() async {
    try {
      // Check for regular authentication first
      final storedToken = await _storage.read(key: _tokenKey);
      final storedUserData = await _storage.read(key: _userKey);

      if (storedToken != null && storedUserData != null) {
        _token = storedToken;
        _currentUser = User.fromJson(jsonDecode(storedUserData));
        _isGuest = false;
        notifyListeners();
        return;
      }

      // Check for guest mode
      final prefs = await SharedPreferences.getInstance();
      final isGuestStored = prefs.getBool(_guestKey) ?? false;
      final guestUserData = prefs.getString(_guestUserKey);

      if (isGuestStored && guestUserData != null) {
        _isGuest = true;
        _currentUser = User.fromJson(jsonDecode(guestUserData));
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error loading stored auth: $e');
    }
  }

  Future<void> _storeAuth(String token, User user) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _userKey, value: jsonEncode(user.toJson()));
  }

  Future<void> _clearAuth() async {
    await _storage.delete(key: _tokenKey);
    await _storage.delete(key: _userKey);
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String? error) {
    _lastError = error;
    notifyListeners();
  }

  Future<bool> register(UserRegistration registration) async {
    _setLoading(true);
    _setError(null);

    try {
      final response = await http.post(
        Uri.parse('${AppConfig.apiBaseUrl}/api/users/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(registration.toJson()),
      );

      if (response.statusCode == 201) {
        final userData = jsonDecode(response.body);
        final user = User.fromJson(userData);
        
        // Auto-login after successful registration
        final loginSuccess = await login(UserLogin(
          email: registration.email,
          password: registration.password,
        ));
        
        _setLoading(false);
        return loginSuccess;
      } else {
        final errorData = jsonDecode(response.body);
        _setError(errorData['detail'] ?? 'Registration failed');
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _setError('Network error: $e');
      _setLoading(false);
      return false;
    }
  }

  Future<bool> login(UserLogin loginData) async {
    _setLoading(true);
    _setError(null);

    try {
      final loginUrl = '${AppConfig.apiBaseUrl}/api/users/login';
      print('🔐 Attempting login to: $loginUrl');
      print('📧 Email: ${loginData.email}');

      final response = await http.post(
        Uri.parse(loginUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(loginData.toJson()),
      );

      print('📡 Login response status: ${response.statusCode}');
      print('📄 Login response body: ${response.body}');

      if (response.statusCode == 200) {
        final tokenData = jsonDecode(response.body);
        final authToken = AuthToken.fromJson(tokenData);
        
        // Get user profile with the token
        final profileResponse = await http.get(
          Uri.parse('${AppConfig.apiBaseUrl}/api/users/profile'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ${authToken.accessToken}',
          },
        );

        if (profileResponse.statusCode == 200) {
          final userData = jsonDecode(profileResponse.body);
          final user = User.fromJson(userData);
          
          _token = authToken.accessToken;
          _currentUser = user;
          
          await _storeAuth(_token!, user);
          
          _setLoading(false);
          notifyListeners();
          return true;
        } else {
          _setError('Failed to load user profile');
          _setLoading(false);
          return false;
        }
      } else {
        print('❌ Login failed with status: ${response.statusCode}');
        try {
          final errorData = jsonDecode(response.body);
          print('❌ Error response: $errorData');
          _setError(errorData['detail'] ?? 'Login failed');
        } catch (parseError) {
          print('❌ Could not parse error response: ${response.body}');
          _setError('Login failed with status ${response.statusCode}');
        }
        _setLoading(false);
        return false;
      }
    } catch (e) {
      print('💥 Network/connection error: $e');
      _setError('Network error: $e');
      _setLoading(false);
      return false;
    }
  }

  Future<void> loginAsGuest() async {
    _setLoading(true);
    _setError(null);

    try {
      // Create a guest user
      final guestId = DateTime.now().millisecondsSinceEpoch; // Use timestamp as unique ID
      final guestUser = User(
        id: guestId,
        fullName: 'Guest User',
        email: 'guest@local.app',
        isActive: true,
        createdAt: DateTime.now(),
      );

      // Store guest state in SharedPreferences
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_guestKey, true);
      await prefs.setString(_guestUserKey, jsonEncode(guestUser.toJson()));

      // Set current state
      _currentUser = guestUser;
      _isGuest = true;
      _token = null; // No token needed for guest

      _setLoading(false);
      notifyListeners();
    } catch (e) {
      _setError('Failed to continue as guest: $e');
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    // Clear user-specific data from SharedPreferences
    if (_currentUser != null) {
      await _clearUserData(_currentUser!.id);
    }

    // Clear guest data if in guest mode
    if (_isGuest) {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_guestKey);
      await prefs.remove(_guestUserKey);
    }

    _currentUser = null;
    _token = null;
    _isGuest = false;
    await _clearAuth();
    _setError(null);
    notifyListeners();
  }

  Future<void> _clearUserData(int userId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final keys = prefs.getKeys();
      
      // Remove all keys that contain the user ID
      final userKeys = keys.where((key) => 
        key.contains('feed_read_${userId}_') || 
        key.contains('feed_streak_$userId') ||
        key.contains('_${userId}_')
      ).toList();
      
      for (final key in userKeys) {
        await prefs.remove(key);
      }
    } catch (e) {
      debugPrint('Error clearing user data: $e');
    }
  }

  Map<String, String> getAuthHeaders() {
    if (_token == null) return {};
    return {
      'Authorization': 'Bearer $_token',
      'Content-Type': 'application/json',
    };
  }

  Future<http.Response> authenticatedGet(String url) async {
    return await http.get(
      Uri.parse(url),
      headers: getAuthHeaders(),
    );
  }

  Future<http.Response> authenticatedPost(String url, Map<String, dynamic> body) async {
    return await http.post(
      Uri.parse(url),
      headers: getAuthHeaders(),
      body: jsonEncode(body),
    );
  }
}