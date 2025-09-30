import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import 'package:easy_localization/easy_localization.dart';
import 'services/auth_service.dart';
import 'screens/login_screen.dart';
import 'config/app_config.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();

  if (AppConfig.showDebugInfo) {
    print('🚀 Starting EduParent App in ${AppConfig.environmentName} mode');
    print('🌐 API Base URL: ${AppConfig.apiBaseUrl}');
  }

  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('en'), Locale('zh', 'HK')],
      path: 'assets/translations',
      fallbackLocale: const Locale('en'),
      child: const EduParentApp(),
    ),
  );
}

enum AppView { home, feed, roleplay, dailyActionChallenge, report, cardStack }

class FeedItem {
  final String title;
  final String text;
  
  FeedItem({required this.title, required this.text});
}

class ContentCard {
  final String id;
  final String title;
  final String content;
  final int order;

  ContentCard({required this.id, required this.title, required this.content, required this.order});

  factory ContentCard.fromJson(Map<String, dynamic> json) {
    return ContentCard(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      order: json['order'],
    );
  }
}

class ActionQuest {
  final String id;
  final String title;
  final String prompt;
  final String inputPlaceholder;
  
  ActionQuest({required this.id, required this.title, required this.prompt, required this.inputPlaceholder});
  
  factory ActionQuest.fromJson(Map<String, dynamic> json) {
    return ActionQuest(
      id: json['id'],
      title: json['title'],
      prompt: json['prompt'],
      inputPlaceholder: json['input_placeholder'],
    );
  }
}

class CardStack {
  final String id;
  final String title;
  final String description;
  final List<ContentCard> cards;
  final String summary;
  final ActionQuest? actionQuest;
  final int estimatedReadTime;
  final int totalCards;

  CardStack({
    required this.id,
    required this.title,
    required this.description,
    required this.cards,
    required this.summary,
    this.actionQuest,
    required this.estimatedReadTime,
    required this.totalCards
  });

  factory CardStack.fromJson(Map<String, dynamic> json) {
    var cardsJson = json['cards'] as List;
    List<ContentCard> cardsList = cardsJson.map((i) => ContentCard.fromJson(i)).toList();

    return CardStack(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      cards: cardsList,
      summary: json['summary'],
      actionQuest: json['action_quest'] != null ? ActionQuest.fromJson(json['action_quest']) : null,
      estimatedReadTime: json['estimated_read_time'],
      totalCards: json['total_cards'],
    );
  }
}

class CardStackPreview {
  final String id;
  final String title;
  final String description;
  final int totalCards;
  final int estimatedReadTime;
  final bool isCompleted;
  
  CardStackPreview({
    required this.id, 
    required this.title, 
    required this.description, 
    required this.totalCards, 
    required this.estimatedReadTime, 
    required this.isCompleted
  });
  
  factory CardStackPreview.fromJson(Map<String, dynamic> json) {
    return CardStackPreview(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      totalCards: json['total_cards'],
      estimatedReadTime: json['estimated_read_time'],
      isCompleted: json['is_completed'],
    );
  }
}

class EnhancedFeedItem {
  final String type;
  final FeedItem? simpleItem;
  final CardStackPreview? stackPreview;
  
  EnhancedFeedItem({required this.type, this.simpleItem, this.stackPreview});
  
  factory EnhancedFeedItem.fromJson(Map<String, dynamic> json) {
    return EnhancedFeedItem(
      type: json['type'],
      simpleItem: json['simple_item'] != null ? FeedItem(
        title: json['simple_item']['title'],
        text: json['simple_item']['text'],
      ) : null,
      stackPreview: json['stack_preview'] != null ? CardStackPreview.fromJson(json['stack_preview']) : null,
    );
  }
}

class ReportData {
  final String goal;
  final String note;

  ReportData({required this.goal, required this.note});
}

class ScenarioInfo {
  final String id;
  final String title;
  final String background;
  final String teenOpening;
  final bool isMultiRound;
  final String level;

  ScenarioInfo({
    required this.id,
    required this.title,
    required this.background,
    required this.teenOpening,
    this.isMultiRound = false,
    this.level = 'Basic',
  });

  factory ScenarioInfo.fromJson(String id, Map<String, dynamic> json) {
    return ScenarioInfo(
      id: id,
      title: json['title'] as String,
      background: json['background'] as String,
      teenOpening: json['teen_opening'] as String,
      level: json['level']?.toString() ?? 'Basic',
      isMultiRound: json['is_multi_round'] as bool? ?? false,
    );
  }
}

class GameState {
  final String scenarioTitle;
  final String scenarioBackground;
  final String teenOpening;
  final String parentResponse;
  final int attempts;
  final int maxAttempts;
  final EvaluationResult? evaluation;
  final String? teenResponse;
  final bool gameCompleted;
  final int? finalScore;

  // Multi-round fields
  final bool isMultiRound;
  final int currentRound;
  final int maxRounds;
  final int roundAttempts;
  final int maxRoundAttempts;
  final MultiRoundEvaluationResult? multiRoundEvaluation;
  final List<RoundSummary> roundsHistory;
  final ScenarioCompletion? scenarioCompletion;

  GameState({
    required this.scenarioTitle,
    required this.scenarioBackground,
    required this.teenOpening,
    this.parentResponse = '',
    this.attempts = 0,
    this.maxAttempts = 3,
    this.evaluation,
    this.teenResponse,
    this.gameCompleted = false,
    this.finalScore,
    this.isMultiRound = false,
    this.currentRound = 1,
    this.maxRounds = 1,
    this.roundAttempts = 0,
    this.maxRoundAttempts = 3,
    this.multiRoundEvaluation,
    this.roundsHistory = const [],
    this.scenarioCompletion,
  });

  GameState copyWith({
    String? scenarioTitle,
    String? scenarioBackground,
    String? teenOpening,
    String? parentResponse,
    int? attempts,
    int? maxAttempts,
    EvaluationResult? evaluation,
    String? teenResponse,
    bool? gameCompleted,
    int? finalScore,
    bool? isMultiRound,
    int? currentRound,
    int? maxRounds,
    int? roundAttempts,
    int? maxRoundAttempts,
    MultiRoundEvaluationResult? multiRoundEvaluation,
    List<RoundSummary>? roundsHistory,
    ScenarioCompletion? scenarioCompletion,
  }) {
    return GameState(
      scenarioTitle: scenarioTitle ?? this.scenarioTitle,
      scenarioBackground: scenarioBackground ?? this.scenarioBackground,
      teenOpening: teenOpening ?? this.teenOpening,
      parentResponse: parentResponse ?? this.parentResponse,
      attempts: attempts ?? this.attempts,
      maxAttempts: maxAttempts ?? this.maxAttempts,
      evaluation: evaluation ?? this.evaluation,
      teenResponse: teenResponse ?? this.teenResponse,
      gameCompleted: gameCompleted ?? this.gameCompleted,
      finalScore: finalScore ?? this.finalScore,
      isMultiRound: isMultiRound ?? this.isMultiRound,
      currentRound: currentRound ?? this.currentRound,
      maxRounds: maxRounds ?? this.maxRounds,
      roundAttempts: roundAttempts ?? this.roundAttempts,
      maxRoundAttempts: maxRoundAttempts ?? this.maxRoundAttempts,
      multiRoundEvaluation: multiRoundEvaluation ?? this.multiRoundEvaluation,
      roundsHistory: roundsHistory ?? this.roundsHistory,
      scenarioCompletion: scenarioCompletion ?? this.scenarioCompletion,
    );
  }
}

class MultiRoundEvaluationResult {
  final Map<String, int> criteriaScores;
  final int totalScore;
  final int maxPossibleScore;
  final String feedback;
  final Map<String, String> detailedFeedback;
  final bool passed;
  final int roundNumber;

