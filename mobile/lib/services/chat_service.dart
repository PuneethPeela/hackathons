/// Chat service interface and implementation
abstract class IChatService {
  Future<ChatMessage> sendMessage(String message, String conversationId);
  Stream<ChatMessage> streamResponse(String message);
  Future<List<ChatMessage>> getHistory(String conversationId);
}

class ChatMessage {
  final String id;
  final String content;
  final String role;
  final DateTime timestamp;
  
  ChatMessage({
    required this.id,
    required this.content,
    required this.role,
    required this.timestamp,
  });
}

class ChatService implements IChatService {
  @override
  Future<ChatMessage> sendMessage(String message, String conversationId) async {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Stream<ChatMessage> streamResponse(String message) {
    // To be implemented
    throw UnimplementedError();
  }

  @override
  Future<List<ChatMessage>> getHistory(String conversationId) async {
    // To be implemented
    throw UnimplementedError();
  }
}
