import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final authService = Provider.of<AuthService>(context, listen: false);
    
    final loginData = UserLogin(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );

    final success = await authService.login(loginData);
    
    if (success && mounted) {
      // Navigation will be handled by the main app when authService notifies
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(authService.lastError ?? 'Login failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _navigateToRegister() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (context) => const RegisterScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: Stack(
          children: [
            Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 400),
                  child: Form(
                    key: _formKey,
                    child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Icon(
                      Icons.school,
                      size: 80,
                      color: Colors.blue,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'app_title'.tr(),
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'welcome_back'.tr(),
                      style: const TextStyle(
                        fontSize: 16,
                        color: Colors.black54,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 48),
                    
                    // Email Field
                    TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: InputDecoration(
                        labelText: 'email'.tr(),
                        border: const OutlineInputBorder(),
                        prefixIcon: const Icon(Icons.email),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'validation_email_required'.tr();
                        }
                        if (!value.contains('@')) {
                          return 'validation_email_invalid'.tr();
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Password Field
                    TextFormField(
                      controller: _passwordController,
                      obscureText: _obscurePassword,
                      decoration: InputDecoration(
                        labelText: 'password'.tr(),
                        border: const OutlineInputBorder(),
                        prefixIcon: const Icon(Icons.lock),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword ? Icons.visibility : Icons.visibility_off,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'validation_password_required'.tr();
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    
                    // Login Button
                    Consumer<AuthService>(
                      builder: (context, authService, child) {
                        return ElevatedButton(
                          onPressed: authService.isLoading ? null : _handleLogin,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: authService.isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                  ),
                                )
                              : Text(
                                  'sign_in'.tr(),
                                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                                ),
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                    
                    // Register Link
                    TextButton(
                      onPressed: _navigateToRegister,
                      child: RichText(
                        text: TextSpan(
                          style: const TextStyle(fontSize: 14),
                          children: [
                            TextSpan(
                              text: "${'dont_have_account'.tr()} ",
                              style: const TextStyle(color: Colors.black54),
                            ),
                            TextSpan(
                              text: 'sign_up'.tr(),
                              style: const TextStyle(
                                color: Colors.blue,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Continue as Guest Button
                    Consumer<AuthService>(
                      builder: (context, authService, child) {
                        return OutlinedButton(
                          onPressed: authService.isLoading ? null : () async {
                            await authService.loginAsGuest();
                          },
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            side: const BorderSide(color: Colors.grey),
                          ),
                          child: Text(
                            'continue_as_guest'.tr(),
                            style: const TextStyle(fontSize: 16, color: Colors.grey),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        // Language Selector
        Positioned(
          top: 16,
          right: 16,
          child: PopupMenuButton<Locale>(
            onSelected: (Locale locale) {
              context.setLocale(locale);
            },
            itemBuilder: (BuildContext context) => [
              PopupMenuItem<Locale>(
                value: const Locale('en'),
                child: Row(
                  children: [
                    const Text('🇺🇸'),
                    const SizedBox(width: 8),
                    const Text('English'),
                  ],
                ),
              ),
              PopupMenuItem<Locale>(
                value: const Locale('zh', 'HK'),
                child: Row(
                  children: [
                    const Text('🇭🇰'),
                    const SizedBox(width: 8),
                    const Text('廣東話'),
                  ],
                ),
              ),
            ],
            child: Container(
              padding: const EdgeInsets.all(8.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: const Icon(
                Icons.language,
                color: Colors.blue,
              ),
            ),
          ),
        ),
        ],
        ),
      ),
    );
  }
}