  MultiRoundEvaluationResult({
    required this.criteriaScores,
    required this.totalScore,
    required this.maxPossibleScore,
    required this.feedback,
    required this.detailedFeedback,
    required this.passed,
    required this.roundNumber,
  });

  factory MultiRoundEvaluationResult.fromJson(Map<String, dynamic> json) {
    return MultiRoundEvaluationResult(
      criteriaScores: Map<String, int>.from(json['criteria_scores'] ?? {}),
      totalScore: json['total_score'] ?? 0,
      maxPossibleScore: json['max_possible_score'] ?? 10,
      feedback: json['feedback'] ?? '',
      detailedFeedback: Map<String, String>.from(json['detailed_feedback'] ?? {}),
      passed: json['passed'] ?? false,
      roundNumber: json['round_number'] ?? 1,
    );
  }
}

class RoundSummary {
  final int roundNumber;
  final bool passed;
  final int score;
  final int attemptsUsed;

  RoundSummary({
    required this.roundNumber,
    required this.passed,
    required this.score,
    required this.attemptsUsed,
  });

  factory RoundSummary.fromJson(Map<String, dynamic> json) {
    return RoundSummary(
      roundNumber: json['round_number'] ?? 1,
      passed: json['passed'] ?? false,
      score: json['score'] ?? 0,
      attemptsUsed: json['attempts_used'] ?? 0,
    );
  }
}

class ScenarioCompletion {
  final String scenarioName;
  final int roundsCompleted;
  final int totalRounds;
  final int roundsPassed;
  final double overallScore;
  final bool masteryAchieved;
  final List<String> badgesEarned;
  final List<String> communicationTechniquesUnlocked;

  ScenarioCompletion({
    required this.scenarioName,
    required this.roundsCompleted,
    required this.totalRounds,
    required this.roundsPassed,
    required this.overallScore,
    required this.masteryAchieved,
    required this.badgesEarned,
    required this.communicationTechniquesUnlocked,
  });

  factory ScenarioCompletion.fromJson(Map<String, dynamic> json) {
    return ScenarioCompletion(
      scenarioName: json['scenario_name'] ?? '',
      roundsCompleted: json['rounds_completed'] ?? 0,
      totalRounds: json['total_rounds'] ?? 0,
      roundsPassed: json['rounds_passed'] ?? 0,
      overallScore: (json['overall_score'] ?? 0.0).toDouble(),
      masteryAchieved: json['mastery_achieved'] ?? false,
      badgesEarned: List<String>.from(json['badges_earned'] ?? []),
      communicationTechniquesUnlocked: List<String>.from(json['communication_techniques_unlocked'] ?? []),
    );
  }
}

class EvaluationResult {
  final int toneScore;
  final int approachScore;
  final int respectScore;
  final int totalScore;
  final String feedback;
  final bool passed;

  EvaluationResult({
    required this.toneScore,
    required this.approachScore,
    required this.respectScore,
    required this.totalScore,
    required this.feedback,
    required this.passed,
  });

  factory EvaluationResult.fromJson(Map<String, dynamic> json) {
    return EvaluationResult(
      toneScore: json['tone_score'] as int,
      approachScore: json['approach_score'] as int,
      respectScore: json['respect_score'] as int,
      totalScore: json['total_score'] as int,
      feedback: json['feedback'] as String,
      passed: json['passed'] as bool,
    );
  }
}

class RolePlayApiService {
  final String baseUrl;

  RolePlayApiService({required this.baseUrl});

  Future<List<String>> getAvailableScenarios() async {
    final response = await http.get(Uri.parse('$baseUrl/api/roleplay/scenarios/'));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return List<String>.from(data['scenarios'] as List);
    } else {
      throw Exception('Failed to load scenarios: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> getScenarioDetails(String scenarioName, {String? language}) async {
    // Add cache-busting timestamp
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    final queryParams = <String, String>{'t': timestamp.toString()};
    if (language != null) {
      queryParams['language'] = language;
    }

    final uri = Uri.parse('$baseUrl/api/roleplay/scenarios/$scenarioName').replace(
      queryParameters: queryParams,
    );

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to load scenario details: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> startGame({String? scenarioName, String? language}) async {
    final uri = scenarioName != null
        ? Uri.parse('$baseUrl/api/roleplay/game/start?scenario_name=$scenarioName${language != null ? '&language=$language' : ''}')
        : Uri.parse('$baseUrl/api/roleplay/game/start${language != null ? '?language=$language' : ''}');

    final response = await http.post(uri);

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to start game: ${response.statusCode}');
    }
  }

  Future<Map<String, dynamic>> submitResponse(
    String sessionId,
    String parentResponse,
    String teenOpening, {
    String? language,
  }) async {
    final body = {
      'parent_response': parentResponse,
      'teen_opening': teenOpening,
    };

    if (language != null) {
      body['language'] = language;
    }

    final response = await http.post(
      Uri.parse('$baseUrl/api/roleplay/game/respond/$sessionId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('Failed to submit response: ${response.statusCode}');
    }
  }
}

class RolePlayScenario {
  final String id;
  final String titleKey;
  final String backgroundKey;
  final String childOpeningKey;
  final List<String> suggestedResponseKeys;
  bool isCompleted;

  RolePlayScenario({
    required this.id,
    required this.titleKey,
    required this.backgroundKey,
    required this.childOpeningKey,
    required this.suggestedResponseKeys,
    this.isCompleted = false,
  });

  // Helper methods to get translated text
  String getTitle() => titleKey.tr();
  String getBackground() => backgroundKey.tr();
  String getChildOpening() => childOpeningKey.tr();
  List<String> getSuggestedResponses() => suggestedResponseKeys.map((key) => key.tr()).toList();
}

final List<FeedItem> feedItems = [
  FeedItem(title: "Ask about today's highlight", text: "One genuine question at dinner builds trust."),
  FeedItem(title: "Read 10 minutes together", text: "Shared reading beats solo scrolling."),
  FeedItem(title: "Plan a study break", text: "A 5-minute stretch improves focus."),
  FeedItem(title: "Celebrate small wins", text: "Notice effort, not just results."),
  FeedItem(title: "Tomorrow's checklist", text: "Set two priorities before bed."),
  FeedItem(title: "Screen-time agreement", text: "Co-create rules; kids follow what they help design."),
  FeedItem(title: "Praise effort", text: "Name the strategy they used, not just the outcome."),
  FeedItem(title: "1:1 time", text: "10 minutes of undistracted attention strengthens bonds."),
  FeedItem(title: "Focus sprint", text: "Try two 25-5 Pomodoros this evening."),
  FeedItem(title: "Ask why", text: "Explore interests behind a new hobby—it reveals motivations."),
  FeedItem(title: "Plan tomorrow", text: "Pack the bag together; lower morning stress."),
  FeedItem(title: "Family walk", text: "Light exercise improves sleep quality."),
];

final List<String> goals = [
  "Improve study habits",
  "Strengthen parent–child relationship",
  "Explore extracurriculars",
  "Plan university pathway",
];

List<RolePlayScenario> getRolePlayScenarios() {
  return [
    RolePlayScenario(
      id: "messy_room",
      titleKey: "room_cleaning_scenario_title",
      backgroundKey: 'room_cleaning_scenario_background',
      childOpeningKey: 'room_cleaning_child_opening',
      suggestedResponseKeys: [
        'room_cleaning_response_1',
        'room_cleaning_response_2',
        'room_cleaning_response_3',
      ],
    ),
  ];
}


class EduParentApp extends StatelessWidget {
  const EduParentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => AuthService(),
      child: MaterialApp(
        title: 'EduParent Prototype',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
          useMaterial3: true,
        ),
        localizationsDelegates: context.localizationDelegates,
        supportedLocales: context.supportedLocales,
        locale: context.locale,
        home: const AuthWrapper(),
      ),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthService>(
      builder: (context, authService, child) {
        if (authService.isAuthenticated) {
          return const MainScreen();
        } else {
          return const LoginScreen();
        }
      },
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  AppView currentView = AppView.home;
  ReportData? reportData;
  CardStack? currentCardStack;
  int? currentCardStackIndex;
  Function(int)? onCardStackComplete;
  Set<int> completedCardStacks = {};
  VoidCallback? _refreshFeed;

  void _navigateTo(AppView view) {
    setState(() {
      currentView = view;
    });
  }

  void _markCardStackComplete(int index) {
    print('🎯 Main app marking card stack complete - Index: $index');
    setState(() {
      completedCardStacks.add(index);
    });
    print('✅ Main app updated completedCardStacks: $completedCardStacks');
  }


  void _openCardStack(CardStack cardStack, {int? index, Function(int)? onComplete}) {
    print('🏠 Main app _openCardStack called');
    print('📦 Received CardStack: ${cardStack.title}');
    print('🔢 Cards in stack: ${cardStack.cards.length}');
    print('🔄 Setting state...');
    setState(() {
      currentCardStack = cardStack;
      currentCardStackIndex = index;
      onCardStackComplete = onComplete;
      currentView = AppView.cardStack;
    });
    print('✅ State updated: currentView = ${currentView.toString()}');
    print('📱 currentCardStack title: ${currentCardStack?.title}');
  }

  void _showLogoutDialog(BuildContext context, AuthService authService) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('logout_dialog_title'.tr()),
          content: Text('logout_dialog_message'.tr()),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text('logout_dialog_cancel'.tr()),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                authService.logout();
              },
              child: Text('logout'.tr()),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      appBar: AppBar(
        backgroundColor: Colors.white.withOpacity(0.8),
        elevation: 1,
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'app_title'.tr(),
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            if (AppConfig.showDebugInfo) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  AppConfig.environmentName.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
            Consumer<AuthService>(
              builder: (context, authService, child) {
                if (authService.isGuest) {
                  return Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.purple,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          'guest_badge'.tr(),
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ],
        ),
        actions: [
          if (currentView != AppView.home)
            TextButton.icon(
              onPressed: () => _navigateTo(AppView.home),
              icon: const Icon(Icons.arrow_back),
              label: Text('home'.tr()),
            ),
          // Language Selector - only show on home view
          if (currentView == AppView.home)
            PopupMenuButton<Locale>(
              onSelected: (Locale locale) {
                context.setLocale(locale);
                // Refresh feed if available
                if (_refreshFeed != null) {
                  _refreshFeed!();
                }
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
              child: const Padding(
                padding: EdgeInsets.all(8.0),
                child: Icon(Icons.language),
              ),
            ),
          Consumer<AuthService>(
            builder: (context, authService, child) {
              return PopupMenuButton<String>(
                onSelected: (value) {
                  if (value == 'logout') {
                    _showLogoutDialog(context, authService);
                  }
                },
                itemBuilder: (BuildContext context) => [
                  PopupMenuItem<String>(
                    value: 'profile',
                    child: Row(
                      children: [
                        const Icon(Icons.person, size: 18),
                        const SizedBox(width: 8),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              authService.currentUser?.fullName ?? 'User',
                              style: const TextStyle(fontWeight: FontWeight.w600),
                            ),
                            Text(
                              authService.currentUser?.email ?? '',
                              style: const TextStyle(fontSize: 12, color: Colors.black54),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  PopupMenuItem<String>(
                    value: 'logout',
                    child: Row(
                      children: [
                        const Icon(Icons.logout, size: 18),
                        const SizedBox(width: 8),
                        Text('logout'.tr()),
                      ],
                    ),
                  ),
                ],
                child: const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Icon(Icons.account_circle),
                ),
              );
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: _buildCurrentView(),
      ),
    );
  }

  Widget _buildCurrentView() {
    switch (currentView) {
      case AppView.home:
        return HomeView(onNavigate: _navigateTo);
      case AppView.feed:
        return FeedView(
          onOpenCardStack: _openCardStack,
          completedItems: completedCardStacks,
          onRegisterRefresh: (refreshCallback) => _refreshFeed = refreshCallback,
        );
      case AppView.roleplay:
        return const RolePlayView();
      case AppView.dailyActionChallenge:
        return const DailyActionChallengeView();
      case AppView.report:
        return ReportView(data: reportData!);
      case AppView.cardStack:
        return CardStackView(
          cardStack: currentCardStack!,
          onComplete: () {
            // Mark as completed using the simple sync method
            if (currentCardStackIndex != null) {
              _markCardStackComplete(currentCardStackIndex!);
            }
            _navigateTo(AppView.feed);
          }
        );
    }
  }
}

class HomeView extends StatefulWidget {
  final Function(AppView) onNavigate;

  const HomeView({super.key, required this.onNavigate});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // This will trigger rebuild when locale changes
  }

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 600),
      child: GridView.count(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.2,
        children: [
          _buildCard(
            title: '📚 ${'daily_feed_title'.tr()}',
            description: 'daily_feed_description'.tr(),
            buttonText: 'open_feed'.tr(),
            onTap: () => widget.onNavigate(AppView.feed),
          ),
          _buildCard(
            title: '🎭 ${'role_play_practice_title'.tr()}',
            description: 'role_play_practice_description'.tr(),
            buttonText: 'start_role_play'.tr(),
            onTap: () => widget.onNavigate(AppView.roleplay),
          ),
          _buildCard(
            title: '🏆 ${'daily_action_challenge_title'.tr()}',
            description: 'daily_action_challenge_description'.tr(),
            buttonText: 'view_challenges'.tr(),
            onTap: () => widget.onNavigate(AppView.dailyActionChallenge),
          ),
        ],
      ),
    );
  }

  Widget _buildCard({
    required String title,
    required String description,
    required String buttonText,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: Text(
                description,
                style: const TextStyle(fontSize: 14, color: Colors.black54),
              ),
            ),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onTap,
                child: Text(buttonText),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class FeedView extends StatefulWidget {
  final Function(CardStack, {int? index, Function(int)? onComplete}) onOpenCardStack;
  final Set<int> completedItems;
  final Function(VoidCallback)? onRegisterRefresh;

  const FeedView({super.key, required this.onOpenCardStack, required this.completedItems, this.onRegisterRefresh});

  @override
  State<FeedView> createState() => _FeedViewState();
}

class _FeedViewState extends State<FeedView> {
  List<EnhancedFeedItem> feedItems = [];
  Set<int> readSet = {};
  int streak = 0;
  bool isLoading = true;
  String? errorMessageKey;
  Map<String, String>? errorMessageArgs;

  @override
  void initState() {
    super.initState();
    // Don't call _loadEnhancedFeed here - will be called in didChangeDependencies
    _loadLocalData();

    // Register refresh callback with parent
    if (widget.onRegisterRefresh != null) {
      widget.onRegisterRefresh!(_loadEnhancedFeed);
    }
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _loadEnhancedFeed();
  }

  Future<void> _loadEnhancedFeed() async {
    try {
      // Get current language from context
      final languageCode = _getLanguageCode(context.locale);
      final response = await http.get(
        Uri.parse('${AppConfig.apiBaseUrl}/api/feed/enhanced?language=$languageCode'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final itemsJson = jsonData['items'] as List;
        
        setState(() {
          feedItems = itemsJson.map((item) => EnhancedFeedItem.fromJson(item)).toList();
          streak = jsonData['streak'] ?? 0;
          isLoading = false;
          errorMessageKey = null;
          errorMessageArgs = null;
        });
      } else {
        setState(() {
          errorMessageKey = 'feed_loading_error';
          errorMessageArgs = null;
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessageKey = 'feed_generic_error';
        errorMessageArgs = {'message': e.toString()};
        isLoading = false;
      });
    }
  }

  Future<void> _loadLocalData() async {
    final prefs = await SharedPreferences.getInstance();
    final authService = Provider.of<AuthService>(context, listen: false);
    
    // Only load data if user is authenticated
    if (!authService.isAuthenticated || authService.currentUser == null) {
      setState(() {
        readSet = {};
        streak = 0;
      });
      return;
    }
    
    final userId = authService.currentUser!.id;
    final todayKey = _getTodayKey();
    final readData = prefs.getString('feed_read_${userId}_$todayKey');
    final streakData = prefs.getInt('feed_streak_$userId') ?? 0;
    
    setState(() {
      if (readData != null) {
        final List<dynamic> readList = jsonDecode(readData);
        readSet = readList.cast<int>().toSet();
      } else {
        readSet = {};
      }
      streak = streakData;
    });
  }

  String _getTodayKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  Future<void> _toggleRead(int index) async {
    print('🔄 _toggleRead called with index: $index');

    // Check if widget is still mounted before accessing context
    if (!mounted) {
      print('❌ Widget is unmounted, cannot toggle read status');
      return;
    }

    final authService = Provider.of<AuthService>(context, listen: false);

    print('📖 Before toggle - readSet: $readSet');

    // Check mounted again before calling setState
    if (mounted) {
      setState(() {
        if (readSet.contains(index)) {
          readSet.remove(index);
          print('➖ Removed index $index from readSet');
        } else {
          readSet.add(index);
          print('➕ Added index $index to readSet');
        }
      });
      print('📖 After toggle - readSet: $readSet');
    } else {
      print('❌ Widget unmounted before setState, skipping UI update');
      return;
    }

    // Only save to preferences if user is authenticated
    if (!authService.isAuthenticated || authService.currentUser == null) {
      print('❌ User not authenticated, skipping preference save but updating UI');
      return;
    }
    
    final prefs = await SharedPreferences.getInstance();
    final userId = authService.currentUser!.id;
    final todayKey = _getTodayKey();
    
    // Save with user-specific key
    await prefs.setString('feed_read_${userId}_$todayKey', jsonEncode(readSet.toList()));
    
    if (readSet.length >= 3) {
      final alreadyCounted = prefs.getBool('feed_read_${userId}_${todayKey}_counted') ?? false;
      if (!alreadyCounted) {
        await prefs.setInt('feed_streak_$userId', streak + 1);
        await prefs.setBool('feed_read_${userId}_${todayKey}_counted', true);
        setState(() {
          streak = streak + 1;
        });
      }
    }
  }

  Future<void> _openCardStack(String stackId, {int? index}) async {
    print('🔵 Blue button clicked! Stack ID: $stackId');
    try {
      // Get current language
      final languageCode = _getLanguageCode(context.locale);
      print('🌐 Making API call to: ${AppConfig.apiBaseUrl}/api/card-stacks/$stackId?language=$languageCode');
      final response = await http.get(
        Uri.parse('${AppConfig.apiBaseUrl}/api/card-stacks/$stackId?language=$languageCode'),
        headers: {'Content-Type': 'application/json'},
      );

      print('📡 Response status: ${response.statusCode}');
      print('📄 Raw JSON response:');
      print(response.body);

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        print('✅ JSON parsed successfully');
        print('📊 Parsed data keys: ${jsonData.keys}');
        
        final cardStack = CardStack.fromJson(jsonData);
        print('🎯 CardStack created: ${cardStack.title}');
        print('📚 Number of cards: ${cardStack.cards.length}');
        
        print('🔄 Calling widget.onOpenCardStack...');
        widget.onOpenCardStack(cardStack, index: index, onComplete: index != null ? _toggleRead : null);
        print('✅ widget.onOpenCardStack completed');
      } else {
        print('❌ API call failed with status: ${response.statusCode}');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('feed_card_stack_error'.tr())),
        );
      }
    } catch (e) {
      print('💥 Exception caught: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'feed_generic_error'.tr(namedArgs: {'message': e.toString()}),
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (errorMessageKey != null) {
      final message = errorMessageKey!.tr(namedArgs: errorMessageArgs ?? {});
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(message),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  isLoading = true;
                  errorMessageKey = null;
                  errorMessageArgs = null;
                });
                _loadEnhancedFeed();
              },
              child: Text('feed_retry'.tr()),
            ),
          ],
        ),
      );
    }

    final totalItemsCount = feedItems.length;  // Count all items (simple + card_stack)
    final completedCount = widget.completedItems.length;  // Use external completion state
    final isCompleted = completedCount >= totalItemsCount;

    return RefreshIndicator(
      onRefresh: _loadEnhancedFeed,
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'feed_title'.tr(),
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
                ),
                Text(
                  'feed_streak'.tr(namedArgs: {'count': streak.toString()}),
                  style: const TextStyle(fontSize: 14, color: Colors.black54),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'feed_complete_tips'.tr(
                namedArgs: {
                  'total': totalItemsCount.toString(),
                  'completed': completedCount.toString(),
                },
              ),
              style: const TextStyle(fontSize: 14, color: Colors.black54),
            ),
            const SizedBox(height: 16),
            
            ...feedItems.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              
              if (item.type == 'simple') {
                return _buildSimpleItem(index, item.simpleItem!);
              } else {
                return _buildCardStackPreview(index, item.stackPreview!);
              }
            }),
            
            if (isCompleted)
              Container(
                margin: const EdgeInsets.only(top: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Text(
                  'feed_completed_message'.tr(),
                  style: const TextStyle(color: Colors.green, fontSize: 14),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSimpleItem(int index, FeedItem item) {
    final isRead = readSet.contains(index);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isRead ? Colors.green : Colors.grey.shade300,
          width: isRead ? 2 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item.text,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.black87,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            ElevatedButton(
              onPressed: () => _toggleRead(index),
              style: ElevatedButton.styleFrom(
                backgroundColor: isRead ? Colors.grey.shade300 : null,
              ),
              child: Text(isRead ? 'feed_done'.tr() : 'feed_mark_done'.tr()),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCardStackPreview(int index, CardStackPreview preview) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue.shade300, width: 2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.blue.shade100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'feed_card_stack_tag'.tr(),
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
                const Spacer(),
                Text(
                  'feed_card_stack_meta'.tr(
                    namedArgs: {
                      'cards': preview.totalCards.toString(),
                      'minutes': preview.estimatedReadTime.toString(),
                    },
                  ),
                  style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              preview.title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                height: 1.3,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              preview.description,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.black87,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  print('🟦 BUTTON CLICKED! Preview ID: ${preview.id}');
                  _openCardStack(preview.id, index: index);
                },
                icon: const Icon(Icons.play_arrow),
                label: Text('feed_card_stack_start'.tr()),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getLanguageCode(Locale locale) {
    // Convert Flutter locale to backend language code
    if (locale.languageCode == 'zh' && locale.countryCode == 'HK') {
      return 'zh-HK';
    } else if (locale.languageCode == 'en') {
      return 'en';
    }
    return 'zh-HK'; // Default to Cantonese
  }
}

class RolePlayView extends StatefulWidget {
  const RolePlayView({super.key});

  @override
  State<RolePlayView> createState() => _RolePlayViewState();
}

class _RolePlayViewState extends State<RolePlayView> {
  final RolePlayApiService _apiService = RolePlayApiService(baseUrl: AppConfig.apiBaseUrl);
  final TextEditingController _responseController = TextEditingController();

  // State management
  bool _isSelectingScenario = true;
  bool _isLoading = false;
  bool _hasScenariosLoaded = false;
  String? _sessionId;
  List<ScenarioInfo> _availableScenarios = [];
  String _debugInfo = '';

  GameState _gameState = GameState(
    scenarioTitle: 'room_cleaning_scenario_title'.tr(),
    scenarioBackground: 'room_cleaning_scenario_background'.tr(),
    teenOpening: 'room_cleaning_child_opening'.tr(),
  );

  @override
  void initState() {
    super.initState();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Load scenarios after language context is available, but only once
    if (!_hasScenariosLoaded) {
      _hasScenariosLoaded = true;
      _loadAvailableScenarios();
    }
  }

  @override
  void dispose() {
    _responseController.dispose();
    super.dispose();
  }

  Future<void> _loadAvailableScenarios() async {
    setState(() => _isLoading = true);

    try {
      // Get current language from context with fallback
      final currentLocale = context.locale;
      final languageCode = _getLanguageCode(currentLocale);

      // Add cache-busting timestamp
      final timestamp = DateTime.now().millisecondsSinceEpoch;

      setState(() {
        _debugInfo = 'Debug Info:\n'
            'Current Locale: $currentLocale\n'
            'Language Code: $languageCode\n'
            'API Base URL: ${AppConfig.apiBaseUrl}\n'
            'Cache Bust: $timestamp\n\n';
      });

      final scenarioIds = await _apiService.getAvailableScenarios();
      final scenarios = <ScenarioInfo>[];

      for (String scenarioId in scenarioIds) {
        try {
          final apiUrl = '${AppConfig.apiBaseUrl}/api/roleplay/scenarios/$scenarioId?language=$languageCode&t=$timestamp';
          setState(() {
            _debugInfo += 'Fetching: $scenarioId\n'
                'URL: $apiUrl\n';
          });

          final details = await _apiService.getScenarioDetails(scenarioId, language: languageCode);
          final title = details["title"] ?? "Unknown";

          setState(() {
            _debugInfo += 'Response Title: $title\n\n';
          });

          scenarios.add(ScenarioInfo.fromJson(scenarioId, details));
        } catch (e) {
          setState(() {
            _debugInfo += 'Error for $scenarioId: $e\n\n';
          });

          // If we can't get details, create a basic entry
          scenarios.add(ScenarioInfo(
            id: scenarioId,
            title: _getScenarioDisplayName(scenarioId),
            background: 'Practice scenario',
            teenOpening: 'Let\'s practice!',
            isMultiRound: scenarioId.contains('school_dropoff'),
          ));
        }
      }

      setState(() {
        _availableScenarios = scenarios;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _debugInfo += 'Critical Error: $e\n';
        _isLoading = false;
        // Fallback scenarios
        _availableScenarios = [
          ScenarioInfo(
            id: 'messy_room',
            title: 'Messy Room',
            background: 'Practice helping your teen clean their messy room.',
            teenOpening: 'Mom (Dad), I\'ll clean it later, I\'m tired now!',
            isMultiRound: false,
          ),
          ScenarioInfo(
            id: 'school_dropoff_anxiety',
            title: 'School Drop-off Anxiety',
            background: 'Help your child overcome separation anxiety during school drop-off through progressive challenges.',
            teenOpening: 'I don\'t want to go in! Don\'t leave me!',
            isMultiRound: true,
          ),
        ];
      });
    }
  }

  String _getScenarioDisplayName(String scenarioId) {
    switch (scenarioId) {
      case 'messy_room':
        return 'Messy Room';
      case 'school_dropoff_anxiety':
        return 'School Drop-off Anxiety';
      default:
        return scenarioId.replaceAll('_', ' ').split(' ')
            .map((word) => word[0].toUpperCase() + word.substring(1))
            .join(' ');
    }
  }

  Future<void> _startScenario(String scenarioId) async {
    try {
      // Get current language from context
      final languageCode = _getLanguageCode(context.locale);

      final gameData = await _apiService.startGame(
        scenarioName: scenarioId,
        language: languageCode,
      );
      setState(() {
        _sessionId = gameData['session_id'] as String;
        _isSelectingScenario = false;
        final scenario = gameData['scenario'] as Map<String, dynamic>;

        _gameState = GameState(
          scenarioTitle: scenario['title'] as String,
          scenarioBackground: scenario['background'] as String,
          teenOpening: scenario['teen_opening'] as String,
          isMultiRound: scenario['is_multi_round'] ?? false,
          currentRound: gameData['current_round'] ?? 1,
          maxRounds: gameData['max_rounds'] ?? 1,
          maxRoundAttempts: 3,
        );
      });
    } catch (e) {
      // Fallback to static content if API fails
      setState(() {
        _gameState = GameState(
          scenarioTitle: 'School Drop-off Anxiety',
          scenarioBackground: 'Your child is feeling anxious about school drop-off. Practice helping them through this challenge.',
          teenOpening: 'I don\'t want to go in! Don\'t leave me!',
          isMultiRound: true,
          maxRounds: 3,
          maxRoundAttempts: 3,
        );
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('API unavailable, using static content: $e')),
        );
      }
    }
  }

  String _getLanguageCode(Locale locale) {
    // Convert Flutter locale to backend language code
    if (locale.languageCode == 'zh' && locale.countryCode == 'HK') {
      return 'zh-HK';
    } else if (locale.languageCode == 'en') {
      return 'en';
    }
    return 'zh-HK'; // Default to Cantonese
  }

  Future<void> _submitResponse() async {
    if (_responseController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('submit_response'.tr())),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      if (_sessionId != null) {
        // Get current language from context
        final languageCode = _getLanguageCode(context.locale);

        // Try API submission
        final result = await _apiService.submitResponse(
          _sessionId!,
          _responseController.text,
          _gameState.teenOpening,
          language: languageCode,
        );

        if (_gameState.isMultiRound && result['is_multi_round'] == true) {
          // Handle multi-round response
          await _handleMultiRoundResponse(result);
        } else {
          // Handle single-round response (legacy)
          await _handleSingleRoundResponse(result);
        }
      } else {
        // Fallback: simple static response when backend unavailable
        await _handleFallbackResponse();
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _handleMultiRoundResponse(Map<String, dynamic> result) async {
    final teenResponse = result['teen_response'] as String?;
    final gameCompleted = result['game_completed'] as bool? ?? false;
    final currentRound = result['current_round'] as int? ?? 1;
    final roundAttemptsUsed = result['round_attempts_used'] as int? ?? 0;

    MultiRoundEvaluationResult? multiEval;
    if (result['evaluation'] != null) {
      multiEval = MultiRoundEvaluationResult.fromJson(result['evaluation'] as Map<String, dynamic>);
    }

    ScenarioCompletion? completion;
    if (result['scenario_completion'] != null) {
      completion = ScenarioCompletion.fromJson(result['scenario_completion'] as Map<String, dynamic>);
    }

    List<RoundSummary> roundsHistory = [];
    if (result['rounds_summary'] != null) {
      roundsHistory = (result['rounds_summary'] as List)
          .map((round) => RoundSummary.fromJson(round as Map<String, dynamic>))
          .toList();
    }

    setState(() {
      _gameState = _gameState.copyWith(
        parentResponse: _responseController.text,
        currentRound: currentRound,
        roundAttempts: roundAttemptsUsed,
        multiRoundEvaluation: multiEval,
        teenResponse: teenResponse,
        gameCompleted: gameCompleted,
        finalScore: result['final_score'] as int?,
        roundsHistory: roundsHistory,
        scenarioCompletion: completion,
      );
      _responseController.clear();
      _isLoading = false;
    });
  }

  Future<void> _handleSingleRoundResponse(Map<String, dynamic> result) async {
    final evaluation = result['evaluation'] as Map<String, dynamic>;
    final teenResponse = result['teen_response'] as String;
    final gameCompleted = result['game_completed'] as bool;
    final finalScore = result['final_score'] as int?;

    final evaluationResult = EvaluationResult(
      toneScore: evaluation['tone_score'] as int,
      approachScore: evaluation['approach_score'] as int,
      respectScore: evaluation['respect_score'] as int,
      totalScore: evaluation['total_score'] as int,
      feedback: evaluation['feedback'] as String,
      passed: evaluation['passed'] as bool,
    );

    setState(() {
      _gameState = _gameState.copyWith(
        parentResponse: _responseController.text,
        attempts: _gameState.attempts + 1,
        evaluation: evaluationResult,
        teenResponse: teenResponse,
        gameCompleted: gameCompleted,
        finalScore: finalScore,
      );
      _responseController.clear();
      _isLoading = false;
    });
  }

  Future<void> _handleFallbackResponse() async {
    setState(() {
      _gameState = _gameState.copyWith(
        parentResponse: _responseController.text,
        attempts: _gameState.attempts + 1,
        evaluation: EvaluationResult(
          toneScore: 3,
          approachScore: 3,
          respectScore: 3,
          totalScore: 9,
          feedback: 'Backend unavailable. Please check server connection.',
          passed: true,
        ),
        teenResponse: 'Thanks for understanding! I\'ll try to be better.',
        gameCompleted: true,
        finalScore: 9,
      );
      _responseController.clear();
      _isLoading = false;
    });
  }

  Future<void> _reset() async {
    setState(() {
      _isLoading = true;
      _isSelectingScenario = true;
      _hasScenariosLoaded = false; // Allow scenarios to be reloaded
      _sessionId = null;
      _responseController.clear();
    });

    try {
      await _loadAvailableScenarios();
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Reset failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isSelectingScenario) {
      return _buildScenarioSelection();
    } else {
      return _buildGameInterface();
    }
  }

  Widget _buildScenarioSelection() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'choose_practice_scenario'.tr(),
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),

          if (_isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32.0),
                child: CircularProgressIndicator(),
              ),
            )
          else
            ..._availableScenarios.map((scenario) => _buildScenarioCard(scenario)),
        ],
      ),
    );
  }

  Widget _buildScenarioCard(ScenarioInfo scenario) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    scenario.title,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                _buildScenarioTypeBadge(scenario),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              scenario.background,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.chat_bubble_outline,
                  size: 16,
                  color: Colors.grey[600],
                ),
                const SizedBox(width: 4),
                Text(
                  '${'scenario_opening'.tr()}: "${scenario.teenOpening}"',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontStyle: FontStyle.italic,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => _startScenario(scenario.id),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  backgroundColor: scenario.isMultiRound ? Colors.purple : Colors.blue,
                ),
                child: Text(
                  'start_practice'.tr(),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScenarioTypeBadge(ScenarioInfo scenario) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: scenario.isMultiRound ? Colors.purple[100] : Colors.blue[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        scenario.isMultiRound ? 'multi_round'.tr() : 'single_round'.tr(),
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.bold,
          color: scenario.isMultiRound ? Colors.purple[800] : Colors.blue[800],
        ),
      ),
    );
  }

  Widget _buildGameInterface() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: _reset,
                    tooltip: 'back_to_scenarios'.tr(),
                  ),
                  Text(
                    '🎭 ${'role_play_practice_title'.tr()}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
              if (_gameState.gameCompleted)
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: _reset,
                  tooltip: 'Reset',
                ),
            ],
          ),
          if (_gameState.isMultiRound) ...[
            const SizedBox(height: 8),
            _buildRoundIndicator(),
          ],
          const SizedBox(height: 16),
          _buildScenarioBackgroundCard(),
          const SizedBox(height: 16),
          _buildTeenSpeechBubble(),
          const SizedBox(height: 24),
          if (!_gameState.gameCompleted) ...[
            _buildResponseInput(),
            const SizedBox(height: 16),
          ],
          if (_gameState.parentResponse?.isNotEmpty == true) ...[
            _buildParentResponseBubble(),
            const SizedBox(height: 16),
          ],
          if (_gameState.evaluation != null || _gameState.multiRoundEvaluation != null) ...[
            _buildEvaluationCard(),
            const SizedBox(height: 16),
          ],
          if (_gameState.teenResponse != null) ...[
            _buildTeenResponseBubble(),
            const SizedBox(height: 16),
          ],
          if (_gameState.gameCompleted) _buildFinalResults(),
        ],
      ),
    );
  }

  Widget _buildScenarioBackgroundCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'scenario_background'.tr(),
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const Divider(),
            Text(
              _gameState.scenarioBackground,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTeenSpeechBubble() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'child_says'.tr(),
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              _gameState.teenOpening,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResponseInput() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'your_response'.tr(),
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _responseController,
          decoration: InputDecoration(
            hintText: 'Type your response as a parent...',
            border: const OutlineInputBorder(),
          ),
          maxLines: 3,
          enabled: !_isLoading,
        ),
        const SizedBox(height: 12),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitResponse,
          child: _isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text('submit_response'.tr()),
        ),
      ],
    );
  }

  Widget _buildEvaluationCard() {
    if (_gameState.multiRoundEvaluation != null) {
      return _buildMultiRoundEvaluationCard();
    } else if (_gameState.evaluation != null) {
      return _buildSingleRoundEvaluationCard();
    }
    return Container();
  }

  Widget _buildSingleRoundEvaluationCard() {
    final eval = _gameState.evaluation!;
    return Card(
      color: eval.passed ? Colors.green[50] : Colors.orange[50],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  eval.passed ? Icons.check_circle : Icons.warning,
                  color: eval.passed ? Colors.green : Colors.orange,
                ),
                const SizedBox(width: 8),
                Text(
                  '📊 Evaluation Results',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(),
            _buildScoreRow('Tone', eval.toneScore, 4),
            _buildScoreRow('Approach', eval.approachScore, 3),
            _buildScoreRow('Respect', eval.respectScore, 3),
            const Divider(),
            _buildScoreRow('Total Score', eval.totalScore, 10, isTotal: true),
            const SizedBox(height: 12),
            Text(
              '💬 ${eval.passed ? "Passed!" : "Score too low (need ≥ 7)"}',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: eval.passed ? Colors.green[700] : Colors.orange[700],
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '💡 Feedback:\n${eval.feedback}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMultiRoundEvaluationCard() {
    final eval = _gameState.multiRoundEvaluation!;
    return Card(
      color: eval.passed ? Colors.green[50] : Colors.orange[50],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  eval.passed ? Icons.check_circle : Icons.warning,
                  color: eval.passed ? Colors.green : Colors.orange,
                ),
                const SizedBox(width: 8),
                Text(
                  '📊 Round ${eval.roundNumber} Evaluation',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(),
            // Dynamic criteria scoring
            ...eval.criteriaScores.entries.map((entry) {
              final maxScore = _getMaxScoreForCriterion(entry.key);
              return _buildScoreRow(_formatCriterionName(entry.key), entry.value, maxScore);
            }),
            const Divider(),
            _buildScoreRow('Total Score', eval.totalScore, eval.maxPossibleScore, isTotal: true),
            const SizedBox(height: 12),
            Text(
              '💬 ${eval.passed ? "Round Passed!" : "Round not passed (need ≥ 7)"}',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: eval.passed ? Colors.green[700] : Colors.orange[700],
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              '💡 Overall Feedback:\n${eval.feedback}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (eval.detailedFeedback.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                'Detailed Feedback:',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 4),
              ...eval.detailedFeedback.entries.map((entry) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 4.0),
                  child: Text(
                    '• ${_formatCriterionName(entry.key)}: ${entry.value}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                );
              }),
            ],
          ],
        ),
      ),
    );
  }

  int _getMaxScoreForCriterion(String criterion) {
    const maxScores = {
      "emotion_acknowledgment": 3, "tone_empathy": 2, "solution_approach": 3,
      "fear_validation": 4, "concrete_reassurance": 3, "collaborative_approach": 3,
      "transition_strategy": 4, "child_agency": 3, "follow_through_clarity": 3,
    };
    return maxScores[criterion] ?? 3;
  }

  String _formatCriterionName(String criterion) {
    return criterion
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }

  Widget _buildScoreRow(String label, int score, int max, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: isTotal ? FontWeight.bold : null,
                ),
          ),
          Text(
            '$score/$max',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: isTotal ? FontWeight.bold : null,
                  color: isTotal ? Theme.of(context).colorScheme.primary : null,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildTeenResponseBubble() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: _getTeenResponseColor(),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Teen Response',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              _gameState.teenResponse!,
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildParentResponseBubble() {
    return Align(
      alignment: Alignment.centerRight,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.blue[100],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'parent_says'.tr(),
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: Colors.blue[600],
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              _gameState.parentResponse ?? '',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoundIndicator() {
    if (!_gameState.isMultiRound) return Container();

    return Card(
      color: Colors.blue[50],
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Round ${_gameState.currentRound} of ${_gameState.maxRounds}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            Row(
              children: List.generate(_gameState.maxRounds, (index) {
                final roundNumber = index + 1;
                final isCompleted = _gameState.roundsHistory.any((r) => r.roundNumber == roundNumber);
                final isPassed = _gameState.roundsHistory
                    .where((r) => r.roundNumber == roundNumber)
                    .any((r) => r.passed);
                final isCurrent = _gameState.currentRound == roundNumber;

                return Container(
                  margin: const EdgeInsets.only(left: 4),
                  child: CircleAvatar(
                    radius: 12,
                    backgroundColor: isCurrent
                        ? Colors.blue
                        : isCompleted
                            ? (isPassed ? Colors.green : Colors.orange)
                            : Colors.grey[300],
                    child: Text(
                      '$roundNumber',
                      style: TextStyle(
                        color: (isCurrent || isCompleted) ? Colors.white : Colors.black,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                );
              }),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFinalResults() {
    if (_gameState.isMultiRound && _gameState.scenarioCompletion != null) {
      return _buildMultiRoundCompletion();
    }

    return Card(
      color: _gameState.finalScore != null ? Colors.green[100] : Colors.grey[100],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(
              _gameState.finalScore != null ? Icons.emoji_events : Icons.assignment,
              size: 48,
              color: _gameState.finalScore != null ? Colors.green[700] : Colors.grey[600],
            ),
            const SizedBox(height: 12),
            Text(
              _gameState.finalScore != null
                  ? '🎮 Game Completed!'
                  : '🎮 Game Ended',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            if (_gameState.finalScore != null) ...[
              const SizedBox(height: 8),
              Text(
                'Final Score: ${_gameState.finalScore}/10',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ] else ...[
              const SizedBox(height: 8),
              const Text('Keep practicing!'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMultiRoundCompletion() {
    final completion = _gameState.scenarioCompletion!;

    return Card(
      color: completion.masteryAchieved ? Colors.green[100] : Colors.blue[100],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(
              completion.masteryAchieved ? Icons.emoji_events : Icons.stars,
              size: 48,
              color: completion.masteryAchieved ? Colors.green[700] : Colors.blue[700],
            ),
            const SizedBox(height: 12),
            Text(
              completion.masteryAchieved ? '🏆 Scenario Mastered!' : '📋 Scenario Complete',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              'Overall Score: ${completion.overallScore.toStringAsFixed(1)}/10',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Rounds Passed: ${completion.roundsPassed}/${completion.totalRounds}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            if (completion.badgesEarned.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                'Badges Earned:',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 4),
              Wrap(
                children: completion.badgesEarned.map((badge) {
                  return Container(
                    margin: const EdgeInsets.all(2),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.amber[200],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '🏅 $badge',
                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color? _getTeenResponseColor() {
    // Check single-round evaluation first
    if (_gameState.evaluation != null) {
      return _gameState.evaluation!.passed ? Colors.green[100] : Colors.grey[300];
    }

    // Check multi-round evaluation
    if (_gameState.multiRoundEvaluation != null) {
      return _gameState.multiRoundEvaluation!.passed ? Colors.green[100] : Colors.grey[300];
    }

    // Default to neutral color if no evaluation available yet
    return Colors.blue[50];
  }
}

class DailyActionChallengeView extends StatefulWidget {
  const DailyActionChallengeView({super.key});

  @override
  State<DailyActionChallengeView> createState() => _DailyActionChallengeViewState();
}

class _DailyActionChallengeViewState extends State<DailyActionChallengeView> {
  bool _hasCheckedIn = false;
  bool _reflectionSaved = false;
  int _selectedRating = 0;
  String? _reflectionNote;

  Widget _buildSection(BuildContext context, String titleKey, String contentKey) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          titleKey.tr(),
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Text(
          contentKey.tr(),
          style: const TextStyle(fontSize: 14, height: 1.5),
        ),
      ],
    );
  }

  Future<_ReflectionResult?> _openReflectionDialog() async {
    int tempRating = _selectedRating;
    final controller = TextEditingController(text: _reflectionNote ?? '');

    final result = await showDialog<_ReflectionResult>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (dialogContext, setDialogState) {
            return AlertDialog(
              title: Text('daily_guidance_reflection_title'.tr()),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(5, (index) {
                      final starIndex = index + 1;
                      return IconButton(
                        icon: Icon(
                          starIndex <= tempRating ? Icons.star : Icons.star_border,
                          color: Colors.amber,
                        ),
                        onPressed: () {
                          setDialogState(() {
                            tempRating = starIndex;
                          });
                        },
                      );
                    }),
                  ),
                  const SizedBox(height: 12),
                  Text('daily_guidance_reflection_note_label'.tr()),
                  const SizedBox(height: 8),
                  TextField(
                    controller: controller,
                    maxLines: 3,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(dialogContext).pop();
                  },
                  child: Text('daily_guidance_reflection_skip'.tr()),
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(dialogContext).pop(
                      _ReflectionResult(
                        rating: tempRating,
                        note: controller.text.trim(),
                      ),
                    );
                  },
                  child: Text('daily_guidance_reflection_save'.tr()),
                ),
              ],
            );
          },
        );
      },
    );

    controller.dispose();
    return result;
  }

  Future<void> _handleTryIt() async {
    final result = await _openReflectionDialog();

    setState(() {
      _hasCheckedIn = true;

      if (result != null) {
        _selectedRating = result.rating;
        _reflectionNote = result.note;
        _reflectionSaved = result.rating > 0 || result.note.isNotEmpty;
      } else {
        _selectedRating = 0;
        _reflectionNote = null;
        _reflectionSaved = false;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(vertical: 16),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade200),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildSection(context, 'daily_guidance_advice_title', 'daily_guidance_advice_text'),
            const SizedBox(height: 16),
            _buildSection(context, 'daily_guidance_communication_title', 'daily_guidance_communication_text'),
            const SizedBox(height: 16),
            _buildSection(context, 'daily_guidance_affirmation_title', 'daily_guidance_affirmation_text'),
            const SizedBox(height: 16),
            _buildSection(context, 'daily_guidance_practice_title', 'daily_guidance_practice_text'),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _handleTryIt,
                icon: Icon(
                  _hasCheckedIn ? Icons.check_circle : Icons.radio_button_unchecked,
                  color: _hasCheckedIn ? Colors.green : null,
                ),
                label: Text('daily_guidance_try_button'.tr()),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(48),
                ),
              ),
            ),
            if (_reflectionSaved && _selectedRating > 0) ...[
              const SizedBox(height: 16),
              Row(
                children: List.generate(
                  _selectedRating,
                  (index) => const Icon(Icons.star, color: Colors.amber),
                ),
              ),
            ],
            if (_reflectionSaved && _reflectionNote != null && _reflectionNote!.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                _reflectionNote!,
                style: const TextStyle(fontSize: 14, height: 1.5),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ReflectionResult {
  final int rating;
  final String note;

  const _ReflectionResult({required this.rating, required this.note});
}

String getScenarioIcon(String scenarioId) {
  switch (scenarioId) {
    case "messy_room":
      return "🧹";
    case "phone_distraction":
      return "📱";
    case "curfew_argument":
      return "🌙";
    default:
      return "🎭";
  }
}

class ReportView extends StatelessWidget {
  final ReportData data;

  const ReportView({super.key, required this.data});

  String _getRecommendation(String goal) {
    switch (goal) {
      case "Improve study habits":
        return 'report_recommendation_improve_study'.tr();
      case "Strengthen parent–child relationship":
        return 'report_recommendation_strengthen_relationship'.tr();
      case "Explore extracurriculars":
        return 'report_recommendation_explore_extracurriculars'.tr();
      case "Plan university pathway":
        return 'report_recommendation_plan_university'.tr();
      default:
        return 'report_recommendation_default'.tr();
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'report_title'.tr(),
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'report_selected_goal'.tr(),
                  style: const TextStyle(fontSize: 14, color: Colors.black54),
                ),
                const SizedBox(height: 4),
                Text(
                  data.goal,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                if (data.note.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    'report_parent_note'.tr(),
                    style: const TextStyle(fontSize: 14, color: Colors.black54),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    data.note,
                    style: const TextStyle(fontSize: 16),
                  ),
                ],
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 16),
                Text(
                  'report_recommendation'.tr(),
                  style: const TextStyle(fontSize: 14, color: Colors.black54),
                ),
                const SizedBox(height: 4),
                Text(
                  _getRecommendation(data.goal),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 16),
                Text(
                  'report_tiny_action'.tr(),
                  style: const TextStyle(fontSize: 14, color: Colors.black54),
                ),
                const SizedBox(height: 4),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'report_action_item_one'.tr(),
                      style: const TextStyle(fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'report_action_item_two'.tr(),
                      style: const TextStyle(fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'report_action_item_three'.tr(),
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'report_prototype_notice'.tr(),
            style: const TextStyle(fontSize: 12, color: Colors.black38),
          ),
        ],
      ),
    );
  }
}

class CardStackView extends StatefulWidget {
  final CardStack cardStack;
  final VoidCallback onComplete;

  const CardStackView({super.key, required this.cardStack, required this.onComplete});

  @override
  State<CardStackView> createState() => _CardStackViewState();
}

class _CardStackViewState extends State<CardStackView> {
  int currentCardIndex = 0;
  bool showSummary = false;
  bool showActionQuest = false;
  String actionResponse = '';
  final TextEditingController _responseController = TextEditingController();

  void _nextCard() {
    setState(() {
      if (currentCardIndex < widget.cardStack.cards.length - 1) {
        currentCardIndex++;
      } else {
        showSummary = true;
      }
    });
  }

  void _previousCard() {
    setState(() {
      if (showSummary) {
        showSummary = false;
        showActionQuest = false;
      } else if (currentCardIndex > 0) {
        currentCardIndex--;
      }
    });
  }

  void _showActionQuest() {
    setState(() {
      showActionQuest = true;
    });
  }

  void _submitResponse() {
    // TODO: Save response to backend
    setState(() {
      actionResponse = _responseController.text;
    });
    
    // Mark as completed and navigate back
    widget.onComplete();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.cardStack.title),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Container(
        color: Colors.red.shade100, // Debug: colored background to see if container renders
        child: Column(
          children: [
            Expanded(
              child: showActionQuest
                  ? _buildActionQuestView()
                  : showSummary
                      ? _buildSummaryView()
                      : _buildCardView(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCardView() {
    print('🔍 _buildCardView called');
    
    // Safety check
    if (widget.cardStack.cards.isEmpty) {
      print('❌ No cards available');
      return Center(
        child: Text(
          'card_stack_no_cards'.tr(),
          style: const TextStyle(fontSize: 20),
        ),
      );
    }
    
    if (currentCardIndex >= widget.cardStack.cards.length) {
      print('❌ Invalid card index: $currentCardIndex >= ${widget.cardStack.cards.length}');
      return Center(
        child: Text(
          'card_stack_invalid_index'.tr(),
          style: const TextStyle(fontSize: 20),
        ),
      );
    }
    
    final card = widget.cardStack.cards[currentCardIndex];
    print('🔍 Rendering card: ${card.title}');
    
    return Container(
      color: Colors.green.shade100, // Debug: different color for card view
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Simple debug info
          Container(
            color: Colors.blue.shade100,
            padding: const EdgeInsets.all(8),
            child: Text(
              'card_stack_progress'.tr(
                namedArgs: {
                  'current': (currentCardIndex + 1).toString(),
                  'total': widget.cardStack.totalCards.toString(),
                  'title': card.title,
                },
              ),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 16),
          
          // Simple content (no markdown for now)
          Expanded(
            child: Container(
              color: Colors.white,
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    card.title,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'card_stack_content_length'.tr(
                      namedArgs: {'count': card.content.length.toString()},
                    ),
                    style: const TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: SingleChildScrollView(
                      child: Text(
                        card.content,
                        style: const TextStyle(fontSize: 16),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          // Simple navigation
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              ElevatedButton(
                onPressed: currentCardIndex > 0 ? _previousCard : null,
                child: Text('previous'.tr()),
              ),
              ElevatedButton(
                onPressed: _nextCard,
                child: Text(
                  currentCardIndex == widget.cardStack.cards.length - 1
                      ? 'summary'.tr()
                      : 'next'.tr(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryView() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            child: Text(
              'card_stack_summary_heading'.tr(),
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
          
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'card_stack_summary_highlights'.tr(),
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  widget.cardStack.summary,
                  style: const TextStyle(
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Row(
                  children: [
                    OutlinedButton(
                      onPressed: _previousCard,
                      child: Text('card_stack_summary_review'.tr()),
                    ),
                    const Spacer(),
                    if (widget.cardStack.actionQuest != null)
                      ElevatedButton(
                        onPressed: _showActionQuest,
                        child: Text('card_stack_summary_action'.tr()),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: widget.onComplete,
                    icon: const Icon(Icons.check_circle),
                    label: Text('feed_mark_done'.tr()),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionQuestView() {
    // Return empty container if actionQuest is null
    if (widget.cardStack.actionQuest == null) {
      return Container();
    }

    final actionQuest = widget.cardStack.actionQuest!;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            child: Text(
              actionQuest.title,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
          ),
          
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 16),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.green.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.green.shade200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'card_stack_action_section_title'.tr(),
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  actionQuest.prompt,
                  style: const TextStyle(
                    fontSize: 16,
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
          
          Container(
            margin: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'card_stack_action_prompt_title'.tr(),
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _responseController,
                  maxLines: 6,
                  decoration: InputDecoration(
                    hintText: actionQuest.inputPlaceholder,
                    border: const OutlineInputBorder(),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    OutlinedButton(
                      onPressed: () => setState(() => showActionQuest = false),
                      child: Text('card_stack_action_back'.tr()),
                    ),
                    const Spacer(),
                    ElevatedButton(
                      onPressed: _responseController.text.trim().isNotEmpty ? _submitResponse : null,
                      child: Text('card_stack_action_complete'.tr()),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _responseController.dispose();
    super.dispose();
  }
}
